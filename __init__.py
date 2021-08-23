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

            row = box.row(align=True)
            row.prop(context.scene.StrewSourceDrop, "StrewSourceDropdown", text="Asset Library")
            row.operator("strew.source_populate", text="", icon= "FILE_REFRESH")

            row = box.row(align=False)

            # sep = row.column()
            # sep.scale_x = 5
            # sep.separator(factor=1.0)

            libs = row.column(align=True)
            libs.scale_x = 0.5
            libs_row = libs.row(align=True)
            libs_row.operator("strew.edit_asset", text="Edit asset", icon="OUTLINER_DATA_GP_LAYER")
            libs_row.operator("strew.remove_library_asset", text="Remove asset", icon="REMOVE")
            libs.operator("Strew.save_asset", icon="ADD", text="New asset").add_to_list = False

            ast = row.column(align=True)
            ast.scale_x = 0.5
            asl_row = ast.row(align=True)
            asl_row.operator("strew.rename_biome_popup", text="Edit library", icon="OUTLINER_DATA_GP_LAYER").target = "library"
            asl_row.operator("strew.remove_biome_popup", text="Remove library", icon="REMOVE").target = "library"
            ast.operator("strew.add_biome_popup", text="New library", icon="ADD").target = "library"


            row = box.row()
            row.template_list("SRCFILES_UL_List", "", scene.SourceLibrary, "asset_library", scene.SourceLibrary, "active_user_index", rows=20)

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
            row = box.row(align=True)
            row.label(text='Biome Editor :')
            row.prop(context.scene.StrewPresetDrop, "StrewPresetDropdown")

            row = box.row(align=True)

            # sep = row.column()
            # sep_row = sep.row()
            # sep_row.scale_x = 5.0
            # sep_row.separator(factor=1.0)
            # sep_row.separator(factor=1.0)

            bms = row.column(align=True)
            bms_row = bms.row(align=True)
            bms_row.operator("strew.clone_biome_popup", text="Clone biome", icon="DUPLICATE")
            bms_row.operator("strew.rename_biome_popup", text="Edit biome", icon="OUTLINER_DATA_GP_LAYER").target = "biome"
            bms_row = bms.row(align=True)
            bms_row.operator("strew.add_biome_popup", text="New biome", icon="ADD").target = "biome"
            bms_row.operator("strew.remove_biome_popup", text="Remove biome", icon="REMOVE").target = "biome"

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
