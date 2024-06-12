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


def calculate_time_by_lat_lon(lat1, lon1, lat2, lon2, mapMask):
    x1, y1 = mapMask.decoder(lat1, lon1)
    x2, y2 = mapMask.decoder(lat2, lon2)
    points = bresenham_line((x1, y1), (x2, y2))
    kilometers = geodesic((lat1, lon1), (lat2, lon2)).kilometers
    km = kilometers / len(points)
    ship_speed = 22
    speed_kmh = ship_speed * 1.852
    time = 0
    for x, y in points:
        if not mapMask.is_aqua(x, y):
            return -1
        index = mapMask.get_ice_index(x, y)
        if index == 1000:
            return -1
        if index == 3:
            time += kilometers / (14 * 1.852) * 3600
        elif index == 2:
            time += kilometers / (19 * 1.852) * 3600
        elif index == 1:
            time += kilometers / speed_kmh * 3600
        else:
            time += kilometers / speed_kmh * index
    return time


def calculate_time(start_point, end_point, map_mask):
    kilometers = geodesic((start_point.lat, start_point.lon), (end_point.lat, end_point.lon)).kilometers
    ship_speed = 22
    speed_kmh = ship_speed * 1.852
    index = map_mask.get_ice_index(end_point.x, end_point.y)
    time = 0
    if index == 1000:
        return -1
    if index == 3:
        time = kilometers / (14 * 1.852) * 3600
    elif index == 2:
        time = kilometers / (19 * 1.852) * 3600
    elif index <= 1:
        time = kilometers / speed_kmh * 3600
    end_point.current_time += time
    end_point.map_mask.change_ice_map(end_point.current_time)
    return time
def get_ice_index(lat, lon, previous_index, mapMask):
    x1, y1 = mapMask.decoder(lat, lon)
    index = mapMask.get_ice_index(x1, y1)
    if index != 0:
        return index
    return previous_index


def f_cost(g_cost, h_cost, weight=0.5):
    return weight * g_cost + (1 - weight) * h_cost


def optimize(path, map_mask):
    i = 1
    while i < len(path) - 1:
        current_point = path[i]

        next_point = path[i + 1]

        prev_point = path[i - 1]

        current_time = current_point.time_in_path + next_point.time_in_path + prev_point.time_in_path

        direct_time = calculate_time_by_lat_lon(prev_point.lat, prev_point.lon, next_point.lat, next_point.lon,
                                                map_mask)

        if direct_time < current_time and direct_time != -1:
            next_point.set_time(direct_time)
            path.pop(i)

        else:
            i += 1

def generate_points(point, map_mask, visited):
    points = []
    distance = 1
    offsets = [-distance, 0, distance]
    for dx in offsets:
        for dy in offsets:
            if dx == 0 and dy == 0:  # Skip the original point
                continue
            # if abs(dx) == distance or abs(dy) == distance:
            x, y = point.x + dx, point.y + dy
            if map_mask.is_aqua(x, y):
                new_point = NodeInfo.from_xy(x, y, 0, point.map_mask, point.current_time)
                time = calculate_time(point, new_point, map_mask)
                if time != -1:
                    new_point.set_time(time)
                    if (x, y) not in visited or new_point.time_in_path < visited[(x, y)].time_in_path:
                        points.append(new_point)
    return points
