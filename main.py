import visualization
import parser_GTFS as gtfs


railways = gtfs.parse_railways('dataset')

visualization.draw_network(railways)
