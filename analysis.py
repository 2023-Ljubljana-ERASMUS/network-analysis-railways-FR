import networkx as nx
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from parser_GTFS import parse_railways
from geopy.distance import distance


def distance_between_stations(railways: nx.Graph, station_a, station_b):
    """ This function compute the distance between two stations.

    :param railways:
    :param station_a:
    :param station_b:
    :return:
    """
    pos_a = (railways.nodes[station_a].get('lat'), railways.nodes[station_a].get('long'))
    pos_b = (railways.nodes[station_b].get('lat'), railways.nodes[station_b].get('long'))
    return distance(pos_a, pos_b).km


def shortest_travel_time_between_major_stations(railways: nx.Graph, stations_by_city):
    def min_travel_time(station_a, station_b):
        return nx.shortest_path_length(railways, station_a, station_b, weight='travel_time')

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
                    stations_distance = distance_between_stations(railways, station_source, station_destination)
                    if best_travel_time is None or travel_time < best_travel_time:
                        best_travel_time = travel_time
                        selected_stations_distance = stations_distance

            travel_times_from_city.append(best_travel_time)
            distances_from_city.append(selected_stations_distance)

        travel_times.append(travel_times_from_city)
        distances.append(distances_from_city)

    return travel_times, distances


def travellers_by_city(railways: nx.Graph, stations_by_city):
    """ This function gives the number of travellers by city

    :param railways: A network
    :param stations_by_city: A list of stations for each city
    :return: The number of travellers for each city
    """
    travellers = []
    for data in stations_by_city:
        temp = 0
        for station in data[0]:
            temp += int(railways.nodes[station].get('travelers_2021'))
        travellers.append(temp)
    return travellers


def travellers_by_station(railways: nx.Graph, stations_by_city):
    """ This function gives the number of travellers by station

    :param railways: A network
    :param stations_by_city: A list of stations for each city
    :return: The number of travellers for each station
    """

    travellers = []
    for data in stations_by_city:
        for station in data[0]:
            travellers.append(int(railways.nodes[station].get('travelers_2021')))
    return travellers


def travel_times_experience_top10():
    # Railways network
    railways = parse_railways('dataset')
    # And also without the high speed network
    railways_without_high_speed = parse_railways('dataset', networks=["french_inter_city_network_GTFS",
                                                                      "french_regional_networks_GTFS"])

    cities = ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg',
              'Montpellier', 'Bordeaux', 'Lille']

    stations_by_city = [(['87271007', '87113001', '87391003', '87547000', '87686006'], 'Paris'),
                        (['87751008'], 'Marseille'), (['87722025', '87723197'], 'Lyon'), (['87611004'], 'Toulouse'),
                        (['87756056'], 'Nice'), (['87481002'], 'Nantes'), (['87212027'], 'Strasbourg'),
                        (['87773002'], 'Montpellier'), (['87581009'], 'Bordeaux'), (['87223263', '87286005'], 'Lille')]

    data_with_high_speed = shortest_travel_time_between_major_stations(railways, stations_by_city)
    data_without_high_speed = shortest_travel_time_between_major_stations(railways_without_high_speed, stations_by_city)

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
    plt.savefig('output/time_saving_with_high_speed_top_10_cities.svg', format="svg", bbox_inches="tight",
                pad_inches=0.3)


def travel_times_experience_top25():
    # Complete railways network
    railways = parse_railways('dataset')

    urban_areas = ["Paris", "Lyon", "Marseille - Aix-en-Provence", "Toulouse", "Bordeaux", "Lille", "Nice", "Nantes", "Strasbourg",
                   "Rennes", "Grenoble", "Rouen", "Toulon", "Montpellier", "Douai - Lens", "Avignon", "Saint-Etienne",
                   "Tours", "Clermont-Ferrand", "Orléans", "Nancy", "Angers", "Caen", "Metz", "Dijon"]

    stations_by_urban_areas = [(['87271007', '87113001', '87391003', '87547000', '87686006'], 'Paris'),
                               (['87722025', '87723197'], 'Lyon'),
                               (['87751008', '87319012'], 'Marseille - Aix-en-Provence'),
                               (['87611004'], 'Toulouse'),
                               (['87581009'], 'Bordeaux'),
                               (['87223263', '87286005'], 'Lille'),
                               (['87756056'], 'Nice'),
                               (['87481002'], 'Nantes'),
                               (['87212027'], 'Strasbourg'),
                               (['87471003'], 'Rennes'),
                               (['87747006'], 'Grenoble'),
                               (['87411017'], 'Rouen'),
                               (['87755009'], 'Toulon'),
                               (['87773002'], 'Montpellier'),
                               (['87345009', '87345025'], 'Douai - Lens'),
                               (['87765008', '87318964'], 'Avignon'),
                               (['87726000'], 'Saint-Étienne'),
                               (['87571000'], 'Tours'),
                               (['87734004'], 'Clermont-Ferrand'),
                               (['87543009'], 'Orléans'),
                               (['87141002'], 'Nancy'),
                               (['87484006'], 'Angers'),
                               (['87444000'], 'Caen'),
                               (['87192039'], 'Metz'),
                               (['87713040'], 'Dijon')]

    data_with_high_speed = shortest_travel_time_between_major_stations(railways, stations_by_urban_areas)

    # --- Normalization by distance ---
    a = np.array(data_with_high_speed[1])
    b = np.array(data_with_high_speed[0])
    normalized_travel_times = np.divide(a, b, out=np.zeros(a.shape, dtype=float), where=b != 0)

    normalized_travel_times *= 60  # Convert km/min to km/h

    # --- Compute average time & speed ---
    average_travel_time = []
    for i in range(len(urban_areas)):
        average_travel_time.append(np.mean(data_with_high_speed[0][i]))

    average_speed = []
    for i in range(len(urban_areas)):
        average_speed.append(np.mean(normalized_travel_times[i]))

    # --- Weighted using the number of travellers by stations ---
    travellers = travellers_by_city(railways, stations_by_urban_areas)
    weighted_travel_time = []
    for i in range(len(urban_areas)):
        temp_data = data_with_high_speed[0][i].copy()
        temp_travellers = travellers.copy()
        to_remove = temp_data.index(0)
        temp_data.remove(0)
        temp_travellers.pop(to_remove)
        weighted_travel_time.append(np.average(temp_data, weights=temp_travellers))

    sns.heatmap(normalized_travel_times, cmap='Blues', xticklabels=urban_areas, yticklabels=urban_areas)
    plt.savefig('output/speed_top_25_urban_areas.svg', format="svg", bbox_inches="tight", pad_inches=0.3)
    plt.clf()

    sns.barplot(x=average_speed, y=urban_areas, width=0.6)
    plt.savefig('output/average_speed_top_25_urban_areas.svg', format="svg", bbox_inches="tight", pad_inches=0.3)
    plt.clf()

    sns.barplot(x=average_travel_time, y=urban_areas, width=0.6)
    plt.savefig('output/average_travel_time_top_25_urban_areas.svg', format="svg", bbox_inches="tight", pad_inches=0.3)
    plt.clf()

    fig = sns.barplot(x=weighted_travel_time, y=urban_areas, width=0.6)
    fig.axvline(np.quantile(weighted_travel_time, 0.5), color='k', linewidth=1)
    fig.axvline(np.quantile(weighted_travel_time, 0.75), color='r', linewidth=1)
    plt.savefig('output/weighted_travel_time_top_25_urban_areas.svg', format="svg", bbox_inches="tight", pad_inches=0.3)
    plt.clf()


def robustness_experience():
    # Complete railways network
    railways = parse_railways('dataset')

    cities = ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg',
              'Montpellier', 'Bordeaux', 'Lille']

    stations_by_city = [(['87271007', '87113001', '87391003', '87547000', '87686006'], 'Paris'),
                        (['87751008'], 'Marseille'), (['87722025', '87723197'], 'Lyon'), (['87611004'], 'Toulouse'),
                        (['87756056'], 'Nice'), (['87481002'], 'Nantes'), (['87212027'], 'Strasbourg'),
                        (['87773002'], 'Montpellier'), (['87581009'], 'Bordeaux'), (['87223263', '87286005'], 'Lille')]

    data_with_high_speed = shortest_travel_time_between_major_stations(railways, stations_by_city)

    for city in cities:
        railways_copy = railways.copy()
        stations_by_city_copy = stations_by_city.copy()

        for i in range(len(stations_by_city)):
            if stations_by_city[i][1] == city:
                stations = stations_by_city_copy.pop(i)
                for station in stations[0]:
                    railways_copy.remove_node(station)

        data_without_city = shortest_travel_time_between_major_stations(railways, stations_by_city_copy)

        average_delta = []
        for i in range(len(stations_by_city_copy)):
            # For each city the average travel time to reach other 8 cities
            temp = []
            for j in range(len(stations_by_city_copy)):
                temp.append(data_without_city[0][i][j] - data_with_high_speed[0][i][j])
            average_delta.append(np.mean(temp))

        print(city, np.mean(average_delta))


def new_line_experience():
    # Complete railways network
    railways = parse_railways('dataset')

    cities = ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", "Bordeaux",
              "Lille", "Rennes", "Reims", "Toulon", "Saint-Étienne", "Le Havre", "Dijon", "Grenoble", "Angers",
              "Nîmes", "Clermont-Ferrand", "Aix-en-Provence", "Le Mans", "Brest", "Tours", "Amiens"]

    stations_by_city = [(['87271007', '87113001', '87391003', '87547000', '87686006'], 'Paris'),
                        (['87751008'], 'Marseille'), (['87722025', '87723197'], 'Lyon'), (['87611004'], 'Toulouse'),
                        (['87756056'], 'Nice'), (['87481002'], 'Nantes'), (['87212027'], 'Strasbourg'),
                        (['87773002'], 'Montpellier'), (['87581009'], 'Bordeaux'), (['87223263', '87286005'], 'Lille'),
                        (['87471003'], 'Rennes'), (['87171009'], 'Reims'), (['87755009'], 'Toulon'),
                        (['87726000'], 'Saint-Étienne'), (['87413013'], 'Le Havre'), (['87713040'], 'Dijon'),
                        (['87747006'], 'Grenoble'), (['87484006'], 'Angers'),
                        (['87703975'], 'Nîmes'), (['87734004'], 'Clermont-Ferrand'), (['87319012'], 'Aix-en-Provence'),
                        (['87396002'], 'Le Mans'), (['87474007'], 'Brest'), (['87571000'], 'Tours'),
                        (['87313874'], 'Amiens')]

    data_with_high_speed = shortest_travel_time_between_major_stations(railways, stations_by_city)
    travellers = travellers_by_city(railways, stations_by_city)

    weighted_travel_time = []
    for i in range(len(cities)):
        a = data_with_high_speed[0][i]
        weighted_travel_time.append(np.average(a, weights=travellers))

    find_best_line_to_build(railways, ["Le Havre", "Nice", "Brest", "Clermont-Ferrand"], stations_by_city, cities, weighted_travel_time)


def build_new_line(railways: nx.Graph, station_a, station_b):
    """ This function add a new connection between two stations.

    :param railways: A network
    :param station_a: A source station
    :param station_b: A destination station
    :return: The new network
    """
    new_railways = railways.copy()

    average_speed = 250  # The minimum speed in km/h for a high speed rail of category I.
    dist = distance_between_stations(railways, station_a, station_b)
    travel_time = dist / average_speed

    new_railways.add_edge(station_a, station_b, travel_time=travel_time)
    cost = dist * 25

    return new_railways, dist, cost


def find_best_line_to_build(railways: nx.Graph, from_cities, stations_by_city, cities, initial_weighted_travel_time):
    travellers = travellers_by_city(railways, stations_by_city)
    new_lines = []
    for data_source in stations_by_city:

        if data_source[1] not in from_cities:
            continue

        best_line = None
        best_perf = None

        for data_destination in stations_by_city:

            if data_source[1] == data_destination[1]:
                continue

            for station_source in data_source[0]:
                for station_destination in data_destination[0]:
                    new_railways, dist, cost = build_new_line(railways, station_source, station_destination)

                    data_with_new_line = shortest_travel_time_between_major_stations(new_railways, stations_by_city)

                    # Compute the weighted travel time
                    i = cities.index(data_source[1])
                    a = np.array(data_with_new_line[0][i])
                    weighted_travel_time = np.average(a, weights=travellers)

                    # Check the delta and the cost of delta
                    delta = initial_weighted_travel_time[i] - weighted_travel_time
                    delta_cost = cost / delta

                    line = f"[{data_source[1]}]<->[{data_destination[1]}] - Distance: {round(dist, 2)} km," \
                           f" Accessibility: {round(weighted_travel_time)} min (-{round(delta)}),"\
                           f" Cost: {round(cost)} M€ ({round(delta_cost, 2)} M€/min) "

                    print(line)

                    if best_perf is None or delta_cost < best_perf:
                        best_perf = delta_cost
                        best_line = line

        print("\n-----------------")
        print("The best line to build is :", best_line)
        print("-----------------\n")


def traffic_law_experience():
    railways = parse_railways('dataset')

    urban_units = ["Paris", "Lyon", "Marseille - Aix-en-Provence", "Bordeaux", "Lille", "Nice", "Nantes", "Strasbourg",
                   "Rennes", "Grenoble", "Rouen", "Toulon", "Montpellier", "Douai - Lens", "Avignon", "Saint-Etienne",
                   "Tours", "Clermont-Ferrand", "Orléans", "Nancy", "Angers", "Caen", "Metz", "Dijon"]

    stations_by_urban_units = [(['87271007', '87113001', '87391003', '87547000', '87686006'], 'Paris'),
                               (['87722025', '87723197'], 'Lyon'),
                               (['87751008', '87319012'], 'Marseille - Aix-en-Provence'),
                               (['87581009'], 'Bordeaux'),
                               (['87223263', '87286005'], 'Lille'),
                               (['87756056'], 'Nice'),
                               (['87481002'], 'Nantes'),
                               (['87212027'], 'Strasbourg'),
                               (['87471003'], 'Rennes'),
                               (['87747006'], 'Grenoble'),
                               (['87411017'], 'Rouen'),
                               (['87755009'], 'Toulon'),
                               (['87773002'], 'Montpellier'),
                               (['87345009', '87345025'], 'Douai - Lens'),
                               (['87765008', '87318964'], 'Avignon'),
                               (['87726000'], 'Saint-Étienne'),
                               (['87571000'], 'Tours'),
                               (['87734004'], 'Clermont-Ferrand'),
                               (['87543009'], 'Orléans'),
                               (['87141002'], 'Nancy'),
                               (['87484006'], 'Angers'),
                               (['87444000'], 'Caen'),
                               (['87192039'], 'Metz'),
                               (['87713040'], 'Dijon')]

    population = [12628266, 2323221, 1760653, 1360829, 1247977, 1191117, 1006201, 972828, 790087, 733320, 689840,
                  666035, 629334, 616296, 539666, 530267, 520640, 495379, 485315, 439343, 435279, 422654, 422152,
                  390600, 387382]

    # Learning phase
    data = [("Paris", "Bordeaux", 22), ("Paris", "Strasbourg", 16),
            ("Marseille - Aix-en-Provence", "Lyon", 17)]

    k = []
    for element in data:
        i1 = urban_units.index(element[0])
        i2 = urban_units.index(element[1])
        nb_trains = element[2]

        p1 = population[i1]
        p2 = population[i2]

        s1 = stations_by_urban_units[i1][0][0]
        s2 = stations_by_urban_units[i2][0][0]

        dist = distance_between_stations(railways, s1, s2)
        traffic = nb_trains

        k.append((traffic * dist) / (p1 * p2))

    print(k)
    k = np.mean(k)
    print(k)

    test_data = [("Paris", "Lyon", 24), ("Lille", "Marseille - Aix-en-Provence", 4), ("Paris", "Nice", 10),
                 ("Paris", "Montpellier", 9), ("Paris", "Rennes", 18)]

    for element in test_data:
        i1 = urban_units.index(element[0])
        i2 = urban_units.index(element[1])
        nb_trains = element[2]

        p1 = population[i1]
        p2 = population[i2]

        s1 = stations_by_urban_units[i1][0][0]
        s2 = stations_by_urban_units[i2][0][0]

        dist = distance_between_stations(railways, s1, s2)
        traffic = float(k) * ((p1 * p2) / dist)

        print(round(traffic), nb_trains)


# travel_times_experience()
# robustness_experience()
# travel_times_experience_top25()
# new_line_experience()
traffic_law_experience()
