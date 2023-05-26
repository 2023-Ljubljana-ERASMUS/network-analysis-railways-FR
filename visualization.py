from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import networkx as nx


def draw_network(network: nx.Graph):

    to_draw = network.copy()

    m = Basemap(llcrnrlon=-5.0, llcrnrlat=41.0, urcrnrlon=10.0, urcrnrlat=52.0,
                resolution='i', projection='merc', lat_0=48., lon_0=-3.5)

    m.drawcoastlines(linewidth=0.5)
    m.drawcountries(linewidth=0.5)

    pos = {}
    node_sizes = []
    for node in network.nodes(data=True):
        lat = node[1].get('lat')
        long = node[1].get('long')
        travelers = node[1].get('travelers_2021')
        if lat is not None and long is not None:
            mx, my = m(float(long), float(lat))
            pos[node[0]] = (mx, my)
        else:
            to_draw.remove_node(node[0])

        if travelers is not None:
            node_sizes.append(int(travelers) * 0.000001)
        else:
            to_draw.remove_node(node[0])

    nx.draw_networkx_edges(G=to_draw, pos=pos, edge_color='g', alpha=0.2, arrows=False, width=0.2)
    plt.savefig('output/map_routes_french_railway_network.svg', format="svg", bbox_inches="tight", pad_inches=0.3)
    plt.clf()

    m = Basemap(llcrnrlon=-5.0, llcrnrlat=41.0, urcrnrlon=10.0, urcrnrlat=52.0,
                resolution='i', projection='merc', lat_0=48., lon_0=-3.5)

    m.drawcoastlines(linewidth=0.5)
    m.drawcountries(linewidth=0.5)

    nx.draw_networkx_nodes(G=to_draw, pos=pos, node_color='r', alpha=0.8, node_size=node_sizes)
    plt.savefig('output/map_stations_french_railway_network.svg', format="svg", bbox_inches="tight", pad_inches=0.3)
    plt.clf()


def draw_network_core(network: nx.Graph):

    to_draw = network.copy()

    m = Basemap(llcrnrlon=0.0, llcrnrlat=47.0, urcrnrlon=8.5, urcrnrlat=52.0,
                resolution='i', projection='merc', lat_0=48., lon_0=-3.5)

    m.drawcoastlines(linewidth=0.5)
    m.drawcountries(linewidth=0.5)

    pos = {}
    for node in network.nodes(data=True):
        lat = node[1].get('lat')
        long = node[1].get('long')
        if lat is not None and long is not None:
            mx, my = m(float(long), float(lat))
            pos[node[0]] = (mx, my)
        else:
            to_draw.remove_node(node[0])

    labels = {}
    for node in to_draw.nodes():
        # set the node name as the key and the label as its value
        labels[node] = to_draw.nodes[node]['stop_name']

    nx.draw_networkx_edges(G=to_draw, pos=pos, edge_color='g', alpha=0.3, arrows=False, width=0.4)
    nx.draw_networkx_nodes(G=labels, pos=pos, node_color='r', alpha=0.8, node_size=50)
    nx.draw_networkx_labels(to_draw, pos, labels, font_size=6, font_color='k')
    plt.savefig('output/k-core_french_railway_network.svg', format="svg", bbox_inches="tight", pad_inches=0.3)
