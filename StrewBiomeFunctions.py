import bpy
from . import StrewUi, StrewManOperators, __init__, StrewProps, StrewFunctions
import json

active_biome = ""
imported_assets_property = "Strew_Imported_Assets"
imported_assets_list = {}
imported_biomes_property = "Strew_Imported_Biomes"

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
            category_list[asset['category']] = []               # creates category if not present

        category_list[asset['category']].append(asset)          # then add the asset to the category

    for category in category_list:

        cat_col, lod0_col, lod1_col, lod2_col, lod3_col, proxy_col = setup_lod_collection(biome_name, category, strew_collection)

        # assign collections to biome
        assign_collection(biome_nodes, lod0_col, lod1_col, lod2_col, lod3_col, proxy_col, category)

        for asset in category_list[category]:
            if asset['type'] == "Object":
                StrewFunctions.import_asset(self, context, asset['file'], asset['name'], asset['type'], proxy_col)
                asset_object = bpy.data.objects[asset["objects"]['PROXY']]
                lod0_col.objects.link(asset_object)
                lod1_col.objects.link(asset_object)
                lod2_col.objects.link(asset_object)
                lod3_col.objects.link(asset_object)

            if asset['type'] == "Collection":
                for number, lod in enumerate(asset['objects']):
                    lod_number = list(asset['objects'].keys())[number]
                    asset_name = asset['objects'][lod]
                    lod_coll = bpy.data.collections[biome_name + "_" + category + "_" + lod_number]

                    StrewFunctions.import_asset(self, context, asset['file'], asset_name, "Object", lod_coll)


def setup_lod_collection(biome_name, category, strew_collection):
    # CALLED FROM:
    #   ImportBiome     (Operator)

    category_coll = bpy.data.collections.new(str(biome_name + "_" + category))
    strew_collection.children.link(category_coll)

    lod_0 = bpy.data.collections.new(str(biome_name + "_" + category + "_LOD_0"))
    category_coll.children.link(lod_0)

    lod_1 = bpy.data.collections.new(str(biome_name + "_" + category + "_LOD_1"))
    category_coll.children.link(lod_1)

    lod_2 = bpy.data.collections.new(str(biome_name + "_" + category + "_LOD_2"))
    category_coll.children.link(lod_2)

    lod_3 = bpy.data.collections.new(str(biome_name + "_" + category + "_LOD_3"))
    category_coll.children.link(lod_3)

    proxy = bpy.data.collections.new(str(biome_name + "_" + category + "_PROXY"))
    category_coll.children.link(proxy)

    return category_coll, lod_0, lod_1, lod_2, lod_3, proxy


def create_biome_object(biome_name, is_imported):
    # CALLED FROM:
    #   apply_geometry_nodes     (Function)

    # Checks if biome has been previously imported or not. returns the biome fully configured

    if is_imported:
        strew_biome = bpy.data.node_groups[biome_name]                                      # get imported biome
        biome = bpy.data.objects[biome_name]
    else:

        Mesh = bpy.data.meshes.new(biome_name + "_terrain")                                 # Create mesh
        biome = bpy.data.objects.new(biome_name, Mesh)                                      # Create object
        biome[StrewFunctions.terrain_property] = biome_name                                 # Apply properties
        bpy.data.collections[StrewFunctions.strew_collection_biomes].objects.link(biome)    # Link to scene
        biome.hide_select = True                                                            # make un-selectable
        geometry_node_master = StrewFunctions.geometry_node_master                          # get initial geo_node
        modifier = biome.modifiers.new                                                      # create modifier
        strew_terrain = modifier(name='Strew_Terrain', type='NODES')                        # configure modifier
        strew_biome = bpy.data.node_groups[geometry_node_master].copy()                     # create proper geo_node
        strew_biome.name = biome_name                                                       # rename geo_node
        strew_terrain.node_group = strew_biome                                              # apply geo_node to modifier

    return strew_biome, biome


def apply_geometry_nodes(terrain_object, biome_name, is_imported):
    # CALLED FROM:
    #   ImportBiome     (Operator)
    #   AssignBiome     (Operator)

    strew_biome, biome_object = create_biome_object(biome_name, is_imported)            # get biome object
    terrain_object[StrewFunctions.terrain_property] = biome_name                # add terrain property to terrain object
    new_object_node = add_object_node(strew_biome, terrain_object)                      # assign terrain object to biome
    strew_biome.nodes[new_object_node.name].inputs[0].default_value = terrain_object    # link the new node to join mesh

    return strew_biome, biome_object


def assign_collection(biome, lod0_col, lod1_col, lod2_col, lod3_col, proxy_col, asset_type):
    # CALLED FROM:
    #   setup_biome_collection  (Function)

    asset_node = biome.nodes[asset_type]               # get asset type nodes

    asset_node.inputs[17].default_value = False          # enable rocks in rocks_node
    asset_node.inputs[25].default_value = True           # Enable Use collection
    asset_node.inputs[26].default_value = proxy_col     # assign collection to field
    asset_node.inputs[27].default_value = lod0_col     # assign collection to field
    asset_node.inputs[28].default_value = lod1_col     # assign collection to field
    asset_node.inputs[29].default_value = lod2_col     # assign collection to field
    asset_node.inputs[30].default_value = lod3_col     # assign collection to field


def add_object_node(biome, terrain_object):

    # Setup Object Info node
    object_info_node = biome.nodes.new(type="GeometryNodeObjectInfo")
    object_info_node.name = "User_Terrain_" + terrain_object.name
    object_info_node.location = (-1075, 1150)
    object_info_node.transform_space = "RELATIVE"
    biome.nodes["Switch.028"].inputs[0].default_value = True

    # Connect object info node
    join_geometry_node = biome.nodes['Join Geometry.007']
    biome.links.new(object_info_node.outputs["Geometry"], join_geometry_node.inputs[0])

    return object_info_node


def desassign_biome(biome, terrain_object):
    # CALLED FROM:
    #   RemoveBiome     (Operator)

    node_tree = bpy.data.node_groups[biome]
    terrain_name_property = StrewFunctions.terrain_property

    if biome == terrain_object.name:
        print("can not remove biome from this object. please select terrain.")
        return
    node_tree.nodes.remove(node_tree.nodes["User_Terrain_" + terrain_object.name])
    node_tree.nodes["Switch.028"].inputs[0].default_value = False
    node_tree.nodes["Switch.028"].inputs[0].default_value = True

    terrain_object[terrain_name_property] = None

#####################################################################################
#
#       BIOME CREATOR SWITCH
#
#####################################################################################


def replace_biome_creator(biome, way):
    new_biome = bpy.data.node_groups[biome]

    if way == "in":
        bpy.data.objects["Strew_Compositor_Biome"].modifiers["Strew_Terrain"].node_group = new_biome
        new_biome.nodes["Switch.028"].inputs[0].default_value = False

    elif way == "out":
        new_biome.nodes["Switch.028"].inputs[0].default_value = True


def switch_active_biome(new_biome):
    global active_biome
    old_biome = active_biome
    if old_biome != "":
        replace_biome_creator(old_biome, 'out')
    replace_biome_creator(new_biome, 'in')

    active_biome = new_biome


#####################################################################################
#
#       LIST IMPORTED BIOMES
#
#####################################################################################


def is_biome_imported(biome_name):
    if bpy.context.scene.get(imported_biomes_property) is not None:
        imported = False
        imported_biomes = bpy.context.scene.get(imported_biomes_property).to_dict()

        for biome in imported_biomes:
            if biome_name == imported_biomes[biome][0]:
                imported = True
                return imported
        return imported
    else:
        return False


def imported_biome_list(biome_name):

    biome_list = {}
    for biome in StrewProps.preset_list_enum:
        if biome[0] == biome_name:
            biome_list[biome[0]] = biome[0], biome[1], biome[2]

    if bpy.context.scene.get(imported_biomes_property) is not None:
        imported_biomes = bpy.context.scene.get(imported_biomes_property).to_dict()
        for biome in imported_biomes:
            if biome not in biome_list:
                biome_list[biome] = imported_biomes[biome][0], imported_biomes[biome][1], imported_biomes[biome][2]
            else:
                return "already imported"

    bpy.context.scene[imported_biomes_property] = biome_list


def get_imported_biomes_list():
    biome_list = []

    for scene in bpy.data.scenes:
        if scene.get('Strew_Imported_Biomes') is not None:
            imported_biomes = scene.get('Strew_Imported_Biomes').to_dict()
            for biome in imported_biomes:
                biome_list.append((imported_biomes[biome][0], imported_biomes[biome][1], imported_biomes[biome][2]))

    return biome_list


def format_asset_list(asset_list, biome_name):
    # CALLED FROM:
    #   UpdateBiome     (Operator)

    # Reformats the assets list to match the imported list format

    formated_asset_list = {}

    for asset in asset_list:
        category = asset["category"]
        if asset["type"] == "Collection":
            for number, lod in enumerate(asset['objects']):
                lod_number = list(asset['objects'].keys())[number]
                asset_name = asset['objects'][lod]
                collection = biome_name + "_" + category + "_" + lod_number
                formated_asset_list[collection + "\\" + asset_name] = {'name': asset_name,
                                                    'file': asset['file'],
                                                    'type': asset['type'],
                                                    'coll': collection,
                                                    'fullname': collection + "\\" + asset_name}

        elif asset["type"] == "Object":
            lod = "PROXY"
            collection = biome_name + "_" + category + "_" + lod
            formated_asset_list[collection + "\\" + asset['name']] = {'name': asset['name'],
                                                   'file': asset['file'],
                                                   'type': asset['type'],
                                                   'coll': collection,
                                                   'fullname': collection + "\\" + asset['name']}

    return formated_asset_list


def is_asset_imported(asset, biome):
    # CALLED FROM:
    #   UpdateBiome     (Operator)

    # checks if submitted asset is imported or not.
    imported = False
    if biome.get(imported_assets_property) is not None:
        imported_list = biome.get(imported_assets_property).to_dict()

        for imported_asset in imported_list:
            if imported_asset == asset:
                imported = True
                return imported
        return imported
    else:
        objects_list_property(biome)


def is_asset_obsolete(asset_list, biome):
    # CALLED FROM:
    #   UpdateBiome     (Operator)

    # checks if submitted asset has to be removed or not.
    is_obsolete = True
    obsolete_assets = {}
    imported_list = biome.get(imported_assets_property).to_dict()

    for imported_asset in imported_list:
        for asset in asset_list:

            if imported_asset == asset_list[asset]:
                is_obsolete = False

        if is_obsolete:
            obsolete_assets[imported_asset] = imported_list[imported_asset]

    return obsolete_assets


def objects_list_property(biome, asset_list={}):
    # CALLED FROM:
    #   ImportBiome     (Operator)
    #   UpdateBiome     (Operator)

    is_obsolete = True

    if biome.get(imported_assets_property) is not None:                     # biome already imported
        imported_list = biome.get(imported_assets_property).to_dict()       # get list of imported assets
        for imported_asset in imported_list:                                # for each asset newly imported
            for asset in asset_list:
                if imported_asset == asset_list[asset]:
                    is_obsolete = False
            if not is_obsolete:
                imported_assets_list[imported_asset] = imported_assets[imported_asset]  # add it to list

    biome[imported_assets_property] = imported_assets_list                  # apply list to property
    imported_assets_list.clear()                                            # clear list


#####################################################################################
#
#       REGISTER AND UNREGISTER
#
#####################################################################################


classes = [
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
