'''
Decodes Link State Advertisement String to a list format
'''
def decode_link_state_advertisement_str(msg_string):
    msg_list = msg_string[7:].split(','); n_msg_list = len(msg_list)
    for i in range(n_msg_list): 
        msg_list[i] = msg_list[i].split(':')
    return msg_list
'''
Builds Link State Advertisement string to be sent based on current data
'''
def build_link_state_advertisement_str(uuid_connected, SEQUENCE_NUMBER, parser_cf):
    link_adv = [{}, SEQUENCE_NUMBER]; link_adv_dict = link_adv[0]
    for nbor_uuid, nbor_dict in uuid_connected.items():
        if nbor_uuid != 'sequence_number': 
            link_adv_dict[nbor_uuid] = uuid_connected[nbor_uuid]['metric']
    
    #need to convert to string before sending
    link_adv_str = "linkadv:" + parser_cf.uuid + ":"
    for nbor, metric in link_adv[0].items():
        link_adv_str += str(nbor) + ":" + metric
        link_adv_str += ","
    link_adv_str += str(SEQUENCE_NUMBER)
    return link_adv_str

'''
Forwards Link State Advertisement to neighbors
'''
def forward_link_advertisement_to_neighbors(msg_list, uuid_connected, parser_cf):
    #msg_list = [[n1, m1], [n2, m2], ... , [metric]]
    n_msg_list = len(msg_list)
    received_sequence_number = msg_list[n_msg_list - 1]; curr_sequence_number = uuid_connected['sequence_number']
    node_received_adv_from = msg_list[0][0]

    neighbors_to_forward = []

    #NEED TO LOOP THROUGH NEIGHBORS IN UUID_CONNECTED
    if received_sequence_number > curr_sequence_number:

        #dont forward to neighbor we received info from, avoid loops
        for nbor in uuid_connected.keys():
            if nbor != node_received_adv_from: 
                neighbors_to_forward.append(node)