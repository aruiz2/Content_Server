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
    client = threading.Thread(target = send_keep_alive_signal, args = (parser_cf, threadLock, uuid_connected), daemon = True)
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
    server = threading.Thread(target = server_thread, args = (parser_cf, s, uuid_connected, threadLock), daemon = True)
    server.start()

def server_thread(parser_cf, s, uuid_connected, threadLock):

    while True:

        #remove inactive nodes
        threadLock.acquire(); 
        uuid_connected = remove_from_connected_dict(uuid_connected); 
        threadLock.release()

        # accept message
        bytesAddressPair = s.recvfrom(BUFSIZE)
        msg_string, client_address = bytesAddressPair[0].decode(), bytesAddressPair[1]

        if msg_string[0:9] == "ka_signal": 
            msg_string = msg_string[9:].split(":")

        #make updates to uuid_connected nodes times
        threadLock.acquire()
        uuid_connected = update_connected_dict(msg_string, uuid_connected) 
        threadLock.release()
    
        #print("Received message", msg_string)

    s.close()

def send_keep_alive_signal(parser_cf, threadLock, uuid_connected):

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
            
            #Keep alive signals
            node_uuid = parser_cf.uuid
            #threadLock.acquire(); print("trying to send signal to ", peer_uuid); threadLock.release()
            for _ in range(3): #send 3 signals
                #print("sending")
                try:
                    ka_signal = ("ka_signal" + 
                                 node_uuid + ":" + 
                                 parser_cf.name + ":" + 
                                 str(parser_cf.backend_port) + ":" + 
                                 str(socket.gethostname()) + ":" +
                                 str(peer_metric))
                    
                    #threadLock.acquire();print("sending signal to " + node_uuid); threadLock.release()
                    
                    s.sendto(ka_signal.encode(), server_address)
                    time.sleep(0.01)
                except:
                    print_lock("Disconnected node")

        #threadLock.acquire(); print("\n"); threadLock.release()

        #update peers variable based on if anyone disconnected
        threadLock.acquire()
        peers = update_peers(peers, uuid_connected)
        threadLock.release()
        s.close()