import socket, sys, threading
from content_server import *
from uuid_connected_functions import *
from config_file_parse import get_peers_uuids
from link_state_advertisement import *

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

        #Link State Advertisement
        if (msg_string[:7] == "linkadv"): 
            msg_list = decode_link_state_advertisement_str(msg_string)
            threadLock.acquire(); uuid_connected = update_connected_dict(msg_list, uuid_connected, 2, SEQUENCE_NUMBER, parser_cf); threadLock.release()

            #TODO: FORWARD SIGNAL TO ALL ITS NEIGHBORS
            forward_link_advertisement_to_neighbors(msg_list, uuid_connected, parser_cf, s)

        #Keep Alive Signal
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
                    link_adv_str = build_link_state_advertisement_str(uuid_connected, SEQUENCE_NUMBER, parser_cf)

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