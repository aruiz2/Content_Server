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

        self.peers = self.get_peers()
    
    def __remove_whitespace_newline(self, msg):
        new_str = ""
        for letter in msg:
            if letter != ' ' and letter != '\n': new_str += letter
        return new_str

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
            key = self.__remove_whitespace_newline(words[0]); val = self.__remove_whitespace_newline(words[1]) #this just removes spacing
            
            if key == 'backend_port' or key == 'peer_count': cf_dict[key] = int(val)
            else: cf_dict[key] = val

        print(cf_dict)
        return cf_dict


    def get_peers(self):
        n = self.peer_count
        peers = []

        for i in range(n):
            #get the peer_i data
            peer = "peer_" + str(i)
            peer_elems = self.config_file_dict[peer].split(',')
            n_peer_elems = len(peer_elems)

            for i_elem in range(n_peer_elems):
                peer_elems[i_elem] = peer_elems[i_elem]
        
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