import bpy
import os
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty
from . import __init__, StrewManOperators, StrewBiomeFunctions, StrewProps, StrewFunctions
import addon_utils


class MainPanel(bpy.types.Panel):
    bl_label = "Strew-Interface"
    bl_idname = "VIEW_3D_PT_STREW_Interface"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "STREW"
    bl_description = "STREW main panel"

    def draw(self, context):
        ui_switch = context.scene.strew_ui_switch
        StrewProperty = context.scene.preset_name_string

        lay = self.layout
        r = lay.row(align=True)
        c = r.column(align=True)

        if ui_switch.panels == {'General'} and\
                bpy.context.window.workspace.name != StrewFunctions.strew_compositor_workspace:
            # Calls the functions here
            c.operator("strew.import_biome", text="Import biome")
            c.prop(context.scene.StrewPresetDrop, "StrewPresetDropdown")
            # c.operator("strew.createpreset", text="Save as new preset")
            # c.operator("strew.importassets", text="Import All")
            # c.operator("strew.addasset", text="Save as asset")
            # c.operator("strew.removeasset", text="remove from asset")
            c.operator("strew.setup_strew", text="setup strew")
            c.operator("strew.instance_prefs_panel", text="Asset Manager")
            c.operator("strew.biome_compositor", text="Biome Compositor").switcher = 0

        elif ui_switch.panels == {'Biomes'} or bpy.context.scene.name == StrewFunctions.strew_compositor_scene or\
                bpy.context.window.workspace.name == StrewFunctions.strew_compositor_workspace:

            Geonode_Tree = bpy.data.node_groups["Geometry Nodes.005"].nodes["Group.012"].inputs
            Geonode_Grass = bpy.data.node_groups["Geometry Nodes.005"].nodes["Group.013"].inputs
            Geonode_Rocks = bpy.data.node_groups["Geometry Nodes.005"].nodes["Group.010"].inputs
            c = r.column(align=True)
            c.scale_x = 0.30
            c.scale_y = 2.0
            c.prop(StrewProperty, "Decorator")
            c.separator(factor=1.0)
            c.prop(StrewProperty, "AssetList")
            r.separator(factor=2.0)
            c = r.column(align=True)
            c.prop(context.scene.StrewPresetDrop, "StrewPresetDropdown")
            # c.operator("strew.createpreset",    text="Save as new preset")
            # c.operator("strew.importassets",    text="Import All")
            # c.operator("strew.addasset",        text="Save as asset")
            # c.operator("strew.removeasset",     text="remove from asset")
            c.operator("strew.biome_compositor", text="Exit Biome Compositor").switcher = 1
            c.separator(factor=3.0)
            if StrewProperty.Decorator == {"Trees"}:
                for Input in Geonode_Tree:
                    c.prop(Input, "default_value")
            if StrewProperty.Decorator == {"Grass"}:
                for Input in Geonode_Grass:
                    c.prop(Input, "default_value")
            if StrewProperty.Decorator == {"Rocks"}:
                for Input in Geonode_Rocks:
                    c.prop(Input, "default_value")

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
