import folium
from geopy.distance import geodesic
import networkx as nx
from search.generateSteps import generate_points
from search.mapmask import MapMask
import pickle

def main(start_point, end_point):
    
    with open('data/color_dict.pkl', 'rb') as f:
        color_dict = pickle.load(f)
    color_dict[(0, 0, 0, 250)] = 25
    G = nx.Graph()

    G.add_node(start_point)
    G.add_node(end_point)

    # G.add_edge(start_point, end_point, weight=geodesic(start_point, end_point).kilometers)
    mapMask = MapMask(r'resultMap\map_ice.png')

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
        if i >= 400:
            break
    G.add_edge(current_point, end_point)
    
    def get_passability(node):
        x,y = mapMask.decoder(node[0],node[1])
        return color_dict.get(mapMask.image.getpixel((x, y)), float('inf'))  # По умолчанию, если узел не найден, вернем бесконечность

    def heuristic(n1, n2):
        base_distance = geodesic(n1, n2).kilometers
        passability_n1 = get_passability(n1)
        passability_n2 = get_passability(n2)
        x1, y1 = mapMask.decoder(n1[0], n1[1])
        x2, y2 = mapMask.decoder(n2[0], n2[1])
        line_points = zip(range(x1, x2), range(y1, y2))

        if any(color_dict.get(mapMask.image.getpixel((x, y)), float('inf')) <= 0 for x, y in line_points):
            return float('inf')  # Если прямая проходит через область с белыми пикселями, вернем бесконечность
        if passability_n1 <= 0 :
            return float('inf')  # Если узел имеет нулевую или отрицательную ледопроходимость, вернем бесконечность
        
        #avg_passability = (passability_n1 + passability_n2) / 2
        return base_distance * passability_n1  # Скорректированное расстояние

    # Вычисляем кратчайший путь с использованием алгоритма A*
    shortest_path = nx.astar_path(G, start_point, end_point, heuristic=lambda n1, n2: heuristic(n1, n2))
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
    end_point = (55.7,164.25)
    main(start_point, end_point)