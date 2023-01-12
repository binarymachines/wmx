#!/usr/bin/env python


import os, sys
import json
from json.decoder import JSONDecodeError
from snap import snap, common
from xfile_utils import *
from collections import namedtuple
from contextlib import contextmanager
import datetime
import time

import sqlalchemy as sqla
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy_utils import UUIDType
import secrets # requires Python 3.6

from mercury import mlog

import uuid
import psycopg2


class TelemetryContext(object):
    def __init__(self, **kwargs):
        self.local_file = kwargs['local_storage_file']


    def store_local(self, json_rec):
        with open(self.local_file, 'a+') as f:
            f.write(json.dumps(json_rec))
            f.write('\n')
        
POSTGRESQL_SVC_PARAM_NAMES = [
    'host',
    'port',
    'dbname',
    'username',
    'password'
]

class PostgreSQLService(object):
    def __init__(self, **kwargs):
        kwreader = common.KeywordArgReader(*POSTGRESQL_SVC_PARAM_NAMES)
        kwreader.read(**kwargs)

        self.db_name = kwargs['dbname']
        self.host = kwargs['host']
        self.port = int(kwargs.get('port', 5432))
        self.username = kwargs['username']
        self.password = kwargs['password']        
        self.schema = kwargs.get('schema', 'public')
        self.metadata = None
        self.engine = None
        self.session_factory = None
        self.Base = None
        self.url = None

        url_template = '{db_type}://{user}:{passwd}@{host}:{port}/{database}'
        db_url = url_template.format(db_type='postgresql+psycopg2',
                                     user=self.username,
                                     passwd=self.password,
                                     host=self.host,
                                     port=self.port,
                                     database=self.db_name)
    
        retries = 0
        connected = False
        while not connected and retries < 3:
            try:
                self.engine = sqla.create_engine(db_url, echo=False)
                self.metadata = MetaData(schema=self.schema)
                self.Base = automap_base(bind=self.engine, metadata=self.metadata)
                self.Base.prepare(self.engine, reflect=True)
                self.metadata.reflect(bind=self.engine)
                self.session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

                # this is required. See comment in SimpleRedshiftService 
                connection = self.engine.connect()                
                connection.close()
                connected = True
                print('### Connected to PostgreSQL DB.', file=sys.stderr)
                self.url = db_url

            except Exception as err:
                print(err, file=sys.stderr)
                print(err.__class__.__name__, file=sys.stderr)
                print(err.__dict__, file=sys.stderr)
                time.sleep(1)
                retries += 1
            
        if not connected:
            raise Exception('!!! Unable to connect to PostgreSQL db on host %s at port %s.' % 
                            (self.host, self.port))

    @contextmanager
    def txn_scope(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


    @contextmanager    
    def connect(self):
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()
