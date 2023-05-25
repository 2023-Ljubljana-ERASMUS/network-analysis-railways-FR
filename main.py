import networkx as nx
from prettytable import PrettyTable
import parser_GTFS as gtfs
import analysis
import visualization
import transnet_generator as transnet
from datetime import datetime

railways = gtfs.parse_railways('dataset')

analysis.tops(railways, nx.betweenness_centrality(railways), 'betweenness_centrality')
# visualization.draw_network(railways)
# transnet.generate_graph(["dataset/french_high_speed_network_GTFS", "dataset/french_inter_city_network_GTFS", "dataset/french_regional_networks_GTFS"], "output/test.gml", output_format="gml")
