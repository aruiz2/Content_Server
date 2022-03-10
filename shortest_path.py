from map_fn import *
import heapq

def build_nodes_data(graph_map):
    nodes_data = dict()
    for node_name in graph_map.keys():
        nodes_data[node_name] = float("inf")
    return nodes_data

def calculate_shortest_paths(graph_map, source):
    nodes_data = build_nodes_data(graph_map); shortest_paths = dict()

    for destination in graph_map.keys():
        if destination != source:
            shortest_paths[destination] = djikstra(graph_map, nodes_data, source, destination)
    return shortest_paths

def djikstra(graph_map, nodes_data, source, destination):
    visited = set(); curr_node = source; nodes = len(graph_map.keys())
    nodes_data[source] = 0

    for iteration in range(nodes):
        #Only iterate through not visited nodes
        if curr_node not in visited:
            visited.add(curr_node)
            heap = []

            for nbor in graph_map[curr_node]:
                if nbor not in visited:
                    #Calculate cost to nbor
                    length = nodes_data[curr_node] + graph_map[curr_node][nbor]
                    
                    #Update min length of nbor
                    if length < nodes_data[nbor]:
                        nodes_data[nbor] = length

                    heapq.heappush(heap, [nodes_data[nbor], nbor])
            
        if heap: curr_node = heap[0][1]
    
    return nodes_data[destination]