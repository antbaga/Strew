from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty
from . import __init__, StrewUi, StrewProps, StrewBiomeFunctions, StrewFunctions
import addon_utils
import bpy
import os

#####################################################################################
#
#       SETUP
#
#####################################################################################


class Initialise(Operator):
    bl_idname = "strew.initialise"
    bl_label = "Initialise"

    def execute(self, context):
        biome = StrewFunctions.get_enum_biomes(self, context)
        # Ensures the first biome is selected, or it causes a bug.
        # for data in biome:                                  # get the biome identifier
        #    identifier = data[0]
        if bpy.context.scene.StrewPresetDrop.StrewPresetDropdown == biome[0][0]:
            bpy.context.scene.StrewPresetDrop.StrewPresetDropdown = biome[0][0]
        else:
            pass
        return {'FINISHED'}


class SetupStrew(bpy.types.Operator):
    bl_idname = "strew.setup_strew"
    bl_label = "setup_strew"

    def execute(self, context):
        StrewFunctions.setup_collections()
        StrewFunctions.setup_scenes(self, context)
        StrewFunctions.setup_workspace(self, context)
        StrewFunctions.import_geometry_nodes(self, context)
        return {'FINISHED'}

#####################################################################################
#
#       INSTANCE PANEL OR CHANGE VIEW
#
#####################################################################################


class InstancePreferencesPanel(Operator):
    bl_idname = "strew.instance_prefs_panel"
    bl_label = "instance_preferences_panel"

    # Instantiate the preferences blender windows
    # configure the window to addons, then look for strew
    # expand the options automatically
    # have to do it via modal to try again and again until it's done, or fail

    def modal(self, context, event):
        mod = addon_utils.addons_fake_modules.get("Strew")
        info = addon_utils.module_bl_info(mod)

        if info["show_expanded"] is True:
            self.cancel(context)
            return {'CANCELLED'}
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}
        if event.type == 'TIMER':
            info["show_expanded"] = True
        return {'PASS_THROUGH'}

    def execute(self, context):
        bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        bpy.context.preferences.active_section = 'ADDONS'
        bpy.data.window_managers["WinMan"].addon_search = "strew"
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        bpy.ops.strew.source_populate()
        bpy.ops.strew.list_populate()
        bpy.ops.strew.initialise()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class InstanceBiomeCompositor(Operator):
    bl_idname = "strew.biome_compositor"
    bl_label = "Instance_Biome_Compositor"

    switcher: bpy.props.IntProperty(name="switcher")
    current_scene: bpy.props.StringProperty(name="Current_Scene", default='Scene')
    current_workspace: bpy.props.StringProperty(name="Current_WorkSpace", default="Layout")

    def execute(self, context):
        global switcher
        global current_scene
        global current_workspace
        strew_workspace = StrewFunctions.strew_compositor_workspace
        strew_scene = StrewFunctions.strew_compositor_scene

        if self.switcher == 0:
            current_scene = bpy.context.scene.name
            current_workspace = bpy.context.workspace.name
            bpy.context.window.scene = bpy.data.scenes[strew_scene]
            bpy.context.window.workspace = bpy.data.workspaces[strew_workspace]
            ui_switch = context.scene.strew_ui_switch
            ui_switch.panels = {'Biomes'}
            self.switcher = 1

            return {'FINISHED'}

        elif self.switcher == 1:
            bpy.context.window.scene = bpy.data.scenes[self.current_scene]
            bpy.context.window.workspace = bpy.data.workspaces[self.current_workspace]
            ui_switch = context.scene.strew_ui_switch
            ui_switch.panels = {'General'}
            self.switcher = 0

            return {'FINISHED'}


#####################################################################################
#
#       POPUP BOX
#
#####################################################################################


class AddPresetPopup(Operator):
    bl_idname = "strew.add_preset_popup"
    bl_label = "Create new preset"

    def draw(self, context):
        biome = context.scene.preset_name_string
        lay = self.layout
        c = lay.column(align=True)
        c.prop(biome, "new_name")
        c.prop(biome, "new_description")

    def execute(self, context):
        biome = context.scene.preset_name_string
        StrewFunctions.new_biome(self, context, biome.new_name, biome.new_description)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class ClonePresetPopup(Operator):
    bl_idname = "strew.clone_preset_popup"
    bl_label = "Clone preset"

    def draw(self, context):
        properties = context.scene.preset_name_string
        lay = self.layout
        c = lay.column(align=True)
        c.prop(properties, "new_name")
        c.prop(properties, "new_description")

    def execute(self, context):
        biome_initial_name = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown
        biome = context.scene.preset_name_string
        StrewFunctions.clone_biome(self, context, biome_initial_name, biome.new_name, biome.new_description)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class RemovePresetPopup(Operator):
    bl_idname = "strew.remove_preset_popup"
    bl_label = "Remove this preset?"

    def execute(self, context):
        biome = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown       # get the biome name
        StrewFunctions.remove_biome(self, context, biome)                   # remove the biome

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class RenamePresetPopup(Operator):
    bl_idname = "strew.rename_preset_popup"
    bl_label = "Rename preset"

    def draw(self, context):
        properties = context.scene.preset_name_string
        lay = self.layout
        c = lay.column(align=True)
        c.prop(properties, "new_name")
        c.prop(properties, "new_description")

    def execute(self, context):
        biome = context.scene.preset_name_string                                    # get the infos of biome
        biome_initial_name = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown       # from the popup box
        StrewFunctions.rename_biome(self, context, biome_initial_name, biome.new_name, biome.new_description)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


#####################################################################################
#
#       ADD OR REMOVE ASSETS FROM BIOME
#
#####################################################################################


class AddAssetManager(Operator):
    bl_idname = "strew.add_asset_manager"
    bl_label = "add_asset_manager"

    # This operator adds an asset to a biome from the asset manager.
    # it takes both source file and target biome
    # then checks if asset comes from this file to ask the user if he wants
    # to register the asset in a permanent file like custom.blend
    # TODO: ask the user and register it

    def execute(self, context):
        cts = bpy.context.scene
        active_object = cts.SMSL.collection[cts.SMSL.active_user_index]
        asset = active_object.name
        preset = StrewFunctions.selected_biome(context)
        source = StrewFunctions.selected_source(context)
        if source == "This_file":
            source = "custom.blend"

        StrewFunctions.add_asset(self, context, preset, source, asset)
        SCENE_OT_list_populate.execute(self, context)
        return {'FINISHED'}


class AddAssetView(Operator):
    bl_idname = "strew.add_asset_view"
    bl_label = "add_asset_view"

    # this operator adds an asset or group of assets to a biome from the manager
    # it takes the biome, and the name of the file
    # if it comes from this file, it asks the user if he wants to add to permanent file
    # then, if the file has not been saved (thus, has no name) it stops and tell the user to save.

    def execute(self, context):
        # TODO: add "if save to custom:"
        if bpy.data.filepath != "":
            biome = context.scene.StrewPresetDrop.StrewPresetDropdown
            file_name = bpy.path.basename(bpy.data.filepath)

            for obj in bpy.context.selected_objects:
                StrewFunctions.add_asset(self, context, biome, file_name, obj.name)
            return {'FINISHED'}
        else:
            print("can't save as asset from temporary blend file yet. please save your file")
            return {'FINISHED'}


class RemoveAssetManager(Operator):
    bl_idname = "strew.remove_asset_manager"
    bl_label = "remove_asset_manager"

    def execute(self, context):
        cts = bpy.context.scene
        asset_id = cts.SMAL.active_user_index                        # find the object id
        biome = cts.StrewPresetDrop.StrewPresetDropdown              # find the biome

        StrewFunctions.remove_asset_id(self, context, biome, asset_id)  # remove the asset
        SCENE_OT_list_populate.execute(self, context)                # update the list in UI

        return {'FINISHED'}


class RemoveAssetView(Operator):
    bl_idname = "strew.remove_asset_view"
    bl_label = "remove_asset_view"

    def execute(self, context):
        biome = context.scene.StrewPresetDrop.StrewPresetDropdown
        file_name = bpy.path.basename(bpy.data.filepath)

        for obj in bpy.context.selected_objects:
            StrewFunctions.remove_asset(self, context, biome, obj.name, file_name)
        return {'FINISHED'}


class SaveAsset(Operator):
    bl_idname = "strew.save_asset"
    bl_label = "save_asset_in_file"

    def execute(self, context):
        StrewFunctions.export_asset(self, context)
        return{'FINISHED'}

#####################################################################################
#
#       UPDATE LISTS FOR UI
#
#####################################################################################


class SCENE_OT_list_populate(Operator):
    bl_idname = "strew.list_populate"
    bl_label = "Populate list"

    def execute(self, context):
        context.scene.SMAL.collection.clear()                                   # clear the list
        biome = context.scene.StrewPresetDrop.StrewPresetDropdown               # get the biome name
        AssetList = StrewFunctions.get_assets_list(self, context, biome)        # get the asset list
        for Asset in AssetList:
            item = context.scene.SMAL.collection.add()                          # add each asset to list
            item.name = Asset['name']
            item.description = Asset
        return {'FINISHED'}


class SCENE_OT_source_populate(Operator):
    bl_idname = "strew.source_populate"
    bl_label = "Populate source"

    def execute(self, context):
        context.scene.SMSL.collection.clear()
        biome = context.scene.StrewSourceDrop.StrewSourceDropdown

        if biome == "This_file":
            blend = bpy.path.basename(bpy.context.blend_data.filepath)
            AssetList = bpy.context.scene.objects
            for Asset in AssetList:
                item = context.scene.SMSL.collection.add()
                item.name = Asset.name
                item.description = blend + "," + Asset.name
            return {'FINISHED'}
        else:
            AssetList = StrewFunctions.get_sources_assets(self, context, biome)
            for Asset in AssetList:
                item = context.scene.SMSL.collection.add()
                item.name = Asset['name']
                item.description = Asset['description']
                item.identifier = Asset['file'] + "\\" + Asset['name']
            return {'FINISHED'}

#####################################################################################
#
#       IMPORT OR EXPORT
#
#####################################################################################


class ImportBiome(Operator):
    bl_idname = "strew.import_biome"
    bl_label = "Import_biome"

    # Since this is the first operator to be called on the UI
    # a full setup is done. However, most functions have fallback
    # in case they are already setup

    def execute(self, context):
        SFunc = StrewFunctions
        SetupStrew.execute(self, context)                                  # setup strew
        strew_collection = SFunc.setup_collections()                       # get collection name
        terrain_object = bpy.context.active_object                         # get future terrain
        selected_biome = SFunc.selected_biome(context)                     # get biome name
        asset_list = SFunc.get_assets_list(self, context, selected_biome)  # get asset list

        master_collection_layer = bpy.context.view_layer.layer_collection.children[SFunc.strew_collection_master]
        master_collection_layer.children[SFunc.strew_collection_assets].exclude = False           # enable collections
        master_collection_layer.children[SFunc.strew_collection_custom_assets].exclude = False    # to import assets

        for asset in asset_list:                                                            # import assets
            StrewFunctions.import_asset(self, context, asset['file'], asset['name'], strew_collection)
        strew_biome = StrewBiomeFunctions.apply_geometry_nodes(terrain_object)              # assign biome
        StrewBiomeFunctions.assign_collection(strew_biome, strew_collection, "rocks")       # configure biome
        """YOU WILL NEED TO CHANGE THE ROCKS FOR SOMETHING MODULAR"""
        master_collection_layer.children[SFunc.strew_collection_assets].exclude = True            # disable collections
        master_collection_layer.children[SFunc.strew_collection_custom_assets].exclude = True     # so user is not bothered

        return {'FINISHED'}


class ImportAsset(Operator):
    bl_idname = "strew.import_assets"
    bl_label = "import_assets"

    def execute(self, context):
        SFunc = StrewFunctions
        strew_collection = SFunc.setup_collections()                                        # get the main collection
        biome = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown                       # get the selected biome
        blend_folder = SFunc.get_path(self, context, "blend")                               # get the blend folder

        master_collection_layer = bpy.context.view_layer.layer_collection.children[SFunc.strew_collection_master]
        master_collection_layer.children[SFunc.strew_collection_assets].exclude = False           # enable collections
        master_collection_layer.children[SFunc.strew_collection_custom_assets].exclude = False    # to import assets

        asset_list = SFunc.get_assets_list(self, context, biome)                            # get the assets list
        for asset in asset_list:                                                            # import the assets
            asset_name = asset['name']
            asset_path = blend_folder + asset['file']
            SFunc.import_asset(self, context, asset_path, asset_name, strew_collection)

        master_collection_layer.children[SFunc.strew_collection_assets].exclude = True         # disable collections
        master_collection_layer.children[SFunc.strew_collection_custom_assets].exclude = True  # so user is not bothered

        return {'FINISHED'}

#####################################################################################
#
#       MANAGE TERRAINS
#
#####################################################################################


#####################################################################################
#
#       REGISTER AND UNREGISTER
#
#####################################################################################


classes = [
    # --- setup ---
    Initialise,                     # strew.initialise
    SetupStrew,                     # strew.setup_strew
    # --- instance panel ---
    InstancePreferencesPanel,       # strew.instance_prefs_panel
    InstanceBiomeCompositor,        # strew.biome_compositor
    # --- popup box ---
    AddPresetPopup,                 # strew.add_preset_popup
    ClonePresetPopup,               # strew.clone_preset_popup
    RemovePresetPopup,              # strew.remove_preset_popup
    RenamePresetPopup,              # strew.rename_preset_popup
    # --- Add & Remove asset ---
    AddAssetManager,                # strew.add_asset_manager
    AddAssetView,                   # strew.add_asset_view
    RemoveAssetManager,             # strew.remove_asset_manager
    RemoveAssetView,                # strew.remove_asset_view
    SaveAsset,                      # strew.save_asset
    # --- ui list updates ---
    SCENE_OT_list_populate,         # strew.list_populate
    SCENE_OT_source_populate,       # strew.source_populate
    # --- import & export ---
    ImportBiome,                    # strew.import_biome
    ImportAsset,                    # strew.import_assets
    # --- Manage terrains ---
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
