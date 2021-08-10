import bpy
from . import StrewUi, StrewManOperators, __init__, StrewProps, StrewFunctions


def apply_geometry_nodes():
    Target = bpy.context.active_object
    Mesh = bpy.data.meshes.new("StrewEmptyMesh")
    Biome = bpy.data.objects.new("StrewBiome", Mesh)
    bpy.context.scene.collection.objects.link(Biome)
    try:
        Target["Strew_Terrain_Type"]
    except:
        Modifier = Biome.modifiers.new
        Strew_Terrain = Modifier(name='Strew_Terrain', type='NODES')
        Strew_Terrain.node_group = bpy.data.node_groups[StrewFunctions.geometry_node_master]
        Target["Strew_Terrain_Type"] = 1
        bpy.data.node_groups["Geometry Nodes.005"].nodes["Object Info.008"].inputs[0].default_value = Target


classes = [

]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
