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