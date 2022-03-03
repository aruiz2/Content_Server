import socket, sys, threading
from content_server import *
from uuid_connected_functions import *
from config_file_parse import get_peers_uuids

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

def start_client_server_threads(parser_cf, uuid_connected, threadLock):

    #TODO: add peers data to connected dictionary initially
    for peer in parser_cf.get_peers(): 
        threadLock.acquire()
        uuid_connected = update_connected_dict(peer, uuid_connected, 0)
        threadLock.release()

    #create and start client thread
    SEQUENCE_NUMBER = 0
    client = threading.Thread(target = send_data, args = (parser_cf, threadLock, uuid_connected, SEQUENCE_NUMBER), daemon = True)
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
        threadLock.acquire()
        print('Error when binding in server thread' , address,
        ' .\n\t'+str(e))
        threadLock.release()
        sys.exit(-1)

    #start the server
    server = threading.Thread(target = server_thread, args = (parser_cf, s, uuid_connected, threadLock, SEQUENCE_NUMBER), daemon = True)
    server.start()

def server_thread(parser_cf, s, uuid_connected, threadLock, SEQUENCE_NUMBER):

    while True:

        #remove inactive nodes
        threadLock.acquire(); 
        uuid_connected = remove_from_connected_dict(uuid_connected); 
        threadLock.release()

        # accept message
        bytesAddressPair = s.recvfrom(BUFSIZE)
        msg_string, client_address = bytesAddressPair[0].decode(), bytesAddressPair[1]
        if (msg_string[:7] == "linkadv"): 
            msg_list = msg_string[7:].split(','); n_msg_list = len(msg_list)
            for i in range(n_msg_list): 
                msg_list[i] = msg_list[i].split(':')
            #our message will be like [[u1, m1], ... , [un, mn], seq_number]
            threadLock.acquire(); uuid_connected = update_connected_dict(msg_list, uuid_connected, 2, SEQUENCE_NUMBER, parser_cf); threadLock.release()


        if msg_string[0:9] == "ka_signal": 
            msg_string = msg_string[9:].split(":")
            threadLock.acquire(); uuid_connected = update_connected_dict(msg_string, uuid_connected, 1); threadLock.release()

        
        #print("Received message", msg_string)

    s.close()

def send_data(parser_cf, threadLock, uuid_connected, SEQUENCE_NUMBER):

    #get peers uuids
    peers = parser_cf.get_peers()
    
    #constantly send keep_alive_signals
    while True:
        #threadLock.acquire(); print(uuid_connected);threadLock.release()

        #create client socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        #make updates to uuid_connected nodes times
        threadLock.acquire()
        uuid_connected = remove_from_connected_dict(uuid_connected)
        threadLock.release()

        #print("Node uuid: %s || Node backend port: %d" %(parser_cf.uuid, parser_cf.backend_port))
        for peer in peers: #peeer = [uuid, hostname, port, count]
            peer_uuid = peer[0]; peer_host = peer[1]; peer_port = peer[2]; peer_metric = peer[3]
            server_ip = socket.gethostbyname(peer_host)
            server_address = (server_ip, int(peer_port))
            node_uuid = parser_cf.uuid

            #Keep alive signals
            for _ in range(3):
                try:
                    ka_signal = ("ka_signal" + 
                                    node_uuid + ":" + 
                                    parser_cf.name + ":" + 
                                    str(parser_cf.backend_port) + ":" + 
                                    str(socket.gethostname()) + ":" +
                                    str(peer_metric))
                    s.sendto(ka_signal.encode(), server_address)
                    time.sleep(0.01)
                except:
                    print_lock("Disconnected node")
                    #threadLock.acquire();print("sending signal to " + peer_uuid); threadLock.release()
                    #threadLock.acquire();print("sending signal " + ka_signal); threadLock.release()

            #Link State Advertisement
            for i in range(3):
                try:
                    link_adv_str = build_link_state_advertisement_str(uuid_connected, SEQUENCE_NUMBER)
                    s.sendto(link_adv_str.encode(), server_address)
                    time.sleep(0.01)
                except:
                    print_lock("Could not send link state advertisement")
            SEQUENCE_NUMBER += 1
        #threadLock.acquire(); print("\n"); threadLock.release()

        #update peers variable based on if anyone disconnected
        threadLock.acquire()
        peers = update_peers(peers, uuid_connected)
        threadLock.release()
        s.close()

def build_link_state_advertisement_str(uuid_connected, SEQUENCE_NUMBER):
    link_adv = [{}, SEQUENCE_NUMBER]; link_adv_dict = link_adv[0]
    for nbor_uuid, nbor_dict in uuid_connected.items():
        if nbor_uuid != 'sequence_number': 
            link_adv_dict[nbor_uuid] = uuid_connected[nbor_uuid]['metric']
    
    #need to convert to string before sending
    link_adv_str = "linkadv"
    for nbor, metric in link_adv[0].items():
        link_adv_str += str(nbor) + ":" + metric
        link_adv_str += ","
    link_adv_str += str(SEQUENCE_NUMBER)
    return link_adv_str