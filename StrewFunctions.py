from . import __init__, StrewProps, StrewUi, StrewBiomeFunctions
import bpy
import os
import json

# variables
biome_file = 'biomes.json'
layout_file = "StrewLayout.blend"
preset_file = "Biomes.json"
source_file = "SourceFilesList.json"
blend_folder = "blend files\\"
preset_folder = "preset files\\"
custom_folder = "custom assets\\"
strew_collection_master = 'Strew'
strew_collection_assets = 'Strew_Biomes_Assets'
strew_collection_biomes = 'Strew_Biomes'
strew_compositor_scene = 'Strew_BiomeCompositor'
strew_compositor_workspace = 'Strew_Compositor'
geometry_node_master = "Geometry Nodes.005"
terrain_property = "Strew_Terrain_Name"
local_folder_path = "%STREW%"
preset_list_enum = []
sources_list_enum = []
imported_list_enum = []
libraries_target_enum = []
strew_folder = os.path.basename(os.path.dirname(__file__))
strew_path = os.path.dirname(__file__)

#####################################################################################
#
#       GET VARIABLES
#
#####################################################################################


def get_path(self, context, path):
    filepath = context.preferences.addons[strew_folder].preferences.filepath

    if not filepath.endswith("\\"):
        filepath = filepath + "\\"
    blends = filepath + blend_folder
    presets = filepath + preset_folder
    if path == 'blend':
        return blends
    if path == 'preset':
        return presets
    if path == 'strew':
        return filepath
    if path == 'preset_file':
        return presets + preset_file
    if path == 'custom_file':
        return filepath + custom_folder


def selected_biome(context):
    biome_name = context.scene.StrewPresetDrop.StrewPresetDropdown
    return biome_name


def selected_source(form):
    # CALLED FROM:
    #   AddAssetManager                         (Operator)
    #   SCENE_OT_source_populate                (Operator)

    if form == "name":
        source_name = bpy.context.scene.StrewSourceDrop.StrewSourceDropdown
    elif form == "id":
        source_name = bpy.context.scene.StrewSourceDrop['StrewSourceDropdown']
    else:       # Should not happen
        source_name = bpy.context.scene.StrewSourceDrop.StrewSourceDropdown

    return source_name


#####################################################################################
#
#       SETUP
#
#####################################################################################


def setup_collections():
    collections = bpy.data.collections

    if strew_collection_master not in collections:                                          # look for master collection
        master_collection = collections.new(strew_collection_master)                        # and creates it if it does
        bpy.context.scene.collection.children.link(master_collection)                       # not exist.
    else:
        master_collection = collections[strew_collection_master]

    if strew_collection_assets not in collections:
        assets_collection = collections.new(strew_collection_assets)                        # look for assets collection
        master_collection.children.link(assets_collection)                                  # and creates it if it does
    else:                                                                                   # not exist.
        assets_collection = collections[strew_collection_assets]

    if strew_collection_biomes not in collections:
        custom_assets_collection = collections.new(strew_collection_biomes)          # look for custom collection
        master_collection.children.link(custom_assets_collection)                           # and creates it if it does
    else:                                                                                   # not exist.
        custom_assets_collection = collections[strew_collection_biomes]

    master_collection_layer = bpy.context.view_layer.layer_collection.children[strew_collection_master]
    master_collection_layer.children[strew_collection_assets].exclude = True                      # disable collections

    return assets_collection


def setup_scenes(self, context):
    blend_file = get_path(self, context, 'blend') + layout_file

    if strew_compositor_scene not in bpy.data.scenes:
        bpy.ops.wm.append(
            filepath=os.path.join(blend_file + "\\Scene\\" + strew_compositor_scene),
            directory=os.path.join(blend_file + "\\Scene\\"),
            filename=strew_compositor_scene
        )


def setup_workspace(self, context):
    blend_file = get_path(self, context, 'blend') + layout_file

    if strew_compositor_workspace not in bpy.data.workspaces:
        bpy.ops.wm.append(
            filepath=os.path.join(blend_file + "\\WorkSpace\\" + strew_compositor_workspace),
            directory=os.path.join(blend_file + "\\WorkSpace\\"),
            filename=strew_compositor_workspace
        )


def import_geometry_nodes(self, context):
    blend_file = get_path(self, context, 'blend') + layout_file

    if geometry_node_master not in bpy.data.node_groups:
        bpy.ops.wm.append(
            filepath=os.path.join(blend_file + "\\NodeTree\\" + geometry_node_master),
            directory=os.path.join(blend_file + "\\NodeTree\\"),
            filename=geometry_node_master
        )


#####################################################################################
#
#       GET LISTS OF ASSETS AND BIOMES
#
#####################################################################################


def get_biomes_list(self, context):
    global blend_folder
    global preset_folder

    preset_folder_path = get_path(self, context, 'preset')

    biomes_list = []
    with open(preset_folder_path+biome_file, 'r') as json_file:
        biomes = json.load(json_file)
        for biome_name in biomes:
            biomes_list.append(biome_name)
    return biomes_list


def get_enum_biomes(self, context):
    global biome_file

    preset_folder_path = get_path(self, context, 'preset')

    biomes_enum = []
    with open(preset_folder_path+biome_file, 'r') as json_file:
        biomes = json.load(json_file)
        number = 0
        for biome in biomes:
            for biome_data in biomes[biome]:
                biome_infos = (
                    biome_data['identifier'],
                    biome_data['name'],
                    biome_data['description'],
                    number
                )
                biomes_enum.append(biome_infos)
                number += 1
    return biomes_enum


def get_source_files(self, context):
    global source_file
    sources_enum = []
    preset_folder_path = get_path(self, context, 'preset')

    with open(preset_folder_path + source_file, 'r') as json_file:
        source = json.load(json_file)
        number = 0
        for source_data in source:
            for data in source[source_data]:
                source_infos = (
                    data['identifier'],
                    data['name'],
                    data['description'],
                    number
                )
                sources_enum.append(source_infos)
                number += 1
        return sources_enum


def get_sources_assets(self, context, source_name):
    # CALLED FROM:
    #   SCENE_OT_source_populate    (Operator)

    # RETURNS:
    # Asset{ "file", "type", "name", "description", "category", "objects"}

    global biome_file
    assets_list = []
    preset_folder_path = get_path(self, context, 'preset')

    with open(preset_folder_path + source_file, 'r') as json_file:
        sources = json.load(json_file)

        if source_name in sources:
            for data in sources[source_name]:
                for Asset in data['assets']:
                    assets_list.append(Asset)
        else:
            print("STREW_WARNING: Could not find " + source_name + " in sources file:\n", sources)

    return assets_list


def get_assets_list(self, context, biome_name):
    # CALLED FROM:
    #   SCENE_OT_list_populate      (Operator)
    #   ImportBiome                 (Operator)
    #   ImportAsset                 (Operator)

    global biome_file
    assets_list = []
    preset_folder_path = get_path(self, context, 'preset')

    with open(preset_folder_path+biome_file, 'r') as json_file:
        biomes = json.load(json_file)

        for data in biomes[biome_name]:
            for Asset in data['assets']:
                assets_list.append(Asset)

    return assets_list


def get_assets_enum(self, context, biome_name):
    # CALLED FROM:
    #   StrewProps.enum                 (function for EnumProperty)
    global biome_file
    assets_enum = []
    preset_folder_path = get_path(self, context, 'preset')

    with open(preset_folder_path+biome_file, 'r') as json_file:
        biomes = json.load(json_file)

        for data in biomes[biome_name]:
            for Asset in data['assets']:
                asset_infos = (
                    Asset['file']+"\\"+Asset['name'],
                    Asset['name'],
                    Asset['description']
                )
                assets_enum.append(asset_infos)

    return assets_enum


#####################################################################################
#
#       ADD OR REMOVE BIOMES
#
#####################################################################################


def new_biome(self, context, target, name, description):
    # CALLED FROM:
    #   AddBiomePopup   (Operator)

    preset_folder_path = get_path(self, context, 'preset')      # get the path of file
    if target == "library":
        file = source_file
    else:
        file = biome_file

    if '"' in str(name):                                        # Ensures there is no hook in name
        name = str(name).replace('"', "'")
    if '"' in str(description):                                 # Ensures there is no hook in description
        description = str(description).replace('"', "'")

    with open(preset_folder_path + file, 'r') as json_file:   # Read the biomes file to build list
        biomes = json.load(json_file)

    if name in biomes:                                      # prevents overriding existing biome
        print("Biome with this name already exists")        # TODO: should inform user
        pass
    else:
        biomes[name] = []                                   # build list that will be sent to json
        biomes[name].append({
            "name": name,
            "identifier": name,
            "description": description,
            "assets": []
        })

    with open(preset_folder_path + file, 'w') as json_file:   # rewrite the file
        json.dump(biomes, json_file, indent=4)


def clone_biome(self, context, original_biome, name, description):
    global biome_file                                                   # get the name of file
    preset_folder_path = get_path(self, context, 'preset')              # get the path of file

    if '"' in str(name):                                        # Ensures there is no hook in name
        name = str(name).replace('"', "'")
    if '"' in str(description):                                 # Ensures there is no hook in description
        description = str(description).replace('"', "'")

    with open(preset_folder_path + biome_file, 'r') as json_file:  # Read the biomes file
        biomes = json.load(json_file)                              # return the file as list

    biomes[name] = biomes[original_biome]                          # Clone existing biome
    for data in biomes[name]:
        data['name'] = name
        data['description'] = description
        data['identifier'] = name

    with open(preset_folder_path + biome_file, 'w') as json_file:  # rewrite the file
        json.dump(biomes, json_file, indent=4)


def remove_biome(self, context, target, name):
    preset_folder_path = get_path(self, context, 'preset')          # get the path of file

    if target == "library":
        file = source_file
    else:
        file = biome_file

    with open(preset_folder_path + file, 'r') as json_file:   # Read the biomes file to build list
        biomes = json.load(json_file)

    del biomes[name]                                                # delete the biome

    with open(preset_folder_path + file, 'w') as json_file:   # rewrite the file
        json.dump(biomes, json_file, indent=4)


def rename_biome(self, context, target, initial_name, new_name, new_description):
    preset_folder_path = get_path(self, context, 'preset')          # get the path of file

    if target == "library":
        file = source_file
    else:
        file = biome_file

    name = str(new_name).replace('"', "'")                          # Ensures there is no hook in name
    description = str(new_description).replace('"', "'")            # Ensures there is no hook in description

    with open(preset_folder_path + file, 'r') as json_file:   # Read the biomes file to build list
        biomes = json.load(json_file)

    biomes[name] = biomes.pop(initial_name)                         # Clone old biome and delete it

    for data in biomes[name]:                                       # update infos
        data['description'] = description
        data['name'] = name
        data['identifier'] = name

    with open(preset_folder_path + file, 'w') as json_file:   # rewrite the file
        json.dump(biomes, json_file, indent=4)


def check_existence(self, context, target, name):

    if target == "library":
        libraries = get_source_files(self, context)
        for library in libraries:
            if name == library[1]:
                return True
    elif target == "biome":
        if name in get_biomes_list(self, context):
            return True
    elif target == "asset":
        for library in get_source_files(self, context):

            for asset in get_sources_assets(self, context, library[0]):
                print(asset['name'])
                print(name)
                if name == asset['name']:
                    return True

    return False

#####################################################################################
#
#       ADD OR REMOVE ASSETS
#
#####################################################################################


def add_asset(self, context, target, biome_name, asset_file, asset_name, asset_type, asset_description, asset_group, asset_category, asset_objects):
    # CALLED FROM:
    #   AddAssetManager                 (Operator)
    #   AddAssetView                    (Operator)
    #   SaveAsset                       (Operator)

    preset_folder_path = get_path(self, context, 'preset')              # get the path of file

    if '"' in asset_name:                                                # prevents " in the file
        asset_name = asset_name.replace("\"", "_")                      # as it will cause problems
    if target == "source":
        with open(preset_folder_path + source_file, 'r') as json_file:       # Read the biomes file to build list
            biomes = json.load(json_file)
    elif target == "biome":
        with open(preset_folder_path + biome_file, 'r') as json_file:       # Read the biomes file to build list
            biomes = json.load(json_file)

    for data in biomes[biome_name]:                                     # add the asset to the list
        data['assets'].append({
            "file": asset_file,
            "name": asset_name,
            "type": asset_type,
            "description": asset_description,
            "category": asset_category,
            "group": asset_group,
            "objects": json.loads(asset_objects.replace("'", "\""))
        })

    if target == "source":
        with open(preset_folder_path + source_file, 'w') as json_file:       # rewrite the file
            json.dump(biomes, json_file, indent=4)
    else:
        with open(preset_folder_path + biome_file, 'w') as json_file:  # rewrite the file
            json.dump(biomes, json_file, indent=4)


def remove_asset_id(self, context, target, biome_name, asset_id):
    # CALLED FROM:
    #   RemoveAssetManager   (Operator)
    #   EditAsset            (Operator)

    global biome_file                                                   # get the name of file
    preset_folder_path = get_path(self, context, 'preset')              # get the path of file

    if target == "source":
        with open(preset_folder_path + source_file, 'r') as json_file:       # Read the biomes file to build list
            biomes = json.load(json_file)
    elif target == "biome":
        with open(preset_folder_path + biome_file, 'r') as json_file:       # Read the biomes file to build list
            biomes = json.load(json_file)

    for data in biomes[biome_name]:                                     # remove the asset from the list
        del data['assets'][asset_id]

    if target == "source":
        with open(preset_folder_path + source_file, 'w') as json_file:  # rewrite the file
            json.dump(biomes, json_file, indent=4)
    else:
        with open(preset_folder_path + biome_file, 'w') as json_file:  # rewrite the file
            json.dump(biomes, json_file, indent=4)


def remove_asset(self, context, target, biome_name, asset_name, asset_file):
    # CALLED FROM:
    #   RemoveAssetView   (Operator)

    global biome_file                                                   # get the name of file
    preset_folder_path = get_path(self, context, 'preset')              # get the path of file

    if target == "source":
        with open(preset_folder_path + source_file, 'r') as json_file:       # Read the biomes file to build list
            biomes = json.load(json_file)
    elif target == "biome":
        with open(preset_folder_path + biome_file, 'r') as json_file:       # Read the biomes file to build list
            biomes = json.load(json_file)

    for data in biomes[biome_name]:                                     # remove the asset from the list
        for asset in data['assets']:
            if asset['name'] == asset_name:
                if asset['file'] == asset_file:
                    del asset

    if target == "source":
        with open(preset_folder_path + source_file, 'w') as json_file:       # rewrite the file
            json.dump(biomes, json_file, indent=4)
    else:
        with open(preset_folder_path + biome_file, 'w') as json_file:  # rewrite the file
            json.dump(biomes, json_file, indent=4)


def export_asset(self, context, assets, asset_name):
    # CALLED FROM:
    #   format_asset    (Function)

    path = get_path(self, context, 'custom_file')                                                      # find the blend target

    bpy.data.libraries.write(f'{path}{asset_name}.blend', assets, fake_user=True)                         # export to blend


def format_asset(self, context, asset):
    # CALLED FROM:
    #   SaveAsset   (Operator)

    if asset.asset_type:
        asset_type = "Collection"
        objects_list = {"LOD_0": asset.lod_0.name, "LOD_1": asset.lod_1.name, "LOD_2": asset.lod_2.name,
                        "LOD_3": asset.lod_3.name, "PROXY": asset.proxy.name}
        assets = {asset.lod_0, asset.lod_1, asset.lod_2, asset.lod_3, asset.proxy}
    else:
        asset_type = "Object"
        objects_list = {"LOD_0": "", "LOD_1": "", "LOD_2": "", "LOD_3": "", "PROXY": asset.proxy.name}
        assets = {asset.proxy}

    if asset.globalsave:
        filepath = "%CUSTOM%" + asset.asset_name + ".blend"
        export_asset(self, context, assets, asset.asset_name)  # does the exportation to file
    else:
        if bpy.data.filepath == "":
            print("can't create asset from unsaved blend. Asset will be save globally")
            filepath = "%CUSTOM%" + asset.asset_name + ".blend"
            export_asset(self, context, assets, asset.asset_name)
        else:
            filepath = bpy.data.filepath

    return asset_type, objects_list, filepath


def format_edit_asset(self, context, asset):
    # CALLED FROM:
    #   SaveAsset   (Operator)

    if asset.asset_type:
        asset_type = "Collection"
        objects_list = {"LOD_0": asset.lod_0, "LOD_1": asset.lod_1, "LOD_2": asset.lod_2,
                        "LOD_3": asset.lod_3, "PROXY": asset.proxy}
        assets = {asset.lod_0, asset.lod_1, asset.lod_2, asset.lod_3, asset.proxy}
    else:
        asset_type = "Object"
        objects_list = "{}"

    return asset_type, objects_list

#####################################################################################
#
#       IMPORT ASSETS AND COLLECTIONS
#
#####################################################################################


def set_active_collection(parent_collection, target_collection):
    for collection in parent_collection.children:
        if collection.name == target_collection.name:
            bpy.context.view_layer.active_layer_collection = collection
            return
        elif len(collection.children):
            set_active_collection(collection, target_collection)
            pass
    return


def import_asset(self, context, asset_path, asset_name, asset_type, target_collection):
    # CALLED FROM:
    #   ImportBiome                 (Operator)
    #   ImportAsset                 (Operator)
    #   setup_biome_collection      (Function)

    if asset_name in target_collection.all_objects:                     # check if object exists
        print("Object with this name already exists.")
        return
    else:                                                               # select target collection
        if '%STREW%' in asset_path:                                     # get real path of asset
            asset_path = asset_path.replace('%STREW%', get_path(self, context, 'blend'))
        elif '%CUSTOM%' in asset_path:                                     # get real path of asset
            asset_path = asset_path.replace('%CUSTOM%', get_path(self, context, 'custom_file'))

        set_active_collection(bpy.context.view_layer.layer_collection, target_collection)

        asset = bpy.ops.wm.append(                                              # import asset
            filepath=os.path.join(asset_path + f"\\{asset_type}\\" + asset_name),
            directory=os.path.join(asset_path + f"\\{asset_type}\\"),
            filename=asset_name
        )
        StrewBiomeFunctions.imported_assets_list[target_collection.name+"\\"+asset_name] = bpy.context.selected_objects[-1].name

#####################################################################################
#
#       REGISTER AND UNREGISTER
#
#####################################################################################


classes = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
