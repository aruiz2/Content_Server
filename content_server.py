from optparse import OptionParser
from config_file_parse import CFParser

#test commit
if __name__ == '__main__':
    '''Parse the input'''
    parser_t = OptionParser() 
    parser_t.add_option("-c", dest = "cf_path", help = "Please enter the path to the config file")
    (options, args) = parser_t.parse_args()

    '''Parse the config file'''
    parser_cf = CFParser(options.cf_path)
    print(parser_cf.uuid)