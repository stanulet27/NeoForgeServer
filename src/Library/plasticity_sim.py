import jax.numpy as np
from jax_fem.solver import solver
from jax_fem.utils import save_sol
import os
import time

class PlasticitySim:
    def __init__(self,problem,presses,data_dir):
        self.problem = problem
        self.presses = presses
        self.data_dir = data_dir
        self.sol_list = [np.zeros_like(problem.mesh[0].points)]
        self.prev_sol_list = [np.copy(self.sol_list[0])]
        self.res_vals = []
        self.avg_stresses = []
        self.step = 0

    def get_dirichlet_bc_info_and_predicted_displacements(self):
        mesh_points = self.problem.mesh[0].points
        predicted_displacements = np.zeros_like(mesh_points)
        location_functions=[];vecs=[];value_functions=[]
        for press in self.presses:
            checks,displacements = press.get_checks_and_displacements(self.problem,self.sol_list,self.prev_sol_list)

            press_dirichlet_bc_info = press.get_dirichlet_bc_info(mesh_points,checks,self.sol_list[0]+displacements)
            location_functions += press_dirichlet_bc_info[0]
            vecs += press_dirichlet_bc_info[1]
            value_functions += press_dirichlet_bc_info[2]

            predicted_displacements += displacements

        return [location_functions,vecs,value_functions],predicted_displacements

    def run_simulation_step(self,problem,dirichlet_bc_info,initial_guess,save_path=False):
        problem.fe.update_Dirichlet_boundary_conditions(dirichlet_bc_info)
        sol_list,res_val = solver(problem,initial_guess=initial_guess)
        #problem.update_stress_strain(sol_list[0])
        avg_stress = problem.compute_avg_stress()
        if save_path: save_sol(problem.fe,sol_list[0],save_path)
        return problem,sol_list,res_val,avg_stress
    
    def update(self,dirichlet_bc_info=False,predicted_displacements=False):
        save_path = os.path.join(self.data_dir,f'u_{self.step+1:03d}.vtu')

        start1 = time.time()
        if not dirichlet_bc_info:
            dirichlet_bc_info,predicted_displacements = self.get_dirichlet_bc_info_and_predicted_displacements()
        print(f"DirichletBCInfo: {time.time()-start1}")

        initial_guess = [self.sol_list[0]+predicted_displacements]

        start2 = time.time()
        problem,sol_list,res_val,avg_stress = self.run_simulation_step(self.problem,dirichlet_bc_info,initial_guess,save_path)
        print(f"Simulation: {time.time()-start2}")
        
        if res_val <= 1:
            self.problem = problem
            self.prev_sol_list = self.sol_list
            self.sol_list = sol_list
            for press in self.presses:
                press.update()
            self.step += 1

            #print("SOL_LIST")
            #print(np.sum(abs(sol_list[0])))
        
        self.res_vals.append(res_val)
        self.avg_stresses.append(avg_stress)

