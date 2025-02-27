from .base_visualizer import BaseVisualizer
import matplotlib.colors as mcolors
import numpy as np

class SceneVisualizer(BaseVisualizer):
    """
    Visualizer for a scene containing sensors and moving objects.

    Supported backends:
        - matplotlib: For 2D visualizations.
        - pyvista: For 3D visualizations.
    """

    supported_backends = ['matplotlib', 'pyvista', 'plotly']

    def __init__(self, backend='pyvista'):
        """
        Initializes the SceneVisualizer with a default backend.

        Args:
            backend (str): The default backend to use ('matplotlib' or 'pyvista').
        """
        super().__init__()
        # self.set_backend(backend)  # Set the default backend

    def set_backend(self, backend):
        """
        Sets the visualization backend. Imports necessary libraries for the selected backend.

        Args:
            backend (str): The backend to use ('matplotlib' or 'pyvista').
        """
        super().set_backend(backend)

        if backend == 'matplotlib':
            import matplotlib.pyplot as plt
            from matplotlib import patches  # Import patches here
            self.backend_lib = {'plt': plt, 'patches': patches}  # Store plt and patches in backend_lib
        elif backend == 'pyvista':
            import pyvista as pv
            self.backend_lib = pv
        elif backend == 'plotly':
            import plotly.graph_objects as go
            self.backend_lib = go


    def visualize(self, sensors, moving_objects, time_sample=None):
        """
        Visualizes the scene using the selected backend.

        Args:
            sensors (dict): Dictionary of sensor data.
            moving_objects (dict): Dictionary of moving objects.
            time_sample (int, optional): The time sample to visualize. If None, visualizes the first time sample.
        """
        self.visualization_method(sensors, moving_objects, time_sample)

    # def _visualize_with_matplotlib(self, sensors, moving_objects, time_sample):
    #     """
    #     Visualizes the scene using matplotlib (2D).

    #     Args:
    #         sensors (dict): Dictionary of sensor data.
    #         moving_objects (dict): Dictionary of moving objects.
    #         time_sample (int, optional): The time sample to visualize.
    #     """
    #     plt = self.backend_lib['plt']
    #     patches = self.backend_lib['patches']

    #     colors = list(mcolors.TABLEAU_COLORS.keys())
    #     color_map = {obj_id: colors[i % len(colors)] for i, obj_id in enumerate(moving_objects)}

    #     fig, ax = plt.subplots()

    #     # Plot sensors
    #     for modality, sensor_dict in sensors.items():
    #         for sensor_id, sensor in sensor_dict.items():
    #             loc = sensor.get_properties().get('location')
    #             if loc:
    #                 ax.scatter(loc[0], loc[1], label=f'{modality} {sensor_id}', marker='o')

    #     # Plot moving objects
    #     for obj_id, obj in moving_objects.items():
    #         properties = obj.get_properties_at_time(time_sample) if time_sample is not None else obj.get_properties_at_time(obj.time[0])  # Default to the first time sample
    #         if properties:
    #             loc = properties['location']
    #             bb = [obj.type['length'], obj.type['width'], obj.type['height']]
    #             # Adjust location to the center of the bounding box for plotting
    #             # Assuming loc[0] is x, loc[1] is y
    #             loc[0] = loc[0]
    #             loc[1] = loc[1]
    #             color = mcolors.to_rgb(color_map[obj_id])
    #             ax.scatter(loc[0], loc[1], label=f'Object {obj_id}', marker='^', color=color)

    #             # Draw bounding box
    #             r = patches.Rectangle((loc[0] - bb[0]/2, loc[1] - bb[1]/2), bb[0], bb[1], angle=properties['angle'], rotation_point='center', fill=False, edgecolor=color, linewidth=2, alpha=0.5)
    #             ax.add_patch(r)

    #     ax.set_aspect('equal')
    #     ax.set_xlabel('X (m)')
    #     ax.set_ylabel('Y (m)')
    #     ax.legend()
    #     plt.title(f"Scene at Time Sample: {time_sample if time_sample is not None else obj.time[0]}")
    #     plt.show()

    def _visualize_with_plotly(self, sensors, moving_objects, time_sample=None):
        """
        Visualizes the scene using Plotly (interactive 3D).

        Args:
            sensors (dict): Dictionary of sensor data.
            moving_objects (dict): Dictionary of moving objects.
            time_sample (int, optional): The time sample to visualize. If None, creates an animation.
        """
        
        go = self.backend_lib

        fig = go.Figure()
        # Set layout for the figure (title, axis labels, etc.)

        # Get min and max time across all objects
        min_time = min(obj.time[0] for obj in moving_objects.values())
        max_time = max(obj.time[-1] for obj in moving_objects.values())

        # Add a trace for each sensor
        for modality, sensor_dict in sensors.items():
            for sensor_id, sensor in sensor_dict.items():
                loc = sensor.get_properties().get('location')
                if loc:
                    fig.add_trace(go.Scatter3d(x=[loc[0]], y=[loc[1]], z=[loc[2]],
                                               mode='markers',
                                               marker=dict(size=10, color='blue'),
                                               name=f'{modality} {sensor_id}'))

        # Add a trace for each moving object at the initial time sample or the specified time_sample
        for obj_id, obj in moving_objects.items():
            properties = obj.get_properties_at_time(time_sample if time_sample is not None else min_time)
            if properties:
                loc = properties['location']
                bb = [obj.type['length'], obj.type['width'], obj.type['height']]
                x, y, z = self.create_box(loc, bb)

                fig.add_trace(go.Mesh3d(x=x, y=y, z=z,
                                       alphahull=0,  # Changed from -1 to 0
                                       opacity=0.5,
                                       color='red',
                                       name=f'Object {obj_id}'))


        # Create animation frames if time_sample is None
        if time_sample is None:
            frames = []
            for t in range(min_time, max_time + 1):
                frame_traces = []
                for obj_id, obj in moving_objects.items():
                    properties = obj.get_properties_at_time(t)
                    if properties:
                        loc = properties['location']
                        bb = [obj.type['length'], obj.type['width'], obj.type['height']]
                        x, y, z = self.create_box(loc, bb)
                        frame_traces.append(go.Mesh3d(x=x, y=y, z=z,
                                                       alphahull=0,  # Changed from -1 to 0
                                                       opacity=0.5,
                                                       color='red',
                                                       name=f'Object {obj_id}'))

                frames.append(go.Frame(data=frame_traces, name=str(t)))

            fig.frames = frames
            fig.update_layout(updatemenus=[dict(type='buttons',
                                                showactive=False,
                                                buttons=[dict(label='Play',
                                                              method='animate',
                                                              args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True)]),
                                                         dict(label='Pause',
                                                              method='animate',
                                                              args=[[None], dict(frame=dict(duration=0, redraw=False), mode='immediate', fromcurrent=True)])])],
                              sliders=[dict(active=0,
                                            yanchor='top',
                                            xanchor='left',
                                            currentvalue=dict(font=dict(size=16), prefix='Time: ', visible=True, xanchor='right'),
                                            pad=dict(b=10, t=70),
                                            len=0.9,
                                            x=0.1,
                                            y=0,
                                            steps=[dict(args=[[f.name], dict(mode='animate', frame=dict(duration=50, redraw=True), fromcurrent=True)],
                                                        label=f.name,
                                                        method='animate') for f in fig.frames])])

        fig.update_layout(scene=dict(xaxis_title='X (m)',
                                     yaxis_title='Y (m)',
                                     zaxis_title='Z (m)'),
                          title=f"Scene at Time Sample: {time_sample if time_sample is not None else min_time}",
                          autosize=True,
                          width=800,
                          height=600
                          )


        fig.show()

    def create_box(self, center, dimensions):
        """
        Creates the vertices of a box for Plotly Mesh3d.

        Args:
            center (list): Center of the box [x, y, z].
            dimensions (list): Dimensions of the box [length, width, height].

        Returns:
            tuple: x, y, z coordinates of the box vertices.
        """
        l, w, h = dimensions
        x_corners = [l/2, l/2, -l/2, -l/2, l/2, l/2, -l/2, -l/2]
        y_corners = [w/2, -w/2, -w/2, w/2, w/2, -w/2, -w/2, w/2]
        z_corners = [h/2, h/2, h/2, h/2, -h/2, -h/2, -h/2, -h/2]

        x = [center[0] + corner for corner in x_corners]
        y = [center[1] + corner for corner in y_corners]
        z = [center[2] + corner for corner in z_corners]

        return x, y, z


    # def _visualize_with_matplotlib(self, sensors, moving_objects, time_sample):
    #     """
    #     Visualizes the scene using matplotlib (2D).

    #     Args:
    #         sensors (dict): Dictionary of sensor data.
    #         moving_objects (dict): Dictionary of moving objects.
    #         time_sample (int, optional): The time sample to visualize.
    #     """
    #     plt = self.backend_lib['plt']
    #     patches = self.backend_lib['patches']

    #     colors = list(mcolors.TABLEAU_COLORS.keys())
    #     color_map = {obj_id: colors[i % len(colors)] for i, obj_id in enumerate(moving_objects)}

    #     fig, ax = plt.subplots()

    #     # Plot sensors
    #     for modality, sensor_dict in sensors.items():
    #         for sensor_id, sensor in sensor_dict.items():
    #             loc = sensor.get_properties().get('location')
    #             if loc:
    #                 ax.scatter(loc[0], loc[1], label=f'{modality} {sensor_id}', marker='o')

    #     # Plot moving objects
    #     for obj_id, obj in moving_objects.items():
    #         properties = obj.get_properties_at_time(time_sample) if time_sample is not None else obj.get_properties_at_time(obj.time[0])  # Default to the first time sample
    #         if properties:
    #             loc = properties['location']
    #             bb = [obj.type['length'], obj.type['width'], obj.type['height']]
    #             # Adjust location to the center of the bounding box for plotting
                
    #             color = mcolors.to_rgb(color_map[obj_id])
    #             ax.scatter(loc[0], loc[1], label=f'Object {obj_id}', marker='^', color=color)

    #             # Draw bounding box
    #             rect = patches.Rectangle((loc[0] - bb[0]/2, loc[1] - bb[1]/2), bb[0], bb[1], angle=properties['angle'], rotation_point='center', fill=False, edgecolor=color, linewidth=2, alpha=0.5)
    #             ax.add_patch(rect)

    #     ax.set_aspect('equal')
    #     ax.set_xlabel('X (m)')
    #     ax.set_ylabel('Y (m)')
    #     ax.legend()
    #     plt.title(f"Scene at Time Sample: {time_sample if time_sample is not None else obj.time[0]}")
    #     plt.show()


    # def _visualize_with_pyvista(self, sensors, moving_objects, time_sample):
    #     """
    #     Visualizes the scene using pyvista (3D).

    #     Args:
    #         sensors (dict): Dictionary of sensor data.
    #         moving_objects (dict): Dictionary of moving objects.
    #         time_sample (int, optional): The time sample to visualize. If None, the slider will be available.
    #     """
                
    #     def add_sensors():
                
    #         # Define sensor colors and shapes
    #         sensor_colors = {
    #             'LiDAR': 'red',
    #             'camera': 'green'
    #         }
    #         # Initial plot (for time_sample=0 or a default)
    #         for modality, sensor_dict in sensors.items():
    #             for sensor_id, sensor in sensor_dict.items():
    #                 loc = sensor.get_properties().get('location')
    #                 if loc:
    #                     # Get color and shape based on modality
    #                     color = sensor_colors.get(modality, 'blue')  # Default to blue if modality not found

    #                     if modality == 'LiDAR':
    #                         # Add a cone for lidar
    #                         mesh = pv.Cone(center=loc, direction=[0, 0, 1], height=1.0, radius=0.5, resolution=10)
    #                     elif modality == 'camera':
    #                         # Add a tetrahedron for camera
    #                         mesh = pv.Tetrahedron()
    #                         # Scale the tetrahedron to make it more visible
    #                         mesh.scale([0.5, 0.5, 1.0], inplace=True)
    #                         # Translate the mesh to the sensor location
    #                         mesh.translate(loc, inplace=True)
    #                         color = 'blue'
    #                     else:
    #                         mesh = pv.Sphere(radius=0.5, center=loc)

    #                     plotter.add_mesh(mesh, color=color, name=f'{modality} {sensor_id}')

    #                     # plotter.add_point_labels([loc], [f"{modality} {sensor_id}"], point_size=0, font_size=14, text_color='black', shape_opacity=0.5)
    #                     plotter.add_point_labels([loc], [f"{sensor_id.split('_')[0]}"], point_size=0, font_size=14, text_color='black', shape_opacity=0.5)
                        
    #     def add_moving_objects(time_sample):
    #         for obj_id, obj in moving_objects.items():
    #             properties = obj.get_properties_at_time(time_sample)
    #             if properties:
    #                 loc = properties['location']
    #                 bb = [obj.type['length'], obj.type['width'], obj.type['height']]
    #                 loc[2] = loc[2] + bb[2]/2
    #                 color = mcolors.to_rgb(color_map[obj_id])
    #                 mesh = pv.Cube(x_length=bb[0], y_length=bb[1], z_length=bb[2])
    #                 mesh.rotate_y(properties['slope'], inplace=True)
    #                 mesh.rotate_z(properties['angle'], inplace=True)
    #                 mesh.translate(loc, inplace=True)
    #                 plotter.add_mesh(mesh, color=color, name=f'Object {obj_id}', opacity=0.5)

    #     def update_plot(time_sample):
    #         """
    #         Updates the plot for a given time sample.
    #         This function is called when the slider is moved (or can be called directly).
    #         """
    #         time_sample = int(time_sample)
    #         plotter.clear_actors() # Clear only actors (meshes), not widgets like the slider

    #         plotter.add_mesh(plane, color="lightgray", opacity=0.5, style='wireframe')

    #         add_sensors()
    #         add_moving_objects(time_sample)
            
    #         plotter.render()
        
        
    #     pv = self.backend_lib

    #     plotter = pv.Plotter()

    #     # Add XY plane
    #     plane = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), i_size=600, j_size=600)
    #     plotter.add_mesh(plane, color="lightgray", opacity=0.5, style='wireframe')

    #     colors = list(mcolors.TABLEAU_COLORS.keys())
    #     color_map = {obj_id: colors[i % len(colors)] for i, obj_id in enumerate(moving_objects)}

    #     add_sensors()
    #     add_moving_objects(0)

    #     # If time_sample is provided, visualize only that time sample
    #     if time_sample is not None:
    #         update_plot(time_sample)
    #         plotter.show()
    #     # Otherwise, create an interactive slider
    #     else:
    #         min_time = min(obj.time[0] for obj in moving_objects.values())
    #         max_time = max(obj.time[-1] for obj in moving_objects.values())

    #         slider = plotter.add_slider_widget(callback=update_plot,
    #                                            rng=[min_time, max_time],
    #                                            title='Time',
    #                                            value=min_time,
    #                                            fmt='%.0f'
    #                                            )
    #         plotter.show()

    def _visualize_with_pyvista(self, sensors, moving_objects, time_sample):
        """
        Visualizes the scene using pyvista (3D).

        Args:
            sensors (dict): Dictionary of sensor data.
            moving_objects (dict): Dictionary of moving objects.
            time_sample (int, optional): The time sample to visualize. If None, the slider will be available.
        """
        min_time = min(obj.time[0] for obj in moving_objects.values())
        max_time = max(obj.time[-1] for obj in moving_objects.values())

        def add_sensors():
            sensor_colors = {
                'LiDAR': 'red',
                'camera': 'green'
            }
            for modality, sensor_dict in sensors.items():
                for sensor_id, sensor in sensor_dict.items():
                    loc = sensor.get_properties().get('location')
                    if loc:
                        color = sensor_colors.get(modality, 'blue')
                        if modality == 'LiDAR':
                            mesh = pv.Cone(center=loc, direction=[0, 0, 1], height=1.0, radius=0.5, resolution=10)
                        elif modality == 'camera':
                            mesh = pv.Tetrahedron()
                            mesh.scale([0.5, 0.5, 1.0], inplace=True)
                            mesh.translate(loc, inplace=True)
                            color = 'blue'
                        else:
                            mesh = pv.Sphere(radius=0.5, center=loc)
                        plotter.add_mesh(mesh, color=color, name=f'{modality} {sensor_id}')
                        plotter.add_point_labels([loc], [f"{sensor_id.split('_')[0]}"], 
                                                point_size=0, font_size=14, 
                                                text_color='black', shape_opacity=0.5)
                            
        def add_moving_objects(time_sample):
            for obj_id, obj in moving_objects.items():
                properties = obj.get_properties_at_time(time_sample)
                if properties:
                    loc = properties['location'].copy()
                    bb = [obj.type['length'], obj.type['width'], obj.type['height']]
                    loc[2] = loc[2] + bb[2] / 2
                    color = mcolors.to_rgb(color_map[obj_id])
                    mesh = pv.Cube(x_length=bb[0], y_length=bb[1], z_length=bb[2])
                    mesh.rotate_y(properties['slope'], inplace=True)
                    mesh.rotate_z(properties['angle'], inplace=True)
                    mesh.translate(loc, inplace=True)
                    plotter.add_mesh(mesh, color=color, name=f'Object {obj_id}', opacity=0.5)

        def _update_plot(time_sample):
            time_sample = int(time_sample)
            plotter.clear_actors()
            plotter.add_mesh(plane, color="lightgray", opacity=0.5, style='wireframe')
            add_sensors()
            add_moving_objects(time_sample)
            plotter.render()

        def update_plot_wrapper(time_sample=None, next=None, prev=None):
            if not time_sample:
                time_sample = slider.GetRepresentation().GetValue()
                if next:
                    time_sample = time_sample + 1
                elif prev:
                    time_sample = time_sample - 1
                else:
                    time_sample = time_sample
            time_sample = max(time_sample, min_time)
            time_sample = min(time_sample, max_time)
            _update_plot(time_sample)
            slider.GetRepresentation().SetValue(time_sample)

        # Initialize pyvista components
        pv = self.backend_lib
        plotter = pv.Plotter()
        plane = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), i_size=600, j_size=600)
        plotter.add_mesh(plane, color="lightgray", opacity=0.5, style='wireframe')

        colors = list(mcolors.TABLEAU_COLORS.keys())
        color_map = {obj_id: colors[i % len(colors)] for i, obj_id in enumerate(moving_objects)}

        add_sensors()
        add_moving_objects(0)

        # If time_sample is provided, visualize only that time sample
        if time_sample is not None:
            _update_plot(time_sample)
            plotter.show()
        # Otherwise, create an interactive slider
        else:
            slider = plotter.add_slider_widget(callback=_update_plot,
                                                rng=[min_time, max_time],
                                                title='Time',
                                                value=min_time,
                                                fmt='%.0f')

            plotter.add_key_event('a', lambda: update_plot_wrapper(prev=True))
            plotter.add_key_event('d', lambda: update_plot_wrapper(next=True))

            # Start the event loop.
            plotter.show()
