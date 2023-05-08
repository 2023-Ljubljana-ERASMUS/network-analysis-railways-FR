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
    for node in network.nodes(data=True):
        lat = node[1].get('lat')
        long = node[1].get('long')
        if lat is not None and long is not None:
            mx, my = m(float(long), float(lat))
            pos[node[0]] = (mx, my)
        else:
            to_draw.remove_node(node[0])

    nx.draw_networkx_nodes(G=to_draw, pos=pos, node_color='r', alpha=0.8, node_size=10)
    nx.draw_networkx_edges(G=to_draw, pos=pos, edge_color='g',
                           alpha=0.2, arrows=False)

    plt.show()
