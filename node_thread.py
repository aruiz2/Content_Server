import socket, sys, threading
from content_server import *

def start_client_server_threads(parser_cf):
    #create and start client thread
    client = threading.Thread(target = send_keep_alive_signal, args = (parser_cf, ), daemon = True)
    client.start()

    #create server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_ip = socket.gethostbyname(socket.gethostname())
    address = (server_ip, parser_cf.backend_port)
    print("server_ip:", server_ip)
    #print("server port: ", parser_cf.backend_port)

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
        # accept a connection
        connection_socket, client_address = s.accept()

        #accept message
        msg_string = connection_socket.recv(BUFSIZE).decode()
        
        print("Received message", msg_string)


    s.close()

def send_keep_alive_signal(parser_cf,):

    #get peers uuids
    peers = parser_cf.get_peers()
    peers_uuids = [peer[0] for peer in parser_cf.peers]

    #constantly send keep_alive_signals
    while True:
        #create client socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
                connected = False
                # threadLock.acquire()
                # #print("Couldnt send keep alive signal to neighbor %s at port %d" %(peer_uuid, int(peer_port)))
                # threadLock.release()
            
            #send keep alive signal if connected
            if connected:
                print_lock("Successfully sent keep alive signal!")
                node_uuid = parser_cf.uuid
                s.send(node_uuid.encode())

        s.close()