from optparse import OptionParser
from config_file_parse import CFParser
import socket, sys, time, threading
from build_graph import *
from add_neighbor import *
from node_thread import *
from shortest_path import *
from map_fn import *
import config

BUFSIZE = 1024
threadLock = threading.Lock()
uuid_nodes = dict()
uuid_connected = dict()
start_time = time.time()
time_limit = 7
ka_signal_time = 0

'''
****************************************************************************************************
****************************************************************************************************
****************************************************************************************************
CONTENT SERVER CODE
****************************************************************************************************
****************************************************************************************************
****************************************************************************************************
'''

def print_lock(message):
    threadLock.acquire()
    print(message)
    threadLock.release()

def content_server():
    global BUFSIZE, threadLock, graph, uuid_nodes, uuid_connected, start, threadLock, all_info, killed_node
    #parse the input    
    parser_t = OptionParser() 
    parser_t.add_option("-c", dest = "cf_path", help = "Please enter the path to the config file")
    (options, args) = parser_t.parse_args()

    #parse the config file
    parser_cf = CFParser(options.cf_path)

    #initialize nodes_names dict
    nodes_names = {parser_cf.uuid:parser_cf.name}
    
    #add node to graph and uuid variables
    threadLock.acquire()
    graph = add_node_and_peers_to_graph(parser_cf, dict())
    uuid_nodes[parser_cf.uuid] = parser_cf.name
    threadLock.release()

    #create threads that acts as server and client for every node
    start_client_server_threads(parser_cf, uuid_connected, threadLock, graph, start_time, time_limit, nodes_names)

    while True:

        #print(uuid_connected)
        command = input()
        if command[:11] == "addneighbor":
            add_neighbor(command[11:], uuid_connected, graph, parser_cf)
    
        elif command == "uuid":
            threadLock.acquire()
            print({"uuid": parser_cf.uuid}); print('\n')
            threadLock.release()

        elif command == "neighbors":
            threadLock.acquire()
            print_active_neighbors(graph, uuid_connected, parser_cf, nodes_names); print('\n')
            threadLock.release()

        elif command == "map":
            threadLock.acquire()
            print(build_map(graph, parser_cf, nodes_names)); print('\n')
            threadLock.release()

        elif command == "rank":
            threadLock.acquire()
            source = nodes_names[parser_cf.uuid]
            print(calculate_shortest_paths(build_map(graph, parser_cf, nodes_names)['map'], source)); print('\n')
            threadLock.release()

        elif command == "kill":
            threadLock.acquire()
            config.killed_node = True
            threadLock.release() 
            exit()

    print_lock("Exited")
    s.close()
    sys.exit(0)

def print_active_neighbors(graph, uuid_connected, parser_cf, nodes_names):
    active_neighbors = {"neighbors" : dict()}
    for peer_uuid, peer_info in uuid_connected.items():
        #Build dictionary of peer
        peer_dict = dict(); 
        peer_dict["backend_port"] = peer_info['backend_port'] 
        peer_dict["host"] = peer_info['host']; peer_dict["uuid"] = peer_uuid
        peer_dict["metric"] = graph[peer_uuid][parser_cf.uuid]

        #Add peer dict to neighbor dictonary
        try:
            peer_name = nodes_names[peer_uuid]
            active_neighbors["neighbors"][peer_name] = peer_dict
        except:
            #If the name is not in nodes_names, then it is not connected
            pass
    
    print(active_neighbors)

if __name__ == '__main__':
    content_server()