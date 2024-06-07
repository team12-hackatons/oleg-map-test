from geopy.distance import geodesic


def generate_points(point, distance_km, step_degrees, mapMask):
    points = []

    for angle in range(0, 360, step_degrees):
        destination = geodesic(kilometers=distance_km).destination(point, angle)
        if mapMask.is_aqua(destination.latitude, destination.longitude):
            points.append((destination.latitude, destination.longitude))

    return points
