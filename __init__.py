from bpy.types import AddonPreferences,\
                      PropertyGroup,\
                      Operator,\
                      UIList,\
                      Panel
from bpy.props import CollectionProperty,\
                      PointerProperty,\
                      StringProperty,\
                      EnumProperty,\
                      IntProperty,\
                      BoolProperty
from . import StrewManOperators,\
              StrewBiomeFunctions,\
              StrewFunctions,\
              StrewProps,\
              StrewUi
import random
import bpy
import os


bl_info = {
    "name": "STREW",
    "author": "Antoine Bagattini, Clovis Flayols, Laura Mercadal",
    "version": (0, 0, 10),
    "blender": (2, 90, 1),
    "location": "View3D > Toolshelf",
    "description": "Strew addon adds gold to your life",
    "category": "Add Mesh",
}


# Place this one in the preferences in a hidden menu
inner_path = 'Object'
StrewMasterCollection_name = 'Strew'
StrewAssetsCollection_name = 'Strew_Assets'


#####################################################################################
#
#       PREFERENCES UI AND ASSET MANAGER
#
#####################################################################################


class StrewPreferences(AddonPreferences):
    bl_idname = __name__
    filepath: StringProperty(
        name="Strew Folder Path",
        subtype='DIR_PATH',
        default=bpy.utils.user_resource('SCRIPTS') + "\\addons\\Strew")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text="Determines where the Strew files will be saved")
        layout.prop(self, "filepath")

        #######################################
        #   START ASSET MANAGER, LIBRARY PART 
        #######################################

        col = layout.row(align=True)
        # split = col.split()
        box = col.box()

        row = box.row()
        row.label(text='Asset Library :')
        row.prop(context.scene.StrewSourceDrop, "StrewSourceDropdown")
        row.separator(factor=5.4)
        # row.operator("scene.source_populate",text= "populate")
        row = box.row()
        row.template_list("SMS_UL_List", "", scene.SMSL, "collection", scene.SMSL, "active_user_index", rows=25)

        #######################################
        #   CENTRAL BUTTONS
        #######################################
        row = col.column(align=True)
        scale_row = row.column()
        scale_row.scale_x = 0.30
        scale_row.scale_y = 2.0
        scale_row.separator(factor=15.0)
        scale_row.operator("strew.add_asset_manager", icon="ADD", text="")
        scale_row.operator("strew.remove_asset_manager", icon="REMOVE", text="")
        scale_row.operator("Strew.save_asset", icon="BLENDER", text="")

        #######################################
        #   PRESET PART OF ASSET MANAGER
        #######################################

        box = col.box()
        row = box.row()
        row.label(text='Biome Editor :')
        row.prop(context.scene.StrewPresetDrop, "StrewPresetDropdown")

        row = box.row()
        split_row = row.split()
        split_row.scale_x = 33.4
        split_row.separator()
        split_row = row.split()
        split_row.operator("strew.add_biome_popup", text="New biome")

        row = box.row()
        split_row = row.split()
        split_row.scale_x = 33.4
        split_row.separator()
        split_row = row.split()
        split_row.operator("strew.remove_biome_popup", text="Remove biome")

        row = box.row()
        split_row = row.split()
        split_row.scale_x = 33.4
        split_row.separator()
        split_row = row.split()
        split_row.operator("strew.clone_biome_popup", text="Clone biome")

        row = box.row()
        split_row = row.split()
        split_row.scale_x = 33.4
        split_row.separator()
        split_row = row.split()
        split_row.operator("strew.rename_biome_popup", text="edit biome")


        row = box.row()
        row.template_list("SMA_UL_List", "", scene.SMAL, "collection", scene.SMAL, "active_user_index", rows=20)


#####################################################################################
#
#       DROPDOWN MENU OF PRESETS
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


# Liste de dropdown
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


# Liste de dropdown


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
#       PRESET LISTS FOR PRESET MANAGER
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
#       PRESET LISTS FOR SOURCE MANAGER
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
#       REGISTER AND UNREGISTER
#
#####################################################################################


classes = [
    StrewPreferences,
    StrewPresetProperty,
    StrewSourceProperty,
    SMAAsset,
    SMAList,
    SMSAsset,
    SMSList,
    SRCFILES_UL_List,
    PRESET_UL_List,
    SMA_UL_List,
    SMS_UL_List,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    StrewUi.register()
    StrewManOperators.register()
    StrewBiomeFunctions.register()
    StrewProps.register()
    bpy.types.Scene.StrewPresetDrop = PointerProperty(type=StrewPresetProperty)
    bpy.types.Scene.StrewSourceDrop = PointerProperty(type=StrewSourceProperty)
    bpy.types.Scene.SMAL = PointerProperty(type=SMAList)
    bpy.types.Scene.SMSL = PointerProperty(type=SMSList)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.StrewPresetDrop
    del bpy.types.Scene.StrewSourceDrop
    del bpy.types.Scene.SMAL
    del bpy.types.Scene.SMSL
    StrewUi.unregister()
    StrewManOperators.unregister()
    StrewBiomeFunctions.unregister()
    StrewProps.unregister()


if __name__ == "__main__":
    register()
