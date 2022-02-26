import uuid_connected_functions as uc
import content_server as cs 
import time

def add_neighbor(input, uuid_connected):
    #1.Parse Data
    parsed_data = parse_data(input)

    #2. Add to uuid_connected dictionary
    uuid_connected = neighbor_to_uuid_connected(uuid_connected, parsed_data)

def parse_data(input):
    n_uuid = len("uuid"); n_port = len("backend_port"); n_host = len("host"); n_metric = len("metric")
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
        
        #TODO: FINISH THIS PART
        elif info[:n_metric] == "metric":
            metric = info[n_metric+1:]
            data[4] = metric
    
    return data

#Adds a new neighbor to uuid connected
def neighbor_to_uuid_connected(uuid_connected, parsed_data):
    #get data needed for neighbor
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
    return uuid_connected