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

import os

import bpy
from bpy.props import CollectionProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper, ImportHelper

bl_info = {
    "author": "Mark Hedley Jones",
    "blender": (2, 80, 0),
    "category": "Import-Export",
    "description": "Import and export Point Cloud Data (PCD) files as editible objects",
    "doc_url": "https://github.com/MarkHedleyJones/blender-pcd-io",
    "location": "File > Import/Export > Point Cloud Data (.pcd)",
    "name": "Point Cloud Data (PCD) format",
    "version": (1, 5, 3),
    "warning": "",
}

if "bpy" in locals():
    import importlib

    if "import_pcd" in locals():
        importlib.reload(import_pcd)
    if "export_pcd" in locals():
        importlib.reload(export_pcd)


class ImportPCD(Operator, ImportHelper):
    """Import a PCD file"""

    bl_idname = "import_mesh.pcd"
    bl_label = "Import PCD file"

    filename_ext = ".pcd"

    files: CollectionProperty(
        name="File Path",
        description="File path used for importing the PCD file",
        type=bpy.types.OperatorFileListElement,
    )

    directory: StringProperty()

    filter_glob: StringProperty(default="*.pcd", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        from . import import_pcd

        paths = [os.path.join(self.directory, name.name) for name in self.files]

        if not paths:
            paths.append(self.filepath)

        for path in paths:
            import_pcd.import_pcd(context, path)

        context.window.cursor_set("DEFAULT")

        return {"FINISHED"}


class ExportPCD(Operator, ExportHelper):
    """Export a PCD file"""

    bl_idname = "export_mesh.pcd"
    bl_label = "Export pcd file"

    filename_ext = ".pcd"

    filter_glob: StringProperty(default="*.pcd", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return "MESH" in [x.type for x in context.selected_objects]

    def execute(self, context):
        from . import export_pcd

        return export_pcd.export_pcd(context, self.filepath)


def menu_func_import(self, context):
    self.layout.operator(ImportPCD.bl_idname, text="Point Cloud Data (.pcd)")


def menu_func_export(self, context):
    self.layout.operator(ExportPCD.bl_idname, text="Point Cloud Data (.pcd)")


def register():
    bpy.utils.register_class(ImportPCD)
    bpy.utils.register_class(ExportPCD)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ImportPCD)
    bpy.utils.unregister_class(ExportPCD)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
