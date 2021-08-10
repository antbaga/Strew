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
