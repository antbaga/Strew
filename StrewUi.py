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

            c.label(text="GENERAL")
            c.prop(biome_tree[2], "default_value", text="minimal distance")
            c.prop(biome_tree[3], "default_value", text="density")
            c.prop(biome_tree[4], "default_value", text="% particle displayed")
            c.prop(biome_tree[5], "default_value", text="Scale")
            c.prop(biome_tree[6], "default_value", text="Align Z")
            c.separator(factor=3.0)
            c.label(text="RANDOM")
            c.prop(biome_tree[9], "default_value", text="Position")
            c.prop(biome_tree[10], "default_value", text="Position Z")
            c.prop(biome_tree[11], "default_value", text="Rotation")
            c.prop(biome_tree[12], "default_value", text="Rotation Z")
            c.prop(biome_tree[13], "default_value", text="scale")
            c.prop(biome_tree[14], "default_value", text="Seed")
            c.separator(factor=3.0)
            c.label(text="VISIBILITY")
            c.prop(biome_tree[17], "default_value", text="disable asset")
            c.prop(biome_tree[18], "default_value", text="Disable in Viewport")
            c.prop(biome_tree[19], "default_value", text="Use Proxy")
            c.prop(biome_tree[20], "default_value", text="Proxy")
            c.prop(biome_tree[21], "default_value", text="LOD0")
            c.prop(biome_tree[22], "default_value", text="LOD1")
            c.prop(biome_tree[23], "default_value", text="LOD2")
            c.prop(biome_tree[24], "default_value", text="LOD3")
            c.prop(biome_tree[25], "default_value", text="Use Collection")
            c.prop(biome_tree[26], "default_value", text="Proxy")
            c.prop(biome_tree[27], "default_value", text="LOD0")
            c.prop(biome_tree[28], "default_value", text="LOD1")
            c.prop(biome_tree[29], "default_value", text="LOD2")
            c.prop(biome_tree[30], "default_value", text="LOD3")
            c.prop(biome_tree[31], "default_value", text="Avoid from LOD 1")
            c.prop(biome_tree[32], "default_value", text="Avoid from LOD 2")
            c.prop(biome_tree[33], "default_value", text="Avoid from LOD 3")
            c.separator(factor=5.0)
            c.label(text="EFFECTORS")
            c.label(text="Path :")
            c.prop(biome_tree[38], "default_value", text="Intensity")
            c.prop(biome_tree[39], "default_value", text="Offset")
            c.prop(biome_tree[40], "default_value", text="Smooth")
            c.prop(biome_tree[41], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="Scale :")
            c.prop(biome_tree[44], "default_value", text="Intensity")
            c.prop(biome_tree[45], "default_value", text="Offset")
            c.prop(biome_tree[46], "default_value", text="Smooth")
            c.prop(biome_tree[47], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="Shapness :")
            c.prop(biome_tree[45], "default_value", text="Intensity")
            c.prop(biome_tree[46], "default_value", text="Offset")
            c.prop(biome_tree[47], "default_value", text="Smooth")
            c.prop(biome_tree[48], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="Cavity :")
            c.prop(biome_tree[56], "default_value", text="Intensity")
            c.prop(biome_tree[57], "default_value", text="Offset")
            c.prop(biome_tree[58], "default_value", text="Smooth")
            c.prop(biome_tree[59], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="Slope :")
            c.prop(biome_tree[62], "default_value", text="Intensity")
            c.prop(biome_tree[63], "default_value", text="Offset")
            c.prop(biome_tree[64], "default_value", text="Smooth")
            c.prop(biome_tree[65], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="Paint :")
            c.prop(biome_tree[68], "default_value", text="Intensity")
            c.prop(biome_tree[69], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="Density :")
            c.prop(biome_tree[72], "default_value", text="Intensity")
            c.prop(biome_tree[73], "default_value", text="Offset")
            c.prop(biome_tree[74], "default_value", text="Smooth")
            c.prop(biome_tree[75], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="Sun :")
            c.prop(biome_tree[78], "default_value", text="Intensity")
            c.prop(biome_tree[79], "default_value", text="Offset")
            c.prop(biome_tree[80], "default_value", text="Smooth")
            c.prop(biome_tree[81], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="River :")
            c.prop(biome_tree[84], "default_value", text="Intensity")
            c.prop(biome_tree[85], "default_value", text="Offset")
            c.prop(biome_tree[86], "default_value", text="Smooth")
            c.prop(biome_tree[87], "default_value", text="Avoid Water")
            c.prop(biome_tree[88], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="Altitude :")
            c.prop(biome_tree[91], "default_value", text="Intensity")
            c.prop(biome_tree[92], "default_value", text="Offset MIN")
            c.prop(biome_tree[93], "default_value", text="Smooth MIN")
            c.prop(biome_tree[94], "default_value", text="Offset MAX")
            c.prop(biome_tree[95], "default_value", text="Smooth MAX")
            c.prop(biome_tree[96], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="Rock :")
            c.prop(biome_tree[99], "default_value", text="Intensity")
            c.prop(biome_tree[100], "default_value", text="Offset")
            c.prop(biome_tree[101], "default_value", text="Smooth")
            c.prop(biome_tree[102], "default_value", text="Avoid")
            c.separator(factor=1.0)
            c.label(text="Tree :")
            c.prop(biome_tree[105], "default_value", text="Intensity")
            c.prop(biome_tree[106], "default_value", text="Offset")
            c.prop(biome_tree[107], "default_value", text="Smooth")
            c.prop(biome_tree[108], "default_value", text="Avoid")
            c.separator(factor=5.0)
            c.label(text="CLUSTER :")
            c.prop(biome_tree[112], "default_value", text="Avoid")
            c.prop(biome_tree[113], "default_value", text="Cluster Type")
            c.prop(biome_tree[114], "default_value", text="Cluster Scale")
            c.prop(biome_tree[115], "default_value", text="Cluster Offset")
            c.prop(biome_tree[116], "default_value", text="Cluster Smooth")
            c.prop(biome_tree[117], "default_value", text="Cluster Smooth")
            c.prop(biome_tree[118], "default_value", text="Cluster Invert")



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
