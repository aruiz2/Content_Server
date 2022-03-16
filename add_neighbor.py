import uuid_connected_functions as uc
import content_server as cs 
import time, socket
import config as c
from uuid_connected_functions import update_peers
from node_thread import *

def add_neighbor(input, uuid_connected, graph, parser_cf):
    #1.Parse Data
    parsed_data = parse_data(input)

    #2. Add to uuid_connected dictionary and graph
    c.threadLock.acquire()
    uuid_connected, graph = add_neighbor_to_uuidconnected_and_graph(uuid_connected, graph, parsed_data, parser_cf)
    c.threadLock.release()

    #set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    #3. Send link state advertisement
    peers = update_peers(parser_cf.get_peers(), uuid_connected)
    for peer in peers:
        #set up server_address
        peer_uuid = peer[0]; peer_host = peer[1]; peer_port = peer[2]; peer_metric = graph[peer_uuid][parser_cf.uuid]
        server_ip, server_port = socket.gethostbyname(peer_host), int(peer_port)
        server_address = (server_ip, server_port)

        #send link
        send_link_state_advertisement_signals(s, server_address, graph, parser_cf)
    c.SEQUENCE_NUMBER += 1
    return uuid_connected, graph


def parse_data(input):
    n_uuid = len("uuid"); n_port = len("backend_port"); n_host = len("host"); n_metric = len("metric");
    data = ["", "", "", "", ""] #[uuid, name, port, host, metric]

    for info in input.split(" ")[1:]:

        if info[:n_uuid] == "uuid":
            uuid = info[n_uuid+1:] #add +1  for '=' sign
            data[0] = uuid

        elif info[:n_host] == "host":
            host = info[n_host+1:]
            data[3] = host

        elif len(info) > n_port and info[:n_port] == "backend_port":
            port = info[n_port+1:]
            data[2] = port
        
        elif info[:n_metric] == "metric":
            metric = info[n_metric+1:]
            data[4] = metric

    return data
    

def add_neighbor_to_uuidconnected_and_graph(uuid_connected, graph, parsed_data, parser_cf):
    #get data needed or neighbor
    uuid_neighbor = parsed_data[0]
    name_neighbor = parsed_data[1] 
    port_neighbor = parsed_data[2] 
    host_neighbor = parsed_data[3]
    metric_neighbor = parsed_data[4]

    #add the neighbor to the dictionary
    uuid_connected[uuid_neighbor] = {}
    uuid_connected[uuid_neighbor]['time'] = time.time() - cs.start_time
    uuid_connected[uuid_neighbor]['name'] = name_neighbor
    uuid_connected[uuid_neighbor]['backend_port'] = port_neighbor
    uuid_connected[uuid_neighbor]['host'] = host_neighbor
    uuid_connected[uuid_neighbor]['metric'] = metric_neighbor

    #add neighbor to graph
    graph[uuid_neighbor] = {'sequence_number':-1, 'connected':True}
    graph[uuid_neighbor][parser_cf.uuid] = metric_neighbor

    return uuid_connected, graph