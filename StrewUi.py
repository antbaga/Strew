import bpy
import os
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty
from . import __init__, StrewManOperators, StrewBiomeFunctions, StrewProps, StrewFunctions
import addon_utils


class MainPanel(bpy.types.Panel):
    bl_label = "Strew"
    bl_idname = "VIEW_3D_PT_STREW_Interface"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "STREW"
    bl_description = "STREW main panel"

    def draw(self, context):
        ui_switch = context.scene.strew_ui_switch
        StrewProperty = context.scene.preset_name_string
        active_object = bpy.context.active_object
        selected_biome = StrewFunctions.selected_biome(context)
        imported_biomes = bpy.context.scene.get('Strew_Imported_Biomes')
        object_biome = active_object.get(StrewFunctions.terrain_property)

        lay = self.layout
        r = lay.row(align=True)
        c = r.column(align=True)

        #####################################################################################
        #       3D VIEW
        #####################################################################################

        if ui_switch.panels == {'General'} and\
                bpy.context.window.workspace.name != StrewFunctions.strew_compositor_workspace:

            c.operator("strew.instance_prefs_panel", text="Strew Settings...")
            c.separator(factor=2.0)

            c.prop(context.scene.StrewPresetDrop, "StrewPresetDropdown")

            #################################################################################
            #       BIOME IMPORTATION
            #################################################################################

            if imported_biomes is not None:
                if selected_biome in imported_biomes:
                    c.operator("strew.biome_compositor", text="Biome Compositor").switcher = 0

            if active_object is not None and active_object.type == 'MESH':
                if object_biome is None:
                    c.operator("strew.import_biome", text="Import biome")
                    c.operator("strew.add_biome_popup", text="Create biome")
                elif object_biome != selected_biome:
                    c.operator("strew.replace_biome", text="Replace biome")
                elif object_biome == selected_biome:
                    c.operator("strew.update_biome", text="Update biome")
                    c.operator("strew.remove_biome", text="Remove biome")

        #####################################################################################
        #       BIOME COMPOSITOR
        #####################################################################################

        elif ui_switch.panels == {'Biomes'} or bpy.context.scene.name == StrewFunctions.strew_compositor_scene or\
                bpy.context.window.workspace.name == StrewFunctions.strew_compositor_workspace:

            Geonode_Tree = bpy.data.node_groups["Geometry Nodes.005"].nodes["trees"].inputs
            Geonode_Grass = bpy.data.node_groups["Geometry Nodes.005"].nodes["rocks"].inputs
            Geonode_Rocks = bpy.data.node_groups["Geometry Nodes.005"].nodes["grass"].inputs
            c = r.column(align=True)
            c.scale_x = 0.30
            c.scale_y = 2.0
            c.prop(StrewProperty, "Decorator")
            c.separator(factor=1.0)
            c.prop(StrewProperty, "AssetList")
            r.separator(factor=2.0)
            c = r.column(align=True)
            c.prop(context.scene.StrewPresetDrop, "StrewPresetDropdown")

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
