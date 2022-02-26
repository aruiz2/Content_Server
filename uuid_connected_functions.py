import content_server as cs
import time

'''
Addds uuid to connected_uuid dictionary if not in there
    -uuid: the uuid to possibly be added
    -time: opti
'''
def update_connected_dict(peer_info, uuid_connected, time_entered = -1):
    #TODO: ONLY NEED TO UPDATE THE NAME OF THE NODE AND SHOULD SEND LESS DATA IN KEEP ALIVE SIGNALS THEN
    if time_entered == -1: 
        peer_uuid = peer_info[0]; peer_name = peer_info[1]; peer_port = peer_info[2]; peer_host = peer_info[3]
        uuid_connected[peer_uuid]['time'] = time.time() - cs.start_time
        uuid_connected[peer_uuid]['name'] = peer_name
        uuid_connected[peer_uuid]['backend_port'] = peer_port
        uuid_connected[peer_uuid]['host'] = peer_host
    else: 
        peer_uuid = peer_info[0]; 
        peer_host = peer_info[1]; 
        peer_port = peer_info[2]; 
        peer_metric = peer_info[3]
        uuid_connected[peer_uuid] = {'time' : 0}
        uuid_connected[peer_uuid]['backend_port'] = peer_port
        uuid_connected[peer_uuid]['host'] = peer_host
        uuid_connected[peer_uuid]['metric'] = peer_metric
    return uuid_connected

'''
Removes a uuid from the connected dictionary if 
last keep alive signal was received over our time limit.
'''
def remove_from_connected_dict(uuid_connected):
    for uuid, uuid_info in list(uuid_connected.items()):
        curr_time = time.time() - cs.start_time
        time_past = curr_time - uuid_info['time']
        if uuid_info['time'] != 0 and time_past > cs.time_limit:  #val != 0 takes care of the case where the node has not connected yet at the beginning
            uuid_connected.pop(uuid, None)
            print("******************************************************\nRemoving '%s' from dictionary which had time %d and current time is %d" %(uuid_info['name'], uuid_info['time'], time.time() - cs.start_time))
    return uuid_connected

'''
This function upadtes the peers of a node at the end
of the client. Adds new peers and deletes disconnected peers
    -peers: the previous peers of the node
'''
def update_peers(peers, uuid_connected):
    new_peers = []

    #remove previous peers that have disconnected
    for peer in peers:
        peer_uuid = peer[0]
        if peer_uuid in uuid_connected:
            new_peers.append(peer)

    #TODO: IMPLEMENT SO THAT IT CAN ADD PEERS THAT WERE NOT CONNECTED. WE WOULD ALSO NEED THEIR PORT AND HOST NAME TO CONNECT TO THEM SO NEED TO THINK ABOUT THIS.
    #add peers that were not previously connected

    #add new peer
    
    set_peers_uuids = set()
    for peer in peers: uuid = peer[0]; set_peers_uuids.add(uuid)

    for uuid in uuid_connected.keys():
        
        if uuid not in set_peers_uuids:
            peer = [uuid, uuid_connected[uuid]['host'], uuid_connected[uuid]['backend_port'], uuid_connected[uuid]['metric']]
            new_peers.append(peer)

    return new_peers
