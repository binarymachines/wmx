#!/usr/bin/env python

import json



class TelemetryContext(object):
    def __init__(self, **kwargs):
        self.local_file = kwargs['local_storage_file']


    def store_local(self, json_rec):
        with open(self.local_file, 'a+') as f:
            f.write(json.dumps(json_rec))
            f.write('\n')
        
