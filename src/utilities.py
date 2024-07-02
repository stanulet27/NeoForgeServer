import numpy as np
 
def quaternion_rotation_matrix(quaternion: 'list[float]') -> np.array:

    q0 = quaternion[0]
    q1 = quaternion[1]
    q2 = quaternion[2]
    q3 = quaternion[3]

    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)

    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)

    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1

    rot_matrix = np.array([[r00, r01, r02],
                           [r10, r11, r12],
                           [r20, r21, r22]])
    return rot_matrix

def translate_vector(quaternion: 'list[float]', 
                     translation_vector: 'list[float]', 
                     points: 'list[float]'
                ) -> 'list[float]':
    vertices = combine_into_vectors(points)
    rotation_matrix = quaternion_rotation_matrix(quaternion)
    position = np.array(translation_vector).reshape(3, 1)
    new_vertices = []
    for vertex in vertices:
        new_vertex = (rotation_matrix @ vertex) + position
        new_vertices.append(new_vertex.transpose().tolist()[0])
    return new_vertices

def untranslate_vector(quaternion: 'list[float]', 
                       translation_vector: 'list[float]', 
                       points: 'list[float]'
                    ) -> 'list[float]':
    vertices = combine_into_vectors(points)
    rotation_matrix = quaternion_rotation_matrix(quaternion)
    position = np.array(translation_vector).reshape(3, 1)
    new_vertices = []
    for vertex in vertices:
        new_vertex = (rotation_matrix.transpose()) @ (vertex - position)
        new_vertices.append(new_vertex.transpose().tolist()[0])
    return unwrap_points(new_vertices)
    
def multiply_vertices(vertices: 'list[np.ndarray[float, float]]', 
                      hits: 'list[int]', 
                      force: float
                    ) -> 'list[float]':
    c = 0
    for i in range(len(vertices)):
        if i in hits:
            vertices[i][1] -= force
            c += 1
    print(f"Deformed {c} vertices")
    return unwrap_points(vertices)


def combine_into_vector(x: float, y: float, z: float) -> 'np.ndarray[float,float]' :
    return np.array([x, y, z]).reshape(3, 1)

def combine_into_vectors(points: 'list[float]') -> 'list[np.ndarray[float,float]]':
    combined = []
    for i in range(round(len(points) / 3)):
        x = points[i * 3]
        y = points[i * 3 + 1]
        z = points[i * 3 + 2]
        combined.append(combine_into_vector(x, y, z))
    return combined

def unwrap_points(points: 'list[np.ndarray[float,float]]') -> 'list[float]':
    unwrapped = []
    for i in range(len(points)):
        unwrapped.append(points[i][0])
        unwrapped.append(points[i][1])
        unwrapped.append(points[i][2])
    return unwrapped

import re
import os

from jax_fem.generate_mesh import get_meshio_cell_type,box_mesh,Mesh

from scipy.spatial.transform import Rotation

# SETUP/INITIALIZATION FUNCTIONS
def create_next_run_folder(directory):
    pattern = re.compile(r"^run_(\d+)$")
    items = os.listdir(directory)
    run_folders = [item for item in items if os.path.isdir(os.path.join(directory, item)) and pattern.match(item)]
    run_folders.sort(key=lambda x: int(pattern.match(x).group(1)))
    
    if run_folders:
        last_run_number = int(pattern.match(run_folders[-1]).group(1))
        next_run_number = last_run_number + 1
    else:
        next_run_number = 1
    
    next_run_folder = f"run_{next_run_number:03d}"
    next_run_folder_path = os.path.join(directory, next_run_folder)
    os.makedirs(next_run_folder_path)
    run_folders.append(next_run_folder)

    return run_folders,next_run_folder_path

def setup_data_dir(outputFolder='data/runs'):
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
    _,run_path = create_next_run_folder(outputFolder)
    return run_path

def setup_starting_mesh(data_dir):
    # Specify mesh-related information(first-order hexahedron element).
    ele_type = 'HEX8'
    cell_type = get_meshio_cell_type(ele_type)
    Lx, Ly, Lz = 2., 2., 2.
    meshio_mesh = box_mesh(Nx=9, Ny=9, Nz=9, Lx=Lx, Ly=Ly, Lz=Lz, data_dir=data_dir, ele_type=ele_type)
    mesh = Mesh(meshio_mesh.points, meshio_mesh.cells_dict[cell_type])
    # ADD NOISE
    # noiseArr = onp.random.normal(0,0.01,mesh.points.shape)
    # mesh.points = mesh.points + noiseArr
    # ROTATE MESH
    # rot = Rotation.from_euler('x',50,degrees=True)
    # mesh.points = rot.apply(mesh.points)
    # rot = Rotation.from_euler('y',10,degrees=True)
    # mesh.points = rot.apply(mesh.points)
    # mesh.points = rotate_points(mesh.points, [0,1,0], onp.degrees(onp.arctan(onp.sqrt(2)/2)), [Lx/2,Ly/2,Lz/2])
    return mesh

from NeoForgeServer.src.Library.plasticity import Plasticity
from Library.create_press import create_flat_rect_press
from NeoForgeServer.src.Library.plasticity_sim import PlasticitySim

def get_rectangular_hit_sim(size,offset,hit_depth,mesh,data_dir,step_size=0.05):
    problem = Plasticity(mesh,vec=3,dim=3)
    press = create_flat_rect_press(size,offset,[0.,0.,-step_size],mesh.points,vecs=[0,1,2])
    table = create_flat_rect_press([10.,10.],[0.,0.],[0.,0.,1e-6],mesh.points,vecs=[0,1,2],isTable=True)
    table.update_displacement([0.,0.,0.])
    num_steps = int(min(abs(hit_depth/step_size),100))

    return PlasticitySim(problem,[press,table],data_dir),num_steps
