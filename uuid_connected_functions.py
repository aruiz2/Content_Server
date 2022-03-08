import time

'''
Addds uuid to connected_uuid dictionary if not in there
    -uuid: the uuid to possibly be added
    -time: opti
'''
def update_connected_dict(peer_info, uuid_connected, start_time, graph, time_entered = -1, SEQUENCE_NUMBER = -1, parser_cf = None):
    #time = 1 --> keep alive signal
    if time_entered == 1:
        peer_uuid = peer_info[0]; peer_name = peer_info[1]; peer_port = peer_info[2]; peer_host = peer_info[3]
        
        #to account for new neighbors added from addneighbor from terminal
        if peer_uuid not in uuid_connected.keys(): 
            uuid_connected[peer_uuid] = {'time' : time.time() - start_time}
        
        #fill in rest of 
        uuid_connected[peer_uuid]['name'] = peer_name
        uuid_connected[peer_uuid]['backend_port'] = int(peer_port)
        uuid_connected[peer_uuid]['host'] = peer_host
    
    #time = 2 --> link state advertisement
    elif time_entered == 2:
        original_sender_uuid = peer_info["original_sender"]; received_sequence_number = peer_info['sequence_number']

        #Check if current sender is a new neigbor that was added to add to uuid_connected
        current_sender_uuid = peer_info["current_sender"]
        if current_sender_uuid == original_sender_uuid and current_sender_uuid not in uuid_connected.keys(): 
            uuid_connected[current_sender_uuid] = {'sequence_number':-1}
        

        #Check if original sender is in the graph, if not add it to the graph
        if original_sender_uuid not in graph.keys():
            graph[original_sender_uuid] = {'sequence_number':-1}

        if received_sequence_number > graph[original_sender_uuid]['sequence_number']:

            for node, node_data in peer_info.items():
                
                if node != "original_sender" and node != "sequence_number" and node != "current_sender":
                    for peer_uuid, peer_metric in node_data.items():
                        
                        #check peer is not current node
                        if peer_uuid != parser_cf.uuid: 

                            #Add new peer if neighbor to uuid_connected!
                            if peer_uuid not in uuid_connected and peer_uuid in parser_cf.peers :
                                uuid_connected = add_neighbor_to_uuid_connected(parser_cf, uuid_connected, peer_uuid)

    #initialize the uuid_connected        
    else: 
        peer_uuid = peer_info[0] 
        peer_host = peer_info[1] 
        peer_port = peer_info[2]
        peer_metric = peer_info[3]

        uuid_connected[peer_uuid] = {'time' : 0}
        uuid_connected[peer_uuid]['backend_port'] = int(peer_port)
        uuid_connected[peer_uuid]['host'] = peer_host
    return uuid_connected

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
def remove_from_connected_dict(uuid_connected, start_time, time_limit):
    for uuid, uuid_info in list(uuid_connected.items()):
        curr_time = time.time() - start_time
        time_past = curr_time - uuid_info['time']
        if uuid_info['time'] != 0 and time_past > time_limit:  #val != 0 takes care of the case where the node has not connected yet at the beginning
            uuid_connected.pop(uuid, None)
            print("******************************************************\nRemoving '%s' from dictionary which had time %d and current time is %d" %(uuid_info['name'], uuid_info['time'], time.time() - start_time))
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
    for peer in peers: 
        uuid = peer[0]
        set_peers_uuids.add(uuid)

    for uuid in uuid_connected.keys():
        
        if uuid not in set_peers_uuids:
            peer = [uuid, uuid_connected[uuid]['host'], uuid_connected[uuid]['backend_port']]
            new_peers.append(peer)

    return new_peers