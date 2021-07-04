import bpy
import os
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty
from . import __init__, StrewManOperators, StrewBiomeManager, StrewEnums
import addon_utils


StrewMasterCollection_name = 'Strew'
StrewAssetsCollection_name = 'Strew_Assets'

class UiSwitch(bpy.types.PropertyGroup):
    general_panel: bpy.props.BoolProperty(
        name="general_panel",
        default=True,
    )
    asset_manager: bpy.props.BoolProperty(
        name="asset_manager",
        default=False,
    )
    panels: bpy.props.EnumProperty(
        name="panels",
        description="Preferences panel",
        items=[
            ("General", "General", "All things in the universe"),
            ("Assets", "Assets", "The asset manager"),
            ("Biomes","Biomes", "The Biome manager")
        ],
        default={"General"},
        options={"ENUM_FLAG"}
    )

class MainPanel(bpy.types.Panel):
    bl_label = "Strew-Interface"
    bl_idname = "VIEW_3D_PT_STREW_Interface"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "STREW"
    bl_description = "STREW main panel"

    def draw(self, context):
        ui_switch = context.scene.strew_ui_switch
        l = self.layout
        r = l.row(align=True)
        c = r.column(align=True)
        c.scale_x = 0.30
        c.scale_y = 2.0
        c.prop(ui_switch, "panels")
        r.separator(factor=2.0)
        c = r.column(align=True)
        #Those two ones are kept here for now since i might use them later
        #c.prop(ui_switch, "general_panel", toggle = True)
        #c.prop(ui_switch, "asset_manager", toggle = True)
        #c.prop(ui_switch, "panels")
        if ui_switch.panels == {'General'}:
            # Calls the functions here
            c.prop(context.scene.StrewPresetDrop, "StrewPresetDropdown")
            c.operator("strew.createpreset", text="Save as new preset")
            c.operator("strew.importassets", text="Import All")
            c.operator("strew.addasset", text="Save as asset")
            c.operator("strew.removeasset", text="remove from asset")
            c.operator("strew.setupstrew", text="setup strew")
            c.operator("strew.invokeprefspanel", text="open Asset Manager")
            c.operator("strew.test", text="test")
        elif ui_switch.panels == {'Assets'}:
            c.prop(context.scene.StrewPresetDrop, "StrewPresetDropdown")
            c.operator("strew.createpreset", text="Save as new preset")
            c.operator("strew.importassets", text="Import All")
            c.operator("strew.addasset", text="Save as asset")
            c.operator("strew.removeasset", text="remove from asset")
        else:
            c.operator("strew.setupstrew", text="setup strew")
            c.operator("strew.invokeprefspanel", text="open Asset Manager")
            c.operator("strew.test", text="test")

class InvokePrefsPanel(bpy.types.Operator):
    bl_idname = "strew.invokeprefspanel"
    bl_label = "InvokePrefsPanel"

    def modal(self, context, event):
        mod = addon_utils.addons_fake_modules.get("Strew")
        info = addon_utils.module_bl_info(mod)
        if info["show_expanded"] == True:
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
        bpy.ops.scene.source_populate()
        bpy.ops.scene.list_populate()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class testop(bpy.types.Operator):
    bl_idname = "strew.test"
    bl_label = "test"

    def execute(self, context):
        Assets = []
        OriginalObject = bpy.context.selected_objects
        Biome = context.scene.StrewPresetDrop.StrewPresetDropdown
        StrewFolder = SetupFolders.getfilepath(self, context)
        PresetFolder = str(StrewFolder) + "preset files\\"
        AssetListPath = PresetFolder + context.scene.StrewPresetDrop.StrewPresetDropdown + '.txt'
        with open(AssetListPath, 'r') as AssetListFile:
            AssetList = AssetListFile.readlines()
            for Asset in AssetList:
                Path = Asset.strip("\n").split(",")
                if len(Path) == 3:
                    Assets.append(f'{Path[1]}_{Path[2]}_LOD0')
                elif len(Path) == 2:
                    Assets.append(Path[1])
        StrewBiomeManager.BiomeCreation.run(Biome, Assets, OriginalObject)
        return {'FINISHED'}


#####################################################################################
#
#       ADD/REMOVE ASSETS FROM PRESETS
#           Operators
#           Definitions       
#
#####################################################################################    
# adds assets at the end of list in the file
class StrewAddAsset(bpy.types.Operator):
    bl_idname = "strew.addasset"
    bl_label = "addasset"

    #####
    #####TODO: make a better check than just look for asset with same name
    #####
    def execute(self, context):
        if bpy.data.filepath != "":
            # Do a Try except so if the preset file is not created or missing, it creates it.
            try:
                preset = context.scene.StrewPresetDrop.StrewPresetDropdown
                basename = bpy.path.basename(bpy.data.filepath)
                for obj in bpy.context.selected_objects:
                    asset = basename + ',' + obj.name
                    ManageAsset.AddAsset(self, context, preset, asset)
                return {'FINISHED'}
            except:
                StrewCreatePreset.execute(self, context)
                return {'FINISHED'}
        else:
            print("can't save as asset from temporary blend file yet. please save your file")
            return {'FINISHED'}


class StrewRemoveAsset(bpy.types.Operator):
    bl_idname = "strew.removeasset"
    bl_label = "removeasset"

    def execute(self, context):
        preset = context.scene.StrewPresetDrop.StrewPresetDropdown
        basename = bpy.path.basename(bpy.data.filepath)

        for obj in bpy.context.selected_objects:
            asset = basename + ',' + obj.name
            ManageAsset.RemoveAsset(self, context, preset, asset)
        return {'FINISHED'}


# Registers the assets in a list in a file
class StrewCreatePreset(bpy.types.Operator):
    bl_idname = "strew.createpreset"
    bl_label = "createpreset"

    def execute(self, context):
        if bpy.data.filepath != "":
            AssetList = []
            preset = context.scene.StrewPresetDrop.StrewPresetDropdown
            basename = bpy.path.basename(bpy.data.filepath)
            for obj in bpy.context.selected_objects:
                asset = basename + ',' + obj.name
                AssetList.append(asset + '\n')
            ManageAsset.CreateNew(self, context, preset, AssetList)
            return {'FINISHED'}
        else:
            print("can't save as asset from temporary blend file yet. please save your file")
            return {'FINISHED'}


class ManageAsset():
    # This is where the assets are written or erased from the textfiles.
    def AddAsset(self, context, preset, asset):
        StrewFolder = SetupFolders.getfilepath(self, context)
        AssetListPath = f'{StrewFolder}preset files\\{preset}.txt'
        AssetList = open(AssetListPath, 'r').readlines()
        AssetList.append(asset + '\n')
        with open(AssetListPath, 'w') as AssetListFile:
            for asset in AssetList:
                AssetListFile.write(asset)
        return {'FINISHED'}

    def RemoveAsset(self, context, preset, asset):
        StrewFolder = SetupFolders.getfilepath(self, context)
        AssetListPath = f'{StrewFolder}preset files\\{preset}.txt'
        AssetList = open(AssetListPath, 'r').readlines()
        AssetList.remove(asset + '\n')
        with open(AssetListPath, 'w') as AssetListFile:
            for asset in AssetList:
                AssetListFile.write(asset)
        return {'FINISHED'}

    def RemoveAssetIndex(self, context, preset, index):
        StrewFolder = SetupFolders.getfilepath(self, context)
        AssetListPath = f'{StrewFolder}preset files\\{preset}.txt'
        AssetList = open(AssetListPath, 'r').readlines()
        del AssetList[index]
        with open(AssetListPath, 'w') as AssetListFile:
            for asset in AssetList:
                AssetListFile.write(asset)
        return {'FINISHED'}

    def CreateNew(self, context, preset, AssetList):
        # gotta find a way to create new files, and new lines with new names without causing problems
        # because for the moment, all the presets are already defined manualy with text file
        # in fact, I just have to ask user what name he wants his preset to have, and write it to presets.txt.
        StrewFolder = SetupFolders.getfilepath(self, context)
        # This is in this line that the name will be defined
        AssetListPath = f'{StrewFolder}preset files\\{preset}.txt'
        with open(AssetListPath, 'w') as AssetListFile:
            for asset in AssetList:
                AssetListFile.write(asset)
        return {'FINISHED'}


#####################################################################################
#
#       IMPORT ASSETS
#           Operators
#           Definitions       
#
#####################################################################################  

# Reads the assets from a list in a file
class StrewImportAssets(bpy.types.Operator):
    bl_idname = "strew.importassets"
    bl_label = "importassets"

    def execute(self, context):
        # setups the collection system where the assets will be stored.
        SAC = SetupStrew.SetupCollections(self)
        StrewFolder = SetupFolders.getfilepath(self, context)
        BlendFolder = str(StrewFolder) + "blend files\\"
        PresetFolder = str(StrewFolder) + "preset files\\"
        # read the file line by line, converting each of them as list
        AssetListPath = PresetFolder + context.scene.StrewPresetDrop.StrewPresetDropdown + '.txt'
        with open(AssetListPath, 'r') as AssetListFile:
            AssetList = AssetListFile.readlines()
            # strips the lines of the file as a Path, and an Object Name.
            # are all the assets going to be in OBJECT inner path? gotta change it eventualy.
            for Asset in AssetList:
                Path = Asset.strip("\n").split(",")
                # actually imports the assets listed in the file.
                if len(Path) == 2:
                    Import.CustomAsset(BlendFolder + Path[0], Path[1].strip(), SAC)
                ###  Difference between 2 and 3, is if the asset comoes from us, it will be in a collection. custom assets are not.
                elif len(Path) == 3:
                    Import.Collection(BlendFolder + Path[0], Path[1], Path[2], SAC)

        # Is THIS realy neccessary?? apparenly yes
        return {'FINISHED'}
    # Pretty self explanatory... right?


class Import():
    def CustomAsset(AssetPath, AssetName, SAC):
        if AssetName in bpy.data.collections[SAC.name].all_objects:
            return {'FINISHED'}
            # I Should inform the user that an object with same name already exists
        else:

            if "Strew_Custom_Assets" not in bpy.data.collections[SAC.name].children:
                StrewCustomCollection = bpy.data.collections.new("Strew_Custom_Assets")
                StrewAssetsCollection = bpy.data.collections[StrewAssetsCollection_name]
                StrewAssetsCollection.children.link(StrewCustomCollection)

            Import.SetActiveCollection(bpy.context.view_layer.layer_collection, "Strew_Custom_Assets")
            print(bpy.context.view_layer.active_layer_collection.name)
            print(AssetName)
            bpy.ops.wm.append(
                filepath=os.path.join(AssetPath + "\\Object\\" + AssetName),
                directory=os.path.join(AssetPath + "\\Object\\"),
                filename=AssetName
                # autoselect = True,
                # active_collection = True
            )

            # obj_object = bpy.context.selected_objects[0]
            # bpy.ops.collection.objects_remove_all()
            # SAC.objects.link(obj_object)

    def Collection(CollPath, CollParent, CollName, SAC):
        ##Ensures the parent collection (specie) exists in the file, and is active
        if CollParent not in bpy.data.collections[SAC.name].children:
            StrewAssetsCollection = bpy.data.collections[StrewAssetsCollection_name]
            StrewSpecieCollection = bpy.data.collections.new(CollParent)
            StrewAssetsCollection.children.link(StrewSpecieCollection)
        Import.SetActiveCollection(bpy.context.view_layer.layer_collection, CollParent)

        if CollName in bpy.data.collections[CollParent].children:
            print("collection already exists")
        else:
            print(bpy.context.view_layer.active_layer_collection.name)
            print(CollName)
            bpy.ops.wm.append(
                filepath=os.path.join(CollPath + "\\Collection\\" + CollName),
                directory=os.path.join(CollPath + "\\Collection\\"),
                filename=CollName
                # autoselect = True,
                # active_collection = True
            )
            # print(f"can't import Collection {AssetName} from {AssetPath}")

    def SetActiveCollection(collection, tofind):
        for c in collection.children:
            if c.name == tofind:
                bpy.context.view_layer.active_layer_collection = c
                # print("found it")
            elif len(c.children):
                Import.SetActiveCollection(c, tofind)
            else:
                # print(f'not in {c.name}')
                pass


#####################################################################################
#
#       SETUP STREW       
#
#####################################################################################  

class SetupFolders(bpy.types.Operator):
    # TODO: MAKE IT CREATE/IMPORT THE TEXT FILES AS WELL
    bl_idname = "strew.setupfolder"
    bl_label = "setupfolder"
    filepath = ""

    def execute(self, context):
        try:
            try:
                preferences = context.preferences
                addon_prefs = preferences.addons["Strew"].preferences
                filepath = addon_prefs.filepath
            except:
                print("couldn't get strew path")
                os.mkdir(filepath)
                return filepath + "\\"
            return filepath + "\\"
        except:
            print("couldn't create strew folders. maybe it already exists.")
            return filepath

    def getfilepath(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons["Strew"].preferences
        filepath = addon_prefs.filepath
        if filepath.endswith("\\"):
            return filepath
        else:
            return filepath + "\\"


class SetupStrew(bpy.types.Operator):
    bl_idname = "strew.setupstrew"
    bl_label = "setupstrew"

    def execute(self, context):
        self.SetupCollections()
        SetupFolders.execute(self, context)
        return {'FINISHED'}

    def SetupCollections(self):
        # Checks if Strew Master Collection exists, otherwise, creates it.
        try:
            StrewMasterCollection = bpy.data.collections[StrewMasterCollection_name]
        except:
            StrewMasterCollection = bpy.data.collections.new(StrewMasterCollection_name)
            bpy.context.scene.collection.children.link(StrewMasterCollection)

        # Checks if Strew Assets Collection exists, otherwise, creates it.
        try:
            StrewAssetsCollection = bpy.data.collections[StrewAssetsCollection_name]
        except:
            StrewAssetsCollection = bpy.data.collections.new(StrewAssetsCollection_name)
            StrewMasterCollection.children.link(StrewAssetsCollection)
        # Gives pack the AssetCollection as a var usable externaly.
        return StrewAssetsCollection
        # Pretty sure that now THIS is not neccessary.
        return {'FINISHED'}






#####################################################################################
#
#       REGISTER TO THE REGISTRE BECAUSE IF NOT, BLENDER DON'T KNOW JOHN SNOOOOOW       
#
#####################################################################################   

classes = [
    MainPanel,
    StrewImportAssets,
    StrewCreatePreset,
    StrewAddAsset,
    StrewRemoveAsset,
    SetupFolders,
    SetupStrew,
    InvokePrefsPanel,
    testop,
    UiSwitch,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.strew_ui_switch = bpy.props.PointerProperty(type=UiSwitch)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.strew_ui_switch