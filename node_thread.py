import socket, sys, threading
from content_server import *

def start_client_server_threads(parser_cf):
    server = threading.Thread(target = server_thread, args = (parser_cf, ), daemon = True)
    server.start()

def server_thread(parser_cf):

    #create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_ip = socket.gethostbyname(socket.gethostname())
    address = (server_ip, parser_cf.backend_port)

    #bind socket
    try:
        s.bind(address)
    except socket.error as e:
        print('Error when binding in server thread' , address,
        ' .\n\t'+str(e))
        sys.exit(-1)

    #listen for new connections
    s.listen()
    
    #create and start client thread
    client = threading.Thread(target = client_thread, args = (parser_cf, ), daemon = True)
    client.start()

    while True:
        # accept a connection
        print("before accept")
        connection_socket, client_address = s.accept()
        print("after accept")

        #accept message
        msg_string = s.recv(BUFSIZE).decode()
        print("Received message ", msg_string)

    s.close()

def client_thread(parser_cf,):
    send_keep_alive_signal(parser_cf,)

def send_keep_alive_signal(parser_cf,):
    
    #create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_ip = socket.gethostbyname(socket.gethostname())

    #get peers uuids
    peers_uuids = [peer[0] for peer in parser_cf.peers]

    print("Node uuid: %s || Node backend port: %d" %(parser_cf.uuid, parser_cf.backend_port))
    for peer_uuid in peers_uuids:
        #obtain peer data
        peer = graph[peer_uuid]
        peer_port = peer['backend_port']
        
        #try connecting and sending signal to peer
        server_address = (server_ip, peer_port)
        connected = True
        try:
            s.connect(server_address)
        except:
            print("Couldnt send keep alive signal to neighbor %s at port %d" %(peer_uuid, peer_port))
            connected = False
        
        #send keep alive signal if connected
        if connected:
            s.send("hello".encode())