# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

""" This script is an exporter to the .pcd files.
It takes the currently selceted object and writes it to a binary encoded .pcd
file."""

import struct


def export_pcd(context, filepath):
    points = []
    for cloud in [x for x in context.selected_objects if x.type == 'MESH']:
        points += [(cloud.matrix_world @ v.co) for v in cloud.data.vertices]

    num_points = len(points)

    with open(filepath, 'wb') as f:
        f.write("# .PCD v0.7 - Point Cloud Data file format\n".encode())
        f.write("VERSION 0.7\n".encode())
        f.write("FIELDS x y z\n".encode())
        f.write("SIZE 4 4 4\n".encode())
        f.write("TYPE F F F\n".encode())
        f.write("COUNT 1 1 1\n".encode())
        f.write("WIDTH {}\n".format(num_points).encode())
        f.write("HEIGHT 1\n".encode())
        f.write("VIEWPOINT 0 0 0 1 0 0 0\n".encode())
        f.write("POINTS {}\n".format(num_points).encode())
        f.write("DATA binary\n".encode())
        for point in points:
            f.write(struct.pack('fff', point[0], point[1], point[2]))

    return {'FINISHED'}
