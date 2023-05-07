import networkx as nx
from parser_GTFS import parse_railways


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


railways = parse_railways('dataset')

info(railways)

tops(railways, nx.closeness_centrality(railways, distance='travel_time'), 'closeness_centrality')
tops(railways, nx.betweenness_centrality(railways), 'betweenness_centrality')
tops(railways, nx.pagerank(railways, weight='travelers_2021'), 'page_rank')


