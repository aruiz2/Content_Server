from optparse import OptionParser
from config_file_parse import CFParser
from print_active_neighbors import *
import socket, sys, time, threading
import node_thread as nt
import build_graph as bg

global BUFSIZE, threadLock, graph, uuid_nodes, uuid_connected, start
BUFSIZE = 1024
threadLock = threading.Lock()
graph = dict()
uuid_nodes = dict()
uuid_connected = dict()
start_time = time.time()
time_limit = 7
ka_signal_time = 0


def print_lock(message):
    threadLock.acquire()
    print(message)
    threadLock.release()

def content_server():
     #parse the input
    parser_t = OptionParser() 
    parser_t.add_option("-c", dest = "cf_path", help = "Please enter the path to the config file")
    (options, args) = parser_t.parse_args()

    #parse the config file
    parser_cf = CFParser(options.cf_path)

    #add node to graph and uuid variables
    threadLock.acquire()
    bg.add_node_and_peers_to_graph(parser_cf)
    uuid_nodes[parser_cf.uuid] = parser_cf.name
    threadLock.release()

    #create threads that acts as server and client for every node
    nt.start_client_server_threads(parser_cf)

    while True:

        command = input()
        if command == "addneighbor":
            print("Adding neighbor...\n")
    
        elif command == "uuid":
            threadLock.acquire(); print({"uuid": parser_cf.uuid}); threadLock.release()

        elif command == "neighbors":
            threadLock.acquire(); print(uuid_connected);print_active_neighbors(uuid_connected); threadLock.release()

        elif command == "map":
            print("Graph Map to be printed...\n")

        elif command == "rank":
            print("Print Djikstra's distances...\n")

        elif command == "kill":
            print("Killing process...\n")
            

    print_lock("Exited")
    s.close()
    sys.exit(0)

if __name__ == '__main__':
    content_server()