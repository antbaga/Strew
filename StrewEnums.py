import bpy
import os
from bpy.types import Operator, AddonPreferences, PropertyGroup, UIList, Panel
from bpy.props import StringProperty, IntProperty, EnumProperty, PointerProperty, CollectionProperty, BoolProperty
from . import __init__, StrewManOperators, StrewBiomeManager, StrewUi
import addon_utils

asset_list_enum = []
# recup la liste des préset dans le fichier text
def enumfrompreset(self, context):
    global asset_list_enum
    asset_list_enum = []
    CurrentPreset = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown
    StrewFolder = str(StrewUi.SetupFolders.getfilepath(self, context))
    PresetPath = f'{StrewFolder}preset files\\{CurrentPreset}.txt'
    with open(PresetPath, 'r') as SourceListFile:
        SourceList = SourceListFile.readlines()
        if SourceList is None:
            return enum_items
        count = 1
        for Source in SourceList:
            Choice = Source.split(",")
            identifier = str(Choice[1]).strip("\n")
            name = str(Choice[1]).strip("\n")
            description = str(Choice[1]).strip("\n")
            number = count
            asset_list_enum.append((identifier, name, description))
            count += 1
    return asset_list_enum

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
        #items=[("1I","1N","1D"),("2I","2N","2D"),("3I","3N","3D")],
        items=enum,
        options={"ENUM_FLAG"},
        update=printer
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