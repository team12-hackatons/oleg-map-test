from math import cos, radians

import folium
from geopy.distance import geodesic
import networkx as nx
from search.generateSteps import generate_points, add_point
from search.mapmask import MapMask
from ship.getShip import get_ship_by_name
from pointFullInfo import PointFullInfo
from rtree import index


def main(start_point, end_point, ship):
    G = nx.Graph()
    #
    tree = index.Index()
    # G.add_edge(start_point, end_point, weight=geodesic(start_point, end_point).kilometers)
    mapMask = MapMask('resultMap/map_ice_03-Mar-2020.png')
    start_point = PointFullInfo(start_point[0], start_point[1], 1, 0, 0)
    end_point = PointFullInfo(end_point[0], end_point[1], 1, 0, 0)
    G.add_node(start_point)
    G.add_node(end_point)
    steps = [start_point]
    visited = []
    add_point(tree, visited, start_point)
    i = 0
    while True:
        current_point = steps.pop()
        if geodesic((end_point.latitude, end_point.longitude), (current_point.latitude, current_point.longitude)).kilometers <= 25:
            G.add_edge(current_point, end_point)
            break
        new_steps = generate_points(current_point, 25, 30, mapMask, visited, end_point, tree)
        for step in new_steps:
            G.add_node(step)
            G.add_edge(current_point, step, weight=step.error)
        steps.extend(new_steps)
        steps = sorted(steps, key=lambda x: x.error, reverse=True)
        i += 1
        if i >= 1000:
            print("закончились итерации")
            break
    G.add_edge(current_point, end_point)
    # Вычисляем кратчайший путь с использованием алгоритма A*
    shortest_path = nx.astar_path(G, start_point, end_point, heuristic=lambda n1, n2: n1.current_time + n2.current_time)
    print(shortest_path)

    m = folium.Map(location=[25, 25], zoom_start=4)

    folium.Marker(location=(start_point.latitude, start_point.longitude), popup='Start Point').add_to(m)
    folium.Marker(location=(end_point.latitude, end_point.longitude), popup='End Point').add_to(m)
    shortest_path_array = []
    for edge in visited:
        shortest_path_array.append((edge.latitude, edge.longitude))
    # Создаем линию, соединяющую отсортированные точки
    line = folium.PolyLine(locations=shortest_path_array, color='blue', weight=5)
    line.add_to(m)

    # Сохраняем карту
    m.save('path_map.html')
    mapMask.plot_graph_on_map(shortest_path_array)

if __name__ == '__main__':
    ship = get_ship_by_name('ШТУРМАН ЩЕРБИНИН')
    start_point = ship['start']
    end_point = ship['end']
    main(start_point, end_point, ship)
