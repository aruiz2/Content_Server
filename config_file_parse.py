'''
Returns the config_file_string given the config_file_path
    - config_file_path: string representing the path to a config file
'''

class CFParser():

    def __init__(self, config_file_path):
        self.config_file_str = self.__get_config_file_str(config_file_path)
        self.config_file_dict = self.__get_config_file_dict()

        self.uuid =  self.config_file_dict['uuid']
        self.name = self.config_file_dict['name']
        self.backend_port = int(self.config_file_dict['backend_port'])
        self.peer_count = int(self.config_file_dict['peer_count'])

        self.peers = self.__get_peers()

    def __get_config_file_str(self, config_file_path):
        '''
        File will be in the format of /private/18441/Project2/node21.conf
        Convert string into list of elements separated by '/', return last element
        '''
        return config_file_path.split("/")[-1]

    def __get_config_file_dict(self):
        f = open(self.config_file_str, 'r')
        Lines = f.readlines()
        f.close()

        cf_dict = {}
        for line in Lines:
            words = line.split('=')
            key = words[0][:-1]; val = words[1][1:][:-1] #this just removes spacing
            cf_dict[key] = val
        return cf_dict


    def __get_peers(self):
        n = self.peer_count
        peers = []
        print(n)
        for i in range(n):
            peer = "peer_" + str(i)
            peer_elems = self.config_file_dict[peer].split(',')
            n_peer_elems = len(peer_elems)

            for i_elem in range(n_peer_elems):
                peer_elems[i_elem] = peer_elems[i_elem][1:]
        
            peers.append(peer_elems)

        return peers


'''
Gets the uuid of every peer and returns it in a list of strings
'''
def get_peers_uuids(peers):
    #peers = [['uuid1', 'host1', 'port1', 'd1'], ... , [, , , ]]
    peers_uuids = []
    for peer in peers:
        peers_uuids.append(peer[0])
    return peers_uuids