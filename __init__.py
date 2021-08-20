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
        default=StrewFunctions.strew_path)

    def draw(self, context):
        panel_switch = context.scene.StrewPanelSwitch

        layout = self.layout
        scene = context.scene
        col = layout.row(align=True)
        col.prop(panel_switch, "Preferences")

        if panel_switch.Preferences == {'Settings'}:

            layout.label(text="Determines where the Strew files will be saved")
            layout.prop(self, "filepath")

        elif panel_switch.Preferences == {'Assets'}:

            #######################################
            #   START ASSET MANAGER, LIBRARY PART
            #######################################

            col = layout.row(align=True)
            box = col.box()

            row = box.row()
            row.prop(context.scene.StrewSourceDrop, "StrewSourceDropdown", text="Asset Library")
            row.scale_x = 0.90
            row.operator("strew.source_populate", text="refresh list")
            row = box.row()
            row.separator(factor=0.85)
            row = box.row()
            row.template_list("SRCFILES_UL_List", "", scene.SourceLibrary, "collection", scene.SourceLibrary, "active_user_index", rows=25)

            #######################################
            #   CENTRAL BUTTONS
            #######################################
            row = col.column(align=True)
            scale_row = row.column()
            scale_row.scale_x = 0.30
            scale_row.scale_y = 2.0
            scale_row.separator(factor=15.0)

            if StrewFunctions.selected_source(context) == "%STREW%This_file":
                scale_row.operator("Strew.save_asset", icon="ADD", text="").add_to_list = True
            else:
                scale_row.operator("strew.add_asset_manager", icon="ADD", text="")
            scale_row.operator("strew.remove_asset_manager", icon="REMOVE", text="")


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
            row.template_list("PRESET_UL_List", "", scene.SMAL, "collection", scene.SMAL, "active_user_index", rows=20)


#####################################################################################
#
#       REGISTER AND UNREGISTER
#
#####################################################################################


classes = [
    StrewPreferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    StrewUi.register()
    StrewManOperators.register()
    StrewBiomeFunctions.register()
    StrewProps.register()



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    StrewUi.unregister()
    StrewManOperators.unregister()
    StrewBiomeFunctions.unregister()
    StrewProps.unregister()


if __name__ == "__main__":
    register()
