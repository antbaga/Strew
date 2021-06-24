bl_info = {
    "name": "STREW",
    "author": "Antoine Bagattini, Clovis Flayols, Laura Mercadal",
    "version": (0,0,10),
    "blender": (2,90,1),
    "location": "View3D > Toolshelf",
    "description": "Strew addon adds gold to your life",
    "category": "Add Mesh",
}

import bpy
import os
import random
from bpy.types import Operator, AddonPreferences, PropertyGroup, UIList, Panel
from bpy.props import StringProperty, IntProperty, EnumProperty, PointerProperty, CollectionProperty, BoolProperty
from . import StrewUi, StrewManOperators, StrewBiomeManager


#Place this one in the preferences in a hidden menu
inner_path = 'Object'
StrewMasterCollection_name = 'Strew'
StrewAssetsCollection_name = 'Strew_Assets'


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
        default=bpy.utils.user_resource('SCRIPTS')+"\\addons\\Strew"
        #default="C:\\Strew"
    )
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text="Determines where the Strew files will be saved")
        layout.prop(self, "filepath")

        #######################################
        #   START ASSET MANAGER, LIBRARY PART 
        #######################################
        
        col = layout.row(align=True)
        split = col.split()
        box = col.box()
        
        row = box.row()
        row.label(text='Asset Library :')
        row.prop(context.scene.StrewSourceDrop, "StrewSourceDropdown")
        #row.operator("scene.source_populate",text= "populate")
        row = box.row()
        row.template_list("SMS_UL_List", "", scene.SMSL, "collection", scene.SMSL, "active_user_index",rows=24)
        
        #######################################
        #   CENTRAL BUTTONS
        #######################################
        row = col.column(align=True)
        scale_row = row.column()
        scale_row.scale_x = 0.30
        scale_row.scale_y = 2.0
        scale_row.separator(factor=15.0)
        scale_row.operator("strew.addassettopreset",icon= "ADD",text="")
        scale_row.operator("strew.removeassetfrompreset",icon= "REMOVE",text="")
        scale_row.operator("Strew.registerasset",icon="BLENDER",text="")

        #######################################
        #   PRESET PART OF ASSET MANAGER
        #######################################
        
        box = col.box()
        row = box.row()
        row.label(text='Biome Editor :')
        row.prop(context.scene.StrewPresetDrop, "StrewPresetDropdown")
        
        row = box.row()
        splitrow = row.split()
        splitrow.scale_x=33.4 
        splitrow.separator()
        splitrow = row.split()
        splitrow.operator("strew.addpresetpopup",text= "New Preset")
        
        row = box.row()
        splitrow = row.split()
        splitrow.scale_x=33.4    
        splitrow.separator()
        splitrow = row.split()
        splitrow.operator("strew.removepresetpopup",text= "Remove Preset")
        
        row = box.row()
        splitrow = row.split()
        splitrow.scale_x=33.4    
        splitrow.separator()
        splitrow = row.split()
        splitrow.operator("strew.clonepresetpopup",text= "Clone Preset")
        
        row = box.row()
        splitrow = row.split()
        splitrow.scale_x=33.4    
        splitrow.separator()
        splitrow = row.split()
        splitrow.operator("strew.renamepresetpopup",text= "edit Preset")
        
        row = box.row()
        row.template_list("SMA_UL_List", "", scene.SMAL, "collection", scene.SMAL, "active_user_index",rows=20)
        
#####################################################################################
#
#       POPUP PANEL FOR ASSET VARIANTS
#
#####################################################################################  

##Deosn't do anything since i can"t put a fucking collectionproperty inside another collectionproperty. fuck you blender.
class VariantPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Variant Panel"
    bl_idname = "OBJECT_PT_variant"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    #bl_options = {'INSTANCED'}
        
    def draw(self, context):
        layout = self.layout
        smsl = context.scene.SMSL
        try: 
            preset = bpy.context.scene.StrewPresetDrop.StrewPresetDropdown
            VariantList, VariantListName= StrewManOperators.GetAssetList.Variant(self, context, preset)
            user = getattr(context,"active_smms_user", smsl.collection[smsl.active_user_index])
            col = layout.column()
            col.label(text=f" {user.name}", icon='WORLD_DATA')
            #for variant in VariantList:
             #   col.prop(user, variant)
        except:
            pass



       
#####################################################################################
#
#       OPERATORS TO MODIFY LISTS
#
#####################################################################################   

#TODO: make a copy of the file on first edition, and only replace original when user click confirm.
# do not delete the temp file, it will be overwritten by next one. can act as a recovery for large edits.
class AddAssetToPreset(Operator):
    bl_idname = "strew.addassettopreset"
    bl_label = "addassettopreset"
    #bl_description = "add asset to preset"
    
    def execute(self, context):
        cts = bpy.context.scene
        active_object = cts.SMSL.collection[cts.SMSL.active_user_index]
        asset = active_object.name
        preset = cts.StrewPresetDrop.StrewPresetDropdown
        if source != "This_file":
            source = f"{cts.SourceDrop.SourceDropdown}.blend"
        else:
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
    

#####################################################################################
#
#       DROPDOWN MENU OF PRESETS
#
#####################################################################################    
def update_StrewPresetDrop(self, context):
    StrewManOperators.SCENE_OT_list_populate.execute(self, context)
    return None

#recup la liste des préset dans le fichier text
def enumfromfile(self, context):
    enum_items = []
    StrewFolder = str(StrewUi.SetupFolders.getfilepath(self, context))
    PresetListPath = f"{StrewFolder}preset files\\presetlist.txt"
    with open(PresetListPath,'r') as PresetListFile:
        PresetList=PresetListFile.readlines()
        if PresetList is None:
            return enum_items
        count = 0
        for preset in PresetList:
            Choice = preset.split(",")
            identifier = str(Choice[0])
            name = str(Choice[1])
            description = str(Choice[2])
            number = count
            enum_items.append((identifier,name,description,number))
            count += 1
    return enum_items

#Property de la liste de dropdown  
class StrewPresetProperty(PropertyGroup):
    StrewPresetDropdown : EnumProperty(
        name="",
        description= "Select preset",
        #items=[]
        default= 0,
        items=enumfromfile,
        update=update_StrewPresetDrop)

#Liste de dropdown
class PRESET_UL_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        custom_icon = 'OBJECT_DATAMODE'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = User)

        
 
 #####################################################################################
#
#       DROPDOWN MENU OF SOURCES FILES
#
#####################################################################################
def update_sourcedrop(self, context):
    StrewManOperators.SCENE_OT_source_populate.execute(self, context)
    return None
#recup la liste des préset dans le fichier text
def enumfromblenderlist(self, context):
    enum_items = []
    StrewFolder = str(StrewUi.SetupFolders.getfilepath(self, context))
    PresetListPath = f'{StrewFolder}preset files\\SourceFilesList.txt'
    with open(PresetListPath,'r') as SourceListFile:
        SourceList=SourceListFile.readlines()
        if SourceList is None:
            return enum_items
        count = 0
        for Source in SourceList:
            Choice = Source.split(",")
            identifier = str(Choice[0])
            name = str(Choice[1])
            description = str(Choice[2])
            number = count
            enum_items.append((identifier,name,description,number))
            count += 1
    return enum_items

#Property de la liste de dropdown  
class StrewSourceProperty(PropertyGroup):
    StrewSourceDropdown : EnumProperty(
        name="",
        description= "Select source",
        #items=[]
        items=enumfromblenderlist,
        update= update_sourcedrop)
        

#Liste de dropdown
class SRCFILES_UL_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        custom_icon = 'OBJECT_DATAMODE'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = User)
            
            

            
#####################################################################################
#
#       PRESET LISTS FOR PRESET MANAGER
#
#####################################################################################    


class SMAAsset(PropertyGroup):
    type : EnumProperty(
        items=(('A', "Option A", ""),('B', "Option B", ""),)
    )
    #val = BoolProperty()
    
class SMAList(PropertyGroup):
    collection : CollectionProperty(
        name = "SMAA",
        type = SMAAsset)
    active_user_index : IntProperty()


class SMA_UL_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
            #layout.prop(item, "val", text="")
            #layout.prop(item, "type", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            


#####################################################################################
#
#       PRESET LISTS FOR SOURCE MANAGER
#
#####################################################################################    
def splash(self, context):
    # AFAICT context override does not get to panel
    bpy.ops.wm.call_panel(
            {"active_smms_user" : self.collection[self.active_user_index]},
            'INVOKE_DEFAULT',
            name="OBJECT_PT_variant",
            )
    return None
    
    
class SMSAsset(PropertyGroup):
    amount = IntProperty()
        
    
class SMSList(PropertyGroup):
    collection : CollectionProperty(
        name = "SMSA",
        type = SMSAsset)
    active_user_index : IntProperty(
    #update=splash
    )
        
class SMS_UL_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.context_pointer_set("active_smms_user", item,)
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
            #layout.prop(item, "val", text="")
            #layout.prop(item, "type", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            

    
#####################################################################################
#
#       REGISTER AND UNREGISTER
#
#####################################################################################    

classes=  [
StrewPreferences,
StrewPresetProperty,
StrewSourceProperty,
SMAAsset,
SMAList,
SMSAsset,
SMSList,
SRCFILES_UL_List,
PRESET_UL_List,
SMA_UL_List,
SMS_UL_List,
VariantPanel,
]

#Here goes the magic thingies
def register() :
    for cls in classes:
        bpy.utils.register_class(cls)
    StrewUi.register()
    StrewManOperators.register()
    StrewBiomeManager.register()
    bpy.types.Scene.StrewPresetDrop = PointerProperty(type= StrewPresetProperty)
    bpy.types.Scene.StrewSourceDrop = PointerProperty(type= StrewSourceProperty)
    bpy.types.Scene.SMAL = PointerProperty(type= SMAList)
    bpy.types.Scene.SMSL = PointerProperty(type= SMSList)
def unregister() :
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.StrewPresetDrop
    del bpy.types.Scene.StrewSourceDrop    
    del bpy.types.Scene.SMAL
    del bpy.types.Scene.SMSL
    StrewUi.unregister()
    StrewManOperators.unregister()
if __name__ == "__main__":
    register()