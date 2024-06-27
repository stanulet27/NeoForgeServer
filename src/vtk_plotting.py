import pyvista as pv
import numpy as np
import os

def make_press(press_frame_info,frame):

    press_radius = press_frame_info["press_radius"]
    press_offset = press_frame_info["press_offset"]
    Lz = press_frame_info["Lz"]
    top_disp = press_frame_info["top_disps"][frame]


    press_mesh = pv.Plane(center=(press_offset[0], press_offset[1], Lz + top_disp),
                        direction=(0, 0, 1),
                        i_size=2 * press_radius,
                        j_size=2 * press_radius,
                        i_resolution=1,
                        j_resolution=1)
    return(press_mesh)

def simple_mesh_plot(geo_path=None,mesh=None):

    assert mesh or geo_path is not None
    if geo_path:
        vtk_mesh = pv.read(geo_path)
        vtk_mesh.set_active_scalars('sol')
        sol_points = vtk_mesh['sol']
    if mesh:
        vtk_mesh = pv.PolyData()
        vtk_mesh.points = mesh.points
        for cell_type, cells in mesh.cells_dict.items():
            cell_size = len(cells[0])    
            faces = np.hstack([[cell_size] + list(face) for face in cells])
        vtk_mesh.faces = faces 
        sol_points = mesh.point_data['sol']
    
    modified_mesh = vtk_mesh.copy()
    modified_mesh.points+=sol_points
    modified_mesh.plot(show_edges=True,  
            show_axes=True,   
            show_grid=True,   
            color='white')


def surface_mesh_plot(geo_path=None,surface_mesh=None):
    """
    Plots a surface mesh along with its computed normals.

    Parameters:
    - surface_mesh (pyvista.PolyData): The surface mesh with normals already computed.
    """
    if geo_path:
        surface_mesh = pv.read(geo_path)
    plotter = pv.Plotter()
    
    # Add the surface mesh to the plot
    plotter.add_mesh(surface_mesh, color='lightblue', show_edges=True, edge_color='black')
    
    # Check if normals are computed and add them to the plot
    if 'Normals' in surface_mesh.point_data:
        # Create arrows for the normals
        arrows = surface_mesh.glyph(orient='Normals', scale_factor=0.1)
        plotter.add_mesh(arrows, color='red')
    else:
        print("No normals found in the surface mesh point data.")
    
    # Add grid and axes for better orientation
    plotter.show_grid()
    plotter.show_axes()
    
    # Display the plot
    plotter.show()  

#simple range check
def create_gif(in_path,out_path,name="animation.gif",negative=False,press_info=False):
    out_path=os.path.join(out_path,name)
    vtk_files = [f for f in os.listdir(in_path) if f.endswith('.vtu')]
    vtk_files.sort()  
    plotter = pv.Plotter(off_screen=False)
    

    def plot_frame(vtk_file, plotter,press_mesh=False):
        mesh = pv.read(os.path.join(in_path, vtk_file))
        mesh.set_active_scalars('sol')
        modified_mesh = mesh.copy()
        modified_mesh.points+=mesh['sol']
        plotter.add_mesh(modified_mesh,show_edges=True)
        if press_mesh:
            plotter.add_mesh(press_mesh, color='red', opacity=0.5)  # Add press_mesh to the plotter
        plotter.show_axes()
        plotter.show_grid()
        plotter.view_isometric(negative=negative)
        plotter.render()
        plotter.write_frame()  
        plotter.clear()

    #delay in ms
    plotter.open_gif(out_path)
    for i,vtk_file in enumerate(vtk_files):
        if press_info:
            plot_frame(vtk_file, plotter,press_mesh=make_press(press_info,frame = i+1))
        else:
            plot_frame(vtk_file, plotter)
    plotter.close()



if __name__ == "__main__":
    #folder_path = 'demos/plasticity/data/vtk'
    in_path = '/Users/josh/coding_projects/jax/jax-fem/demos/plasticity/data/runs/run_002'
    out_path = in_path
    create_gif(in_path,out_path)


# for vtk_file in vtk_files:
#     mesh = pv.read(os.path.join(folder_path,vtk_file))
#     sol_values = mesh['sol']
#     print(mesh.points)
#     print(sol_values)
#     print("Original Points Statistics:")
#     print("Range X:", np.ptp(mesh.points[:, 0]))
#     print("Range Y:", np.ptp(mesh.points[:, 1]))
#     print("Range Z:", np.ptp(mesh.points[:, 2]))

#     print("Sol Data Statistics:")
#     print("Range X:", np.ptp(sol_values[:, 0]))
#     print("Range Y:", np.ptp(sol_values[:, 1]))
#     print("Range Z:", np.ptp(sol_values[:, 2]))
    
#     break
