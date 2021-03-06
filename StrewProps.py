import bpy
import os
from bpy.types import Operator, AddonPreferences, PropertyGroup, UIList, Panel
from bpy.props import StringProperty, IntProperty, EnumProperty, PointerProperty, CollectionProperty, BoolProperty
from . import __init__, StrewUi, StrewFunctions, StrewManOperators, StrewBiomeFunctions
import addon_utils
import json

asset_list_enum = []
old_preset = ""


#####################################################################################
#
#       DROPDOWNS
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


imported_biomes_enum = StrewFunctions.imported_list_enum


class StrewImportedBiomes(PropertyGroup):

    def update_imported_biomes(self, context):
        StrewBiomeFunctions.switch_active_biome(self.ImportedBiomes)   # update biome
        return None

    def get_imported_biomes(self, context):
        global preset_list_enum
        preset_list_enum.clear()
        thumb_list = StrewBiomeFunctions.get_imported_biomes_list()    # get list of imported biomes
        for i in thumb_list:
            preset_list_enum.append(i)
        return preset_list_enum

    ImportedBiomes: EnumProperty(
        name="",
        description="Select biome",
        items=get_imported_biomes,
        update=update_imported_biomes)


#####################################################################################
#
#       LISTS
#
#####################################################################################


class PRESET_UL_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=User)


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
#       LISTS PROPS
#
#####################################################################################


class SMAAsset(PropertyGroup):
    description: StringProperty()
    file: StringProperty()
    type: StringProperty()
    category: StringProperty()
    group: StringProperty()
    objects: StringProperty()


class SMAList(PropertyGroup):
    # FILLED FROM:
    #   strew.list_populate (Operator)

    collection: CollectionProperty(
        name="SMAA",
        type=SMAAsset)
    active_user_index: IntProperty()


class SMSAsset(PropertyGroup):
    description: StringProperty()
    file: StringProperty()
    type: StringProperty()
    category: StringProperty()
    group: StringProperty()
    objects: StringProperty()


class LibraryList(PropertyGroup):
    # FILLED FROM:
    #   strew.source_populate (Operator)

    asset_library: CollectionProperty(
        name="Assets Library",
        type=SMSAsset)
    active_user_index: IntProperty(
    )


#####################################################################################
#
#       PANELS
#
#####################################################################################


class PanelSwitch(bpy.types.PropertyGroup):
    MainView: bpy.props.EnumProperty(
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
    Preferences: bpy.props.EnumProperty(
        name="panels",
        description="Preferences panel",
        items=[
            ("Settings", "Settings", "Strew settings"),
            ("Assets", "Assets manager", "The asset manager"),
            ("Biomes","Biomes manager", "The Biome manager")
        ],
        default={"Settings"},
        options={"ENUM_FLAG"}
    )
    # Useless prop, only there for UI style
    false_prop: BoolProperty(default=False)
    expand_general: BoolProperty(default=True)
    expand_random: BoolProperty(default=True)
    expand_visibility: BoolProperty(default=True)
    expand_effectors: BoolProperty(default=True)

    expand_effectors_path: BoolProperty(default=False)
    expand_effectors_scale: BoolProperty(default=False)
    expand_effectors_sharpness: BoolProperty(default=False)
    expand_effectors_cavity: BoolProperty(default=False)
    expand_effectors_slope: BoolProperty(default=False)
    expand_effectors_paint: BoolProperty(default=False)
    expand_effectors_density: BoolProperty(default=False)
    expand_effectors_sun: BoolProperty(default=False)
    expand_effectors_river: BoolProperty(default=False)
    expand_effectors_altitude: BoolProperty(default=False)
    expand_effectors_rocks: BoolProperty(default=False)
    expand_effectors_trees: BoolProperty(default=False)
    expand_effectors_cluster: BoolProperty(default=False)

#####################################################################################
#
#       FIELDS
#
#####################################################################################


libraries_list = StrewFunctions.libraries_target_enum


class SaveAsset(PropertyGroup):
    def enum_target_libraries(self, context):
        global libraries_list
        libraries_list.clear()
        thumb_list = StrewFunctions.get_source_files(self, context)
        for source in thumb_list:
            if source[0] != "%STREW%This_file":
                libraries_list.append(source)
        return libraries_list

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
    asset_group: EnumProperty(
        name="group",
        description="kind of asset. will determine it's behaviour",
        items=[("grass", "grass", "grass"),
                 ("rocks", "rocks", "rocks"),
                 ("trees", "trees", "trees")]
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
    target_library: EnumProperty(
        name="Target library",
        description="Library in which the asset will be saved",
        items=enum_target_libraries,
        default=1
        )


class EditAsset(PropertyGroup):
    def enum_target_libraries(self, context):
        global libraries_list
        libraries_list.clear()
        thumb_list = StrewFunctions.get_source_files(self, context)
        for source in thumb_list:
            if source[0] != "%STREW%This_file":
                libraries_list.append(source)
        return libraries_list

    asset_name: StringProperty(
        default="",
        name="Name"
    )
    asset_description: StringProperty(
        default="",
        name="Description"
    )
    asset_group: EnumProperty(
        name="group",
        description="kind of asset. will determine it's behaviour",
        items=[("grass", "grass", "grass"),
               ("rocks", "rocks", "rocks"),
               ("trees", "trees", "trees")]
    )
    asset_category: StringProperty(
        default="",
        name="Category"
    )
    asset_type: BoolProperty(
        default=False,
        name="Use LOD"
    )
    lod_0: StringProperty(
        name="LOD 0",
        default="",
    )
    lod_1: StringProperty(
        name="LOD 1",
        default="",
    )
    lod_2: StringProperty(
        name="LOD 2",
        default="",
    )
    lod_3: StringProperty(
        name="LOD 3",
        default="",
    )
    proxy: StringProperty(
        name="Proxy",
        default="",
    )
    file: StringProperty(
        name="File path",
        description="Path to the blender file containing the asset"
    )
    target_library: EnumProperty(
        name="Target library",
        description="Library in which the asset will be saved",
        items=enum_target_libraries,
        default=1
        )


class BiomeNamesFields(PropertyGroup):
    new_name: bpy.props.StringProperty(
        name="name",
        default="New preset",
    )
    new_description: bpy.props.StringProperty(
        name="description",
        default="Custom Preset",
    )


#####################################################################################
#
#       REGISTER AND UNREGISTER
#
#####################################################################################


classes = [
    # --- Dropdowns ---
    StrewPresetProperty,
    StrewSourceProperty,
    StrewImportedBiomes,
    # --- lists ---
    PRESET_UL_List,
    SRCFILES_UL_List,
    # --- ui lists ---
    SMAAsset,
    SMAList,
    SMSAsset,
    LibraryList,
    # --- Panels ---
    BiomeNamesFields,
    PanelSwitch,
    # --- Save Assets ---
    SaveAsset,
    EditAsset,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.biomes_names_fields = PointerProperty(type=BiomeNamesFields)
    bpy.types.Scene.StrewPanelSwitch = PointerProperty(type=PanelSwitch)
    bpy.types.Scene.StrewPresetDrop = PointerProperty(type=StrewPresetProperty)
    bpy.types.Scene.StrewSourceDrop = PointerProperty(type=StrewSourceProperty)
    bpy.types.Scene.StrewImportedBiomes = PointerProperty(type=StrewImportedBiomes)
    bpy.types.Scene.StrewSaveAsset = PointerProperty(type=SaveAsset)
    bpy.types.Scene.StrewEditAsset = PointerProperty(type=EditAsset)
    bpy.types.Scene.SMAL = PointerProperty(type=SMAList)
    bpy.types.Scene.SourceLibrary = PointerProperty(type=LibraryList)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.biomes_names_fields
    del bpy.types.Scene.StrewPanelSwitch
    del bpy.types.Scene.StrewPresetDrop
    del bpy.types.Scene.StrewSourceDrop
    del bpy.types.Scene.StrewSaveAsset
    del bpy.types.Scene.StrewEditAsset
    del bpy.types.Scene.StrewImportedBiomes
    del bpy.types.Scene.SMAL
    del bpy.types.Scene.SourceLibrary
