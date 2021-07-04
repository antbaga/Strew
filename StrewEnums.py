import bpy
import os
from bpy.types import Operator, AddonPreferences, PropertyGroup, UIList, Panel
from bpy.props import StringProperty, IntProperty, EnumProperty, PointerProperty, CollectionProperty, BoolProperty
from . import __init__, StrewManOperators, StrewBiomeManager
import addon_utils

class Presetnamestring(bpy.types.PropertyGroup):
    presetname: bpy.props.StringProperty(
        name="name :",
        default="New Preset",
    )
    presetdesc: bpy.props.StringProperty(
        name="Description :",
        default="Custom Preset",
    )





# recup la liste des préset dans le fichier text
def enumfromblenderlist(self, context):
    enum_items = []
    CurrentPreset = cts.StrewPresetDrop.StrewPresetDropdown
    StrewFolder = str(StrewUi.SetupFolders.getfilepath(self, context))
    PresetPath = f'{StrewFolder}preset files\\{CurrentPreset}.txt'
    with open(PresetPath, 'r') as SourceListFile:
        SourceList = SourceListFile.readlines()
        if SourceList is None:
            return enum_items
        count = 0
        for Source in SourceList:
            Choice = Source.split(",")
            identifier = str(Choice[0])
            name = str(Choice[1])
            description = str(Choice[2])
            number = count
            enum_items.append((identifier, name, description, number))
            count += 1
    return enum_items


# Property de la liste de dropdown
class StrewSourceProperty(PropertyGroup):
    StrewSourceDropdown: EnumProperty(
        name="",
        description="Select source",
        # items=[]
        items=enumfromblenderlist,
    )


# Liste de dropdown
class SRCFILES_UL_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=User)



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