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

import enum
import os
import struct
import sys
import time

header = {
    "VERSION": None,
    "FIELDS": None,
    "SIZE": None,
    "TYPE": None,
    "COUNT": None,
    "WIDTH": None,
    "HEIGHT": None,
    "VIEWPOINT": None,
    "POINTS": None,
    "DATA": None,
}


class CompressonLib(enum.Enum):
    AUTO = 0
    FORCE_INTERNAL = -1
    FORCE_EXTERNAL = 1


lzf_library = CompressonLib.AUTO


def validated_header(header):
    assert None not in header.values()
    transformers = {
        "VERSION": lambda x: x,
        "FIELDS": lambda x: x.split(" "),
        "SIZE": lambda x: list(map(int, x.split(" "))),
        "TYPE": lambda x: x.split(" "),
        "COUNT": lambda x: list(map(int, x.split(" "))),
        "WIDTH": lambda x: int(x),
        "HEIGHT": lambda x: int(x),
        "VIEWPOINT": lambda x: list(map(float, x.split(" "))),
        "POINTS": lambda x: int(x),
        "DATA": lambda x: str(x),
    }
    header = {key: transformers[key](header[key]) for key in header}
    assert header["WIDTH"] * header["HEIGHT"] == header["POINTS"]
    assert header["DATA"] in ["ascii", "binary", "binary_compressed"]
    assert len(header["FIELDS"]) == len(header["SIZE"])
    assert len(header["FIELDS"]) == len(header["TYPE"])
    assert len(header["FIELDS"]) == len(header["COUNT"])
    for field_type in header["TYPE"]:
        assert field_type in ["I", "U", "F"]
    for field_size in header["SIZE"]:
        assert field_size in [1, 2, 4, 8]
    return header


def read_header(binary_file):
    def first(arr):
        return arr[0], arr[1:]

    def convert_text(binary_line):
        text_line = binary_line.decode("utf-8")
        # Clean line-endings from binary data
        clean_line_ending = text_line.rstrip("\n\r")
        return clean_line_ending.rstrip()

    for binary_line in binary_file:
        line = convert_text(binary_line)
        head, tail = first(line.split(" "))
        if head in header:
            header[head] = " ".join(tail)
        if head == "DATA":
            break
    return validated_header(header)


def get_struct_format_chars(header):
    """Convert the field types/sizes into format specifiers for the
    struct package"""
    struct_formats = {
        "I": ["b", "h", "l", "q"],
        "U": ["B", "H", "I", "Q"],
        "F": ["x", "e", "f", "d"],
    }
    struct_formatting = []
    for field_type, field_size in zip(header["TYPE"], header["SIZE"]):
        field_size_index = int(field_size**0.5)
        struct_formatting.append(struct_formats[field_type][field_size_index])
    # Check that a 1 byte float hasn't been specified!
    assert "x" not in struct_formatting
    return "".join(struct_formatting)


def lzf_decompress(compressed, expected_length, lzf_library=CompressonLib.AUTO):
    """This decompression function was copied from:
    https://programtalk.com/python-examples/lzf.decompress
    which is under an MIT License
    """

    if lzf_library == CompressonLib.FORCE_INTERNAL:
        # Force to use internal implementation
        HAS_PYTHON_LZF = False
    elif lzf_library == CompressonLib.FORCE_EXTERNAL:
        # Force to use python-lzf
        import lzf

        HAS_PYTHON_LZF = True
    else:
        # Autodetect presence of python-lzf
        HAS_PYTHON_LZF = False
        try:
            import lzf

            if "decompress" in dir(lzf):
                HAS_PYTHON_LZF = True
            else:
                print(
                    "WARNING: An incompatible compression library (lzf) is",
                    "installed on your system, which conflicts with the target",
                    "compression library (python-lzf). Please remove this",
                    "library if blender cannot detect your installation of",
                    " python-lzf.",
                )
        except ModuleNotFoundError as e:
            print(
                "WARNING: This PCD file is compressed, but the target",
                "compression library (python-lzf) is not installed.",
            )

    if HAS_PYTHON_LZF:
        return lzf.decompress(compressed, expected_length)
    else:
        print(
            "NOTICE: Importing PCD using a pure Python implementation for",
            "lzf-decompression. Please note that performance will be limited.",
            "To improve performance please install python-lzf for Python",
            f"{sys.version_info[0]}. For example, by running: ",
            "pip install python-lzf",
        )
        in_stream = bytearray(compressed)
        in_len = len(in_stream)
        in_index = 0
        out_stream = bytearray()
        out_index = 0

        while in_index < in_len:
            ctrl = in_stream[in_index]
            if not isinstance(ctrl, int):
                raise Exception(
                    "lzf_decompress",
                    "ctrl should be a number %s for key %s" % (str(ctrl), self._key),
                )
            in_index = in_index + 1
            if ctrl < 32:
                for x in range(0, ctrl + 1):
                    out_stream.append(in_stream[in_index])
                    in_index = in_index + 1
                    out_index = out_index + 1
            else:
                length = ctrl >> 5
                if length == 7:
                    length = length + in_stream[in_index]
                    in_index = in_index + 1

                ref = out_index - ((ctrl & 0x1F) << 8) - in_stream[in_index] - 1
                in_index = in_index + 1
                for x in range(0, length + 2):
                    out_stream.append(out_stream[ref])
                    ref = ref + 1
                    out_index = out_index + 1
        if len(out_stream) != expected_length:
            raise Exception(
                "lzf_decompress",
                "Expected lengths do not match %d != %d for key %s"
                % (len(out_stream), expected_length, self._key),
            )
        return bytes(out_stream)


def parse_ascii_points(file, header, struct_format):
    return [list(map(float, row.decode().rstrip().split(" "))) for row in file]


def parse_binary_points(file, header, struct_format):
    bytes_per_point = sum(header["SIZE"])
    return [
        (struct.unpack(struct_format, file.read(bytes_per_point)))
        for x in range(header["POINTS"])
    ]


def parse_binary_compressed_points(file, header, struct_format):
    # Two unsigned-ints at beginning of data block hold the sizes
    # (in bytes) of the compressed and uncompressed point data.
    len_compressed, len_decompressed = struct.unpack("II", file.read(8))
    # Data is organised as: [x0, x1, x2, y0, y1, y2, z0, z1, z2, ...]
    data = lzf_decompress(file.read(len_compressed), len_decompressed, lzf_library)
    # Unzipped will be organised like so (convenient for zipping):
    # [[x0, x1, x2, ...], [y0, y1, y2, ...], [z0, z1, z2, ...], ...]
    unzipped = []
    for field_idx in range(len(header["FIELDS"])):
        # E.g if points are float type (f) and there are 5 points in total
        # then the 'x' field block_format will be: 'fffff'
        blk_fmt = "".join(struct_format[field_idx] for x in range(header["POINTS"]))
        # Figure out how big this block would be in bytes
        blk_fmt_num_bytes = struct.calcsize(blk_fmt)
        chunk_start = field_idx * blk_fmt_num_bytes
        chunk_end = chunk_start + blk_fmt_num_bytes
        unzipped.append(struct.unpack(blk_fmt, data[chunk_start:chunk_end]))
    return list(zip(*unzipped))


def load_pcd_file(filepath):
    """Load the file and return a dictionary like:
    {"points": [(1.0, 1.0, 1.0), ...], "fields": ['x', 'y', 'z']}"""
    with open(filepath, "rb") as file:
        header = read_header(file)
        struct_format = get_struct_format_chars(header)
        parsers = {
            "ascii": parse_ascii_points,
            "binary": parse_binary_points,
            "binary_compressed": parse_binary_compressed_points,
        }
        points = parsers[header["DATA"]](file, header, struct_format)
        return {"points": points, "fields": header["FIELDS"]}


def convert_points_to_mesh_verticies(pcd_data, pcd_name):
    import bpy, itertools

    mesh = bpy.data.meshes.new(pcd_name)
    mesh.vertices.add(len(pcd_data["points"]))
    points = list(itertools.chain(*[list(pt[:3]) for pt in pcd_data["points"]]))
    mesh.vertices.foreach_set("co", points)
    # Maybe we can store extra fileds in this object somehow?
    return mesh


def import_pcd(context, filepath):
    import bpy

    t = time.time()
    pcd_name = bpy.path.display_name_from_filepath(filepath)
    pcd_data = load_pcd_file(filepath)

    if type(pcd_data) == str:
        return pcd_data
    elif len(pcd_data["points"]) == 0:
        return "Point cloud contains no points"

    mesh_verticies = convert_points_to_mesh_verticies(pcd_data, pcd_name)

    obj = bpy.data.objects.new(pcd_name, mesh_verticies)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    print(
        "\nSuccessfully imported %d points from %r in %.3f sec"
        % (len(pcd_data["points"]), filepath, time.time() - t)
    )

    return {"FINISHED"}


if __name__ == "__main__":
    """For testing interactively inside Blender. For testing outside Blender, run pytest under ./test
    """
    import bpy
    import os

    pointcloud = "xyz_binary_compressed.pcd"
    path_dev_repo = "./repos/blender-pcd-io"  # Adjust for your environment!
    path_pointcloud = os.path.join(path_dev_repo, "test/pointclouds", pointcloud)

    import_pcd(bpy.context, path_pointcloud)
