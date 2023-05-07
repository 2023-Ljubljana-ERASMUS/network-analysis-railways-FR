import networkx as nx
from datetime import datetime


def stop_point_to_code_UIC(stop_point):
    return stop_point.split('-')[1]


def parse_stops(network_path, railways: nx.Graph):
    """ This function is used to add stations attributes.

    :param network_path: The GTFS directory path
    :param railways: The railways graph
    """

    with open(network_path + "/stops.txt", 'r') as file:
        for line in file:
            fields = line.split(',')
            stop_id = fields[0]
            if stop_id.startswith('StopPoint:'):
                code_UIC = stop_point_to_code_UIC(stop_id)
                stop_name = fields[1]
                nx.set_node_attributes(railways, {code_UIC: stop_name}, "stop_name")


def parse_railways(dataset_path):
    """ This function parse GTFS files to a NetworkX graph.

    :param dataset_path: The dataset path where GTFS files are stored
    :return: The graph of the railways
    """

    railways = nx.Graph(name='railways')

    networks = ["french_high_speed_network_GTFS", "french_inter_city_network_GTFS", "french_regional_networks_GTFS"]

    for network in networks:
        network_path = dataset_path + "/" + network
        with open(network_path + "/stop_times.txt", 'r') as file:
            file.readline()  # Skip header
            previous_stop_id = None
            departure_time = None
            for line in file:
                fields = line.split(',')

                arrival_time = fields[1]
                code_UIC = stop_point_to_code_UIC(fields[3])  # Using the UIC code of the station
                stop_sequence = int(fields[4])

                if stop_sequence == 0:
                    # This is the starting point of the trip
                    railways.add_node(code_UIC)
                else:
                    # Compute travel time
                    # --> Check validity
                    departure_hour = int(departure_time.split(':')[0])
                    arrival_hour = int(arrival_time.split(':')[0])
                    if departure_hour > 23 or arrival_hour > 23:
                        continue
                    departure = datetime.strptime(departure_time, '%H:%M:%S')
                    arrival = datetime.strptime(arrival_time, '%H:%M:%S')

                    delta = arrival - departure

                    railways.add_node(code_UIC)
                    railways.add_edge(code_UIC, previous_stop_id)

                previous_stop_id = code_UIC
                departure_time = fields[2]

        parse_stops(network_path, railways)

    return railways


def info(G):
    print("{:>12s} | '{:s}'".format('Graph', G.name))

    n = G.number_of_nodes()
    m = G.number_of_edges()

    print("{:>12s} | {:,d} ({:,d})".format('Nodes', n, nx.number_of_isolates(G)))
    print("{:>12s} | {:,d} ({:,d})".format('Edges', m, nx.number_of_selfloops(G)))
    print("{:>12s} | {:.2f} ({:,d})".format('Degree', 2 * m / n, max([k for _, k in G.degree()])))

    if isinstance(G, nx.DiGraph):
        G = nx.MultiGraph(G)

    C = list(nx.connected_components(G))

    print("{:>12s} | {:.1f}% ({:,d})".format('LCC', 100 * max(len(c) for c in C) / n, len(C)))

    if isinstance(G, nx.MultiGraph):
        G = nx.Graph(G)

    print("{:>12s} | {:.4f}".format('Clustering', nx.average_clustering(G)))

    return G