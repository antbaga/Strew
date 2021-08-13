import bpy
from . import StrewUi, StrewManOperators, __init__, StrewProps, StrewFunctions
import json

#####################################################################################
#
#       SETUP
#
#####################################################################################


def setup_biome_collection(self, context, asset_list, biome_name, strew_collection, biome_nodes):
    # CALLED FROM:
    #   ImportBiome     (Operator)
    #   ImportAsset     (Operator)

    category_list = {}

    for asset in asset_list:
        if asset['category'] not in category_list:              # rebuild the dictionary to sort assets
            category_list[str(asset['category'])] = []          # by category.
            category_list[str(asset['category'])].append(asset)    # then add the asset to the dictionary
        else:
            category_list[str(asset['category'])][len(category_list[str(asset['category'])])] = asset

    # category_list = json.loads(thumb_list)
    for category in category_list:

        cat_col, lod0_col, lod1_col, lod2_col, lod3_col, proxy_col = setup_lod_collection(biome_name, category, strew_collection)

        # assign collections to biome
        assign_collection(biome_nodes, lod0_col, lod1_col, lod2_col, lod3_col, proxy_col, category)

        for asset in category_list[category]:
            if asset['type'] == "Object":
                StrewFunctions.import_asset(self, context, asset['file'], asset['name'], asset['type'], proxy_col)
                obj = bpy.data.objects[asset['name']]
                lod0_col.objects.link(obj)
                lod1_col.objects.link(obj)
                lod2_col.objects.link(obj)
                lod3_col.objects.link(obj)
            if asset['type'] == "Collection":
                for number, lod in enumerate(asset['objects']):
                    lod_number = list(asset['objects'].keys())[number]
                    asset_name = asset['objects'][lod]
                    lod_coll = bpy.data.collections[biome_name + "_" + category + "_" + lod_number]
                    print(lod_coll)
                    StrewFunctions.import_asset(self, context, asset['file'], asset_name, "Object", lod_coll)


def setup_lod_collection(biome_name, category, strew_collection):

    category_coll = bpy.data.collections.new(str(biome_name + "_" + category))
    strew_collection.children.link(category_coll)

    lod_0_collection = bpy.data.collections.new(str(biome_name + "_" + category + "_LOD_0"))
    category_coll.children.link(lod_0_collection)

    lod_1_collection = bpy.data.collections.new(str(biome_name + "_" + category + "_LOD_1"))
    category_coll.children.link(lod_1_collection)

    lod_2_collection = bpy.data.collections.new(str(biome_name + "_" + category + "_LOD_2"))
    category_coll.children.link(lod_2_collection)

    lod_3_collection = bpy.data.collections.new(str(biome_name + "_" + category + "_LOD_3"))
    category_coll.children.link(lod_3_collection)

    proxy_collection = bpy.data.collections.new(str(biome_name + "_" + category + "_PROXY"))
    category_coll.children.link(proxy_collection)

    return category_coll, \
           lod_0_collection, \
           lod_1_collection, \
           lod_2_collection, \
           lod_3_collection, \
           proxy_collection


def apply_geometry_nodes(terrain_object):

    Mesh = bpy.data.meshes.new(terrain_object.name+"_terrain")
    biome = bpy.data.objects.new("StrewBiome", Mesh)
    bpy.data.collections[StrewFunctions.strew_collection_biomes].objects.link(biome)
    geometry_node_master = StrewFunctions.geometry_node_master
    if StrewFunctions.terrain_property in terrain_object:         # checks if object has terrain property
        print("object already a terrain. replace current biome?")
    else:
        modifier = biome.modifiers.new
        strew_terrain = modifier(name='Strew_Terrain', type='NODES')
        strew_biome = bpy.data.node_groups[geometry_node_master].copy()
        strew_terrain.node_group = strew_biome
        terrain_object["Strew_Terrain_Type"] = 1        # assign terrain property to object
        strew_biome.nodes["Object Info.008"].inputs[0].default_value = terrain_object

    return strew_biome


def assign_collection(biome, lod0_col, lod1_col, lod2_col, lod3_col, proxy_col, asset_type):
    rocks_node = biome.nodes['Group.010']               # get rocks nodes
    trees_node = biome.nodes['Group.012']               # get trees nodes
    grass_node = biome.nodes['Group.013']               # get grass nodes
    settings_node = biome.nodes['Group.011']            # get settings nodes

    if asset_type == 'rocks':
        rocks_node.inputs[17].default_value = False          # enable rocks in rocks_node
        settings_node.inputs[11].default_value = False       # enable rocks in biome
        rocks_node.inputs[25].default_value = True           # Enable Use collection
        rocks_node.inputs[26].default_value = proxy_col     # assign collection to field
        rocks_node.inputs[27].default_value = lod0_col     # assign collection to field
        rocks_node.inputs[28].default_value = lod1_col     # assign collection to field
        rocks_node.inputs[29].default_value = lod2_col     # assign collection to field
        rocks_node.inputs[30].default_value = lod3_col     # assign collection to field
        return
    if asset_type == 'trees':
        settings_node.inputs[12].default_value = False       # enable trees in biome
        trees_node.inputs[25].default_value = True           # Enable Use collection
        trees_node.inputs[26].default_value = proxy_col  # assign collection to field
        trees_node.inputs[27].default_value = lod0_col  # assign collection to field
        trees_node.inputs[28].default_value = lod1_col  # assign collection to field
        trees_node.inputs[29].default_value = lod2_col  # assign collection to field
        trees_node.inputs[30].default_value = lod3_col  # assign collection to field
        return
    if asset_type == 'grass':
        grass_node.inputs[25].default_value = True           # Enable Use collection
        grass_node.inputs[26].default_value = proxy_col  # assign collection to field
        grass_node.inputs[27].default_value = lod0_col  # assign collection to field
        grass_node.inputs[28].default_value = lod1_col  # assign collection to field
        grass_node.inputs[29].default_value = lod2_col  # assign collection to field
        grass_node.inputs[30].default_value = lod3_col  # assign collection to field
        return


classes = [
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
