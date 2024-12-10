# blender-pcd-io

Add-on for importing and exporting PCD files from [Blender](https://www.blender.org/) 2.8+.
### Features:
* Adds ability to view & edit point-clouds using Blender's built-in tools.
* No external dependencies. However, if installed - `python-lzf` will be used to speed-up decompression of *binary_compressed* clouds.
* Supports exporting of PCD files in *binary* format.
* Supports importing of PCD files in *ascii*, *binary*, and *binary_compressed* formats.

### Missing Features:
* No support for coloured point-clouds (due to use of Blender mesh verticies).
* No support for exporting point-clouds in formats other than *binary*.
* No support for labelled point-clouds.
* No drag-and-drop support for importing/exporting files.

<p align="center">
  <img src="https://github.com/MarkHedleyJones/blender-pcd-io/raw/master/media/screenshot.png"/>
</p>

## Installation
Download the latest zip archive (pcd-io.zip) from the [releases page](https://github.com/MarkHedleyJones/blender-pcd-io/releases).

### Blender 4.2+
#### Easy Install (Recommended)
Drag and drop the zip file `pcd-io.zip` into the Blender window.

#### Manual Install
Open Blender and navigate to:

  Edit -> Preferences -> Add-ons

Click the small drop-down arrow at the top right of the dialog and select `Install from disk...`.

When prompted select the zip file `pcd-io.zip`.

<img src="https://github.com/MarkHedleyJones/blender-pcd-io/raw/master/media/screenshot-enable-addon-4.2.png"/>

### Blender 2.8+

Open Blender and navigate to:

  Edit -> Preferences -> Add-ons -> Install

When prompted select the zip file `pcd-io.zip`.
Afterwards you will see a screen like in the following image.

**NOTE:** You must enable the plugin by clicking the box shown in the screenshot before you can use it!

<img src="https://github.com/MarkHedleyJones/blender-pcd-io/raw/master/media/screenshot-enable-addon.png"/>

## Usage
After installing this plugin, there are two ways to import and export PCD files.

### 1. Import/Export from the user interface
You can import and export PCD files from the File menu (shown in first screenshot):

>  *File -> Import -> Point Cloud Data (.pcd)*

>  *File -> Export -> Point Cloud Data (.pcd)*

### 2. Import/Export programatically
You can also import and export PCD files programatically. For example:

```python
bpy.ops.import_mesh.pcd(filepath="/home/username/pointcloud_to_import.pcd")
```
```python
bpy.ops.export_mesh.pcd(filepath="/home/username/output_pointcloud.pcd")
```

### Tips:
1. Although you can't drag-and-drop .pcd files directly into the viewport (yet), you can drag-and-drop files into the file dialog to quickly navigate to the relevant folder.
1. When exporting, ensure you have selected the items you wish to export. If no objects are selected in Blender, nothing will be exported and you may see an error.
1. When exporting a pointcloud after making edits, make sure to exit the *Edit Mode* context (e.g. return to *Object Mode* context) otherwise your changes may not be reflected in the output file.
1. If you have trouble with paths not being found when importing/exporting programatically, try using an *absolute path* and without path expansion. For example: `/home/username/thing.pcd`, rather than `~/thing.pcd`.
