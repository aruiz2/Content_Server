from optparse import OptionParser
from config_file_parse import CFParser
import socket, sys, time, threading
from build_graph import *
from add_neighbor import *
from node_thread import *
from shortest_path import *
from map_fn import *
import config as c

BUFSIZE = 1024
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
    c.threadLock.acquire()
    print(message)
    c.threadLock.release()

def content_server():
    global BUFSIZE, graph, uuid_nodes, uuid_connected, start, all_info
    #parse the input    
    parser_t = OptionParser() 
    parser_t.add_option("-c", dest = "cf_path", help = "Please enter the path to the config file")
    (options, args) = parser_t.parse_args()

    #parse the config file
    parser_cf = CFParser(options.cf_path)

    #initialize nodes_names dict
    nodes_names = {parser_cf.uuid:parser_cf.name}
    
    #add node to graph and uuid variables
    c.threadLock.acquire()
    graph = add_node_and_peers_to_graph(parser_cf, dict())
    uuid_nodes[parser_cf.uuid] = parser_cf.name
    c.threadLock.release()

    #create threads that acts as server and client for every node
    start_client_server_threads(parser_cf, uuid_connected, graph, start_time, time_limit, nodes_names)

    while True:

        command = input()
        if command[:11] == "addneighbor":
            uuid_connected, graph = add_neighbor(command[11:], uuid_connected, graph, parser_cf, nodes_names)

        elif command == "uuid":
            c.threadLock.acquire()
            print({"uuid": parser_cf.uuid}); print('\n')
            c.threadLock.release()

        elif command == "neighbors":
            c.threadLock.acquire()
            print_active_neighbors(graph, uuid_connected, parser_cf, nodes_names); print('\n')
            c.threadLock.release()

        elif command == "map":
            c.threadLock.acquire()
            print(build_map(graph, parser_cf, nodes_names)); print('\n')
            c.threadLock.release()

        elif command == "rank":
            c.threadLock.acquire()
            source = nodes_names[parser_cf.uuid]
            print(calculate_shortest_paths(build_map(graph, parser_cf, nodes_names)['map'], source)); print('\n')
            c.threadLock.release()

        elif command == "kill":
            c.threadLock.acquire()
            c.killed_node = True
            c.threadLock.release() 
            exit()

        #These commands are for my debugging
        elif command == "graph":
            c.threadLock.acquire()
            print(graph); print('\n')
            c.threadLock.release()

        elif command == "connected":
            c.threadLock.acquire()
            print(uuid_connected); print('\n')
            c.threadLock.release()

        elif command == "names":
            c.threadLock.acquire()
            print(nodes_names)
            c.threadLock.release()

    print_lock("Exited")
    s.close()
    sys.exit(0)

def print_active_neighbors(graph, uuid_connected, parser_cf, nodes_names):
    active_neighbors = {"neighbors" : dict()}
    for peer_uuid, peer_info in uuid_connected.items():
        if peer_uuid != parser_cf.uuid:
            #Build dictionary of peer
            peer_dict = dict(); add = True
            peer_dict["backend_port"] = peer_info['backend_port'] 
            peer_dict["host"] = peer_info['host']; peer_dict["uuid"] = peer_uuid
            try:
                peer_dict["metric"] = int(graph[peer_uuid][parser_cf.uuid])
            except:
                add = False

            if add:
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