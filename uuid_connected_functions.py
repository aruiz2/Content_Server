import time
from build_graph import *

'''
Addds uuid to connected_uuid dictionary if not in there
    -uuid: the uuid to possibly be added
    -time: opti
''' 
def update_connected_dict(peer_info, uuid_connected, start_time, graph, time_entered = -1, parser_cf = None,):
    added = False

    #time = 1 --> keep alive signal
    if time_entered == 1:
        peer_uuid = peer_info[0]; peer_name = peer_info[1]; peer_port = peer_info[2]; peer_host = peer_info[3]
        
        #to account for new neighbors added from addneighbor from terminal
        if peer_uuid not in uuid_connected.keys(): 
            uuid_connected[peer_uuid] = {'time':time.time() - start_time}
            added = True
        
        #this chekcs at the beginning when first connection is made between neighbors nodes
        if uuid_connected[peer_uuid]['time'] == 0: added = True

        #fill in rest of information
        uuid_connected[peer_uuid]['name'] = peer_name
        uuid_connected[peer_uuid]['backend_port'] = int(peer_port)
        uuid_connected[peer_uuid]['host'] = peer_host
        uuid_connected[peer_uuid]['time'] = time.time() - start_time
        
    #time = 2 --> link state advertisement
    elif time_entered == 2:
        original_sender_uuid = peer_info["original_sender"]; received_sequence_number = peer_info['sequence_number']

        #Check if current sender is a new neighbor that was added to add to uuid_connected
        current_sender_uuid = peer_info["current_sender"]
        if current_sender_uuid == original_sender_uuid and current_sender_uuid not in uuid_connected.keys(): 
            uuid_connected[current_sender_uuid] = {'sequence_number':-1, 'time': time.time() - start_time}
            added = True
        
        #Check if original sender is in the graph, if not add it to the graph
        if original_sender_uuid not in graph.keys():
            graph[original_sender_uuid] = {'sequence_number':-1, 'connected':True}
            added = True

        if received_sequence_number > graph[original_sender_uuid]['sequence_number']:

            for node, node_data in peer_info.items():
                
                if node != "original_sender" and node != "sequence_number" and node != "current_sender":
                    for peer_uuid, peer_metric in node_data.items():
                        
                        #check peer is not current node
                        if peer_uuid != parser_cf.uuid: 

                            #Add new peer if neighbor to uuid_connected!
                            if peer_uuid not in uuid_connected and peer_uuid in parser_cf.peers :
                                uuid_connected = add_neighbor_to_uuid_connected(parser_cf, uuid_connected, peer_uuid)
                                added = True
                        
    #initialize the uuid_connected        
    else: 
        peer_uuid = peer_info[0] 
        peer_host = peer_info[1] 
        peer_port = peer_info[2]
        peer_metric = peer_info[3]

        uuid_connected[peer_uuid] = {'time' : 0}
        uuid_connected[peer_uuid]['backend_port'] = int(peer_port)
        uuid_connected[peer_uuid]['host'] = peer_host
    return uuid_connected, added

'''
Adds a neighbor data to uuid_connected if received from a link advertisement
'''
def add_neighbor_to_uuid_connected(parser_cf, uuid_connected, peer_uuid):
    node_peers = parser_cf.get_peers()
    for peer_data in node_peers:
        if peer[0] == peer_uuid:
            uuid_connected[peer_uuid] = {'uuid': peer_uuid, 
                                        'host': peer[1], 
                                        'backend_port': int(peer[2]), 
                                        'time': 0}
            return uuid_connected
    return None

'''
Removes a uuid from the connected dictionary if 
last keep alive signal was received over our time limit.
'''
def remove_from_connected_dict(uuid_connected, start_time, time_limit, graph):
    node_uuids_removed = []
    for uuid, uuid_info in list(uuid_connected.items()):
        curr_time = time.time() - start_time
        time_past = curr_time - uuid_info['time']
        if uuid_info['time'] != 0 and time_past > time_limit:  #val != 0 takes care of the case where the node has not connected yet at the beginning
            uuid_connected.pop(uuid, None)
            #print("removing node ", uuid, "from graph! already removed from uuid")
            graph, removed = remove_from_graph([uuid], graph)
            #print("******************************************************\nRemoving '%s' from dictionary which had time %d and current time is %d" %(uuid_info['name'], uuid_info['time'], time.time() - start_time))
            node_uuids_removed.append(uuid)
    return uuid_connected, node_uuids_removed, graph

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

    #add new peer
    set_peers_uuids = set()
    for peer in new_peers: 
        uuid = peer[0]
        set_peers_uuids.add(uuid)

    for uuid in uuid_connected.keys():
        
        if uuid not in set_peers_uuids:
            try:
                peer = [uuid, uuid_connected[uuid]['host'], uuid_connected[uuid]['backend_port']]
                new_peers.append(peer)
            except: pass

    return new_peers