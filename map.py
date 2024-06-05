import folium
import os
import geopandas as gpd
from folium.plugins import MarkerCluster
from shapely.geometry import Polygon
from geopy.distance import geodesic
import pandas as pd
import ast

file_path = 'data/parse_data_with_polygon.xlsx'

df = None

if os.path.exists(file_path):
    df = pd.read_excel(file_path)

    print(df)
else:
    file_path_integr_velocity = 'data/IntegrVelocity.xlsx'

    sheets = pd.ExcelFile(file_path_integr_velocity).sheet_names

    lon_df = pd.read_excel(file_path_integr_velocity, sheet_name='lon')
    lat_df = pd.read_excel(file_path_integr_velocity, sheet_name='lat')

    index_sheets = {sheet: pd.read_excel(file_path_integr_velocity, sheet_name=sheet) for sheet in sheets if
                    sheet not in ['lon', 'lat']}

    data = []

    side_length_km = 25


    def normalize_longitude(start_longitude, normalize_longitude):
        index = (start_longitude % 360) + 1
        if normalize_longitude < 0:
            return normalize_longitude + (360 * 1)
        return normalize_longitude


    # =====================================================================================
    #               Найти ошибку почему эта функция возвращает отрицательные значения
    # =====================================================================================
    def generate_square(longitude, latitude, side_length):
        # longitude = normalize_longitude(longitude)
        top_right_point = geodesic(kilometers=side_length).destination((latitude, longitude), 90)
        bottom_right_point = geodesic(kilometers=side_length).destination(
            (top_right_point.latitude, top_right_point.longitude), 180)
        bottom_left_point = geodesic(kilometers=side_length).destination((latitude, longitude), 180)

        return [
            [latitude, longitude],
            [top_right_point.latitude, normalize_longitude(longitude, top_right_point.longitude)],
            [bottom_right_point.latitude, normalize_longitude(longitude, bottom_right_point.longitude)],
            [bottom_left_point.latitude, normalize_longitude(longitude, bottom_left_point.longitude)]
        ]

        # bottom_left = list(geodesic(kilometers=side_length).destination((latitude, longitude), 225))[:2]
        # bottom_right = list(geodesic(kilometers=side_length).destination((latitude, longitude), 315))[:2]
        # top_right = list(geodesic(kilometers=side_length).destination((latitude, longitude), 45))[:2]
        # top_left = list(geodesic(kilometers=side_length).destination((latitude, longitude), 135))[:2]

        # square_polygon = [bottom_left, bottom_right, top_right, top_left]
        #
        # return square_polygon


    for i in range(len(lon_df)):
        started_lon = None
        for j in range(lon_df.shape[1]):
            lon = lon_df.iloc[i, j]
            lat = lat_df.iloc[i, j]
            if started_lon is None:
                started_lon = lon
            elif started_lon <= lon:
                started_lon = lon
            else:
                lon = started_lon
            square = generate_square(lon, lat, side_length_km)
            started_lon = square[1][1]
            indices = [square, lon, lat]

            for sheet, index_df in index_sheets.items():
                index = float(index_df.iloc[i, j])
                indices.append(index if pd.notna(index) else None)

            data.append(indices)

    columns = ['Polygon', 'Longitude', 'Latitude']
    for sheet in index_sheets.keys():
        columns.append(sheet)

    df = pd.DataFrame(data, columns=columns)

    output_file_path = 'data/parse_data_with_polygon.xlsx'
    df.to_excel(output_file_path, index=False)

    print(df)

print(df.iloc[26078]["Polygon"])
print(df.iloc[26078])

m = folium.Map(location=[70.0, -30.0], zoom_start=2)


def get_color(index):
    if index <= 0:
        return "red"
    elif 22 > index >= 21:
        return "#42AAFF"
    elif 21 > index >= 15:
        return "#0000FF"
    else:
        return "#000096"


def add_ice_area(map_object, polygon_info, get_ice_index_from, index):
    folium.Polygon(
        locations=ast.literal_eval(polygon_info["Polygon"]),
        color=get_color(polygon_info[get_ice_index_from]),
        fill=True,
        fill_color=get_color(polygon_info[get_ice_index_from]),
        fill_opacity=0.5,
        tooltip=str(index)
    ).add_to(map_object)


current_cluster = MarkerCluster().add_to(m)

for index, polygon_data in df.iterrows():
    # Каждые 100 полигонов создаем новый кластер
    if index % 100 == 0:
        current_cluster = MarkerCluster().add_to(m)

    add_ice_area(current_cluster, polygon_data, "03-Mar-2020", index)

    # if index >= 30000:
    #     break

m.save('ice_map.html')
