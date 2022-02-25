import uuid_connected_functions as uc
import content_server as cs 
def add_neighbor(input, uuid_connected):
    #1.Parse Data
    parsed_data = parse_data(input)
    #2. Add to uuid_connected dictionary
    uc.update_connected_dict(parsed_data, uuid_connected, 0)
    
    return input

def parse_data(input):
    n_uuid = len("uuid"); n_port = len("backend_port"); n_host = len("host") 
    data = ["", "", "", ""] #[uuid, name, port, host]

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
    
    return data