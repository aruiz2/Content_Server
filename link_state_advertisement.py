import socket
import json
'''
Decodes Link State Advertisement String to a list format
'''
def decode_link_state_advertisement_str(msg_string):
    return json.loads(msg_string)
    
'''
Builds Link State Advertisement string to be sent based on current data
'''
def build_link_state_advertisement_str(graph, SEQUENCE_NUMBER, parser_cf):
    #Set Up Initial data for msg
    msg = dict()
    msg['original_sender'] = parser_cf.uuid
    msg['sequence_number'] = SEQUENCE_NUMBER
    msg['current_sender'] = parser_cf.uuid

    #Initialize empty dictonaries
    for node_uuid in graph.keys(): msg[node_uuid] = dict()

    #Set up metrics data for msg
    for node_uuid in graph.keys():
        for peer_uuid, metric in graph[node_uuid].items():
            if peer_uuid != 'sequence_number':
                msg[node_uuid][peer_uuid] = metric
                msg[peer_uuid][node_uuid] = metric
    
    return json.dumps(msg)

'''
Forwards Link State Advertisement to neighbors
'''
def forward_link_advertisement_to_neighbors(msg_list, uuid_connected, parser_cf, s, graph):
    neighbors_to_forward_adv = []
    link_adv_sender_uuid = msg_list['current_sender']

    #dont forward to the neighbor we received message from
    for nbor_uuid in uuid_connected.keys():
        if nbor_uuid != link_adv_sender_uuid:
            neighbors_to_forward_adv.append(nbor_uuid)

    original_sender_uuid = msg_list['original_sender']; original_sender_seq_num = msg_list['sequence_number']

    #rebuild the message to be sent
    msg = dict()
    msg['original_sender'] = original_sender_uuid
    msg['sequence_number'] = original_sender_seq_num
    msg['current_sender'] = parser_cf.uuid
    for node_uuid in graph.keys(): msg[node_uuid] = dict()
    for node_uuid in graph.keys():
        for peer_uuid, metric in graph[node_uuid].items():
            if peer_uuid != 'sequence_number':
                msg[node_uuid][peer_uuid] = metric
                msg[peer_uuid][node_uuid] = metric
    msg = json.dumps(msg)

    #forward the link advertisement to each neighbor
    for nbor_uuid in neighbors_to_forward_adv:
        #get nbor data
        nbor_host = uuid_connected[nbor_uuid]['host']; 
        nbor_port = uuid_connected[nbor_uuid]['backend_port']; 

        #connect to neighbor and send message
        server_ip = socket.gethostbyname(nbor_host); server_address = (server_ip, nbor_port)
        s.sendto(msg.encode(), server_address)