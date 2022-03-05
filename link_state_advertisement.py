import socket
'''
Decodes Link State Advertisement String to a list format
'''
def decode_link_state_advertisement_str(msg_string):
    msg_list = msg_string[8:].split(','); n_msg_list = len(msg_list)
    for i in range(n_msg_list): 
        msg_list[i] = msg_list[i].split(':')
    msg_list[n_msg_list - 1] = int(msg_list[n_msg_list-1][0])
    return msg_list
'''
Builds Link State Advertisement string to be sent based on current data
'''
def build_link_state_advertisement_str(graph, SEQUENCE_NUMBER, parser_cf):
    link_adv = [{}, SEQUENCE_NUMBER]; link_adv_dict = link_adv[0]
    for nbor_uuid, nbor_metric in graph.items():
        link_adv_dict[nbor_uuid] = nbor_metric
    
    #need to convert to string before sending
    link_adv_str = "linkadv:" + parser_cf.uuid + ","
    for nbor, metric in link_adv_dict.items():
        if nbor != 'sequence_number':
            link_adv_str += str(nbor) + ":" + str(metric)
            link_adv_str += ","
    link_adv_str += str(SEQUENCE_NUMBER)
    return link_adv_str

'''
Forwards Link State Advertisement to neighbors
'''
def forward_link_advertisement_to_neighbors(msg_list, uuid_connected, parser_cf, s):
    #msg_list = [[n1, m1], [n2, m2], ... , [metric]]
    n_msg_list = len(msg_list)
    received_sequence_number = msg_list[n_msg_list - 1]; curr_sequence_number = uuid_connected['sequence_number']
    node_received_adv_from = msg_list[0][0]
    neighbors_to_forward_adv = []

    #get list of neighbors to which forward the link advertisement to
    if received_sequence_number > curr_sequence_number:
        #dont forward to neighbor we received info from, avoid loops
        for nbor in uuid_connected.keys():
            if nbor != node_received_adv_from and nbor != 'sequence_number': 
                neighbors_to_forward_adv.append(nbor)

    #forward the link advertisement to each neighbor
    for nbor_uuid in neighbors_to_forward_adv:
        #get nbor data for socket
        nbor_host = uuid_connected[nbor_uuid]['host']; nbor_port = uuid_connected[nbor_uuid]['backend_port']
        server_ip = socket.gethostbyname(nbor_host)
        server_address = (server_ip, nbor_port)

        #rebuild the message to be sent
        msg_str = "linkadv:" + parser_cf.uuid + ","
        for nbor, metric in msg_list[1:n_msg_list-1]:
            msg_str += str(nbor) + ":" + metric
            msg_str += ","
        msg_str += str(received_sequence_number)

        #connect to neighbor
        s.sendto(msg_str.encode(), server_address)