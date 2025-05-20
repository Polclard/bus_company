from geopy.distance import geodesic

def get_distance(town1_coords, town2_coords):
    return geodesic(town1_coords, town2_coords).km