import bpy
import os
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, BoolProperty
from . import __init__, StrewManOperators, StrewBiomeFunctions, StrewProps, StrewFunctions
import addon_utils
import json


class MainPanel(bpy.types.Panel):
    bl_label = "Strew"
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
            r.separator(factor=2.0)
            c = r.column(align=True)
            c.prop(context.scene.StrewImportedBiomes, "ImportedBiomes")

            row = c.row(align=True)
            row.scale_y= 2.0
            row.operator("strew.biome_compositor", text="Exit Biome Compositor").switcher = 1

            c.label(text=StrewFunctions.current_node.upper())
            c.prop(panel_switch, "expand_general",
                   icon="TRIA_DOWN" if panel_switch.expand_general else "TRIA_RIGHT",
                   icon_only=True, emboss=False, text="GENERAL"
                   )
            if panel_switch.expand_general:
                c.prop(biome_tree[2], "default_value", text="minimal distance")
                c.prop(biome_tree[3], "default_value", text="density")
                c.prop(biome_tree[4], "default_value", text="% particle displayed")
                c.prop(biome_tree[5], "default_value", text="Scale")
                c.prop(biome_tree[6], "default_value", text="Align Z")
                c.separator(factor=3.0)

            c.separator(factor=1.0)
            c.prop(panel_switch, "expand_random",
                   icon="TRIA_DOWN" if panel_switch.expand_random else "TRIA_RIGHT",
                   icon_only=True, emboss=False, text="RANDOM")
            if panel_switch.expand_random:
                c.prop(biome_tree[9], "default_value", text="Position")
                c.prop(biome_tree[10], "default_value", text="Position Z")
                c.prop(biome_tree[11], "default_value", text="Rotation")
                c.prop(biome_tree[12], "default_value", text="Rotation Z")
                c.prop(biome_tree[13], "default_value", text="scale")
                c.prop(biome_tree[14], "default_value", text="Seed")
                c.separator(factor=3.0)

            c.separator(factor=1.0)
            c.prop(panel_switch, "expand_visibility",
                   icon="TRIA_DOWN" if panel_switch.expand_visibility else "TRIA_RIGHT",
                   icon_only=True, emboss=False, text="VISIBILITY"
                   )
            if panel_switch.expand_visibility:
                c.prop(biome_tree[17], "default_value", text="disable asset")
                c.prop(biome_tree[18], "default_value", text="Disable in Viewport")
                c.prop(biome_tree[19], "default_value", text="Use Proxy")
                c.prop(biome_tree[25], "default_value", text="Use Collection")
                if not biome_tree[25].default_value:
                    c.prop(biome_tree[20], "default_value", text="Proxy")
                    c.prop(biome_tree[21], "default_value", text="LOD0")
                    c.prop(biome_tree[22], "default_value", text="LOD1")
                    c.prop(biome_tree[23], "default_value", text="LOD2")
                    c.prop(biome_tree[24], "default_value", text="LOD3")
                if biome_tree[25].default_value:
                    c.prop(biome_tree[26], "default_value", text="Proxy")
                    c.prop(biome_tree[27], "default_value", text="LOD0")
                    c.prop(biome_tree[28], "default_value", text="LOD1")
                    c.prop(biome_tree[29], "default_value", text="LOD2")
                    c.prop(biome_tree[30], "default_value", text="LOD3")
                c.prop(biome_tree[31], "default_value", text="Avoid from LOD 1")
                c.prop(biome_tree[32], "default_value", text="Avoid from LOD 2")
                c.prop(biome_tree[33], "default_value", text="Avoid from LOD 3")
                c.separator(factor=5.0)

            c.separator(factor=1.0)
            c.prop(panel_switch, "expand_effectors",
                   icon="TRIA_DOWN" if panel_switch.expand_effectors else "TRIA_RIGHT",
                   icon_only=True, emboss=False, text="EFFECTORS"
                   )
            if panel_switch.expand_effectors:
                # effectors table
                row = c.row(align=True)
                row.prop(biome_tree[41], "default_value", index=1, toggle=True, text=" ", icon="CON_FOLLOWPATH")
                row.prop(biome_tree[47], "default_value", index=2, toggle=True, text=" ", icon="FULLSCREEN_ENTER")
                row.prop(biome_tree[53], "default_value", index=3, toggle=True, text=" ", icon="SHARPCURVE")
                row.prop(biome_tree[59], "default_value", index=4, toggle=True, text=" ", icon="IPO_BACK")
                row.prop(biome_tree[65], "default_value", index=5, toggle=True, text=" ", icon="IPO_EASE_IN_OUT")
                row.prop(biome_tree[69], "default_value", index=6, toggle=True, text=" ", icon="BRUSH_DATA")
                row.prop(biome_tree[75], "default_value", index=7, toggle=True, text=" ", icon="NODE_TEXTURE")
                row = c.row(align=True)
                row.prop(biome_tree[81], "default_value", index=8, toggle=True, text=" ", icon="LIGHT_SUN")
                row.prop(biome_tree[88], "default_value", index=9, toggle=True, text=" ", icon="MOD_NOISE")
                row.prop(biome_tree[96], "default_value", index=10, toggle=True, text=" ", icon="IPO_BEZIER")
                row.prop(biome_tree[102], "default_value", index=11, toggle=True, text=" ", icon="EVENT_R")
                row.prop(biome_tree[108], "default_value", index=12, toggle=True, text=" ", icon="EVENT_T")
                row.prop(biome_tree[112], "default_value", index=13, toggle=True, text=" ", icon="SEQ_LUMA_WAVEFORM")
                col = row.column(align=True)
                col.enabled = False
                col.prop(panel_switch, "false_prop", toggle=True, text=" ")
                c.separator(factor=5.0)

                # effectors parameters
                if not biome_tree[41].default_value:
                    c.prop(panel_switch, "expand_effectors_path",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_path else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Path")
                    if panel_switch.expand_effectors_path:
                        c.prop(biome_tree[38], "default_value", text="Intensity")
                        c.prop(biome_tree[39], "default_value", text="Offset")
                        c.prop(biome_tree[40], "default_value", text="Smooth")
                        c.separator(factor=3.0)

                if not biome_tree[47].default_value:
                    c.prop(panel_switch, "expand_effectors_scale",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_scale else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Scale")
                    if panel_switch.expand_effectors_scale:
                        c.prop(biome_tree[44], "default_value", text="Intensity")
                        c.prop(biome_tree[45], "default_value", text="Offset")
                        c.prop(biome_tree[46], "default_value", text="Smooth")
                        c.separator(factor=3.0)

                if not biome_tree[53].default_value:
                    c.prop(panel_switch, "expand_effectors_sharpness",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_scale else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Sharpness")
                    if panel_switch.expand_effectors_sharpness:
                        c.prop(biome_tree[50], "default_value", text="Intensity")
                        c.prop(biome_tree[51], "default_value", text="Offset")
                        c.prop(biome_tree[52], "default_value", text="Smooth")
                        c.separator(factor=3.0)

                if not biome_tree[59].default_value:
                    c.prop(panel_switch, "expand_effectors_cavity",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_cavity else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Cavity")
                    if panel_switch.expand_effectors_cavity:
                        c.prop(biome_tree[56], "default_value", text="Intensity")
                        c.prop(biome_tree[57], "default_value", text="Offset")
                        c.prop(biome_tree[58], "default_value", text="Smooth")
                        c.separator(factor=3.0)

                if not biome_tree[65].default_value:
                    c.prop(panel_switch, "expand_effectors_slope",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_slope else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Slope")
                    if panel_switch.expand_effectors_slope:
                        c.prop(biome_tree[62], "default_value", text="Intensity")
                        c.prop(biome_tree[63], "default_value", text="Offset")
                        c.prop(biome_tree[64], "default_value", text="Smooth")
                        c.separator(factor=3.0)

                if not biome_tree[69].default_value:
                    c.prop(panel_switch, "expand_effectors_paint",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_paint else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Pain")
                    if panel_switch.expand_effectors_paint:
                        c.prop(biome_tree[68], "default_value", text="Intensity")
                        c.separator(factor=3.0)

                if not biome_tree[75].default_value:
                    c.prop(panel_switch, "expand_effectors_density",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_density else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Density")
                    if panel_switch.expand_effectors_density:
                        c.prop(biome_tree[72], "default_value", text="Intensity")
                        c.prop(biome_tree[73], "default_value", text="Offset")
                        c.prop(biome_tree[74], "default_value", text="Smooth")
                        c.separator(factor=3.0)

                if not biome_tree[81].default_value:
                    c.prop(panel_switch, "expand_effectors_sun",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_sun else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Sun")
                    if panel_switch.expand_effectors_sun:
                        c.prop(biome_tree[78], "default_value", text="Intensity")
                        c.prop(biome_tree[79], "default_value", text="Offset")
                        c.prop(biome_tree[80], "default_value", text="Smooth")
                        c.separator(factor=3.0)

                if not biome_tree[88].default_value:
                    c.prop(panel_switch, "expand_effectors_river",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_river else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="River")
                    if panel_switch.expand_effectors_river:
                        c.prop(biome_tree[84], "default_value", text="Intensity")
                        c.prop(biome_tree[85], "default_value", text="Offset")
                        c.prop(biome_tree[86], "default_value", text="Smooth")
                        c.prop(biome_tree[87], "default_value", text="Avoid Water")
                        c.separator(factor=3.0)

                if not biome_tree[96].default_value:
                    c.prop(panel_switch, "expand_effectors_altitude",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_altitude else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Altitude")
                    if panel_switch.expand_effectors_altitude:
                        c.prop(biome_tree[91], "default_value", text="Intensity")
                        c.prop(biome_tree[92], "default_value", text="Offset MIN")
                        c.prop(biome_tree[93], "default_value", text="Smooth MIN")
                        c.prop(biome_tree[94], "default_value", text="Offset MAX")
                        c.prop(biome_tree[95], "default_value", text="Smooth MAX")
                        c.separator(factor=3.0)

                if not biome_tree[102].default_value:
                    c.prop(panel_switch, "expand_effectors_rocks",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_rocks else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Rocks")
                    if panel_switch.expand_effectors_rocks:
                        c.prop(biome_tree[99], "default_value", text="Intensity")
                        c.prop(biome_tree[100], "default_value", text="Offset")
                        c.prop(biome_tree[101], "default_value", text="Smooth")
                        c.separator(factor=3.0)

                if not biome_tree[108].default_value:
                    c.prop(panel_switch, "expand_effectors_trees",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_trees else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Trees")
                    if panel_switch.expand_effectors_trees:
                        c.prop(biome_tree[105], "default_value", text="Intensity")
                        c.prop(biome_tree[106], "default_value", text="Offset")
                        c.prop(biome_tree[107], "default_value", text="Smooth")
                        c.separator(factor=3.0)

                if not biome_tree[112].default_value:
                    c.prop(panel_switch, "expand_effectors_cluster",
                           icon="TRIA_DOWN" if panel_switch.expand_effectors_cluster else "TRIA_RIGHT",
                           icon_only=True, emboss=False, text="Cluster")
                    if panel_switch.expand_effectors_cluster:
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
