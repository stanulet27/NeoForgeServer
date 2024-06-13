import part_material as p
import utilities as u

class SimulationHandler:
    def __init__(self, mesh_data: 'dict[str,object]', material: p.Material):
        self.mesh_data = mesh_data
        print(f"Setting material to {material.name}")
        self.material = material

    def return_material(self) -> 'dict[str,object]':
        return self.material.get_dict()
    
    def set_mesh(self, mesh_data: 'dict[str,object]'):
        self.mesh_data = mesh_data

    def get_result_mesh(self) -> 'dict[str,object]':
        return self.mesh_data
    
    def execute_simulation(self, 
                           hits: 'list[int]', 
                           force: float, 
                           quaternion:'list[float]' , 
                           translation_vector: 'list[float]', 
                           num_segments: int=5
                        ) -> 'dict[str,object]':
        steps = []
        # Apply translation and rotation
        vertices = self.mesh_data['Vertices']
        new_vertices = u.translate_vector(quaternion, translation_vector, vertices)
        # Break deformation into segments
        last_step = []
        for _ in range(num_segments):
            # Apply deformation
            last_step = u.multiply_vertices(new_vertices, hits, force/num_segments)
            steps.extend(u.untranslate_vector(quaternion, translation_vector, last_step))    
        #save new mesh
        self.mesh_data['Vertices'] = u.untranslate_vector(quaternion, translation_vector, last_step)
        #return new mesh data
        return {"Vertices": steps, "Triangles": self.mesh_data['Triangles'], "Steps": num_segments}
    
