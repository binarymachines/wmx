
#!/usr/bin/env python

 
import uuid
from snap import snap
from snap import core
import json
from datetime import datetime
from snap.loggers import transform_logger as log



class ObjectFactory(object):

    @classmethod
    def create_db_object(cls, table_name, db_svc, **kwargs):
        DbObject = getattr(db_svc.Base.classes, table_name)
        return DbObject(**kwargs)



def convert_to_timestamp(raw_date_string: str):
    
    #  "2021-10-01T08:33:00"

    date_string = raw_date_string.split('.')[0]

    date_tokens = date_string.split('T')
    if len(date_tokens) != 2:
        raise Exception(f'Unsupported date format: {date_string}')

    date_string = f'{date_tokens[0]} {date_tokens[1]}'
    date_time = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    return datetime.timestamp(date_time)


def convert_to_datetime(raw_date_string: str):
    '''
    On the input, we are actually getting a string that looks like this:

    "2023-01-11T18:03:59.423556"

    So I just needed to get rid of the value after the period, which represents milliseconds.
    (we don't need that much precision for our purposes)

    '''
   
    date_string = raw_date_string.split('.')[0]

    date_tokens = date_string.split('T')
    if len(date_tokens) != 2:
        raise Exception(f'Unsupported date format: {date_string}')

    date_string = f'{date_tokens[0]} {date_tokens[1]}'
    date_time = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    return date_time


def ping_func(input_data, service_objects, **kwargs):

    return core.TransformStatus(json.dumps({'ok': True, 'message': 'telemetry service is alive.'}))



def itemequip_func(input_data, service_objects, **kwargs):

    '''
                                Table "public.fact_item_action"
        Column      |            Type             | Collation | Nullable | Default 
    ------------------+-----------------------------+-----------+----------+---------
    id               | uuid                        |           | not null | 
    item_id          | character varying(255)      |           | not null | 
    event_timestamp  | timestamp without time zone |           |          | 
    time_minute_id   | integer                     |           |          | 
    time_hour_id     | integer                     |           |          | 
    date_day_id      | integer                     |           |          | 
    date_month_id    | integer                     |           |          | 
    date_year_id     | integer                     |           |          | 
    game_instance_id | character varying(64)       |           | not null | 
    action_type_id   | integer                     |           | not null | 

    '''

    input_data['timestamp'] = datetime.now().isoformat()

    db_svc = service_objects.lookup('db')

    with db_svc.txn_scope() as session:

        new_record = dict()
        new_record['id'] = str(uuid.uuid4())
        new_record['item_id'] = input_data['item_id']
        new_record['event_timestamp'] = convert_to_datetime(input_data['timestamp'])
        new_record['time_minute_id'] = 1
        new_record['time_hour_id'] = 1
        new_record['date_day_id'] = 1
        new_record['date_month_id'] = 1
        new_record['date_year_id'] = 1
        new_record['game_instance_id'] = 'abc123'
        new_record['action_type_id'] = 100

        db_record = ObjectFactory.create_db_object('fact_item_action', db_svc, **new_record)

        session.add(db_record)

    return core.TransformStatus(json.dumps({'ok': True, 'message': 'item-equip telemetry message received.'}))
    
    


