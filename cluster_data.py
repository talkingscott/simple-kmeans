"""
A simple k-means clustering
"""
# pylint: disable=invalid-name

from collections import OrderedDict
import csv
from math import sqrt
import sys

def coords_add(coords0, coords1):
    """ Add two coordinates """
    return tuple([x0 + x1 for x0, x1 in zip(coords0, coords1)])

def coords_distance(coords0, coords1):
    """ Euclidean distance between two coordinates """
    total = 0
    for x0, x1 in zip(coords0, coords1):
        total += (x0 - x1) ** 2
    return sqrt(total)

def coords_div(coords, n):
    """ Divide coordinates by a scalar """
    return tuple([x / n for x in coords])

def coords_zero(coords):
    """ Return the origin for the coords """
    return (0,) * len(coords)

class Point:
    """ A point with coordinates and a label """
    def __init__(self, coords, label):
        self._coords = tuple(coords)
        self._label = label

    @property
    def coords(self):
        return self._coords

    @property
    def label(self):
        return self._label

class Cluster:
    """ A cluster (but not its members) """
    def __init__(self, centroid):
        self._centroid = centroid

    @property
    def centroid(self):
        return self._centroid

    @centroid.setter
    def centroid(self, centroid):
        self._centroid = centroid

    def distance(self, coords):
        return coords_distance(self._centroid, coords)

class Clusters:
    """ A set of clusters and the members of each """
    def __init__(self, centroids):
        clusters = []
        points = []
        for centroid in centroids:
            clusters.append(Cluster(centroid))
            points.append([])
        self._clusters = tuple(clusters)
        self._points = tuple(points)

    def assign(self, point):
        best_points = None
        best_distance = sys.float_info.max

        for points, cluster in zip(self._points, self._clusters):
            distance = cluster.distance(point.coords)
            if distance < best_distance:
                best_points = points
                best_distance = distance

        best_points.append(point)

    def calculate_centroid(self, points):
        sums = coords_zero(points[0].coords)
        for point in points:
            sums = coords_add(sums, point.coords)
        return coords_div(sums, len(points))

    def clear_assignments(self):
        for point_list in self._points:
            point_list[:] = []

    def update_centroids(self):
        for cluster, point in zip(self._clusters, self._points):
            cluster.centroid = self.calculate_centroid(point)

    @property
    def clusters(self):
        return self._clusters

    @property
    def points(self):
        return self._points

class Player:
    """ A baseball player's batting stats """
    def __init__(self, stats):
        self._stats = stats

    @property
    def home_runs(self):
        return int(self._stats['HR'])

    @property
    def name(self):
        return self._stats['Name']

    @property
    def plate_appearances(self):
        return int(self._stats['PA'])

    @property
    def pretty_name(self):
        name = self.name.split("\\")[0]
        if name[-1] in ('*', '#'):
            name = name[:-1]
        return name

    @property
    def position(self):
        return self._stats['Pos']

    @property
    def stats(self):
        return OrderedDict(self._stats)

    @property
    def stolen_bases(self):
        return int(self._stats['SB'])

    def __str__(self):
        return self.pretty_name

def print_clusters(clusters):
    """ Print basic cluster info. """
    for cluster, points in zip(clusters.clusters, clusters.points):
        print('%.3f %.3f %s' % (cluster.centroid[0], cluster.centroid[1],
                                ', '.join(map(lambda p: str(p.label), points))))

def make_clusters(points, k):
    """ Make clusters, which is the algorithm of interest in this script """

    clusters = Clusters(map(lambda p: p.coords, points[0:k]))

    # TODO: while True
    for i in range(4):
        for point in points:
            clusters.assign(point)

        # TODO: save centroids

        clusters.update_centroids()

        # TODO: if new centroids == saved centroids, break

        print_clusters(clusters)

        clusters.clear_assignments()

def _point_for_player(player):
    """
    Creates a Point for a Player, where the coordinates of the Point will be used for clustering
    """
    coords = (player.home_runs * 100 / player.plate_appearances,
              player.stolen_bases * 100 / player.plate_appearances)
    return Point(coords, player)

def _main(filename):
    position_player_points = []
    with open(filename, 'r', newline='') as fp:
        reader = csv.DictReader(fp)
        for stats in reader:
            player = Player(stats)
            if player.position != 'P' and player.plate_appearances != 0:
                position_player_points.append(_point_for_player(player))

    make_clusters(position_player_points, 4)

if __name__ == '__main__':
    _main('1979-Pittsburgh-Pirates-Batting.csv')
