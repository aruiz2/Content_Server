def build_map(graph, parser_cf, nodes_names):
    map = {"map":{}}
    node_name = None; peer_name = None


    #Initialize empty dictionaries for all nodes
    for node_uuid, node_data in nodes_names.items():
        if node_uuid in graph.keys() or node_uuid == parser_cf.uuid: 
            node_name = parser_cf.name if node_uuid == parser_cf.uuid else nodes_names[node_uuid]
            map["map"][node_name] = {}

    #Fill in the data
    for node_uuid, node_data in graph.items():
        if node_uuid in nodes_names.keys():
            node_name = parser_cf.name if node_uuid == parser_cf.uuid else nodes_names[node_uuid]

            for peer_uuid, metric in node_data.items():
                if peer_uuid != "sequence_number" and peer_uuid in nodes_names.keys():
                    peer_name = parser_cf.name if peer_uuid == parser_cf.uuid else nodes_names[peer_uuid]
                    
                    map["map"][node_name][peer_name] = metric
                    map["map"][peer_name][node_name] = metric
    return map