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

# Загрузка изображения карты
image_path = r'resultMap\map_image.png'
map_img = Image.open(image_path)
df = pd.read_excel('data\parse_data_with_polygon.xlsx')
map = MapMask()
img_width, img_height = map_img.size

color_dict = {}
color_reverse  = {}
cmap = plt.cm.get_cmap('viridis', len(df['03-Mar-2020'].unique()))

for i, value in enumerate(df['03-Mar-2020'].unique()):
    rgba = cmap(i)  # Получаем RGBA значение цвета
    hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255))
    color_dict[hex_color] = value
    color_reverse[value] = hex_color

def draw_poly(row):
    coords_lat_lon = ast.literal_eval(row['Polygon'])
    pixel_coords = [map.decoder(coord[0], coord[1]) for coord in coords_lat_lon]
    polygon = plt.Polygon(pixel_coords, facecolor=color_reverse[row['03-Mar-2020']], linewidth=0)
    ax.add_patch(polygon)
# Создание фигуры и осей
fig, ax = plt.subplots()

# Показ изображения
ax.imshow(map_img)


df.apply(lambda x: draw_poly(x), axis=1)
ax.set_xlim(0, img_width)
ax.set_ylim(0, img_height)
plt.gca().invert_yaxis() 
plt.show()

