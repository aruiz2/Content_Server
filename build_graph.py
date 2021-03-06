from config_file_parse import get_peers_uuids

'''
Adds the node metrics to the graphs
'''
def add_node_and_peers_to_graph(parser_cf, graph):
    peers = parser_cf.get_peers()

    for peer in peers:
        peer_uuid = peer[0]; peer_metric = peer[3]
        graph[peer_uuid]= dict()
        graph[peer_uuid][parser_cf.uuid] = int(peer_metric)
        graph[peer_uuid]['sequence_number'] = -1
        graph[peer_uuid]['connected'] = False
    
    return graph

def update_graph(graph, peer_info, parser_cf, uuid_connected):
    sender_uuid = peer_info['original_sender']; sender_seq_num = peer_info['sequence_number']
    forward = False
    
    if sender_uuid not in graph.keys():
        graph[sender_uuid] = {'sequence_number': c.SEQUENCE_NUMBER,
                              'connected': True}
        forward = True

    elif sender_seq_num > graph[sender_uuid]['sequence_number']:
        prev_value = graph[sender_uuid]['sequence_number']
        graph[sender_uuid]['sequence_number'] = sender_seq_num
        graph[sender_uuid]['connected'] = True
        forward = True
    
    if graph[sender_uuid]['connected']:
        
        for node_uuid, node_data in peer_info.items():
            if is_valid_node_uuid(node_uuid):
                if node_uuid != parser_cf.uuid and node_uuid not in graph.keys(): 
                    graph[node_uuid] = {'sequence_number':-1, 'connected':True}

                #Check if this node is currently labeled as disconnected
                if node_uuid != parser_cf.uuid and not graph[node_uuid]['connected']: 
                    graph[node_uuid]['connected'] = True
                    graph[node_uuid]['sequence_number'] = sender_seq_num
                    forward = True

                for peer_uuid, peer_metric in node_data.items():
                    if peer_uuid != parser_cf.uuid and peer_uuid not in graph.keys(): 
                        graph[peer_uuid] = {'sequence_number':sender_seq_num, 'connected':True}
                        forward = True

                    if peer_uuid != parser_cf.uuid and not graph[peer_uuid]['connected']:
                        graph[peer_uuid]['connected'] = True
                        graph[peer_uuid]['sequence_number'] = sender_seq_num
    
                    if node_uuid != parser_cf.uuid:
                        if peer_uuid not in graph[node_uuid]:
                            graph[node_uuid][peer_uuid] = peer_metric
                            graph[node_uuid]['sequence_number'] = sender_seq_num
                            forward = True
                    
                    if peer_uuid != parser_cf.uuid:
                        if node_uuid not in graph[peer_uuid]:
                            graph[peer_uuid][node_uuid] = peer_metric
                            graph[peer_uuid]['sequence_number'] = sender_seq_num
                            forward = True

    return graph, forward

'''Doesnt remove marks as disconnected but same idea'''
def remove_from_graph(rem_uuids, graph):
    removed = False
    sent_seq_num = int(rem_uuids[-1])
    for rem_uuid in rem_uuids:
        if rem_uuid != '':
            for node_uuid, node_uuid_dict in list(graph.items()):
                if node_uuid == rem_uuid and graph[node_uuid]['connected'] == True: 
                    graph[node_uuid]['connected'] = False
                    graph[node_uuid]['sequence_number'] = sent_seq_num
                    removed = True
    
    return graph, removed

def is_valid_node_uuid(node_uuid):
    return node_uuid != "original_sender" and node_uuid != "sequence_number" and node_uuid != "current_sender"