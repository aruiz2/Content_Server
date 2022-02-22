import socket, sys, threading
from content_server import *
from uuid_connected import *
from config_file_parse import get_peers_uuids

def start_client_server_threads(parser_cf):

    #add peers to connected dictionary initially
    for peer_uuid in get_peers_uuids(parser_cf.get_peers()):
        update_connected_dict([peer_uuid], 0)

    #create and start client thread
    client = threading.Thread(target = send_keep_alive_signal, args = (parser_cf, ), daemon = True)
    client.start()

    #create server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_ip = socket.gethostbyname(socket.gethostname())
    address = (server_ip, parser_cf.backend_port)
    
    # print("server_ip:", server_ip)
    # print("server port: ", parser_cf.backend_port)

    #bind socket
    try:
        s.bind(address)
    except socket.error as e:
        threadLock.acquire()
        print('Error when binding in server thread' , address,
        ' .\n\t'+str(e))
        threadLock.release()
        sys.exit(-1)

    #listen for new connections
    s.listen()

    server = threading.Thread(target = server_thread, args = (parser_cf, s), daemon = True)
    server.start()

def server_thread(parser_cf, s):

    while True:

        #remove inactive nodes
        threadLock.acquire(); remove_from_connected_dict(); threadLock.release()

        # accept a connection
        connection_socket, client_address = s.accept()

        #accept message
        msg_string = connection_socket.recv(BUFSIZE).decode() #this will be the uuid of peer
        if msg_string[0:9] == "ka_signal": 
            msg_string = msg_string[9:].split(":")

        #make updates to uuid_connected nodes times
        #TODO: UNCOMMENT THE NEXT LINE
        threadLock.acquire(); update_connected_dict(msg_string); threadLock.release()
    
        #print("Received message", msg_string)

    s.close()

def send_keep_alive_signal(parser_cf,):

    #get peers uuids
    peers = parser_cf.get_peers()
    
    #constantly send keep_alive_signals
    while True:
        threadLock.acquire(); print(cs.uuid_connected);threadLock.release()

        #create client socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        #make updates to uuid_connected nodes times
        threadLock.acquire(); remove_from_connected_dict(); threadLock.release()

        #print("Node uuid: %s || Node backend port: %d" %(parser_cf.uuid, parser_cf.backend_port))
        for peer in peers: #peeer = [uuid, hostname, port, peer_count]
            peer_uuid = peer[0]; peer_host = peer[1]; peer_port = peer[2]
            server_ip = socket.gethostbyname(peer_host)
            
            #threadLock.acquire(); print("sending to ip", server_ip, "with port", peer_port); threadLock.release()
            
            #try connecting and sending signal to peer
            server_address = (server_ip, int(peer_port))
            connected = True
            try:
                s.connect(server_address)
            except:
                #print_lock("Disconnected")
                connected = False
            
            if connected:
                #print_lock("connected successfully")
                node_uuid = parser_cf.uuid
                #Keep alive signals
                for _ in range(3): #send 3 signals
                    #print("sending")
                    try:
                        ka_signal = "ka_signal" + node_uuid + ":" + parser_cf.name + ":" + str(parser_cf.backend_port)
                        s.send(ka_signal.encode())
                        time.sleep(0.01)
                    except:
                        print_lock("Disconnected node")

        #update peers variable based on if anyone disconnected
        threadLock.acquire()
        peers = update_peers(peers)
        threadLock.release()
        s.close()