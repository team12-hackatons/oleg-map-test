import PIL
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from mpl_toolkits.basemap import Basemap

img = plt.imread('../resultMap/map_image.png')


map = Basemap(projection='mill', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180)

lat, lon = (73.86761, 59.23828)
# lon = 42.20947


x, y = map(lon, lat)
x = int((x - map.xmin) / (map.xmax - map.xmin) * 5250)
y = int((map.ymax - y) / (map.ymax - map.ymin) * 3850)
print(x,y)
image = Image.open('../resultMap/map_image.png')

# Получение цвета пикселя по координатам x, y
pixel_color = image.getpixel((int(x), int(y)))
print(f'Цвет пикселя по координатам ({x}, {y}): {pixel_color}')

draw = ImageDraw.Draw(image)
radius = 10
draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill='red')


# Сохранение изображения с красной точкой
image.save('map_image_with_red_dot.png')
image.show()
