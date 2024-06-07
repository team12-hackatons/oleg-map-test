import folium
from geopy.distance import geodesic
import networkx as nx
from search.generateSteps import generate_points
from search.mapmask import MapMask

def main(start_point, end_point):
    G = nx.Graph()

    G.add_node(start_point)
    G.add_node(end_point)

    # G.add_edge(start_point, end_point, weight=geodesic(start_point, end_point).kilometers)
    mapMask = MapMask()

    steps = [start_point]
    visited = set()
    i = 0
    while True:
        current_point = steps.pop()
        if geodesic(end_point, current_point).kilometers <= 25:
            break
        visited.add(current_point)
        new_steps = generate_points(current_point, 25, 30, mapMask)
        for step in new_steps:
            if step not in visited:
                G.add_node(step)
                G.add_edge(current_point, step, weight=geodesic(current_point, step).kilometers)
        steps.extend(new_steps)
        steps = sorted(steps, key=lambda x: geodesic(end_point, x).kilometers, reverse=True)
        i += 1
        if i >= 100:
            break
    G.add_edge(current_point, end_point)
    # Вычисляем кратчайший путь с использованием алгоритма A*
    shortest_path = nx.astar_path(G, start_point, end_point, heuristic=lambda n1, n2: geodesic(n1, n2).kilometers)
    print(shortest_path)

    m = folium.Map(location=[25, 25], zoom_start=4)

    folium.Marker(location=start_point, popup='Start Point').add_to(m)
    folium.Marker(location=end_point, popup='End Point').add_to(m)

    # Создаем линию, соединяющую отсортированные точки
    line = folium.PolyLine(locations=shortest_path, color='blue', weight=5)
    line.add_to(m)

    # Сохраняем карту
    m.save('path_map.html')
    mapMask.plot_graph_on_map(shortest_path)

if __name__ == '__main__':
    start_point = (67.64268, 42.20947)
    end_point = (72.1818, 73.91602)
    main(start_point, end_point)
