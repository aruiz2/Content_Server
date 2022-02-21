import content_server as cs
import time

'''
Addds uuid to connected_uuid dictionary if not in there
    -uuid: the uuid to possibly be added
'''
def update_connected_dict(uuid):
    cs.uuid_connected[uuid] = time.time()
    return
'''
Removes a uuid from the connected dictionary if 
last keep alive signal was received over our time limit.
'''
def remove_from_connected_dict():
    for key, val in list(cs.uuid_connected.items()):
        time_past = time.time() - val
        if time_past > cs.time_limit: 
            cs.uuid_connected.pop(key, None)
    return

'''
This function upadtes the peers of a node at the end
of the client. Adds new peers and deletes disconnected peers
    -peers: the previous peers of the node
'''
def update_peers(peers):
    #dont add peers that have disconnecteds
    new_peers = []

    for peer in peers:
        peer_uuid = peer[0]
        if peer_uuid in cs.uuid_connected:
            new_peers.append(peer)

    #add peers that were not previously connected
    for uuid in cs.uuid_connected.keys():
        if uuid not in peers:
            new_peers.append(uuid)

    return new_peers
