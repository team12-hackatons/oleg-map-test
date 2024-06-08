from geopy.distance import geodesic
import numpy as np
from mapmask import MapMask

def calculate_error(latitude1, longitude1, latitude2, longitude2, current_error, mapMask, distance_km):
    x1, y1 = mapMask.decoder(latitude1, longitude1)
    x2, y2 = mapMask.decoder(latitude2, longitude2)

    x_coords = np.linspace(x1, x2, 10)
    y_coords = np.linspace(y1, y2, 10)
    km = distance_km / 10
    speed_kmh = 22 * 1.852
    time_seconds = 0
    for x, y in zip(x_coords, y_coords):
        x = int(round(x))
        y = int(round(y))
        index = mapMask.get_ice_index(x, y)
        time_hours = None
        if index == 1000:
            return -1
        elif index == 3:
            time_hours = distance_km / (14 * 1.852)
        elif index == 2:
            time_hours = distance_km / (19 * 1.852)
        elif index <= 1:
            time_hours = distance_km / speed_kmh
        time_seconds += time_hours * 3600

    return time_seconds


def generate_points(point, distance_km, step_degrees, mapMask):
    points = []

    for angle in range(0, 360, step_degrees):
        destination = geodesic(kilometers=distance_km).destination(point, angle)
        if mapMask.is_aqua(destination.latitude, destination.longitude):
            error = (calculate_error(point[0], point[1], destination.latitude, destination.longitude, 10, mapMask,
                                     distance_km))
            if error != -1:
                points.append((destination.latitude, destination.longitude, error))

    return points

map = MapMask('../resultMap/map_ice.png')
res = generate_points((76.47577, 69.78516),25, 5, map)
print(res)