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
        self.backend_port = self.config_file_dict['backend_port']
        self.peer_count = self.config_file_dict['peer_count']
        self.peer_0 = self.config_file_dict['peer_0']
        self.peer_1 = self.config_file_dict['peer_1']

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
            key = words[0][:-1]; val = words[1][:-1]
            cf_dict[key] = val
        return cf_dict