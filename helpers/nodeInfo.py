from geopy.distance import geodesic


class NodeInfo:
    end_lat = None
    end_lon = None
    map_mask = None

    def __init__(self, lat, lon, time_in_path, x=None, y=None):
        if x is None and y is None:
            x, y = self.map_mask.decoder(lat, lon)
        self.lat = lat
        self.lon = lon
        self.x = x
        self.y = y
        self.ice_index = self.map_mask.get_ice_index(x, y)
        self.time_in_path = time_in_path
        self.distance_to_end = geodesic((lat, lon), (NodeInfo.end_lat, NodeInfo.end_lon)).kilometers

    def set_time(self, time_in_path):
        self.time_in_path = time_in_path

    @classmethod
    def from_xy(cls, x, y, time_in_path):
        lat, lon = cls.map_mask.reverse_decoder(x, y)
        return cls(lat, lon, time_in_path, x, y)

    @classmethod
    def set_class(cls, lat, lon, map_mask):
        cls.map_mask = map_mask
        cls.end_lat = lat
        cls.end_lon = lon
