import socket, sys, threading

BUFSIZE = 1024

'''
client = threading.Thread(nt.client_node_thread(parser_cf)); client.daemon = True
client.start()
'''

def start_client_server_threads(parser_cf):
    server = threading.Thread(target = server_thread, args = (parser_cf,), daemon = True)
    server.start()

def client_thread(parser_cf):
    server_port = parser_cf.backend_port
    server_ip = socket.gethostbyname(socket.gethostname())
    server_address = (server_ip, server_port)

    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server
    s.connect(server_address)

    #send message to server    
    msg = "hello"
    s.send(msg.encode())

    s.close()

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

    while True:
        #start the client thread
        client = threading.Thread(target = client_thread, args = (parser_cf,), daemon = True)
        client.start()

        # accept a connection
        connection_socket, client_address = s.accept()

    s.close()