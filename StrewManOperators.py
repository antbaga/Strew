from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, EnumProperty
from . import __init__, StrewUi, StrewProps, StrewBiomeFunctions
from . import StrewFunctions as SFunc
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
        biome = SFunc.get_enum_biomes(self, context)
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
        SFunc.setup_collections()
        SFunc.setup_scenes(self, context)
        SFunc.setup_workspace(self, context)
        SFunc.import_geometry_nodes(self, context)
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
        strew_workspace = SFunc.strew_compositor_workspace
        strew_scene = SFunc.strew_compositor_scene

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
#       ADD & REMOVE BIOMES
#
#####################################################################################


class AddBiomePopup(Operator):
    bl_idname = "strew.add_biome_popup"
    bl_label = "Create new biome"

    def draw(self, context):
        biome = context.scene.preset_name_string
        lay = self.layout
        c = lay.column(align=True)
        c.prop(biome, "new_name")
        c.prop(biome, "new_description")

    def execute(self, context):
        biome = context.scene.preset_name_string
        SFunc.new_biome(self, context, biome.new_name, biome.new_description)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CloneBiomePopup(Operator):
    bl_idname = "strew.clone_biome_popup"
    bl_label = "Clone biome"

    def draw(self, context):
        properties = context.scene.preset_name_string
        lay = self.layout
        c = lay.column(align=True)
        c.prop(properties, "new_name")
        c.prop(properties, "new_description")

    def execute(self, context):
        biome_initial_name = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown
        biome = context.scene.preset_name_string
        SFunc.clone_biome(self, context, biome_initial_name, biome.new_name, biome.new_description)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class RemoveBiomePopup(Operator):
    bl_idname = "strew.remove_biome_popup"
    bl_label = "Remove this biome?"

    def execute(self, context):
        biome = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown       # get the biome name
        SFunc.remove_biome(self, context, biome)                   # remove the biome

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class RenameBiomePopup(Operator):
    bl_idname = "strew.rename_biome_popup"
    bl_label = "Rename biome"

    def draw(self, context):
        properties = context.scene.preset_name_string
        lay = self.layout
        c = lay.column(align=True)
        c.prop(properties, "new_name")
        c.prop(properties, "new_description")

    def execute(self, context):
        biome = context.scene.preset_name_string                                    # get the infos of biome
        biome_initial_name = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown       # from the popup box
        SFunc.rename_biome(self, context, biome_initial_name, biome.new_name, biome.new_description)
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
        asset = cts.SMSL.collection[cts.SMSL.active_user_index]

        biome_name = SFunc.selected_biome(context)

        # TODO: add a prompt asking user if he wants to save it locally or not
        SFunc.add_asset(self, context, biome_name, asset['file'],
                                                   asset['name'],
                                                   asset['type'],
                                                   asset['description'],
                                                   asset['category'],
                                                   asset['objects'])
        SCENE_OT_list_populate.execute(self, context)
        return {'FINISHED'}


class AddAssetView(Operator):
    bl_idname = "strew.add_asset_view"
    bl_label = "add_asset_view"

    # this operator adds an asset or group of assets to a biome from the 3d view
    # it takes the biome, and the name of the file
    # if it comes from this file, it asks the user if he wants to add to permanent file
    # then, if the file has not been saved (thus, has no name) it stops and tell the user to save.

    def execute(self, context):
        # TODO: add "if save to custom:"
        if bpy.data.filepath != "":
            biome_name = SFunc.selected_biome(context)
            file_name = bpy.path.basename(bpy.data.filepath)

            for obj in bpy.context.selected_objects:
                SFunc.add_asset(self, context, biome_name, file_name,
                                                           obj.name,
                                                           "Object",
                                                           "Custom asset",
                                                           "grass",
                                                            "{}")
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

        SFunc.remove_asset_id(self, context, biome, asset_id)  # remove the asset
        SCENE_OT_list_populate.execute(self, context)                # update the list in UI

        return {'FINISHED'}


class RemoveAssetView(Operator):
    bl_idname = "strew.remove_asset_view"
    bl_label = "remove_asset_view"

    def execute(self, context):
        biome = context.scene.StrewPresetDrop.StrewPresetDropdown
        file_name = bpy.path.basename(bpy.data.filepath)

        for obj in bpy.context.selected_objects:
            SFunc.remove_asset(self, context, biome, obj.name, file_name)
        return {'FINISHED'}


class SaveAsset(Operator):
    bl_idname = "strew.save_asset"
    bl_label = "save_asset_in_file"

    def execute(self, context):
        SFunc.export_asset(self, context)
        # TODO: ADD IT TO THE JSON FILES
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
        context.scene.SMAL.collection.clear()                          # clear the list
        biome = context.scene.StrewPresetDrop.StrewPresetDropdown      # get the biome name
        AssetList = SFunc.get_assets_list(self, context, biome)        # get the asset list
        for Asset in AssetList:
            item = context.scene.SMAL.collection.add()                 # add each asset to list
            item.name = Asset['name']
            item.description = Asset['description']
            item.file = Asset['file']
            item.type = Asset['type']
            item.category = Asset['category']
            item.objects = str(Asset['objects'])
        return {'FINISHED'}


class SCENE_OT_source_populate(Operator):
    bl_idname = "strew.source_populate"
    bl_label = "Populate source"

    # Creates the list visible in AssetManager ( left column )
    # If biome == This_file returns the list of objects present in the file
    # else, it will display the files from the strew library

    def execute(self, context):
        context.scene.SMSL.collection.clear()
        biome = SFunc.selected_source("name")

        if biome == "%STREW%This_file":
            blend = bpy.context.blend_data.filepath
            AssetList = bpy.context.scene.objects
            for Asset in AssetList:
                item = context.scene.SMSL.collection.add()
                item.name = Asset.name
                item.file = blend
                item.description = "Custom Asset"
                item.type = "Object"
                item.category = "grass"     # TODO: ask the user what category it is
                item.objects = "{}"
            return {'FINISHED'}
        else:
            AssetList = SFunc.get_sources_assets(self, context, biome)
            for Asset in AssetList:
                item = context.scene.SMSL.collection.add()
                item.name = Asset['name']
                item.description = Asset['description']
                item.file = Asset['file']
                item.type = Asset['type']
                item.category = Asset['category']
                item.objects = str(Asset['objects'])
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
        SetupStrew.execute(self, context)                                  # setup strew
        strew_collection = SFunc.setup_collections()                       # get collection name
        terrain_object = bpy.context.active_object                         # get future terrain
        selected_biome = SFunc.selected_biome(context)                     # get biome name
        asset_list = SFunc.get_assets_list(self, context, selected_biome)  # get asset list

        master_collection_layer = bpy.context.view_layer.layer_collection.children[SFunc.strew_collection_master]
        master_collection_layer.children[SFunc.strew_collection_assets].exclude = False           # enable collections

        biome_node = StrewBiomeFunctions.apply_geometry_nodes(terrain_object)  # assign biome

        StrewBiomeFunctions.setup_biome_collection(self, context, asset_list, selected_biome, strew_collection, biome_node)

        # StrewBiomeFunctions.assign_collection(strew_biome, strew_collection, "rocks")       # configure biome
        """YOU WILL NEED TO CHANGE THE ROCKS FOR SOMETHING MODULAR"""
        master_collection_layer.children[SFunc.strew_collection_assets].exclude = True            # disable collections

        return {'FINISHED'}


class ImportAsset(Operator):
    bl_idname = "strew.import_assets"
    bl_label = "import_assets"

    def execute(self, context):
        strew_collection = SFunc.setup_collections()                                        # get the main collection
        biome = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown                       # get the selected biome
        blend_folder = SFunc.get_path(self, context, "blend")                               # get the blend folder

        layer_collection = bpy.context.view_layer.layer_collection.children[SFunc.strew_collection_master]
        layer_collection.children[SFunc.strew_collection_assets].exclude = False           # enable collections

        asset_list = SFunc.get_assets_list(self, context, biome)                            # get the assets list
        SFunc.setup_biome_collection(self, context, asset_list)
        for asset in asset_list:                                                            # import the assets
            #   IF type = Object
            # check if category is present in thumblist
            # if not, add it, and
            # create another collection with the name   Strew_Biome_name+category_name
            # return this collection to use.
            # else, return the collection Strew_Biome_name+category_name
            # and use this one.
            #       ELSE
            # look for objects key and for each, create a collection.
            # in order to have everything homogeneous, if there are LOD that other do not have,
            # take the lesser poly first to fill in the blanks.
            asset_name = asset['name']
            asset_path = asset['file']
            asset_type = asset['type']

            if SFunc.local_folder_path in asset_path:
                asset_path = asset_path.replace(SFunc.local_folder_path, blend_folder)

            SFunc.import_asset(self, context, asset_path, asset_name, asset_type, strew_collection)

        layer_collection.children[SFunc.strew_collection_assets].exclude = True             # disable collections

        return {'FINISHED'}

#####################################################################################
#
#       MANAGE TERRAINS
#
#####################################################################################


class ReplaceBiome(Operator):
    bl_idname = "strew.replace_biome"
    bl_label = "replace biome"

    def execute(self, context):
        return {'FINISHED'}


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
    AddBiomePopup,                 # strew.add_preset_popup
    CloneBiomePopup,               # strew.clone_preset_popup
    RemoveBiomePopup,              # strew.remove_preset_popup
    RenameBiomePopup,              # strew.rename_preset_popup
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
    ReplaceBiome,                   # strew.replace_biome
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
