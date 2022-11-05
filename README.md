# blender-pcd-io

Add-on for importing and exporting PCD files from [Blender](https://www.blender.org/) 2.8+.
### Features:
* No external dependencies. Although, `python-lzf` will be used, if installed, when importing compressed pointclouds.
* Point-clouds are editable using Blender's standard modelling tools.
* Supports importing of PCD files in *ascii*, *binary*, and *binary_compressed* formats.

### Missing Features:
* No support for coloured point-clouds (due to use of Blender mesh verticies).
* No support for labelled point-clouds.
* Exports PCD files as *binary* encoded, and currently has no option to select other export formats.

<p align="center">
  <img src="https://github.com/MarkHedleyJones/blender-pcd-io/raw/master/media/screenshot.png"/>
</p>

## Installation
Download the latest zip archive (pcd-io.zip) from the [releases page](https://github.com/MarkHedleyJones/blender-pcd-io/releases).

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

  >*File -> Export -> Point Cloud Data (.pcd)*

### 2. Import/Export programatically
You can also import and export PCD files programatically. For example:

```python
bpy.ops.import_mesh.pcd(filepath="/home/username/pointcloud_to_import.pcd")
```
```python
bpy.ops.export_mesh.pcd(filepath="/home/username/output_pointcloud.pcd")
```
