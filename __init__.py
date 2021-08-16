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
        default=os.path.dirname(os.path.realpath(__file__)))

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
