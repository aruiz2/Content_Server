def update_nodes_names(msg_string, nodes_names):
    n_msg_string = len(msg_string)
    for i in range(n_msg_string): msg_string[i] = msg_string[i].split(':')
    
    for node_uuid, node_name in msg_string:
        if node_uuid not in nodes_names.keys(): 
            nodes_names[node_uuid] = node_name
    return nodes_names