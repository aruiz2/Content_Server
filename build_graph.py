from config_file_parse import get_peers_uuids

'''
Adds the node metrics to the graphs
'''
def add_node_and_peers_to_graph(parser_cf, graph):
    peers = parser_cf.get_peers()
    for peer in peers:
        peer_uuid = peer[0]; peer_metric = peer[3]
        graph[peer_uuid] = int(peer_metric)
    graph['sequence_number'] = -1
    return graph

def update_graph(graph, peer_info, parser_cf, SEQUENCE_NUMBER = -1):
    n_peer_info = len(peer_info)
    received_sequence_number = peer_info[n_peer_info - 1]

    if received_sequence_number > graph['sequence_number']:
        graph['sequence_number'] = received_sequence_number

        #update metrics of neighbors
        for i in range(1, n_peer_info - 1): #skip first node since its current node uuid
            peer_uuid = peer_info[i][0]; peer_metric = peer_info[i][1]
            
            #check peer is not current node
            if peer_uuid != parser_cf.uuid: 
                if peer_uuid =='sequence_number': print("FUCKME")
                graph[peer_uuid] = peer_metric
    return graph