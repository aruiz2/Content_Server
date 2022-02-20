from config_file_parse import get_peers_uuids

'''
Adds a node with its information as a key and adds the uuids of the peers as the value
'''
def add_node_to_graph(graph, parser_cf):
    node_data = [[parser_cf.name, parser_cf.backend_port]]
    node_peers_uuids = get_peers_uuids(parser_cf.peers)
    graph[parser_cf.uuid] = [node_data, node_peers_uuids]