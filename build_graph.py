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
    
    return graph

def update_graph(graph, peer_info, parser_cf, SEQUENCE_NUMBER = -1):
    sender_uuid = peer_info['original_sender']; sender_seq_num = peer_info['sequence_number']
    forward = False

    if sender_seq_num > graph[sender_uuid]['sequence_number']:
        graph[sender_uuid]['sequence_number'] = sender_seq_num

        for node_uuid, node_data in peer_info.items():
            if is_valid_node_uuid(node_uuid):
                if node_uuid not in graph.keys() and node_uuid != parser_cf.uuid: 
                    graph[node_uuid] = {'sequence_number':-1}

                for peer_uuid, peer_metric in node_data.items():
                    if peer_uuid not in graph.keys() and peer_uuid != parser_cf.uuid: 
                        graph[peer_uuid] = {'sequence_number':-1}
                    
                    if node_uuid != parser_cf.uuid:
                        graph[node_uuid][peer_uuid] = peer_metric
                    
                    if peer_uuid != parser_cf.uuid:
                        graph[peer_uuid][node_uuid] = peer_metric
        forward = True

    return graph, forward

def is_valid_node_uuid(node_uuid):
    return node_uuid != "original_sender" and node_uuid != "sequence_number" and node_uuid != "current_sender"