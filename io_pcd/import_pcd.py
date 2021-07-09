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

""" This script is an importer for the .pcd files"""

import os
import struct
import sys

header = {
    'VERSION': None,
    'FIELDS': None,
    'SIZE': None,
    'TYPE': None,
    'COUNT': None,
    'WIDTH': None,
    'HEIGHT': None,
    'VIEWPOINT': None,
    'POINTS': None,
    'DATA': None,
}


def validated_header(header):
    assert None not in header.values()
    transformers = {
        'VERSION': lambda x: x,
        'FIELDS': lambda x: x.split(' '),
        'SIZE': lambda x: list(map(int, x.split(' '))),
        'TYPE': lambda x: x.split(' '),
        'COUNT': lambda x: list(map(int, x.split(' '))),
        'WIDTH': lambda x: int(x),
        'HEIGHT': lambda x: int(x),
        'VIEWPOINT': lambda x: list(map(float, x.split(' '))),
        'POINTS': lambda x: int(x),
        'DATA': lambda x: str(x),
    }
    header = {key: transformers[key](header[key]) for key in header}
    assert header['WIDTH'] * header['HEIGHT'] == header['POINTS']
    assert header['DATA'] in ['binary', 'binary_compressed']
    assert len(header['FIELDS']) == len(header['SIZE'])
    assert len(header['FIELDS']) == len(header['TYPE'])
    assert len(header['FIELDS']) == len(header['COUNT'])
    for field_type in header['TYPE']:
        assert field_type in ['I', 'U', 'F']
    for field_size in header['SIZE']:
        assert field_size in [1, 2, 4, 8]
    return header


def read_header(file_descriptor):
    def first(arr):
        return arr[0], arr[1:]

    def front(arr):
        return arr[:-1], arr[-1]

    for line in file_descriptor:
        row, _ = front(line.decode("utf-8"))
        head, tail = first(row.split(' '))
        if head in header:
            header[head] = " ".join(tail)
        if head == 'DATA':
            break
    return validated_header(header)


def get_struct_format_chars(header):
    """Convert the field types/sizes into format specifiers for the
    struct package"""
    struct_formats = {
        'I': ['b', 'h', 'l', 'q'],
        'U': ['B', 'H', 'I', 'Q'],
        'F': ['x', 'e', 'f', 'd'],
    }
    struct_formatting = []
    for field_type, field_size in zip(header['TYPE'], header['SIZE']):
        field_size_index = int(field_size ** 0.5)
        struct_formatting.append(struct_formats[field_type][field_size_index])
    # Check that a 1 byte float hasn't been specified!
    assert 'x' not in struct_formatting
    return ''.join(struct_formatting)


def load_compressed_data(f):
    import lzf

    return []


def load_pcd_file(filepath):
    points = []
    with open(filepath, 'rb') as f:
        header = read_header(f)
        struct_format = get_struct_format_chars(header)
        point_bytes = sum(header['SIZE'])
        points = []
        if header['DATA'] == 'binary_compressed':
            try:
                import lzf
            except ModuleNotFoundError as e:
                py_version = sys.version_info
                return (
                    "This PCD file is compressed but the decompressor "
                    "library is not installed on your system. Please install "
                    f"python-lzf for Python {py_version.major}. "
                    "For example, by running: pip install python-lzf"
                )
            # Two unsigned ints at start of data block hold the compressed
            # and uncompressed size of the point data.
            len_compressed, len_decompressed = struct.unpack('II', f.read(8))
            data = lzf.decompress(f.read(len_compressed), len_decompressed)
            stride = struct.calcsize(struct_format)
            indicies = range(0, header['POINTS'] * stride, stride)
            chunks = (data[index : index + stride] for index in indicies)
            for chunk in chunks:
                # keep only x, y, z from each point
                points += struct.unpack(struct_format, chunk)[:3]
            return points
        else:
            for index in range(header['POINTS']):
                # keep only x, y, z from each point
                points += struct.unpack(struct_format, f.read(point_bytes))[:3]
    return points


def convert_points_to_mesh_verticies(points, pcd_name):
    import bpy

    mesh = bpy.data.meshes.new(pcd_name)
    mesh.vertices.add(len(points))
    mesh.vertices.foreach_set("co", points)
    return mesh


def import_pcd(context, filepath):

    import time
    import bpy

    t = time.time()
    pcd_name = bpy.path.display_name_from_filepath(filepath)
    points = load_pcd_file(filepath)

    if type(points) == str:
        return points
    elif len(points) == 0:
        return {'CANCELLED'}

    mesh_verticies = convert_points_to_mesh_verticies(points, pcd_name)

    obj = bpy.data.objects.new(pcd_name, mesh_verticies)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    print(
        "\nSuccessfully imported %d points from %r in %.3f sec"
        % (num_points, filepath, time.time() - t)
    )

    return {'FINISHED'}
