import socket

def external_node_thread(parser_cf):
    #create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    #bind socket
    try:
        s.bind((parser_cf.peer_0_host, parser_cf.backend_port))
    except socket.error as e:
        print('Error when binding' , (parser_cf.peer_0_host, parser_cf.backend_port),
        ' .\n\t'+str(e))
        sys.exit(-1)

    s.listen(10)