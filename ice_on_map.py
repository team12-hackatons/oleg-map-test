from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
import folium
import os
import geopandas as gpd
from folium.plugins import MarkerCluster
from shapely.geometry import Polygon
from geopy.distance import geodesic
import pandas as pd
import ast
from search.mapmask import MapMask
import matplotlib.pyplot as plt
import numpy as np
import pickle

# Загрузка изображения карты
image_path = 'resultMap/map_image.png'
map_img = Image.open(image_path)
df = pd.read_excel('data/parse_data_with_polygon.xlsx')
map = MapMask()
img_width, img_height = map_img.size

color_dict = {}
color_reverse  = {}

def get_color(index):
    if index <= 0:
        return "red"
    elif 22 > index >= 21:
        return "#42AAFF"
    elif 21 > index >= 15:
        return "#0000FF"
    else:
        return "#000096"
def draw_poly(row, date):
    coords_lat_lon = ast.literal_eval(row['Polygon'])
    color = get_color(row[date])
    pixel_coords = [map.decoder(coord[0], coord[1]) for coord in coords_lat_lon]
    polygon = plt.Polygon(pixel_coords, facecolor=color, linewidth=0)
    ax.add_patch(polygon)

# Создание фигуры и осей
fig, ax = plt.subplots()

# Показ изображения
ax.imshow(map_img)

for date in df.columns[3:]:
    # Создание нового изображения для каждой недели
    fig, ax = plt.subplots()

    # Показ изображения
    ax.imshow(map_img)

    # Применение функции draw_poly к каждой строке DataFrame для текущей недели
    df.apply(lambda x: draw_poly(x, date), axis=1)

    ax.set_xlim(0, img_width)
    ax.set_ylim(0, img_height)
    plt.gca().invert_yaxis()
    ax.axis('off')
    fig.set_size_inches(5250 / 900, 3850 / 900)

    # Сохранение изображения в отдельный файл для каждой недели
    plt.savefig(f'resultMap/map_ice_{date}.png', dpi=900, bbox_inches='tight', pad_inches=0)
    plt.close()

