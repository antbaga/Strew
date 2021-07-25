import bpy
import os
from bpy.types import Operator, AddonPreferences, PropertyGroup, UIList, Panel
from bpy.props import StringProperty, IntProperty, EnumProperty, PointerProperty, CollectionProperty, BoolProperty
from . import __init__, StrewManOperators, StrewBiomeManager, StrewUi
import addon_utils


asset_list_enum = []
OldPreset = ""
# recup la liste des préset dans le fichier text
def enum(self, context):
    global asset_list_enum
    global OldPreset
    CurrentPreset = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown
    if CurrentPreset == OldPreset:
        return asset_list_enum
    else:
        asset_list_enum.clear()
        StrewFolder = str(StrewUi.SetupFolders.getfilepath(self, context))
        PresetPath = f'{StrewFolder}preset files\\{CurrentPreset}.txt'
        with open(PresetPath, 'r') as SourceListFile:
            SourceList = SourceListFile.readlines()
            if SourceList is None:
                return enum_items
        for count, source in enumerate(SourceList, 1):
            name = source.strip("\n").split(",")[1]
            identifier = source.strip("\n").split(",")[1]
            description = source.strip("\n").split(",")[1]
            asset_list_enum.append((identifier, name, description))
        OldPreset = CurrentPreset
        return asset_list_enum

def materialupdate(self,context):
    value = bpy.context.scene.preset_name_string.MaterialFloat
    bpy.data.materials["Material"].node_tree.nodes["Principled BSDF"].inputs[5].default_value = value

class Presetnamestring(bpy.types.PropertyGroup):
    presetname: bpy.props.StringProperty(
        name="name :",
        default="New preset",
    )
    presetdesc: bpy.props.StringProperty(
        name="Description :",
        default="Custom Preset",
    )
    AssetList: EnumProperty(
        items=enum,
        options={"ENUM_FLAG"},
    )
    Decorator: EnumProperty(
        items=[("Trees","Trees","Trees"),("Grass","Grass","Grass"),("Rocks","Rocks","Rocks")],
        #items=enum,
        options={"ENUM_FLAG"},
    )
    MaterialFloat: bpy.props.FloatProperty(
        name="name:",
        default=1.0,
        update=materialupdate
    )





classes = [
Presetnamestring,
]

def register() :
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.preset_name_string = bpy.props.PointerProperty(type=Presetnamestring)


def unregister() :
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.preset_name_string