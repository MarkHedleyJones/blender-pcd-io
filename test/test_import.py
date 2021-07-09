#!/usr/bin/env python3

import sys, os

# Import the import script for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'io_pcd'))
import import_pcd

path_pointclouds = os.path.join(os.path.dirname(__file__), 'pointclouds')


class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __lt__(self, other):
        if self.x != other.x:
            return self.x < other.x
        elif self.y != other.y:
            return self.y < other.y
        else:
            return self.z < other.z

    def __str__(self):
        return f"({self.x},{self.y},{self.z})"

    def __repr__(self):
        return self.__str__()


def pcd_data_to_points(data):
    stride = 3  # Should only have x, y, z fields
    assert len(data) % stride == 0
    num_points = int(len(data) / stride)
    indicies = range(0, num_points * stride, stride)
    chunks = (data[index : index + stride] for index in indicies)
    return map(lambda x: Point(*x), chunks)


def get_expected_points():
    return [
        Point(-1, -1, -1),
        Point(-1, -1, 1),
        Point(-1, 1, -1),
        Point(-1, 1, 1),
        Point(1, -1, -1),
        Point(1, -1, 1),
        Point(1, 1, -1),
        Point(1, 1, 1),
    ]


def test_xyz_binary():
    path_pcd = os.path.join(path_pointclouds, 'xyz_binary.pcd')
    pcd = import_pcd.load_pcd_file(path_pcd)
    points = sorted(pcd_data_to_points(pcd))
    expected_points = get_expected_points()
    assert len(expected_points) == len(points)
    for index in range(len(points)):
        print(index, points[index], expected_points[index])
        assert points[index] == expected_points[index]


def test_xyz_binary_compressed():
    path_pcd = os.path.join(path_pointclouds, 'xyz_binary_compressed.pcd')
    pcd = import_pcd.load_pcd_file(path_pcd)
    points = sorted(pcd_data_to_points(pcd))
    expected_points = get_expected_points()
    assert len(expected_points) == len(points)
    for index in range(len(points)):
        print(index, points[index], expected_points[index])
        assert points[index] == expected_points[index]
