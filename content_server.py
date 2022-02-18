from optparse import OptionParser
from config_file_parse import CFParser
import socket, sys, time
from node_thread import external_node_thread

BUFSIZE = 1024

#test commit
if __name__ == '__main__':
    #parse the input
    parser_t = OptionParser() 
    parser_t.add_option("-c", dest = "cf_path", help = "Please enter the path to the config file")
    (options, args) = parser_t.parse_args()

    #parse the config file
    parser_cf = CFParser(options.cf_path)

    #create thread that accepts connections from other machine s
    external_node_thread(parser_cf)

    while True:

        command = input()
        if command == "addneighbor":
            print("Adding neighbor...\n")
    
        elif command == "uuid":
            print("Node identifier...\n")

        elif command == "neighbors":
            print("Node neighbors...\n")

        elif command == "map":
            print("Graph Map to be printed...\n")

        elif command == "rank":
            print("Print Djikstra's distances...\n")

        elif command == "kill":
            print("Killing process...\n")
            

    print("Exited")
    s.close()
    sys.exit(0)