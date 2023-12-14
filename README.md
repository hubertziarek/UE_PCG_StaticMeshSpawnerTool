# UE_PCG_StaticMeshSpawnerTool
Tool for Unreal Engine 5.3 created to support adding Static Mesh Spawner's entries to the PCG graph.
It allows you to select meshes in the World Editor Window, then add them to the list, set the required weights, and add them at once to the Static Mesh Spawner node. The node might be chosen from the existing ones or created a completely new one.

The tool was created with
- Python (core of the logic)
- C++ (definition of the custom structure)
- UE Blueprints (design and display windows of the tool widget).

NOTE: It works only with the PCGMeshSelectorWeighted type of the Static Mesh Spawner.
