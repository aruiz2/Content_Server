import content_server as cs
import time

'''
Addds uuid to connected_uuid dictionary if not in there
    -uuid: the uuid to possibly be added
    -time: opti
'''
def update_connected_dict(uuid, time_entered = -1):
    if time_entered == -1: cs.uuid_connected[uuid] = time.time() - cs.start_time
    else: cs.uuid_connected[uuid] = 0
    return
'''
Removes a uuid from the connected dictionary if 
last keep alive signal was received over our time limit.
'''
def remove_from_connected_dict():
    for key, val in list(cs.uuid_connected.items()):
        curr_time = time.time() - cs.start_time
        time_past = curr_time - val
        if val != 0 and time_past > cs.time_limit:  #val != 0 takes care of the case where the node has not connected yet at the beginning
            cs.uuid_connected.pop(key, None)
            print("******************************************************\nRemoving %s from dictionary which had time %d and current time is %d" %(key, val, time.time()))
    return

'''
This function upadtes the peers of a node at the end
of the client. Adds new peers and deletes disconnected peers
    -peers: the previous peers of the node
'''
def update_peers(peers):
    new_peers = []

    #dont add peers that have disconnected
    for peer in peers:
        peer_uuid = peer[0]
        if peer_uuid in cs.uuid_connected:
            new_peers.append(peer)

    #TODO: IMPLEMENT SO THAT IT CAN ADD PEERS THAT WERE NOT CONNECTED. WE WOULD ALSO NEED THEIR PORT AND HOST NAME TO CONNECT TO THEM SO NEED TO THINK ABOUT THIS.
    #add peers that were not previously connected

    # for uuid in cs.uuid_connected.keys():
    #     if uuid not in peers:
    #         peer = ??
    #         new_peers.append(uuid)

    return new_peers
