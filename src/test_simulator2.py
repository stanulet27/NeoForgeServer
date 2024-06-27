import part_material as p
import utilities as u
from jax_fem.generate_mesh import get_meshio_cell_type,box_mesh,Mesh
import numpy as np
import logging
import warnings
from vtk_plotting import create_gif

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
                           num_segments: int=1
                        ) -> 'dict[str,object]':
        
        data_dir = u.setup_data_dir()
        mesh = u.setup_starting_mesh(data_dir)
        vertices = list(np.reshape(mesh.points,(-1)))
        new_vertices = u.translate_vector(quaternion, translation_vector, vertices)
        mesh.points = np.reshape(new_vertices,(-1,3))

        simulation,num_steps = u.get_rectangular_hit_sim([1,1],[-x for x in translation_vector[:2]],force,mesh,data_dir)

        #logging.disable(logging.CRITICAL)
        warnings.filterwarnings("ignore",message="Optimal rotation is not uniquely or poorly defined for the given sets of vectors.")
        for i in range(num_steps):
            print(f"STEP {i+1} OF {num_steps}")
            #start = time.time()
            simulation.update()
            #print(f"Update: {time.time()-start}")

            #print(simulation.presses[0].points)
            #print(simulation.presses[1].points)
            if simulation.res_vals[-1] > 1:
                print("SIMULATION BLEW UP")
                print(f"RES VAL: {simulation.res_vals[-1]}")
                break
        
        sol_vertices = list(np.reshape(mesh.points+simulation.sol_list[0],(-1)))

        create_gif(data_dir,data_dir)
        create_gif(data_dir,data_dir,name="animation2.gif",negative=True)

        return {"Vertices": sol_vertices, "Triangles": self.mesh_data['Triangles'], "Steps": num_segments}
    
