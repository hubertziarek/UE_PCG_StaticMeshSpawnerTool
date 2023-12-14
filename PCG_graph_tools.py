import unreal
from pathlib import Path


def load_graph_from_selection():
    graph = unreal.EditorUtilityLibrary.get_selected_assets()
    
    for i in graph:
        if isinstance(i, unreal.PCGGraph):
            return unreal.PCGGraph.cast(i)
    
    return

#user can choose in the property view a graph that is part of default content, including subgraphs used as a default set of tool
#it's important to check if the user doesn't try to edit default content by mistake
def if_graph_belongs_to_default(path):
    p = Path(path)
    first_part = p.parts[1]
    if first_part == "PCG":
        return True
    else:
        return False

def get_static_mesh_spawner_list(graph):
    nodes = graph.get_editor_property("nodes")
    output_array = unreal.Array(unreal.NodeToChoose)
    number_of_elems = 0
        
    for n in nodes:
        title = n.get_editor_property("NodeTitle")

        #picking only static mesh spawners with weighted mode
        node_interface = n.get_editor_property("settings_interface")
        if isinstance(node_interface, unreal.PCGStaticMeshSpawnerSettings):
            static_mesh_spawner = unreal.PCGStaticMeshSpawnerSettings.cast(node_interface)
        else:
            continue 
        selector_type = static_mesh_spawner.get_editor_property("mesh_selector_parameters")   
        if isinstance(selector_type, unreal.PCGMeshSelectorWeighted):
            weighted = unreal.PCGMeshSelectorWeighted.cast(selector_type)
        else:
            continue

        path = unreal.SystemLibrary.get_path_name(weighted)
        path = path.split(":")[1]
        path = path.split(".")[0]
        index = int(path.split("_")[1])

        elem = unreal.NodeToChoose()
        elem.set_editor_property("Index", index)
        elem.set_editor_property("Reference", weighted)
        if title != "None":
            elem.set_editor_property("Title", title)
        else:
            elem.set_editor_property("Title", "Static Mesh Spawner")

        #append elem in order
        i = 0
        while (i < number_of_elems and
               index > output_array[i].get_editor_property("Index")):
            i = i + 1

        output_array.insert(i, elem)
        number_of_elems = number_of_elems + 1

    return output_array

def find_new_node_position(graph):
    nodes = graph.get_editor_property("nodes")
    left = 0
    right = 0
    top = 0
    bottom = 0
    
    for n in nodes:
        if n.get_node_position()[0] < left:
            left = n.get_node_position()[0]
        if n.get_node_position()[0] > right:
            right = n.get_node_position()[0]
        if n.get_node_position()[1] > top:
            top = n.get_node_position()[1]
        if n.get_node_position()[1] < bottom:
            bottom = n.get_node_position()[1]
    
    return (left, right, top, bottom)

def get_selected_meshes():
    actors = unreal.VRScoutingInteractor.get_selected_actors()
    output_array = unreal.Array(unreal.StaticMesh)

    for a in actors:
        if isinstance(a, unreal.StaticMeshActor):
            mesh_actor = unreal.StaticMeshActor.cast(a)
        else:
            continue
        
        mesh_component = mesh_actor.get_editor_property("static_mesh_component")
        mesh = mesh_component.get_editor_property("static_mesh")
        output_array.append(mesh)

    return output_array

def add_entries_to_new_spawner(weighted, list_entries):
    entries = weighted.get_editor_property("mesh_entries")
    
    for i in list_entries:

        mesh = i.get_editor_property("StaticMeshReference")
        weight = i.get_editor_property("WeightInput").get_value()
    
        descriptor = unreal.SoftISMComponentDescriptor()
        descriptor.set_editor_property("static_mesh", mesh)
        new_entry = unreal.PCGMeshSelectorWeightedEntry(weight)
        new_entry.set_editor_property("descriptor", descriptor)
        entries.append(new_entry)
        
    weighted.set_editor_property("mesh_entries", entries)

def add_new_node_to_graph(graph, option, x, y, list_entries):
    new_node_position = find_new_node_position(graph)

    (node, settings) = graph.add_node_of_type(unreal.PCGStaticMeshSpawnerSettings)
    settings.set_mesh_selector_type(unreal.PCGMeshSelectorWeighted)
    selector_type = settings.get_editor_property("mesh_selector_parameters")   

    if isinstance(selector_type, unreal.PCGMeshSelectorWeighted):
        weighted = unreal.PCGMeshSelectorWeighted.cast(selector_type)
    else:
        return

    #if the option is "custom" then x and y keep the values; differently, they need to be updated based on the option
    # selected by the user in the combo box
    if option == "center":
        x = 0
        y = 0
    if option == "top-left":
        x = new_node_position[0] - 20
        y = new_node_position[3] + 20
    if option == "top-right":
        x = new_node_position[1] + 20
        y = new_node_position[3] + 20
    if option == "bottom-left":
        x = new_node_position[0] - 20
        y = new_node_position[2] - 20
    if option == "bottom-right":
        x = new_node_position[1] + 20
        y = new_node_position[2] - 20

    node.set_node_position(x, y)

    add_entries_to_new_spawner(weighted, list_entries)
    
    #refresh editor to show the node
    asset_subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    asset_subsystem.close_all_editors_for_asset(graph)
    asset_subsystem.open_editor_for_assets([graph])

#combo box provides a selected option as a string; extracting and comparing data in Python is much easier than in blueprints
def find_weighted (option, nodes_to_choose):
    option = option.split(")")[0]
    index = int(option.split(":")[1])
    
    for n in nodes_to_choose:
        if n.get_editor_property("Index") == index:
            weighted = n.get_editor_property("Reference")
            return weighted

#the node could be removed in the meantime in the asset editor window but can still exist in memory,
#so it needs to be checked before attempting to add new meshes
def if_weighted_still_exist (graph, weighted_to_check):
    nodes = graph.get_editor_property("nodes")
        
    for n in nodes:
        node_interface = n.get_editor_property("settings_interface")
        if isinstance(node_interface, unreal.PCGStaticMeshSpawnerSettings):
            static_mesh_spawner = unreal.PCGStaticMeshSpawnerSettings.cast(node_interface)
        else:
            continue 
        selector_type = static_mesh_spawner.get_editor_property("mesh_selector_parameters")   
        if isinstance(selector_type, unreal.PCGMeshSelectorWeighted):
            weighted = unreal.PCGMeshSelectorWeighted.cast(selector_type)
        else:
            continue

        if weighted_to_check == weighted:
            return True

    return False


def add_entries_to_node(graph, option, nodes_to_choose, list_entries):
    weighted = find_weighted (option, nodes_to_choose)

    if not if_weighted_still_exist(graph, weighted):
        return False

    entries = weighted.get_editor_property("mesh_entries")
    new_entries = unreal.Array(unreal.PCGMeshSelectorWeightedEntry)
    
    for i in list_entries:
        mesh = i.get_editor_property("StaticMeshReference")
        weight = i.get_editor_property("WeightInput").get_value()
        
        skip_creating_entry = False
        #to avoid duplicates, if any mesh is on the mesh entries list, it's not added, but the weight is updated
        for entry in entries:
            descriptor = entry.get_editor_property("descriptor")
            if mesh == descriptor.get_editor_property("static_mesh"):
                entry.set_editor_property("weight", weight)
                new_entries.append(entry)
                skip_creating_entry = True
                break 
    
        if not skip_creating_entry:
            descriptor = unreal.SoftISMComponentDescriptor()
            descriptor.set_editor_property("static_mesh", mesh)
            new_entry = unreal.PCGMeshSelectorWeightedEntry(weight)
            new_entry.set_editor_property("descriptor", descriptor)
            new_entries.append(new_entry)
        
    weighted.set_editor_property("mesh_entries", new_entries)
    return True