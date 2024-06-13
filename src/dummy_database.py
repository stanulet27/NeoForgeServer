import part_material as p
import hammer as h
import json

class DBMS:
    def __init__(self):
        print('Database connection successful.')
        self.meshes = []

    def __del__(self):
        print('Database connection closed.')

    def get_material(self, material_id: int) -> p.Material:
        return p.Material("Test", 0.5)

    def get_start_mesh(self, mesh_id:int ) -> 'dict[str,object]':
        f = open("sample_mesh_definitions/mesh.json", "r")
        self.start_mesh = json.load(f)
        return self.start_mesh
        
    def get_target_mesh(self, mesh_id: int) -> 'dict[str,object]':
        f = open("sample_mesh_definitions/targetmesh.json", "r")
        return json.load(f)

    def get_hammer(self, hammer_id: int) -> 'dict[str,object]':
        hammer_object = h.Hammer("Hammer", 1 ,1)
        return hammer_object.get_dict()
        
    def record_action(self, position: 'list[int]', rotation: 'list[int]', result: 'dict[str,object]') -> bool:
        self.meshes.append(result)
        return True
        
    def start_series(self, start_mesh_id: int, target_mesh_id: int, material_id: int, hammer_id: int) -> bool:
        return True
        
    def end_series(self, score: float) -> bool:
        return True
    
    def undo_strike(self) -> 'dict[str,object]':
        for mesh in self.meshes:
            print(mesh['Vertices'])
        print(f"length at start is {len(self.meshes)}")
        if len(self.meshes) > 0:
            self.meshes.pop() 
            print(f"length at end is {len(self.meshes)}")
            if len(self.meshes) > 0:
                return self.meshes[-1]
        print("returning start mesh")
        f = open("sample_mesh_definitions/mesh.json", "r")
        return json.load(f)
    
