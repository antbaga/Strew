from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty
from . import __init__, StrewUi, StrewEnums
import addon_utils,shutil,bpy,os,zipfile

#####################################################################################
#
#       POPUP BOX
#
#####################################################################################   

    
class AddPresetPopup(bpy.types.Operator):
    bl_idname = "strew.addpresetpopup"
    bl_label = "Create new preset"

    
    def draw(self,context):
        properties = context.scene.preset_name_string
        l = self.layout
        c = l.column(align=True)
        c.prop(properties, "presetname")
        c.prop(properties, "presetdesc")

    def execute(self, context):
        properties = context.scene.preset_name_string
        ManagePreset.New(self, context, properties.presetname, properties.presetdesc)
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
class ClonePresetPopup(bpy.types.Operator):
    bl_idname = "strew.clonepresetpopup"
    bl_label = "Clone preset"

    def draw(self, context):
        properties = context.scene.preset_name_string
        l = self.layout
        c = l.column(align=True)
        c.prop(properties, "presetname")
        c.prop(properties, "presetdesc")
        ##Bon, ça marche toujours pas
        #Name = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown
    def execute(self, context):
        id = bpy.context.scene.StrewPresetDrop["StrewPresetDropdown"]
        properties = context.scene.preset_name_string
        ManagePreset.Clone(self, context,id, properties.presetname, properties.presetdesc)
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class RemovePresetPopup(bpy.types.Operator):
    bl_idname = "strew.removepresetpopup"
    bl_label = "Remove this preset?"


    def execute(self, context):
        dropid = bpy.context.scene.StrewPresetDrop["StrewPresetDropdown"]
        ManagePreset.Remove(self, context, dropid)
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class RenamePresetPopup(bpy.types.Operator):
    bl_idname = "strew.renamepresetpopup"
    bl_label = "Rename preset"
    
    def draw(self,context):
        properties = context.scene.preset_name_string
        l = self.layout
        c = l.column(align=True)
        c.prop(properties, "presetname")
        c.prop(properties, "presetdesc")

    def execute(self, context):
        properties = context.scene.preset_name_string
        id = bpy.context.scene.StrewPresetDrop["StrewPresetDropdown"]
        oldname = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown
        ManagePreset.Rename(self, context,id, oldname, properties.presetname, properties.presetdesc)
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
class SubListPopup(bpy.types.Operator):
    bl_idname = "strew.sublistpopup"
    bl_label = "sub list popup"

    

    def execute(self, context):
        name = self.text
        desc = self.desc
        ManagePreset.New(self, context, name, desc)
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

#####################################################################################
#
#       OPERATORS TO MODIFY LISTS
#
#####################################################################################   

#TODO: make a copy of the file on first edition, and only replace original when user click confirm.
# do not delet the temp file, it will be overwritten by next one. can act as a recovery for large edits.
class RegisterAsset(Operator):
    bl_idname = "strew.registerasset"
    bl_label = "registerasset"
    
    def execute(self, context):
        objname = bpy.context.scene.SMSL.collection[bpy.context.scene.SMSL.active_user_index].name
        obj= {bpy.context.scene.objects[objname]}
        #obj= {objects for objects in bpy.context.selected_objects}
        StrewFolder = StrewUi.SetupFolders.getfilepath(self, context)  
        base_path= f'{StrewFolder}blend files\\'
        bpy.data.libraries.write(f'{base_path}custom.blend',obj, fake_user=True)
        return {'FINISHED'}

class AddAssetToPreset(Operator):
    bl_idname = "strew.addassettopreset"
    bl_label = "addassettopreset"
    #bl_description = "add asset to preset"
    
    def execute(self, context):
        cts = bpy.context.scene
        active_object = cts.SMSL.collection[cts.SMSL.active_user_index]
        asset = active_object.name
        preset = cts.StrewPresetDrop.StrewPresetDropdown
        source = cts.StrewSourceDrop.StrewSourceDropdown
        print(source)
        if source == "This_file":
            source = "custom.blend"
        
        StrewUi.ManageAsset.AddAsset(self, context, preset, f"{source},{asset}")
        SCENE_OT_list_populate.execute(self, context)
        return {'FINISHED'}
    
class RemoveAssetFromPreset(Operator):
    bl_idname = "strew.removeassetfrompreset"
    bl_label = "remove asset from preset"
    #bl_description = "remove asset from preset"
    
    def execute(self, context):
        cts = bpy.context.scene
        active_object = cts.SMAL.collection[cts.SMAL.active_user_index]
        preset = cts.StrewPresetDrop.StrewPresetDropdown

        StrewUi.ManageAsset.RemoveAssetIndex(self, context, preset, cts.SMAL.active_user_index)
        SCENE_OT_list_populate.execute(self, context)
        
        return {'FINISHED'}
    
class SCENE_OT_list_populate(Operator):
    bl_idname = "scene.list_populate"
    bl_label = "Populate list"
    
    def execute(self, context):
        context.scene.SMAL.collection.clear()
        preset = context.scene.StrewPresetDrop.StrewPresetDropdown
        AssetList, AssetListName = GetAssetList.Variant(self, context, preset)
        for Asset in AssetList:
            item = context.scene.SMAL.collection.add()
            Path = Asset.split(",")
            if len(Path) == 3: item.name = Path[2]
            if len(Path) == 2: item.name = Path[1]
            item.description = Asset
        return {'FINISHED'}
    
class SCENE_OT_source_populate(Operator):
    bl_idname = "scene.source_populate"
    bl_label = "Populate source"
    
    def execute(self,context):
        context.scene.SMSL.collection.clear()
        preset = context.scene.StrewSourceDrop.StrewSourceDropdown
        
        if preset != "This_file":
            AssetList, AssetListName = GetAssetList.Variant(self, context, preset)
            for Asset in AssetList:
                item = context.scene.SMSL.collection.add()
                Path = Asset.split(",")
                item.name = Path[2]
                item.description = Asset
            return {'FINISHED'}
        else:
            blend = bpy.path.basename(bpy.context.blend_data.filepath)
            AssetList = bpy.context.scene.objects
            for Asset in AssetList:
                item = context.scene.SMSL.collection.add()
                item.name = Asset.name
                item.description = blend +","+ Asset.name
            return {'FINISHED'}
#####################################################################################
#
#       OPERATORS TO ADD OR REMOVE PRESETS
#
##################################################################################### 

class ManagePreset():
    def New(self, context, name, desc):
        formatname = str(name).replace(" ", "_")
        formatdesc = str(desc).replace(",", ".")
        StrewFolder = StrewUi.SetupFolders.getfilepath(self, context)  
        PresetPath = str(f'{StrewFolder}preset files\\{formatname}.txt')
        with open(PresetPath,'w') as PresetFile:
            PresetFile.write("")  
        EnumFormat = str(formatname)+","+str(name)+","+str(formatdesc)
        PresetListPath = f'{StrewFolder}preset files\\presetlist.txt'
        PresetList=open(PresetListPath,'r').readlines()
        PresetList.append(EnumFormat+'\n')
        with open(PresetListPath,'w') as PresetListFile:
            for preset in PresetList:
                PresetListFile.write(preset)
        return{'FINISHED'}
    def Clone(self, context,id, name, desc):
        formatname = str(name).replace(" ", "_")
        formatdesc = str(desc).replace(",", ".")
        StrewFolder = StrewUi.SetupFolders.getfilepath(self, context)  
        original = str(f'{StrewFolder}preset files\\{context.scene.StrewPresetDrop.StrewPresetDropdown}.txt')
        target = str(f'{StrewFolder}preset files\\{formatname}.txt')
        shutil.copyfile(original,target)
        EnumFormat = str(formatname)+","+str(name)+","+str(formatdesc)
        PresetListPath = f'{StrewFolder}preset files\\presetlist.txt'
        PresetList=open(PresetListPath,'r').readlines()
        PresetList.append(EnumFormat+'\n')
        with open(PresetListPath,'w') as PresetListFile:
            for preset in PresetList:
                PresetListFile.write(preset)
        return{'FINISHED'}
    def Remove(self, context, id):
        name = context.scene.StrewPresetDrop.StrewPresetDropdown
        formatname = str(name).replace(" ", "_")
        StrewFolder = StrewUi.SetupFolders.getfilepath(self, context)
        PresetPath = str(f'{StrewFolder}preset files\\{formatname}.txt')
        os.remove(PresetPath)
        PresetListPath = f'{StrewFolder}preset files\\presetlist.txt'
        PresetList=open(PresetListPath,'r').readlines()
        del PresetList[id]
        with open(PresetListPath,'w') as PresetListFile:
            for preset in PresetList:
                PresetListFile.write(preset)
        return{'FINISHED'}
    def Rename(self, context, id, oldname, name, desc):
        formatname = str(name).replace(" ", "_")
        formatoldname = str(oldname).replace(" ", "_")
        formatdesc = str(desc).replace(",", ".")
        StrewFolder = StrewUi.SetupFolders.getfilepath(self, context)
        PresetPath = f'{StrewFolder}preset files\\{formatoldname}.txt'
        NewPresetPath = f'{StrewFolder}preset files\\{formatname}.txt'
        PresetListPath = f'{StrewFolder}preset files\\presetlist.txt'
        PresetList=open(PresetListPath,'r').readlines()
        newvalue = str(formatname)+","+str(name)+","+str(formatdesc)+'\n'
        PresetList[id]=newvalue
        with open(PresetListPath,'w') as PresetListFile:
            for preset in PresetList:
                PresetListFile.write(preset)
        os.rename(PresetPath, NewPresetPath)
    def Update(self, context, id):
        print("nothing here for the moment. come back in a few.")
        return{'FINISHED'}
    
#####################################################################################
#
#       OPERATORS TO IMPORT OR EXPORT ASSETSLIST AS LISTS
#
##################################################################################### 

class GetAssetList():
    def Specie(self, context, preset):
        Species_List = []
        StrewFolder = str(StrewUi.SetupFolders.getfilepath(self, context))
        AssetListPath = f'{StrewFolder}preset files\\{preset}.txt'
        with open(AssetListPath,'r') as AssetListFile:
            AssetList=AssetListFile.readlines()
            if AssetList is None:
                return Species_List
            for Asset in AssetList:
                Asset = Asset.strip("\n")
                path = Asset.split(",")
                if len(path) == 3:
                    #Variante = Asset.strip(path[3]).strip(",")
                    Specie = Asset.strip(path[2]).strip(",")
                    if Specie not in Species_List:
                        Species_List.append(Specie)
                elif len(path) == 2:
                    if Asset not in Variant_List:
                        Variant_List.append(Asset)
                else:
                    print("there is an invalid item in the list")
        return Species_List
    
    def Variant(self, context, preset):
        Variant_List = []
        VariantName_List = []
        StrewFolder = str(StrewUi.SetupFolders.getfilepath(self, context))
        AssetListPath = f'{StrewFolder}preset files\\{preset}.txt'
        with open(AssetListPath,'r') as AssetListFile:
            AssetList=AssetListFile.readlines()
            if AssetList is None:
                return Variant_List
            for Asset in AssetList:
                Asset = Asset.strip("\n")
                path = Asset.split(",")                
                if len(path) == 3:
                    #Variant = Asset.strip(path[3]).strip(",")
                    #Prevents LOD from being added to the list
                    if Asset not in Variant_List:
                        Variant_List.append(Asset)
                        VariantName_List.append(path[2])
                #handles the custom mesh added to lists
                elif len(path) == 2:
                    if Asset not in Variant_List:
                        Variant_List.append(Asset)
                        VariantName_List.append(path[1])
                else:
                    print("there is an invalid item in the list")
                    pass
        return Variant_List, VariantName_List
    
    #Not used actualy. maybe later.
    def Mesh(self, context, preset):
        asset_list= []
        StrewFolder = str(StrewUi.SetupFolders.getfilepath(self, context))
        AssetListPath = f'{StrewFolder}preset files\\{preset}.txt'
        with open(AssetListPath,'r') as AssetListFile:
            AssetList=AssetListFile.readlines()
            if AssetList is None:
                return asset_list
            for Asset in AssetList:
                Asset = Asset.strip("\n")
                path = Asset.split(",")
                if len(path) == 3:
                    Variante = Asset.strip(path[3]).strip(",")
                    if Variante not in VarianteList:
                        VarianteList.append(Variante)
                elif len(path) == 2:
                    if Asset not in Variant_List:
                        Variant_List.append(Asset)
                else:
                    print("there is an invalid item in the list")
                    pass
        return asset_list


#####################################################################################
#
#       REGISTER AND UNREGISTER
#
##################################################################################### 


classes=  [
AddAssetToPreset,
RemoveAssetFromPreset,
AddPresetPopup,
ClonePresetPopup,
RemovePresetPopup,
SCENE_OT_source_populate,
SCENE_OT_list_populate,
RenamePresetPopup,
SubListPopup,
RegisterAsset,
]

def register() :
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister() :
    for cls in classes:
        bpy.utils.unregister_class(cls)