import uuid_connected as uc
import content_server as cs 
def add_neighbor(input):
    #1.Parse Data

    parsed_data = input.split(" ")
    #2. Add to uuid_connected dictionary
    uc.update_connected_dict(parsed_data, 0)
    print(cs.uuid_connected)
    return input
