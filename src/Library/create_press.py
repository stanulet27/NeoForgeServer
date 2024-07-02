import jax.numpy as np

import shapely
from shapely.geometry.polygon import Polygon

from scipy.spatial.transform import Rotation
from scipy.linalg import norm

from NeoForgeServer.src.Library.press import Press
from NeoForgeServer.src.Library.table import Table

def create_flat_press(press_points,offset,displacement,mesh_points,vecs=[0,1,2],center=True,isTable=False):
    if center:
        press_points -= np.mean(press_points,axis=0)

    if displacement[2] >= 0:
        rot,_ = Rotation.align_vectors([[0.,0.,1.]],[displacement])
    else:
        rot,_ = Rotation.align_vectors([[0.,0.,-1.]],[displacement])

    rot_mesh_points = rot.apply(mesh_points)
    points_xy = shapely.points([(rm_point[0],rm_point[1]) for rm_point in rot_mesh_points])

    press_points += np.mean(rot_mesh_points,axis=0)+offset
    polygon_xy = Polygon([(press_point[0],press_point[1]) for press_point in press_points]+[(press_points[0][0],press_points[0][1])])

    if displacement[2] >= 0:
        press_points = press_points.at[:,2].set(min(rot_mesh_points[polygon_xy.covers(points_xy),2])-norm(displacement))
    else:
        press_points = press_points.at[:,2].set(max(rot_mesh_points[polygon_xy.covers(points_xy),2])+norm(displacement))

    final_press_points = rot.inv().apply(press_points)
    faces = np.array([range(len(final_press_points))])

    if isTable: return Table(final_press_points,faces,displacement,vecs)
    return Press(final_press_points,faces,displacement,vecs)

def create_flat_rect_press(size,offset,displacement,mesh_points,vecs=[0,1,2],center=True,isTable=False):
    press_points = np.array([[size[0],size[1],0.],[-size[0],size[1],0.],[-size[0],-size[1],0.],[size[0],-size[1],0.]])/2.
    offset = np.array([offset[0],offset[1],0.])
    displacement = np.array(displacement)

    return create_flat_press(press_points,offset,displacement,mesh_points,vecs,center,isTable)
