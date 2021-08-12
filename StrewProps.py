import bpy
import os
from bpy.types import Operator, AddonPreferences, PropertyGroup, UIList, Panel
from bpy.props import StringProperty, IntProperty, EnumProperty, PointerProperty, CollectionProperty, BoolProperty
from . import __init__, StrewUi, StrewFunctions
import addon_utils

asset_list_enum = []
old_preset = ""


class UiSwitch(bpy.types.PropertyGroup):
    general_panel: bpy.props.BoolProperty(
        name="general_panel",
        default=True,
    )
    asset_manager: bpy.props.BoolProperty(
        name="asset_manager",
        default=False,
    )
    panels: bpy.props.EnumProperty(
        name="panels",
        description="Preferences panel",
        items=[
            ("General", "General", "All things in the universe"),
            ("Assets", "Assets", "The asset manager"),
            ("Biomes","Biomes", "The Biome manager")
        ],
        default={"General"},
        options={"ENUM_FLAG"}
    )


# recup la liste des préset dans le fichier text
def enum(self, context):
    global asset_list_enum
    global old_preset

    current_preset = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown

    if current_preset == old_preset:        # if no preset is selected or not changed
        return asset_list_enum              # it return empty list or previous list
    else:
        asset_list_enum.clear()             # clear the list

        asset_list_enum = StrewFunctions.get_assets_enum(self, context, current_preset)     # get the assets list
        old_preset = current_preset         # tell the preset has been changed
        return asset_list_enum


class PresetNameString(PropertyGroup):
    new_name: bpy.props.StringProperty(
        name="name :",
        default="New preset",
    )
    new_description: bpy.props.StringProperty(
        name="Description :",
        default="Custom Preset",
    )
    AssetList: EnumProperty(
        items=enum,
        options={"ENUM_FLAG"},
    )
    Decorator: EnumProperty(
        items=[("Trees", "Trees", "Trees"), ("Grass", "Grass", "Grass"), ("Rocks", "Rocks", "Rocks")],
        options={"ENUM_FLAG"},
    )


classes = [
    PresetNameString,
    UiSwitch,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.preset_name_string = bpy.props.PointerProperty(type=PresetNameString)
    bpy.types.Scene.strew_ui_switch = bpy.props.PointerProperty(type=UiSwitch)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.preset_name_string
    del bpy.types.Scene.strew_ui_switch






"""






import os
import bpy

preview_collections = {}

def enum_previews_from_directory_items(self, context):
    pcoll = preview_collections.get("main")
    if not pcoll:
        return []

    if self.my_previews_dir == "": # use better default
        # put some code in here to populate default list
        print("MAKE A NEW THUMB LIST HERE")
        newlist = []
        
        # a list of items with name, filepath to image, and unique i

        #thumb = pcoll.load(filepath, filepath, 'IMAGE')
        #item = (name, name, "", thumb.icon_id, i) 
        #newlist.append(item)
             
        return newlist

    return pcoll.my_previews


class PreviewsExamplePanel(bpy.types.Panel):

    bl_label = "Previews Example Panel"
    bl_idname = "OBJECT_PT_previews"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        row = layout.row()
        row.prop(wm, "my_previews_dir")

        row = layout.row()
        row.template_icon_view(wm, "my_previews")

        row = layout.row()
        row.prop(wm, "my_previews")


# We can store multiple preview collections here,
# however in this example we only store "main"


def preview_dir_update(wm, context):
    print("wm.my_previews_dir = %s" % wm.my_previews_dir)


    enum_items = []

    wm = context.window_manager
    directory = wm.my_previews_dir

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    print("Scanning directory: %s" % directory)

    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((name, name, name, thumb.icon_id, i))

    pcoll.my_previews = enum_items
    pcoll.my_previews_dir = directory

    return None

def preview_enum_update(wm, context):
    print("wm.my_previews = %s" % wm.my_previews)
    return None

def register():
    from bpy.types import WindowManager
    from bpy.props import (
            StringProperty,
            EnumProperty,
            )

    WindowManager.my_previews_dir = StringProperty(
            name="Folder Path",
            subtype='DIR_PATH',
            default="",
            update=preview_dir_update,
            )

    WindowManager.my_previews = EnumProperty(
            items=enum_previews_from_directory_items,
            update=preview_enum_update,
                )

    # Note that preview collections returned by bpy.utils.previews
    # are regular Python objects - you can use them to store custom data.
    #
    # This is especially useful here, since:
    # - It avoids us regenerating the whole enum over and over.
    # - It can store enum_items' strings
    #   (remember you have to keep those strings somewhere in py,
    #   else they get freed and Blender references invalid memory!).
    import bpy.utils.previews

    pcol = preview_collections.setdefault("main", bpy.utils.previews.new())

    bpy.utils.register_class(PreviewsExamplePanel)


def unregister():
    from bpy.types import WindowManager

    del WindowManager.my_previews

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    bpy.utils.unregister_class(PreviewsExamplePanel)


if __name__ == "__main__":
    register()









"""