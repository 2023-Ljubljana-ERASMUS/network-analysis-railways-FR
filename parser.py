import networkx as nx
from datetime import datetime


def parse_stops(export_path, railways: nx.Graph):

    with open(export_path + "/stops.txt", 'r') as file:
        for line in file:
            fields = line.split(',')
            stop_id = fields[0]
            if stop_id.startswith('StopPoint:'):
                stop_name = fields[1]
                nx.set_node_attributes(railways, {stop_id: stop_name}, "stop_name")


def parse_railways(export_path):

    railways = nx.Graph()

    with open(export_path + "/stop_times.txt", 'r') as file:
        file.readline()  # Skip header
        previous_fields = None
        for line in file:
            fields = line.split(',')

            arrival_time = fields[1]
            stop_id = fields[3]
            stop_sequence = int(fields[4])

            if stop_sequence == 0:
                # This is the starting point of the trip
                railways.add_node(stop_id)
            else:
                previous_stop_id = previous_fields[3]
                previous_departure_time = previous_fields[2]

                # Compute travel time
                # --> Check validity
                departure_hour = int(previous_departure_time.split(':')[0])
                arrival_hour = int(arrival_time.split(':')[0])
                if departure_hour > 23 or arrival_hour > 23:
                    continue
                departure = datetime.strptime(previous_departure_time, '%H:%M:%S')
                arrival = datetime.strptime(arrival_time, '%H:%M:%S')

                delta = arrival - departure

                railways.add_node(stop_id)
                railways.add_edge(stop_id, previous_stop_id)

            previous_fields = fields

    parse_stops(export_path, railways)

    print(railways.nodes(data=True))


parse_railways("dataset/french_high_speed_network_GTFS")
