import jax.numpy as np
import numpy as onp

import shapely
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from skspatial.objects import Plane

from scipy.spatial.transform import Rotation

from Library.utils import get_value_function,get_location_function

class Press:
    # TODO: fix edge case for concave meshes
    def __init__(self,points,faces,displacement,vecs=[0,1,2]):
        self.points = np.array(points)
        self.faces = np.array(faces)
        self.displacement = np.array(displacement)
        self.vecs = vecs
    
    def get_checks_and_displacements(self,problem,sol_list,prev_sol_list):
        prob_points = problem.mesh[0].points
        prev_sol_points = prob_points+prev_sol_list[0]
        sol_points = prob_points+sol_list[0]

        prev_unchecked = onp.full(sol_points.shape[0], True)
        prev_sol_displacements = onp.zeros_like(sol_points)
        # for face in self.faces:
        #     prev_sol_points_tmp = prev_sol_points[prev_unchecked]
        #     sol_points_tmp = sol_points[prev_unchecked]
        #     checks = self.check_intersects(face,prev_sol_points_tmp,sol_points_tmp)
        #     #print("CHECKS1")
        #     #print(np.sum(checks))
        #     for i in np.argwhere(checks):
        #         checks = checks.at[i].set(self.check_contain(face,prev_sol_points_tmp[i][0],sol_points_tmp[i][0]-prev_sol_points_tmp[i][0]))
        #     #print("CHECKS1.1")
        #     #print(np.sum(checks))
        #     if checks.any():
        #         prev_sol_displacements_cpy = prev_sol_displacements[prev_unchecked]
        #         prev_sol_displacements_cpy[checks] = self.get_displacements(face,sol_points_tmp[checks])
        #         prev_sol_displacements[prev_unchecked] = prev_sol_displacements_cpy

        #         prev_unchecked_cpy = prev_unchecked[prev_unchecked]
        #         prev_unchecked_cpy[checks] = False
        #         prev_unchecked[prev_unchecked] = prev_unchecked_cpy

        #         #print("DISPS1")
        #         #print(np.sum(abs(prev_sol_displacements)))
        #         #print("PREV_UNCHECKED")
        #         #print(np.sum(prev_unchecked))
        prev_sol_displacements = np.array(prev_sol_displacements)

        mod_sol_points = sol_points+prev_sol_displacements

        unchecked = onp.full(sol_points.shape[0], True)
        sol_displacements = onp.zeros_like(sol_points)
        for face in self.faces:
            mod_sol_points_tmp = mod_sol_points[unchecked]
            checks = self.check_intersects(face,mod_sol_points_tmp,mod_sol_points_tmp-self.displacement)
            #print("CHECKS2")
            #print(np.sum(checks))
            if checks.any():
                checks = checks.at[checks].set(self.check_contains(face,mod_sol_points_tmp[checks],self.displacement))
                #print("CHECKS2.1")
                #print(np.sum(checks))
                if checks.any():
                    sol_displacements_cpy = sol_displacements[unchecked]
                    sol_displacements_cpy[checks] = self.get_displacements(face,mod_sol_points_tmp[checks]-self.displacement)
                    sol_displacements[unchecked] = sol_displacements_cpy

                    unchecked_cpy = unchecked[unchecked]
                    unchecked_cpy[checks] = False
                    unchecked[unchecked] = unchecked_cpy
                    
                    #print("DISPS2")
                    #print(np.sum(abs(sol_displacements)))
                    #print("UNCHECKED")
                    #print(np.sum(unchecked))
        sol_displacements = np.array(sol_displacements)

        combined_checks = np.invert(np.array([prev_unchecked,unchecked]).all(axis=0))
        # print("COMBINED_CHECKS")
        # print(combined_checks.shape)
        # print(np.sum(combined_checks))
        
        combined_displacements = prev_sol_displacements+sol_displacements
        # print("COMBINED_DISPLACEMENTS")
        # print(combined_displacements.shape)
        # print(combined_displacements[combined_checks])

        return combined_checks,combined_displacements

    def get_dirichlet_bc_info(self,points,checks,displacements):
        location_functions = [get_location_function(points,checks)]*len(self.vecs)
        value_functions = [get_value_function(points,displacements,vec) for vec in self.vecs]
        return [location_functions,self.vecs,value_functions]

    def get_displacements(self,face,disp_points):
        plane = self.get_plane(face)
        return np.array(plane.project_points(disp_points)-disp_points)

    def check_intersects(self,face,points,disp_points):
        plane = self.get_plane(face)
        dists = plane.distance_points_signed(points)
        disp_dists = plane.distance_points_signed(disp_points)
        sign_diffs = np.sign(dists) != np.sign(disp_dists)
        return np.array([sign_diffs,abs(dists)<1e-5,abs(disp_dists)<1e-5]).any(axis=0)

    def check_contain(self,face,point,displacement):
        rot,_ = Rotation.align_vectors([[0.,0.,1.]],[displacement])
        face_points = [self.points[i] for i in face]
        rot_face_points = rot.apply(face_points)
        rot_point = rot.apply(point)

        point_xy = Point(rot_point[0],rot_point[1])
        rf_points_xy = [(rf_point[0],rf_point[1]) for rf_point in rot_face_points]+[(rot_face_points[0][0],rot_face_points[0][1])]
        polygon_xy = Polygon(rf_points_xy)
        
        return np.array(polygon_xy.covers(point_xy))

    def check_contains(self,face,points,displacement):
        rot,_ = Rotation.align_vectors([[0.,0.,1.]],[displacement])
        face_points = [self.points[i] for i in face]
        rot_face_points = rot.apply(face_points)
        rot_points = rot.apply(points)

        points_xy = shapely.points([(rot_point[0],rot_point[1]) for rot_point in rot_points])
        rf_points_xy = [(rf_point[0],rf_point[1]) for rf_point in rot_face_points]+[(rot_face_points[0][0],rot_face_points[0][1])]
        polygon_xy = Polygon(rf_points_xy)
        
        return np.array(polygon_xy.covers(points_xy))

    def get_plane(self,face):
        return Plane.from_points(self.points[face[0]],self.points[face[1]],self.points[face[2]])
    
    def update_points(self,displacement=False):
        if displacement:
            self.points += np.array(displacement)
        else:
            self.points += self.displacement

    def update_displacement(self,displacement):
        self.displacement = np.array(displacement)

    def update(self):
        self.update_points()
