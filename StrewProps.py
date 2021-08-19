import bpy
import os
from bpy.types import Operator, AddonPreferences, PropertyGroup, UIList, Panel
from bpy.props import StringProperty, IntProperty, EnumProperty, PointerProperty, CollectionProperty, BoolProperty
from . import __init__, StrewUi, StrewFunctions, StrewManOperators
import addon_utils

asset_list_enum = []
old_preset = ""


#####################################################################################
#
#       DROPDOWN MENU OF BIOME
#
#####################################################################################


preset_list_enum = StrewFunctions.preset_list_enum


class StrewPresetProperty(PropertyGroup):

    def update_strewpresetdrop(self, context):
        StrewManOperators.SCENE_OT_list_populate.execute(self, context)
        return None

    def enumfromfile(self, context):
        global preset_list_enum
        preset_list_enum.clear()
        thumb_list = StrewFunctions.get_enum_biomes(self, context)
        for i in thumb_list:
            preset_list_enum.append(i)
        return preset_list_enum

    StrewPresetDropdown: EnumProperty(
        name="",
        description="Select preset",
        items=enumfromfile,
        update=update_strewpresetdrop)


class PRESET_UL_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=User)


#####################################################################################
#
#       DROPDOWN MENU OF SOURCES FILES
#
#####################################################################################


sources_list_enum = StrewFunctions.sources_list_enum


class StrewSourceProperty(PropertyGroup):

    def update_sourcedrop(self, context):
        StrewManOperators.SCENE_OT_source_populate.execute(self, context)
        return None

    def enumfromblenderlist(self, context):
        global sources_list_enum
        sources_list_enum.clear()
        thumb_list = StrewFunctions.get_source_files(self, context)
        for i in thumb_list:
            sources_list_enum.append(i)
        return sources_list_enum

    StrewSourceDropdown: EnumProperty(
        name="",
        description="Select source",
        items=enumfromblenderlist,
        update=update_sourcedrop,
        default=0)


class SRCFILES_UL_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=User)


#####################################################################################
#
#       BIOME LISTS FOR BIOME MANAGER
#
#####################################################################################


class SMAAsset(PropertyGroup):
    description: StringProperty()
    file: StringProperty()
    type: StringProperty()
    category: StringProperty()
    objects: StringProperty()


class SMAList(PropertyGroup):
    collection: CollectionProperty(
        name="SMAA",
        type=SMAAsset)
    active_user_index: IntProperty()


class SMA_UL_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


#####################################################################################
#
#       BIOME LISTS FOR SOURCE MANAGER
#
#####################################################################################


class SMSAsset(PropertyGroup):
    description: StringProperty()
    file: StringProperty()
    type: StringProperty()
    category: StringProperty()
    objects: StringProperty()


class SMSList(PropertyGroup):
    collection: CollectionProperty(
        name="SMSA",
        type=SMSAsset)
    active_user_index: IntProperty(
    )


class SMS_UL_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.context_pointer_set("active_smms_user", item, )
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


#####################################################################################
#
#       PROPERTIES
#
#####################################################################################


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


def imported_biome_list(biome_name):

    biome_list = [biome_name]

    if bpy.context.scene.get('Strew_Imported_Biomes') is not None:
        for biome in bpy.context.scene.get('Strew_Imported_Biomes'):
            if biome not in biome_list:
                biome_list.append(biome)
            else:
                return "already imported"

    bpy.context.scene["Strew_Imported_Biomes"] = biome_list


#####################################################################################
#
#       SAVE ASSET PROPS
#
#####################################################################################

class SaveAsset(PropertyGroup):
    asset_name: StringProperty(
        default="",
        name="Name"
    )
    asset_description: StringProperty(
        default="",
        name="Description"
    )
    asset_category: StringProperty(
        default="",
        name="Category"
    )
    asset_type: BoolProperty(
        default=False,
        name="Use LOD"
    )
    lod_0: PointerProperty(
        name="LOD 0",
        type=bpy.types.Object
    )
    lod_1: PointerProperty(
        name="LOD 1",
        type=bpy.types.Object
    )
    lod_2: PointerProperty(
        name="LOD 2",
        type=bpy.types.Object
    )
    lod_3: PointerProperty(
        name="LOD 3",
        type=bpy.types.Object
    )
    proxy: PointerProperty(
        name="Proxy",
        type=bpy.types.Object
    )
    globalsave: BoolProperty(
        name="Save globally",
        description="If true, a copy of the asset will be saved in the Strew library"
    )

#####################################################################################
#
#       REGISTER AND UNREGISTER
#
#####################################################################################


classes = [
    # --- Dropdown menu of biome ---
    StrewPresetProperty,
    PRESET_UL_List,
    # --- Dropdown menu of biome ---
    StrewSourceProperty,
    SRCFILES_UL_List,
    # --- Biome list for manager ---
    SMAAsset,
    SMAList,
    SMA_UL_List,
    # --- Sources list for manager ---
    SMSAsset,
    SMSList,
    SMS_UL_List,
    # --- Properties ---
    PresetNameString,
    UiSwitch,
    # --- Save Assets ---
    SaveAsset,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.preset_name_string = bpy.props.PointerProperty(type=PresetNameString)
    bpy.types.Scene.strew_ui_switch = bpy.props.PointerProperty(type=UiSwitch)
    bpy.types.Scene.StrewPresetDrop = PointerProperty(type=StrewPresetProperty)
    bpy.types.Scene.StrewSourceDrop = PointerProperty(type=StrewSourceProperty)
    bpy.types.Scene.StrewSaveAsset = PointerProperty(type=SaveAsset)
    bpy.types.Scene.SMAL = PointerProperty(type=SMAList)
    bpy.types.Scene.SMSL = PointerProperty(type=SMSList)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.preset_name_string
    del bpy.types.Scene.strew_ui_switch
    del bpy.types.Scene.StrewPresetDrop
    del bpy.types.Scene.StrewSourceDrop
    del bpy.types.Scene.StrewSaveAsset
    del bpy.types.Scene.SMAL
    del bpy.types.Scene.SMSL
