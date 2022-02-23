from optparse import OptionParser
from config_file_parse import CFParser
import socket, sys, time, threading
import node_thread as nt
import build_graph as bg
import add_neighbor as an

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

        #print(uuid_connected)
        command = input()
        if command[:11] == "addneighbor":
            an.add_neighbor(command[11:])
            print("Adding neighbor...\n")
    
        elif command == "uuid":
            threadLock.acquire(); print({"uuid": parser_cf.uuid}); threadLock.release()

        elif command == "neighbors":
            threadLock.acquire(); print(uuid_connected);print_active_neighbors(); threadLock.release()

        elif command == "map":
            print("Graph Map to be printed...\n")

        elif command == "rank":
            print("Print Djikstra's distances...\n")

        elif command == "kill":
            print("Killing process...\n")
            

    print_lock("Exited")
    s.close()
    sys.exit(0)

def print_active_neighbors():
    active_neighbors = {"neighbors" : dict()}
    x = 0
    print("uuid_conected", uuid_connected)
    for peer_uuid, peer_info in uuid_connected.items():
        x += 1
        #Build dictionary of peer
        peer_dict = dict(); 
        peer_dict["port"] = peer_info['port'] 
        peer_dict["host"] = peer_info['host']; peer_dict["uuid"] = peer_uuid


        #Add peer dict to neighbor dictonary
        peer_name = peer_info['name']
        active_neighbors["neighbors"][peer_name] = peer_dict
    
    # print(uuid_connected)
    # print("Amount of times we have been in loop", x)
    print(active_neighbors)

if __name__ == '__main__':
    content_server()