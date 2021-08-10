import bpy
from . import StrewUi, StrewManOperators, __init__, StrewProps, StrewFunctions


def apply_geometry_nodes(terrain_object):

    Mesh = bpy.data.meshes.new(terrain_object.name+"_terrain")
    biome = bpy.data.objects.new("StrewBiome", Mesh)
    bpy.context.scene.collection.objects.link(biome)
    geometry_node_master = StrewFunctions.geometry_node_master
    try:
        terrain_object["Strew_Terrain_Type"]            # checks if object has terrain property
    except:
        modifier = biome.modifiers.new
        strew_terrain = modifier(name='Strew_Terrain', type='NODES')
        strew_biome = bpy.data.node_groups[geometry_node_master].copy()
        strew_terrain.node_group = strew_biome
        terrain_object["Strew_Terrain_Type"] = 1        # assign terrain property to object
        strew_biome.nodes["Object Info.008"].inputs[0].default_value = terrain_object

    return strew_biome


def assign_collection(biome, collection, asset_type):
    rocks_node = biome.nodes['Group.010']               # get rocks nodes
    trees_node = biome.nodes['Group.012']               # get trees nodes
    grass_node = biome.nodes['Group.013']               # get grass nodes
    settings_node = biome.nodes['Group.011']            # get settings nodes

    if asset_type == 'rocks':
        rocks_node.inputs[17].default_value = False          # enable rocks in rocks_node
        settings_node.inputs[11].default_value = False       # enable rocks in biome
        rocks_node.inputs[25].default_value = True           # Enable Use collection
        rocks_node.inputs[26].default_value = collection     # assign asset to field
        return
    if asset_type == 'trees':
        settings_node.inputs[12].default_value = False       # enable trees in biome
        trees_node.inputs[25].default_value = True           # Enable Use collection
        trees_node.inputs[26].default_value = collection     # assign asset to field
        return
    if asset_type == 'grass':
        grass_node.inputs[25].default_value = True           # Enable Use collection
        grass_node.inputs[26].default_value = collection     # assign asset to field
        return


classes = [

]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
