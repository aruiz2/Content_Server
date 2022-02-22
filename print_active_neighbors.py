
#1. TODO: NEED TO KNOW THE NAMES OF THE NODES
#2. TODO: NEED TO BE ABLE TO GET THE DATA OF THE ACTIVE NEIGHBORS THAT WERE NOT IN THE CONFIG FILE
def print_active_neighbors(parser_cf):
    active_neighbors = {"neighbors" : dict()}
    peers_data = parser_cf.get_peers() #[[peer0], [peer1], ... ,[peern]]
    for peer in peers_data:
        peer_uuid = peer[0]; peer_host = peer[1]; peer_port = peer[2]; peer_metric = peer[3]


    return
    # for uuid in cs.uuid_connected.keys():
