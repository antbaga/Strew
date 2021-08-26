import bpy
import os
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty
from . import __init__, StrewManOperators, StrewBiomeFunctions, StrewProps, StrewFunctions
import addon_utils
import json


class MainPanel(bpy.types.Panel):
    bl_label = __name__
    bl_idname = "VIEW_3D_PT_STREW_Interface"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "STREW"
    bl_description = "STREW main panel"

    def draw(self, context):
        panel_switch = context.scene.StrewPanelSwitch
        BiomesNodes = context.scene.StrewBiomesNodes
        selected_biome = StrewFunctions.selected_biome(context)
        imported_biomes = bpy.context.scene.get('Strew_Imported_Biomes')

        lay = self.layout
        r = lay.row(align=True)
        c = r.column(align=True)

        #####################################################################################
        #       3D VIEW
        #####################################################################################

        if panel_switch.MainView == {'General'} and\
                bpy.context.window.workspace.name != StrewFunctions.strew_compositor_workspace:

            c.operator("strew.instance_prefs_panel", text="Strew Settings...")
            c.separator(factor=2.0)

            c.prop(context.scene.StrewPresetDrop, "StrewPresetDropdown")

            #################################################################################
            #       BIOME IMPORTATION
            #################################################################################

            if bpy.context.active_object is not None and bpy.context.active_object.type == 'MESH':
                active_object = bpy.context.active_object

                object_biome = active_object.get(StrewFunctions.terrain_property)
                if object_biome is None:
                    if imported_biomes is not None:
                        if selected_biome in imported_biomes:
                            c.operator("strew.assign_biome", text="Assign biome")
                        else:
                            c.operator("strew.import_biome", text="Import biome")
                    else:
                        c.operator("strew.import_biome", text="Import biome")

                    # c.operator("strew.add_biome_popup", text="Create biome")
                else:
                    if object_biome != selected_biome:
                        c.operator("strew.replace_biome", text="Replace biome")

                if imported_biomes is not None:
                    if selected_biome in imported_biomes:
                        c.operator("strew.biome_compositor", text="Biome Compositor").switcher = 0
                        c.separator(factor=2.0)

                if object_biome is not None:
                    c.label(text=str(object_biome))
                    c.operator("strew.update_biome", text="Update biome")
                    c.operator("strew.remove_biome", text="Remove biome")


        #####################################################################################
        #       BIOME COMPOSITOR
        #####################################################################################

        elif panel_switch.MainView == {'Biomes'} or bpy.context.scene.name == StrewFunctions.strew_compositor_scene or\
                bpy.context.window.workspace.name == StrewFunctions.strew_compositor_workspace:

            biome = StrewFunctions.selected_biome(context)

            imported_list = json.loads(bpy.data.texts[biome].as_string())

            c = r.column(align=True)
            c.scale_x = .5
            c.scale_y = 2.0
            c.operator("strew.switchcompopanel", text='grass').node = 'grass'
            c.operator("strew.switchcompopanel", text='trees').node = 'trees'
            c.operator("strew.switchcompopanel", text='rocks').node = 'rocks'
            c.separator(factor=2.0)
            for category in imported_list:
                c.operator("strew.switchcompopanel", text=category).node = f"{imported_list[category]['group']}_{category}"

            node = StrewFunctions.current_node
            biome_tree = bpy.data.node_groups[biome].nodes[node].inputs
            # c = r.column(align=True)
            # c.scale_x = 0.30
            # c.scale_y = 2.0
            # c.prop(BiomesNodes, "NodesList")
            r.separator(factor=2.0)
            c = r.column(align=True)
            c.prop(context.scene.StrewImportedBiomes, "ImportedBiomes")

            c.operator("strew.biome_compositor", text="Exit Biome Compositor").switcher = 1

            c.separator(factor=10.0)

            c.prop(biome_tree[2], "default_value", text="minimal distance")
            c.prop(biome_tree[3], "default_value", text="density")
            c.prop(biome_tree[4], "default_value", text="% particle displayed")
            c.prop(biome_tree[5], "default_value", text="Scale")
            c.prop(biome_tree[6], "default_value", text="Align Z")
            c.separator(factor=3.0)
            c.prop(biome_tree[9], "default_value", text="Position")
            c.prop(biome_tree[9], "default_value", text="Position Z")
            c.prop(biome_tree[9], "default_value", text="Rotation")
            c.prop(biome_tree[9], "default_value", text="Rotation Z")
            c.prop(biome_tree[9], "default_value", text="scale")
            c.prop(biome_tree[9], "default_value", text="Seed")


        #####################################################################################
        #       ASSET CREATOR
        #####################################################################################

        #####################################################################################
        #       FALLBACK
        #####################################################################################

        else:
            c.operator("strew.setup_strew", text="setup strew")
            c.operator("strew.instance_prefs_panel", text="open Asset Manager")


#####################################################################################
#
#       REGISTER AND UNREGISTER
#
#####################################################################################


classes = [
    MainPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
