from config_file_parse import get_peers_uuids
import content_server as cs

'''
Adds a node with its information as a key and adds the uuids of the peers as the value
'''
def add_node_and_peers_to_graph(parser_cf):
    node_peers_uuids = get_peers_uuids(parser_cf.peers)
    peers = parser_cf.get_peers()

    #add the node
    node_data = {'name' : parser_cf.name, 'backend_port' : parser_cf.backend_port, 'peers' : node_peers_uuids}
    cs.graph[parser_cf.uuid] = node_data

    #add peers if not existing
    for peer in peers:
        peer_uuid = peer[0]
        if peer_uuid not in cs.graph:
            cs.graph[peer_uuid] = {'backend_port': int(peer[2])}