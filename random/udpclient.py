#!/usr/bin/env python3

# 18-441/741 UDP Client

import socket, sys



BUFSIZE = 1024  # size of receiving buffer


if __name__ == '__main__':

    # get server information from keyboard input
    if len(sys.argv) < 3:
        print('Format: python3 /path/udpclient.py <server_ip_address> <server_port_number>\nExiting...')
        sys.exit(-1)
    else:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
    
    ''' For simplicity, im setting the port and address here'''
    server = "172.19.137.179"
    server_port = 8099
    server_address = (server, server_port)

    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server
    s.connect((server_address, server_port))

    # get message from keyboard
    msg_string = input('Send this to the server: ')

    # send message to server
    s.send(msg_string.encode())

    # get echo message
    echo_string = s.recv(BUFSIZE).decode()

    # print echo message
    print('Echo from the server: '+echo_string)

    # exit
    s.close()
    sys.exit(0)