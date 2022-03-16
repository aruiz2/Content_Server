import socket, sys, threading
from content_server import *
from uuid_connected_functions import *
from config_file_parse import get_peers_uuids
from link_state_advertisement import *
from build_graph import *
from nodes_names_functions import *
import config as c

def print_lock(message):
    c.threadLock.acquire()
    print(message)
    c.threadLock.release()

'''
****************************************************************************************************
****************************************************************************************************
****************************************************************************************************
THREADING CODE STARTS HERE
****************************************************************************************************
****************************************************************************************************
****************************************************************************************************
'''
BUFSIZE = 1024

def start_client_server_threads(parser_cf, uuid_connected, graph, start_time, time_limit, nodes_names):
    added = False
    initial_seq_number = -1
    c.threadLock.acquire()
    #initialize uuid_connected
    for peer in parser_cf.get_peers():
        uuid_connected, added = update_connected_dict(peer, uuid_connected, start_time, graph, 0)
    
    #initialize graph
    graph = add_node_and_peers_to_graph(parser_cf, graph)
    c.threadLock.release()

    #create and start client thread
    client = threading.Thread(target = send_data, args = (parser_cf, uuid_connected, graph, start_time, time_limit, nodes_names), daemon = True)
    client.start()

    #create server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_ip = socket.gethostbyname(socket.gethostname())
    address = (server_ip, parser_cf.backend_port)

    #bind socket
    try:
        s.bind(address)
    except socket.error as e:
        c.threadLock.acquire()
        print('Error when binding in server thread' , address,
        ' .\n\t'+str(e))
        c.threadLock.release()
        sys.exit(-1)

    #start the server
    server = threading.Thread(target = server_thread, args = (parser_cf, s, uuid_connected, graph, start_time, time_limit, nodes_names), daemon = True)
    server.start()

def server_thread(parser_cf, s, uuid_connected, graph, start_time, time_limit, nodes_names):
    global server

    while True:
         
        if c.killed_node:
            server.join()
            break
        
        # accept message
        bytesAddressPair = s.recvfrom(BUFSIZE)
        msg_string, client_address = bytesAddressPair[0].decode(), bytesAddressPair[1]
        
        #Keep Alive Signal
        if msg_string[0:9] == "ka_signal": 
            msg_string = msg_string[9:].split(":")

            c.threadLock.acquire()
            uuid_connected, added = update_connected_dict(msg_string, uuid_connected, start_time, graph, 1);
            c.threadLock.release()
            
            #New node added -> Link State Advertisement
            if added:
                peers = update_peers(parser_cf.get_peers(), uuid_connected)
                for peer in peers:
                    #get peer values
                    peer_uuid = peer[0]; peer_host = peer[1]; peer_port = peer[2]; 
                    try:
                        peer_metric = graph[peer_uuid][parser_cf.uuid]
                    except: pass

                    #get server data
                    server_ip, server_port = socket.gethostbyname(peer_host), int(peer_port)
                    server_address = (server_ip, server_port)

                    send_link_state_advertisement_signals(s, server_address, graph, parser_cf)
            c.SEQUENCE_NUMBER += 1

        #Nodes Names Signal
        elif msg_string[0:11] == "nodes_names":
            msg_string = msg_string[12:].split(',')
            
            c.threadLock.acquire()
            nodes_names = update_nodes_names(msg_string, nodes_names)
            c.threadLock.release()

        #Node Disconnected Signal
        elif msg_string[0:9] == "remsignal":
            rem_uuids = msg_string[9:].split(':')
            c.threadLock.acquire()
            graph, removed = remove_from_graph(rem_uuids, graph)
            if removed: forward_remove_from_graph(s, uuid_connected, rem_uuids, graph)
            c.threadLock.release()

        #New Node Signal
        elif msg_string[0:12] == "new_neighbor":
            #Get new neighbor data
            new_nbor_name = ''
            new_nbor_data = msg_string[13:].split(',')
            new_nbor_uuid = new_nbor_data[0]
            try:
                new_nbor_name = nodes_names[new_nbor_uuid]
            except: pass
            new_nbor_port = int(new_nbor_data[2])
            new_nbor_host = new_nbor_data[3]
            new_nbor_metric = int(new_nbor_data[4])
            sent_seq_num = int(new_nbor_data[5])

            #Add to uuid_connected the new neighbor and forward it to the rest of the neighbors

            #TODO: This if statement the second part is probably not correct try to figure out logical way
            if new_nbor_uuid not in uuid_connected.keys() or new_nbor_uuid not in graph.keys() or graph[new_nbor_uuid]['sequence_number'] < sent_seq_num:
                uuid_connected[new_nbor_uuid] = {'name':new_nbor_name, 
                                                'backend_port':int(new_nbor_port), 
                                                'host':new_nbor_host, 
                                                'sequence_number':int(sent_seq_num),
                                                'time': 0}
                #TODO: FORWARD MESSAGE, TIENES QUE HACER ESTO DE VERDAD!
                for peer in parser_cf.get_peers(): #peer : [uuid, host, port, metric]
                    server_ip, server_port = socket.gethostbyname(peer[1]), int(peer[2])
                    server_address = (server_ip, server_port)

                    s.sendto(msg_string.encode(), server_address)
                    
        #Link State Advertisement
        else:
            msg_list = decode_link_state_advertisement_str(msg_string)

            c.threadLock.acquire(); 
            uuid_connected, added = update_connected_dict(msg_list, uuid_connected, start_time, graph, 2, parser_cf)
            graph, forward = update_graph(graph, msg_list, parser_cf , uuid_connected)
            c.threadLock.release()

            if (forward): 
                uuid_connected = forward_link_advertisement_to_neighbors(msg_list, uuid_connected, parser_cf, s, graph)

    s.close()

def send_data(parser_cf, uuid_connected, graph, start_time, time_limit, nodes_names):
    global client
    #get peers uuids
    peers = parser_cf.get_peers()
    
    #constantly send keep_alive_signals
    while True:
        #c.threadLock.acquire(); print(uuid_connected);c.threadLock.release()
        #c.threadLock.acquire(); print(graph);c.threadLock.release()
        #c.threadLock.acquire(); print(nodes_names); c.threadLock.release()

        #Check if user kills node
        if c.killed_node:
            client.join()
            break
            
        node_uuids_removed = []
        #create client socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        #make updates to uuid_connected nodes times
        c.threadLock.acquire()
        uuid_connected, node_uuids_removed, graph = remove_from_connected_dict(uuid_connected, start_time, time_limit, graph)
        c.threadLock.release()

        #print("Node uuid: %s || Node backend port: %d" %(parser_cf.uuid, parser_cf.backend_port))
        for peer in peers: #peeer = [uuid, hostname, port, count]
            try:
                peer_uuid = peer[0]; peer_host = peer[1]; peer_port = peer[2]; peer_metric = graph[peer_uuid][parser_cf.uuid]
            except:
                continue
            server_ip = socket.gethostbyname(peer_host)
            server_address = (server_ip, int(peer_port))

            #Send the data
            c.threadLock.acquire()

            #Keep alive signals
            send_keep_alive_signals(s, server_address, parser_cf, peer_metric)

            #Nodes names signals
            send_nodes_names_signals(s, server_address, parser_cf, uuid_connected, nodes_names)

            #Disconnected Signals - sent when a node disconnects
            if node_uuids_removed != []: 
                send_node_disconnected_signals(s, node_uuids_removed, graph, server_address)
            
            c.threadLock.release()
        
        #c.threadLock.acquire(); print("\n"); c.threadLock.release()

        #update peers variable based on if anyone disconnected
        c.threadLock.acquire()
        peers = update_peers(peers, uuid_connected)
        c.threadLock.release()
        s.close()

'''
****************************************************************************************************
****************************************************************************************************
****************************************************************************************************
SIGNALS CODE STARTS HERE
****************************************************************************************************
****************************************************************************************************
****************************************************************************************************
'''

def send_node_disconnected_signals(s, removed_uuids, graph, server_address):
    #Construct message to be sent
    msg = "remsignal"
    for rem_uuid in removed_uuids: msg += ':' + rem_uuid

    #Send message to nodes we are connected to
    for _ in range(3):
        try:
            s.sendto(msg.encode(), server_address)
            #time.sleep(0.01)

        except:
            print_lock("Could not send disconnected signal to a node")

def send_keep_alive_signals(s, server_address, parser_cf, peer_metric):
    for _ in range(3):
        try:
            ka_signal = ("ka_signal" + 
                            parser_cf.uuid + ":" + 
                            parser_cf.name + ":" + 
                            str(parser_cf.backend_port) + ":" + 
                            str(socket.gethostname()) + ":" +
                            str(peer_metric))
            s.sendto(ka_signal.encode(), server_address)
            #time.sleep(0.01)
            #print("Keep Alive")
        except:
            print_lock("Could not send keep alive signal to a node")
            #c.threadLock.acquire();print("sending signal to " + peer_uuid); c.threadLock.release()
            #c.threadLock.acquire();print("sending signal " + ka_signal); c.threadLock.release()

def send_link_state_advertisement_signals(s, server_address, graph, parser_cf):
    for i in range(3):
        try:
            link_adv_str = build_link_state_advertisement_str(graph, parser_cf)
            s.sendto(link_adv_str.encode(), server_address)
            #time.sleep(0.01)
            #print("Link Advertisement")
        except:
            print_lock("Could not send link state advertisement to a node")

def send_nodes_names_signals(s, server_address, parser_cf, uuid_connected, nodes_names):
    for _ in range(3):
        msg = "nodes_names," + parser_cf.uuid + ':' + parser_cf.name
        
        #send connected names
        for node_uuid in uuid_connected.keys():
            if node_uuid != parser_cf.uuid and "name" in uuid_connected[node_uuid].keys():
                msg += ',' + node_uuid + ':' + uuid_connected[node_uuid]["name"]

        #send names that may not be connected
        for node_uuid in nodes_names.keys():
            if node_uuid not in uuid_connected.keys():
                msg += ',' + node_uuid + ':' + nodes_names[node_uuid]

        try:
            s.sendto(msg.encode(), server_address)
            #time.sleep(0.01)
        except:
            print_lock("Could not send node_name signal to a node")

def send_new_neighbor_signals(s, msg, parser_cf, uuid_connected):
    for _ in range(3):

        for node_uuid in uuid_connected.keys():
            server_ip, server_port = socket.gethostbyname(uuid_connected[node_uuid]['host']), int(uuid_connected[node_uuid]['backend_port'])
            server_address = (server_ip, server_port)
            s.sendto(msg.encode(), server_address)


def forward_remove_from_graph(s, uuid_connected, rem_uuids, graph):
    neighbors_to_forward = []
    for nbor_uuid in uuid_connected.keys():
        neighbors_to_forward.append(nbor_uuid)
    
    msg = "remsignal"
    for rem_uuid in rem_uuids: msg += ':' + rem_uuid

    #print("forwarding remove from graph! to:", neighbors_to_forward, "\n")
    for nbor in neighbors_to_forward:
        nbor_host = uuid_connected[nbor]['host']
        nbor_port = int(uuid_connected[nbor]['backend_port'])

        server_ip = socket.gethostbyname(nbor_host); server_address = (server_ip, nbor_port)
        s.sendto(msg.encode(), server_address)