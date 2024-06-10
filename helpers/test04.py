# from math import cos, radians
import folium
from geopy.distance import geodesic
import networkx as nx
from search.testGenerateSteps import generate_points
from search.testMapMask import MapMask
from ship.getShip import get_ship_by_name
from helpers.nodeInfo import NodeInfo

# from pointFullInfo import PointFullInfo
# from rtree import index




def main(start_point, end_point, ship):
    G = nx.Graph()
    map_mask = MapMask('../resultMap/map_image.png')
    NodeInfo.set_class(end_point[0], end_point[1], map_mask)
    start_point_node = NodeInfo(start_point[0], start_point[1], 0.)
    end_point_node = NodeInfo(end_point[0], end_point[1], 0)

    G.add_node(start_point_node)
    G.add_node(end_point_node)

    steps = [start_point_node]
    visited = {}
    i = 0

    while True:
        if i == 3660:
            print("fd")
        if len(steps) == 0:
            print("пути нет")
            break
        current_point = steps.pop()
        if current_point.distance_to_end <= 25:
            G.add_edge(current_point, end_point_node)
            break
        new_steps = generate_points(current_point, map_mask, visited)
        for step in new_steps:
            G.add_node(step)
            G.add_edge(current_point, step, weight=step.distance_to_end)
        steps.extend(new_steps)
        steps = sorted(steps, key=lambda x: x.distance_to_end, reverse=True)
        i += 1
        if i >= 10000:
            print("Достигнут предел итераций")
            break

    G.add_edge(current_point, end_point_node)

    # Функция эвристики для алгоритма A*
    def heuristic(n1, n2):
        return n1.time_in_path + n2.time_in_path

    # Вычисляем кратчайший путь с использованием алгоритма A*
    shortest_path = nx.astar_path(G, start_point_node, end_point_node, heuristic=heuristic)
    # print(shortest_path)

    m = folium.Map(location=[25, 25], zoom_start=4)

    folium.Marker(location=(start_point_node.lat, start_point_node.lon), popup='Start Point').add_to(m)
    folium.Marker(location=(start_point_node.end_lat, start_point_node.end_lon), popup='End Point').add_to(m)
    shortest_path_array = []
    for x, y in visited:
        edge = visited[(x, y)]
        shortest_path_array.append((edge.lat, edge.lon))
    # Создаем линию, соединяющую отсортированные точки
    line = folium.PolyLine(locations=shortest_path_array, color='blue', weight=5)
    line.add_to(m)

    # Сохраняем карту
    m.save('path_map.html')
    map_mask.plot_graph_on_map(shortest_path_array)


if __name__ == '__main__':
    ship = get_ship_by_name('ШТУРМАН ЩЕРБИНИН', directory='../ship')
    start_point = ship['start']
    end_point = ship['end']
    main(start_point, end_point, ship)
