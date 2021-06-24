import bpy

class BiomeCreation():

    ###########################################################
    #
    #                  CREATE OR FIND BIOME
    #
    ###########################################################

    def GetBiome(BiomeName, OriginalObject):
        AssetCount = 0
        #For each element, try to find it, and if it can't, create it.
        #
        ## BIOME
        if bpy.data.node_groups.get(f'Strew_Biome_{BiomeName}'):
            Master_Tree = bpy.data.node_groups.get(f'Strew_Biome_{BiomeName}')
        else:
            Master_Tree = bpy.data.node_groups.new(name=f'Strew_Biome_{BiomeName}',type='GeometryNodeTree')
        
        ## EFFECTOR 
        if Master_Tree.nodes.get('Strew_Node_Effector'):
            Effector_Node = Master_Tree.nodes.get('Strew_Node_Effector')
        else:
            Effector_Node = Master_Tree.nodes.new('GeometryNodeGroup')
            Effector_Node.node_tree = bpy.data.node_groups.get('Nature_GeoNode_Effector')
            Effector_Node.name = "Strew_Node_Effector"
            Effector_Node.location = (-450,0)
            
        ## BIOME  
        if Master_Tree.nodes.get('Strew_Node_Biome'): 
            Biome_Node = Master_Tree.nodes.get('Strew_Node_Biome')
        else:
            Biome_Node = Master_Tree.nodes.new('GeometryNodeGroup')
            Biome_Node.node_tree = bpy.data.node_groups.get('Nature_GeoNode_Biome')
            Biome_Node.name = "Strew_Node_Biome"
            Biome_Node.location = (-450,-150)
         
        ## INPUT   
        if Master_Tree.nodes.get('Group Input'):
            Input_Node = Master_Tree.nodes.get('Group Input')
        else:
            Input_Node = Master_Tree.nodes.new('NodeGroupInput')
            Input_Node.location = (-650,0)
            Master_Tree.links.new(Input_Node.outputs[0],Biome_Node.inputs["Count"])
            Master_Tree.links.new(Input_Node.outputs[1],Biome_Node.inputs["Scale"])
            Master_Tree.links.new(Input_Node.outputs[2],Biome_Node.inputs["Random Position"])
            Master_Tree.links.new(Input_Node.outputs[3],Biome_Node.inputs["Seed"])
            
        ##OBJECT INFO
        if Master_Tree.nodes.get('Object Info'):
            Object_Node = Master_Tree.nodes.get('Object Info')
        else:
            Object_Node = Master_Tree.nodes.new('GeometryNodeObjectInfo')
            Object_Node.location = (300,-180)
            Object_Node.transform_space = 'RELATIVE'
            Object_Node.inputs[0].default_value = OriginalObject[0]  ####### TODO QUICKLY: MAKE IT HANDLE MULTIPLE OBJECT SELECTION
            Master_Tree.links.new(Object_Node.outputs['Geometry'],Effector_Node.inputs["Geometry"])
        ## JOIN
        if Master_Tree.nodes.get('Join Geometry'):
            Join_Node = Master_Tree.nodes.get('Join Geometry')
        else:    
            Join_Node = Master_Tree.nodes.new('GeometryNodeJoinGeometry')
            Join_Node.location = (300,0)
        
        ##OUTPUT
        if Master_Tree.nodes.get('Group Output'):
            Output_Node = Master_Tree.nodes.get('Group Output')
        else:
            Output_Node = Master_Tree.nodes.new('NodeGroupOutput')
            Output_Node.location = (470,0)
            Master_Tree.links.new(Join_Node.outputs[0],Output_Node.inputs[0])
            
            
        ##get the number of assets to put them on the same line
        for AssetNodes in Master_Tree.nodes: 
            if "Strew_Asset_" in AssetNodes.name:
                AssetCount += 1

        return Master_Tree, Effector_Node, Biome_Node, Join_Node, AssetCount


    ###########################################################
    #
    #                  ADD ASSET
    #
    ###########################################################

    def AddAsset(Master_Tree, Effector_Node, Biome_Node, Join_Node, AssetName, AssetCount):
        
        ## Create the asset node and place it correctly
        if Master_Tree.nodes.get(f'Strew_Node_Asset_{AssetName}'):
            pass
        else:
            AssetNode = Master_Tree.nodes.new('GeometryNodeGroup')
            AssetNode.name = f'Strew_Node_Asset_{AssetName}'
            AssetNode.node_tree = bpy.data.node_groups.get('Nature_GeoNode_Asset')
            AssetNode.show_options = False

            AssetNode.location.x = 0
            AssetNode.location.y = AssetCount*-380


            ##Link the asset node and fill values
            try:
                AssetNode.inputs["Asset"].default_value = bpy.data.objects[AssetName]
            except:
                print(f"can't find {AssetName}. reimport it") ##TODO:  MAKE IT REIMPORT AUTOMATICALY
            
            Master_Tree.links.new(Biome_Node.outputs["Count"],AssetNode.inputs["Count"])
            Master_Tree.links.new(Biome_Node.outputs["Scale"],AssetNode.inputs["Scale"])
            Master_Tree.links.new(Biome_Node.outputs["Paint Layer"],AssetNode.inputs["Paint Layer"])
            Master_Tree.links.new(Biome_Node.outputs["Random Position"],AssetNode.inputs["Random Position"])

            Master_Tree.links.new(Effector_Node.outputs["Geometry"],AssetNode.inputs["Geometry"])
            Master_Tree.links.new(AssetNode.outputs["Geometry"],Join_Node.inputs["Geometry"])

        
        ##randomise seed of placed assets
        if Master_Tree.nodes.get(f'Strew_{AssetName}_Randomiser'):
            try:
                Master_Tree.links.new(Biome_Node.outputs["Seed"],AssetRandomiser.inputs[0])
                Master_Tree.links.new(AssetRandomiser.outputs[0],AssetNode.inputs["Seed"])
            except:
                pass
        else:
            AssetRandomiser = Master_Tree.nodes.new('ShaderNodeMath')
            AssetRandomiser.name = f'Strew_{AssetName}_Randomiser'
            Master_Tree.links.new(Biome_Node.outputs["Seed"],AssetRandomiser.inputs[0])
            AssetRandomiser.inputs[1].default_value = AssetCount
            AssetRandomiser.location.x = -150
            AssetRandomiser.location.y = AssetCount*-380-220
            Master_Tree.links.new(AssetRandomiser.outputs[0],AssetNode.inputs["Seed"])
        
    def run(Biome, Assets, OriginalObject):
        Master_Tree, Effector_Node, Biome_Node, Join_Node, AssetCount = BiomeCreation.GetBiome(Biome, OriginalObject)
        for AssetName in Assets:
            BiomeCreation.AddAsset(Master_Tree, Effector_Node, Biome_Node, Join_Node, AssetName, AssetCount)
            AssetCount += 1

classes = [
#BiomeCreation,
]

def register() :
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister() :
    for cls in classes:
        bpy.utils.unregister_class(cls)