from math import cos, radians

import numpy as np
from geopy.distance import geodesic
from pointFullInfo import PointFullInfo
from search.mapmask import MapMask
from helpers.nodeInfo import NodeInfo

def bresenham_line(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    pixels = []

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        pixels.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    return pixels


def add_point(rtree_idx, points_data, point):
    """
    Добавляет точку в R-дерево с фиксированным радиусом 1 км.

    :param rtree_idx: rtree index, созданный из points_data
    :param points_data: список данных о точках
    :param point: объект PointFullInfo
    """
    radius = 10.0  # Радиус в километрах
    lat, lon = point.latitude, point.longitude
    lat_change = radius / 111.0  # 1 градус широты ~ 111 км
    lon_change = radius / (111.0 * abs(cos(radians(lat))))
    rtree_idx.insert(len(points_data), (lon - lon_change, lat - lat_change, lon + lon_change, lat + lat_change))
    # points_data.append(point)


def remove_point(rtree_idx, points_data, index_to_remove):
    point = points_data[index_to_remove]
    radius = 10.0
    lat, lon = point.latitude, point.longitude
    lat_change = radius / 111.0
    lon_change = radius / (111.0 * abs(cos(radians(lat))))
    rtree_idx.delete(index_to_remove, (lon - lon_change, lat - lat_change, lon + lon_change, lat + lat_change))
    points_data.pop(index_to_remove)


def is_point_within_any_radius(point, radius_data, rtree_idx):
    lat, lon = point.latitude, point.longitude

    possible_ids = list(rtree_idx.intersection((lon, lat, lon, lat)))
    for i in possible_ids:
        center, radius = (radius_data[i].latitude, radius_data[i].longitude), 1
        if geodesic(center, (lat, lon)).kilometers <= radius:
            # if point.current_time < radius_data[i].current_time:
            #     remove_point(rtree_idx, radius_data, i)
            #     # radius_data.pop()
            #     return False
            return True
    return False


def calculate_time(start_point, end_point, map_mask):
    kilometers = geodesic((start_point.lat, start_point.lon), (end_point.lat, end_point.lon)).kilometers
    ship_speed = 22
    speed_kmh = ship_speed * 1.852
    time_seconds = start_point.time_in_path
    index = map_mask.get_ice_index(end_point.x, end_point.y)
    # if index == 1000:
    #     return -1
    if index == 3:
        return kilometers / (14 * 1.852) * 3600
    elif index == 2:
        return kilometers / (19 * 1.852) * 3600
    elif index <= 1:
        return kilometers / speed_kmh * 3600



def get_ice_index(lat, lon, previous_index, mapMask):
    x1, y1 = mapMask.decoder(lat, lon)
    index = mapMask.get_ice_index(x1, y1)
    if index != 0:
        return index
    return previous_index


def f_cost(g_cost, h_cost, weight=0.5):
    return weight * g_cost + (1 - weight) * h_cost


def generate_points(point, map_mask, visited):
    points = []
    for dx in range(-1, 2):  # dx will take values -1, 0, 1
        for dy in range(-1, 2):  # dy will take values -1, 0, 1
            if dx == 0 and dy == 0:  # Skip the original point
                continue
            x, y = point.x + dx, point.y + dy
            if map_mask.is_aqua(x, y):
                new_point = NodeInfo.from_xy(x, y, 0)
                new_point.set_time(calculate_time(point, new_point, map_mask))
                if (x, y) not in visited or new_point.time_in_path < visited[(x, y)].time_in_path:
                    visited[(x, y)] = new_point
                    points.append(new_point)
    return points
    # for angle in range(0, 360, step_degrees):
    #     destination = geodesic(kilometers=distance_km).destination((point.latitude, point.longitude), angle)
    #     if mapMask.is_aqua(destination.latitude, destination.longitude):
    #         time = calculate_error(point.latitude, point.longitude, destination.latitude, destination.longitude,
    #                                point.current_time, mapMask, distance_km)
    #         if time != -1:
    #             ice_index = get_ice_index(destination.latitude, destination.longitude, point.ice_index, mapMask)
    #             dd = PointFullInfo(destination.latitude, destination.longitude, ice_index, time,
    #                                error=geodesic((end_point.latitude, end_point.longitude),
    #                                               (destination.latitude, destination.longitude)).kilometers)
    #             test = is_point_within_any_radius(dd, visited, tree)
    #             if not test:
    #                 add_point(tree, visited, destination)
    #                 visited.append(dd)
    #                 points.append(dd)
                # visited.pop()

            # points.append((destination.latitude, destination.longitude))

    # return points


# lat1, lon1 = 69.05482, 73.46008
# lat2, lon2 = 41.77131, 153.28125

# some_thing = calculate_error(lat1, lon1, lat2, lon2, 0, MapMask('../resultMap/map_ice_03-Mar-2020.png'), 1000)
# print(some_thing)


# point1 = (2, 3)
# point2 = (10, 8)
# line_pixels = bresenham_line(point1, point2)
# print(line_pixels)