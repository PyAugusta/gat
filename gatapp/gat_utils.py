from mpl_toolkits.basemap import pyproj

wgs84 = pyproj.Proj('+init=EPSG:3395')

def get_center(box):
    x = [pair[0] for pair in box[0]]
    y = [pair[1] for pair in box[0]]
    center = (sum(x) / len(x), sum(y) / len(y))
    return center
