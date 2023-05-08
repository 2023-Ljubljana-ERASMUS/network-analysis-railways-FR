import networkx as nx
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from parser_GTFS import parse_railways
from geopy.distance import distance


def tops(G, data_dict, label, n=10):
    print(f"--- [{label}] ---")
    for i, c in sorted(data_dict.items(), key=lambda item: item[1], reverse=True)[:n]:
        print(G.nodes[i]['stop_name'], c)


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
    print()

    return G


def shortest_travel_time_between_major_stations(railways: nx.Graph):
    stations_by_city = [(['87271007', '87113001', '87391003', '87547000', '87686006'], 'Paris'),
                        (['87751008'], 'Marseille'), (['87722025', '87723197'], 'Lyon'), (['87611004'], 'Toulouse'),
                        (['87756056'], 'Nice'), (['87481002'], 'Nantes'), (['87212027'], 'Strasbourg'),
                        (['87773002'], 'Montpellier'), (['87581009'], 'Bordeaux'), (['87223263', '87286005'], 'Lille')]

    def min_travel_time(station_a, station_b):
        return nx.shortest_path_length(railways, station_a, station_b, weight='travel_time')

    def distance_between_stations(station_a, station_b):
        pos_a = (railways.nodes[station_a].get('lat'), railways.nodes[station_a].get('long'))
        pos_b = (railways.nodes[station_b].get('lat'), railways.nodes[station_b].get('long'))
        return distance(pos_a, pos_b).km

    travel_times = []
    distances = []
    for data_source in stations_by_city:
        travel_times_from_city = []
        distances_from_city = []

        for data_destination in stations_by_city:
            best_travel_time = None
            selected_stations_distance = None

            for station_source in data_source[0]:
                for station_destination in data_destination[0]:
                    travel_time = min_travel_time(station_source, station_destination)
                    stations_distance = distance_between_stations(station_source, station_destination)
                    if best_travel_time is None or travel_time < best_travel_time:
                        best_travel_time = travel_time
                        selected_stations_distance = stations_distance

            travel_times_from_city.append(best_travel_time)
            distances_from_city.append(selected_stations_distance)

        travel_times.append(travel_times_from_city)
        distances.append(distances_from_city)

    return travel_times, distances


def travel_times_experience():
    # Complete railways network
    railways = parse_railways('dataset')
    # And also without the high speed network
    railways_without_high_speed = parse_railways('dataset', networks=["french_inter_city_network_GTFS",
                                                                      "french_regional_networks_GTFS"])

    cities = ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 'Montpellier', 'Bordeaux', 'Lille']

    data_with_high_speed = shortest_travel_time_between_major_stations(railways)
    data_without_high_speed = shortest_travel_time_between_major_stations(railways_without_high_speed)

    # Normalization by distance
    normalized_travel_times = np.divide(np.array(data_with_high_speed[1]), np.array(data_with_high_speed[0]))
    # Convert km/min to km/h
    normalized_travel_times *= 60

    sns.heatmap(data_with_high_speed[0], cmap='Blues', xticklabels=cities, yticklabels=cities)
    plt.savefig('output/travel_time_top_10_cities.svg', format="svg", bbox_inches="tight", pad_inches=0.3)
    plt.clf()

    sns.heatmap(normalized_travel_times, cmap='Blues', xticklabels=cities, yticklabels=cities)
    plt.savefig('output/travel_time_top_10_cities_normalized.svg', format="svg", bbox_inches="tight", pad_inches=0.3)
    plt.clf()

    data_delta = []
    average_travel_time = []
    for i in range(len(cities)):
        # For each city the average travel time to reach other 9 cities
        average_travel_time.append(np.mean(data_with_high_speed[0][i]))

        # Compute the delta time saving with high speed train
        temp = []
        for j in range(len(cities)):
            temp.append(data_without_high_speed[0][i][j] - data_with_high_speed[0][i][j])
        data_delta.append(temp)

    sns.barplot(x=cities, y=average_travel_time, width=0.6)
    plt.savefig('output/average_travel_time_top_10_cities.svg', format="svg", bbox_inches="tight", pad_inches=0.3)
    plt.clf()

    sns.heatmap(data_delta, cmap='Greens', xticklabels=cities, yticklabels=cities)
    plt.savefig('output/time_saving_with_high_speed_top_10_cities.svg', format="svg", bbox_inches="tight", pad_inches=0.3)


travel_times_experience()

# info(railways)
# tops(railways, nx.closeness_centrality(railways, distance='travel_time'), 'closeness_centrality')
# tops(railways, nx.betweenness_centrality(railways), 'betweenness_centrality')
# tops(railways, nx.pagerank(railways, weight='travelers_2021'), 'page_rank')


