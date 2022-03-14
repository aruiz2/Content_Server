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
            if shortest_paths[destination] == float("inf"): shortest_paths.pop(destination, None)
    return shortest_paths


def djikstra(graph_map, nodes_data, source, destination):
    visited = set(); curr_node = source; nodes = len(graph_map.keys())
    nodes_data[source] = 0; 
    heap = [(0, curr_node)]; visited = set()

    for node in graph_map.keys(): 
        heapq.heappush(heap, (nodes_data[node], node))
    
    while heap:
        curr_dist, curr_node = heapq.heappop(heap)

        if curr_node not in visited:
            visited.add(curr_node)

            for nbor in graph_map[curr_node].keys():
                
                nbor_dist = curr_dist + int(graph_map[curr_node][nbor])
                
                if nbor_dist < nodes_data[nbor]:
                    nodes_data[nbor] = nbor_dist
                    heapq.heappush(heap, (nbor_dist, nbor))

    return nodes_data[destination]