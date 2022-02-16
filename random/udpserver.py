#!/usr/bin/env python3

# 18-441/741 UDP Server
# It keeps receiving messages from possible clients
# And echoes back

import socket, sys



SERVER_HOST = ''  # Symbolic name, meaning all available interfaces
BUFSIZE = 1024  # size of receiving buffer



if __name__ == '__main__':

    # get server port from keyboard input
    if len(sys.argv) < 2:
        print('Format: python3 /path/udpserver.py <port_number>\nExiting...')
        sys.exit(-1)
    else:
        SERVER_PORT = int(sys.argv[1])

    SERVER_PORT = 8091

    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # without this line, if the previous execution has left the socket in a TIME_WAIT state, 
    # the socket can’t be immediately reused ([Errno 98] Address already in use)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind socket
    try:
        s.bind((SERVER_HOST, SERVER_PORT))
    except socket.error as e:
        print('Error when binding.\n\t'+str(e))
        sys.exit(-1)

    # listen on socket
    s.listen(10)

    # main loop
    while True:

        # accept a connection
        connection_socket, client_address = s.accept()

        # receive the message
        msg_string = connection_socket.recv(BUFSIZE).decode()

        # print the message
        print('New connection from '+client_address[0]+'; Message: '+msg_string)

        # echo the message back
        connection_socket.send(msg_string.encode())

    # exit
    s.close()
    sys.exit(0)