# Пример данных о судах
ships_data = {
    'ship_id': [1, 2, 3, 4, 5],
    'latitude': [70.0, 70.2, 70.4, 70.6, 70.8],
    'longitude': [180.0, 180.1, 180.2, 180.3, 180.4],
    'ready_time': ['2024-06-01', '2024-06-01', '2024-06-02', '2024-06-02', '2024-06-03']
}

ships_df = pd.DataFrame(ships_data)
ships_df['ready_time'] = pd.to_datetime(ships_df['ready_time'])

# Кластеризация судов
coords = ships_df[['latitude', 'longitude']]
kmeans = KMeans(n_clusters=2)
ships_df['cluster'] = kmeans.fit_predict(coords)

print(ships_df)

# Пример данных о графе переходов
graph_data = {
    'node_id': [1, 2, 3, 4],
    'latitude': [70.0, 70.5, 71.0, 71.5],
    'longitude': [180.0, 180.5, 181.0, 181.5],
    'connections': [[2, 3], [1, 3, 4], [1, 2, 4], [2, 3]],
    'distances': [[10, 15], [10, 5, 20], [15, 5, 10], [20, 10]]
}

graph_df = pd.DataFrame(graph_data)

# Создание графа
G = nx.Graph()
for index, row in graph_df.iterrows():
    node_id = row['node_id']
    connections = row['connections']
    distances = row['distances']
    for conn, dist in zip(connections, distances):
        G.add_edge(node_id, conn, weight=dist)

print(G.edges(data=True))


# Функция для поиска оптимального пути для каждого кластера (каравана)
def find_optimal_path_for_convoy(cluster_df, graph):
    start_node = 1  # Начальная точка (условно)
    end_node = 4  # Конечная точка (условно)
    shortest_path = nx.shortest_path(graph, source=start_node, target=end_node, weight='weight')
    return shortest_path


# Применение функции к каждому кластеру
for cluster_id in ships_df['cluster'].unique():
    cluster_df = ships_df[ships_df['cluster'] == cluster_id]
    optimal_path = find_optimal_path_for_convoy(cluster_df, G)
    print(f'Optimal path for cluster {cluster_id}: {optimal_path}')

# Визуализация маршрутов на карте
map_center = [np.mean(graph_df['latitude']), np.mean(graph_df['longitude'])]
route_map = folium.Map(location=map_center, zoom_start=5)

# Добавление узлов на карту
for index, row in graph_df.iterrows():
    folium.Marker(location=[row['latitude'], row['longitude']], popup=f"Node {row['node_id']}").add_to(route_map)

# Добавление маршрутов на карту для каждого кластера
colors = ['blue', 'green']  # Цвета для кластеров

for cluster_id in ships_df['cluster'].unique():
    cluster_df = ships_df[ships_df['cluster'] == cluster_id]
    optimal_path = find_optimal_path_for_convoy(cluster_df, G)

    # Координаты узлов для маршрута
    path_coords = [(graph_df[graph_df['node_id'] == node]['latitude'].values[0],
                    graph_df[graph_df['node_id'] == node]['longitude'].values[0]) for node in optimal_path]

    # Добавление линии маршрута на карту
    folium.PolyLine(locations=path_coords, color=colors[cluster_id % len(colors)], weight=2.5, opacity=1).add_to(
        route_map)

# Сохранение карты в HTML файл
route_map.save("route_map.html")

print("Карта маршрутов сохранена в файл route_map.html")
