import networkx as nx
from datetime import datetime


def stop_point_to_code_UIC(stop_point):
    return stop_point.split('-')[1]


def parse_stops(network_path, railways: nx.Graph):
    """ This function is used to add stations attributes.

    :param network_path: The GTFS directory path
    :param railways: The railways graph
    """

    with open("dataset/frequentation-stations.csv") as file:
        file.readline()  # Skip header
        frequentation = {}
        for line in file:
            fields = line.split(';')
            code_UIC = fields[1]
            travelers_2021 = fields[4]
            frequentation[code_UIC] = travelers_2021

    with open(network_path + "/stops.txt", 'r', encoding='utf-8') as file:
        for line in file:
            fields = line.split(',')
            stop_id = fields[0]
            if stop_id.startswith('StopPoint:'):
                code_UIC = stop_point_to_code_UIC(stop_id)
                stop_name = fields[1]
                lat = fields[3]
                long = fields[4]
                travelers_2021 = frequentation.get(code_UIC, 1000)

                nx.set_node_attributes(railways, {code_UIC: stop_name}, "stop_name")
                nx.set_node_attributes(railways, {code_UIC: travelers_2021}, "travelers_2021")
                nx.set_node_attributes(railways, {code_UIC: lat}, "lat")
                nx.set_node_attributes(railways, {code_UIC: long}, "long")


def parse_railways(dataset_path, networks=None):
    """ This function parse GTFS files to a NetworkX graph.

    :param dataset_path: The dataset path where GTFS files are stored
    :param networks:
    :return: The graph of the railways
    """

    if networks is None:
        networks = ["french_high_speed_network_GTFS", "french_inter_city_network_GTFS", "french_regional_networks_GTFS"]

    railways = nx.Graph(name='railways')

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
                    travel_time = int(delta.total_seconds() // 60)

                    railways.add_node(code_UIC)
                    railways.add_edge(code_UIC, previous_stop_id, travel_time=travel_time)

                previous_stop_id = code_UIC
                departure_time = fields[2]

        parse_stops(network_path, railways)

    return railways
