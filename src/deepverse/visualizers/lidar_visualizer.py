# lidar_visualizer.py
import time
import numpy as np

from .base_visualizer import BaseVisualizer

class LidarVisualizer(BaseVisualizer):
    """
    Visualizer class for LiDAR data that supports multiple backends including Open3D, Mayavi, PCL, Matplotlib, VTK, and Plotly.

    Attributes:
        supported_backends (list): List of supported backend names.
        backend (str): The currently selected backend.
        backend_lib (module): The library module corresponding to the selected backend.
        visualization_method (function): The method used for visualization with the selected backend.
    """
    
    # Supported backends for LiDAR visualization
    supported_backends = ['open3d']
    # TODO: Alternative visualization backends: 'mayavi', 'pcl', 'matplotlib', 'vtk', 'plotly' to be fixed

    def __init__(self, backend='open3d'):
        """
        Initializes the LidarVisualizer with the specified backend.

        Args:
            backend (str): The name of the backend to use for visualization. Default is 'open3d'.
        """
        super().__init__()
        # self.set_backend(backend)  # Set the default backend

    def set_backend(self, backend):
        """
        Sets the backend for LiDAR visualization and loads the corresponding library.

        Args:
            backend (str): The name of the backend to set.

        Raises:
            ValueError: If the backend is not supported.
        """
        super().set_backend(backend)  # Call the base method to set the backend
        if backend == 'open3d':
            import open3d as o3d
            self.backend_lib = o3d
        elif backend == 'mayavi':
            import mayavi.mlab as mlab
            self.backend_lib = mlab
        elif backend == 'pcl':
            import pcl
            self.backend_lib = pcl
        elif backend == 'matplotlib':
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D  # Ensure Axes3D is imported here
            self.backend_lib = plt
        elif backend == 'vtk':
            import vtk
            self.backend_lib = vtk
        elif backend == 'plotly':
            import plotly.graph_objects as go
            self.backend_lib = go

    def _visualize_with_open3d(self, pcd_path):
        """
        Visualizes a point cloud using the Open3D backend.

        Args:
            pcd_path (str): The path to the point cloud file.
        """
        pcd = self.backend_lib.io.read_point_cloud(pcd_path)
        self.backend_lib.visualization.draw_geometries([pcd])

    def _visualize_with_mayavi(self, pcd_path):
        """
        Visualizes a point cloud using the Mayavi backend.

        Args:
            pcd_path (str): The path to the point cloud file.
        """
        points = np.genfromtxt(pcd_path, skip_header=11, usecols=(0, 1, 2), delimiter=' ')
        
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        self.backend_lib.points3d(x, y, z, colormap="spectral")
        self.backend_lib.show()

    def _visualize_with_pcl(self, pcd_path):
        """
        Visualizes a point cloud using the PCL backend.

        Args:
            pcd_path (str): The path to the point cloud file.
        """
        cloud = self.backend_lib.load_XYZRGB(pcd_path)  # Use pcl.load_XYZRGB for PCD files with RGB data
        
        visual = self.backend_lib.pcl_visualization.CloudViewing()
        visual.ShowMonochromeCloud(cloud)

        # Use a small sleep interval in the loop to prevent excessive CPU usage
        while not visual.WasStopped():
            time.sleep(0.01)  # Add a small delay

    def _visualize_with_matplotlib(self, pcd_path):
        """
        Visualizes a point cloud using the Matplotlib backend.

        Args:
            pcd_path (str): The path to the point cloud file.
        """
        import numpy as np
        points = np.genfromtxt(pcd_path, delimiter=' ', skip_header=11, usecols=(0, 1, 2))
        x, y, z = points[:, 0], points[:, 1], points[:, 2]

        fig = self.backend_lib.figure()
        ax = fig.add_subplot(111, projection='3d')  # Use projection='3d' to create a 3D plot
        ax.scatter(x, y, z, c='r', marker='o')
        self.backend_lib.show()

    def _visualize_with_vtk(self, pcd_path):
        """
        Visualizes a point cloud using the VTK backend.

        Args:
            pcd_path (str): The path to the point cloud file.
        """
        import numpy as np
        points = np.loadtxt(pcd_path, delimiter=',')
        x, y, z = points[:, 0], points[:, 1], points[:, 2]

        vtk_points = self.backend_lib.vtkPoints()
        for i in range(len(x)):
            vtk_points.InsertNextPoint(x[i], y[i], z[i])

        polydata = self.backend_lib.vtkPolyData()
        polydata.SetPoints(vtk_points)

        mapper = self.backend_lib.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        actor = self.backend_lib.vtkActor()
        actor.SetMapper(mapper)

        renderer = self.backend_lib.vtkRenderer()
        render_window = self.backend_lib.vtkRenderWindow()
        render_window.AddRenderer(renderer)

        interactor = self.backend_lib.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        renderer.AddActor(actor)
        renderer.SetBackground(0, 0, 0)
        render_window.Render()
        interactor.Start()

    def _visualize_with_plotly(self, pcd_path):
        """
        Visualizes a point cloud using the Plotly backend.

        Args:
            pcd_path (str): The path to the point cloud file.
        """
        import numpy as np
        points = np.loadtxt(pcd_path, delimiter=',')
        x, y, z = points[:, 0], points[:, 1], points[:, 2]

        fig = self.backend_lib.Figure(data=[self.backend_lib.Scatter3d(
            x=x, y=y, z=z, mode='markers', marker=dict(size=2)
        )])
        fig.show()
