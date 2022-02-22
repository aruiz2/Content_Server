#1. TODO: NEED TO ADD THE METRIC OF THE NODE
#2. TODO: NEED TO BE ABLE TO GET THE DATA OF THE ACTIVE NEIGHBORS THAT WERE NOT IN THE CONFIG FILE
def print_active_neighbors(uuid_connected):
    active_neighbors = {"neighbors" : dict()}
    x = 0
    for peer_uuid, peer_info in uuid_connected.items():
        x += 1
        #Build dictionary of peer
        peer_dict = dict(); 
        peer_dict["port"] = peer_info['port'] 
        peer_dict["host"] = peer_info['host']; peer_dict["uuid"] = peer_uuid


        #Add peer dict to neighbor dictonary
        peer_name = peer_info['name']
        active_neighbors["neighbors"][peer_name] = peer_dict
    
    print(uuid_connected)
    print("Amount of times i have been in loop")
    print(active_neighbors)