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
# cmap = plt.cm.get_cmap('viridis', len(df['03-Mar-2020'].unique()))

# for i, value in enumerate(df['03-Mar-2020'].unique()):
#     rgba = cmap(i)  # Получаем RGBA значение цвета
#     RGBA_1 = (int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255), int(rgba[3]*255))
#     hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255))
#     color_dict[RGBA_1] = value
#     color_reverse[value] = hex_color

with open('data\color_dict.pkl', 'wb') as f:
    pickle.dump(color_dict, f)

def get_color(index):
    if index <= 0:
        return "red"
    elif 22 > index >= 21:
        return "#42AAFF"
    elif 21 > index >= 15:
        return "#0000FF"
    else:
        return "#000096"
def draw_poly(row):
    coords_lat_lon = ast.literal_eval(row['Polygon'])
    color = get_color(row["03-Mar-2020"])
    pixel_coords = [map.decoder(coord[0], coord[1]) for coord in coords_lat_lon]
    polygon = plt.Polygon(pixel_coords, facecolor=color, linewidth=0)
    ax.add_patch(polygon)

# Создание фигуры и осей
fig, ax = plt.subplots()

# Показ изображения
ax.imshow(map_img)


df.apply(lambda x: draw_poly(x), axis=1)
ax.set_xlim(0, img_width)
ax.set_ylim(0, img_height)
plt.gca().invert_yaxis() 
ax.axis('off')
fig.set_size_inches(5250 / 900, 3850 / 900)
plt.savefig('resultMap/map_ice.png', dpi=900, bbox_inches='tight', pad_inches=0)
plt.show()

