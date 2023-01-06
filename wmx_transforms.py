
#!/usr/bin/env python

 
from snap import snap
from snap import core
import json
from snap.loggers import transform_logger as log

import datetime



def ping_func(input_data, service_objects, **kwargs):

    return core.TransformStatus(json.dumps({'ok': True, 'message': 'telemetry service is alive.'}))



def itemequip_func(input_data, service_objects, **kwargs):

    tctx = service_objects.lookup('telemetry_context')

    input_data['timestamp'] = datetime.datetime.now().isoformat()
    tctx.store_local(input_data)

    return core.TransformStatus(json.dumps({'ok': True, 'message': 'item-equip telemetry message received.'}))
    
    


