from optparse import OptionParser
from config_file_parse import CFParser
from print_uuid import print_uuid
import socket, sys, time, threading
import node_thread as nt
import build_graph as bg

BUFSIZE = 1024
threadLock = threading.Lock()
graph = dict()
nodes_uuid = dict()

#test commit
if __name__ == '__main__':
    #parse the input
    parser_t = OptionParser() 
    parser_t.add_option("-c", dest = "cf_path", help = "Please enter the path to the config file")
    (options, args) = parser_t.parse_args()

    #parse the config file
    parser_cf = CFParser(options.cf_path)

    #add node to graph and uuid global variables
    threadLock.acquire()
    bg.add_node_to_graph(graph, parser_cf)
    nodes_uuid[parser_cf.uuid] = parser_cf.name
    threadLock.release()

    print(graph)
    #still need to add as a neighbor the peer_1

    #create threads that acts as server and client for every node
    nt.start_client_server_threads(parser_cf)

    while True:

        command = input()
        if command == "addneighbor":
            print("Adding neighbor...\n")
    
        elif command == "uuid":
            print_uuid(parser_cf, threadLock)

        elif command == "neighbors":
            print("Node neighbors...\n")

        elif command == "map":
            print("Graph Map to be printed...\n")

        elif command == "rank":
            print("Print Djikstra's distances...\n")

        elif command == "kill":
            print("Killing process...\n")
            

    print("Exited")
    s.close()
    sys.exit(0)