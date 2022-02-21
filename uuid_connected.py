import content_server as cs
import time

'''
Addds uuid to connected_uuid dictionary if not in there
    -uuid: the uuid to possibly be added
'''
def update_uuid_in_connected_dict(uuid):
    if uuid not in cs.uuid_connected: 
        cs.uuid_connected[uuid] = time.time() - cs.start_time
    else:
        cs.uuid_connected[uuid] = time.time()
    return

'''
Removes a uuid from the connected dictionary if 
last keep alive signal was received over our time limit.
'''
def remove_from_connected_dict():
    for key, val in cs.uuid_connected.items():
        time_past = time.time() - val
        if time_past > cs.time_limit: 
            cs.uuid_connected.pop(key, None)
    return