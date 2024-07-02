from NeoForgeServer.src.Library.press import Press

import jax.numpy as np

class Table (Press):
    # TODO: fix edge case for concave meshes
    def get_checks_and_displacements(self,problem,sol_list,prev_sol_list):
        sol_points = problem.mesh[0].points + sol_list[0]
        combined_checks = np.array(sol_points[:,2] <= self.points[0][2]+1e-5)
        combined_displacements = np.zeros_like(sol_list[0])
        combined_displacements = combined_displacements.at[combined_checks,2].set(self.points[0][2] - sol_points[combined_checks,2])

        # print("TABLE")
        # print("COMBINED_CHECKS")
        # print(combined_checks.shape)
        # print(np.sum(combined_checks))
        # print("COMBINED_DISPLACEMENTS")
        # print(combined_displacements.shape)
        # print(combined_displacements[combined_checks])

        return combined_checks,combined_displacements