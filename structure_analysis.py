from collections import deque

import networkx as nx
import numpy as np
import seaborn as sns
import random
from matplotlib import pyplot as plt
from parser_GTFS import parse_railways
from geopy.distance import distance


def degree_distribution(G: nx.DiGraph):
    """ This function is used to compute the degree distribution of a given graph

    :param G: The given graph
    :return: degree distribution, in-degree distribution, out-degree distribution
    """
    distribution = {}

    d = []

    for node in G.nodes():
        degree = G.degree(node)

        if degree > 0:
            d.append(degree)

        if degree in distribution:
            distribution[degree] += 1
        else:
            distribution[degree] = 1

    plt.xlabel('Number of links (k)')
    plt.ylabel('Number of nodes with k links')

    plt.plot(distribution.keys(), distribution.values(), 'r.', markersize=4, label="Degree distribution")
    plt.legend()
    plt.savefig('output/degree_distribution.svg', format="svg", bbox_inches="tight", pad_inches=0.3)

    return d


def distance(G, i):
    D = {}
    Q = deque()
    D[i] = 0
    Q.append(i)
    while Q:
        i = Q.popleft()
        for j in G[i]:
            if j not in D:
                D[j] = D[i] + 1
                Q.append(j)
    return [d for d in list(D.values()) if d > 0]


def distances(G, n=300):
    D = {}
    for i in G.nodes() if len(G) <= n else random.sample(G.nodes(), n):
        D[i] = distance(G, i)
    return D


def erdos_renyi(n, m):
    G = nx.MultiGraph()
    for i in range(n):
        G.add_node(i)
    edges = []
    while len(edges) < m:
        i = random.randint(0, n - 1)
        j = random.randint(0, n - 1)
        if i != j:
            edges.append((i, j))
    G.add_edges_from(edges)
    return G


def small_world(G: nx.Graph):

    D = distances(G)
    D = np.mean([i for d in list(D.values()) for i in d])

    C = nx.average_clustering(G)

    G_random = nx.Graph(erdos_renyi(G.number_of_nodes(), G.number_of_edges()))

    D_random = distances(G_random)
    D_random = np.mean([i for d in list(D_random.values()) for i in d])

    C_random = nx.average_clustering(G_random)

    sigma = (C / C_random) / (D / D_random)
    return sigma, C / C_random, D / D_random


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

    score = small_world(railways)
    print("{:>12s} | {:.2f} {:.2f} {:.2f}".format('Small world', score[0], score[1], score[2]))
    print()

    return G


# Complete
railways = parse_railways('dataset')
info(railways)

score = nx.degree_assortativity_coefficient(railways)
print("{:>12s} | {:.2f}".format('Assort.', score))

degree_distribution(railways)

# High-speed
railways = parse_railways('dataset', networks=["french_high_speed_network_GTFS"])
info(railways)

# Inter-city
railways = parse_railways('dataset', networks=["french_inter_city_network_GTFS"])
info(railways)

# Regional
railways = parse_railways('dataset', networks=["french_regional_networks_GTFS"])
info(railways)

# tops(railways, nx.closeness_centrality(railways, distance='travel_time'), 'closeness_centrality')
# tops(railways, nx.betweenness_centrality(railways), 'betweenness_centrality')
# tops(railways, nx.pagerank(railways, weight='travelers_2021'), 'page_rank')
