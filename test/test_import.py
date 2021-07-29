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
    # Strip out any additional fields and convert to Point objects
    return [Point(*x[0:3]) for x in data['points']]


def get_expected_points():
    return [
        Point(-2.0, -2.0, -2.0),
        Point(-1.0, -1.0, -1.0),
        Point(0.0, 0.0, 0.0),
        Point(1.0, 1.0, 1.0),
        Point(2.0, 2.0, 2.0),
    ]


def check_points(points):
    expected_points = get_expected_points()
    assert len(expected_points) == len(points)
    for index in range(len(points)):
        assert points[index] == expected_points[index]


def check_pcd_data(pcd_data):
    check_points(pcd_data_to_points(pcd_data))


def test_xyz_ascii():
    path_pcd = os.path.join(path_pointclouds, 'xyz_ascii.pcd')
    check_pcd_data(import_pcd.load_pcd_file(path_pcd))


def test_xyz_binary():
    path_pcd = os.path.join(path_pointclouds, 'xyz_binary.pcd')
    check_pcd_data(import_pcd.load_pcd_file(path_pcd))


def test_xyz_binary_compressed_internal_lzf_decompression():
    path_pcd = os.path.join(path_pointclouds, 'xyz_binary_compressed.pcd')
    check_pcd_data(
        import_pcd.load_pcd_file(
            path_pcd, lzf_library=import_pcd.CompressonLib.FORCE_INTERNAL
        )
    )


def test_xyz_binary_compressed_external_lzf_decompression():
    path_pcd = os.path.join(path_pointclouds, 'xyz_binary_compressed.pcd')
    check_pcd_data(
        import_pcd.load_pcd_file(
            path_pcd, lzf_library=import_pcd.CompressonLib.FORCE_EXTERNAL
        )
    )
