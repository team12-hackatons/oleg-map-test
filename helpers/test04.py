# from math import cos, radians
from datetime import datetime

import folium
from geopy.distance import geodesic
import networkx as nx
from search.testGenerateSteps import generate_points, optimize
from search.testMapMask import MapMask
from ship.getShip import get_ship_by_name
from helpers.nodeInfo import NodeInfo

# from pointFullInfo import PointFullInfo
# from rtree import index




def main(start_point, end_point, ship):
    G = nx.Graph()
    map_mask = MapMask('../resultMap/map_image.png')
    current_time = int(datetime.strptime(ship["startTime"], '%Y-%m-%d %H:%M:%S').timestamp())
    map_mask.change_ice_map(current_time, r'/home/oleg/PycharmProjects/moscowHackTest/resultMap')
    NodeInfo.set_class(end_point[0], end_point[1], current_time)
    start_point_node = NodeInfo(start_point[0], start_point[1], 0., map_mask, current_time)
    end_point_node = NodeInfo(end_point[0], end_point[1], 0, map_mask, current_time)

    G.add_node(start_point_node)
    G.add_node(end_point_node)

    steps = [start_point_node]
    visited = {}
    i = 0

    is_path_exist = False

    while True:
        if len(steps) == 0:
            print("пути нет")
            break
        current_point = steps.pop()
        if current_point.distance_to_end <= 10:
            print("Путь есть")
            is_path_exist = True
            G.add_edge(current_point, end_point_node)
            break
        if (current_point.x, current_point.y) in visited:
            continue
        visited[(current_point.x, current_point.y)] = current_point
        new_steps = generate_points(current_point, map_mask, visited)
        for step in new_steps:
            G.add_node(step)
            G.add_edge(current_point, step, weight=step.distance_to_end)
        steps.extend(new_steps)
        steps = sorted(steps, key=lambda x: x.distance_to_end, reverse=True)
        i += 1
        if i >= 15000:
            print("Достигнут предел итераций")
            break

    # G.add_edge(current_point, end_point_node)

    # Функция эвристики для алгоритма A*
    def heuristic(n1, n2):
        return n1.time_in_path + n2.time_in_path

    m = folium.Map(location=[25, 25], zoom_start=4)

    folium.Marker(location=(start_point_node.lat, start_point_node.lon), popup='Start Point').add_to(m)
    folium.Marker(location=(start_point_node.end_lat, start_point_node.end_lon), popup='End Point').add_to(m)
    shortest_path_array = []
    if is_path_exist:
        shortest_path = nx.astar_path(G, start_point_node, end_point_node, heuristic=heuristic)
        origin_path = []
        for edge in shortest_path:
            origin_path.append((edge.lat, edge.lon))
        optimize(shortest_path, map_mask)
        optimize(shortest_path, map_mask)
        for edge in shortest_path:
            shortest_path_array.append((edge.lat, edge.lon))

    else:
        for x, y in visited:
            edge = visited[(x, y)]
            shortest_path_array.append((edge.lat, edge.lon))
    # Создаем линию, соединяющую отсортированные точки
    line = folium.PolyLine(locations=shortest_path_array, color='blue', weight=5)
    line.add_to(m)
    # line = folium.PolyLine(locations=origin_path, color='green', weight=5)
    # line.add_to(m)
    map_mask.plot_graph_on_map(shortest_path_array)

    # Сохраняем карту
    m.save('path_map.html')


if __name__ == '__main__':
    ship = get_ship_by_name('ДЮК II', directory='../ship')
    # ship = get_ship_by_name('GEORGIY USHAKOV', directory='../ship')
    start_point = ship['start']
    end_point = ship['end']
    main(start_point, end_point, ship)
