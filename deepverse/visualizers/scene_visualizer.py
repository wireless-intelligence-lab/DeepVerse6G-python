from .base_visualizer import BaseVisualizer
import matplotlib.colors as mcolors

class SceneVisualizer(BaseVisualizer):
    
    supported_backends = ['matplotlib', 'pyvista']

    def __init__(self, backend='pyvista'):
        
        super().__init__()
        self.set_backend(backend)  # Set the default backend

    def set_backend(self, backend):
        super().set_backend(backend)
        
        if backend == 'matplotlib':
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            from matplotlib import patches
            import mpl_toolkits.mplot3d.art3d as art3d
            self.backend_lib = {'plt': plt, 'patches': patches}
        elif backend == 'pyvista':
            import pyvista as pv
            self.backend_lib = pv
            
    def visualize(self, sensors, moving_objects, time_sample=None):
        self.visualization_method(sensors, moving_objects, time_sample)

    def _visualize_with_matplotlib(self, sensors, moving_objects, time_sample):
        plt = self.backend_lib['plt']
        patches = self.backend_lib['patches']

        colors = list(mcolors.TABLEAU_COLORS.keys())
        color_map = {obj_id: colors[i % len(colors)] for i, obj_id in enumerate(moving_objects)}

        fig, ax = plt.subplots()

        # Plot sensors
        for modality, sensor_dict in sensors.items():
            for sensor_id, sensor in sensor_dict.items():
                loc = sensor.get_properties().get('location')
                if loc:
                    ax.scatter(loc[0], loc[1], label=f'{modality} {sensor_id}', marker='o')

        # Plot moving objects
        for obj_id, obj in moving_objects.items():
            properties = obj.get_properties_at_time(time_sample) if time_sample is not None else obj.get_properties_at_time(0)
            if properties:
                loc = properties['location']
                bb = [obj.type['length'], obj.type['width'], obj.type['height']]
                loc[2] += bb[2]/2
                color = mcolors.to_rgb(color_map[obj_id])
                ax.scatter(loc[0], loc[1], label=f'Object {obj_id}', marker='^', color=color)

                # Draw bounding box
                r = patches.Rectangle((loc[0] - bb[0]/2, loc[1] - bb[1]/2), bb[0], bb[1], angle=properties['angle'], rotation_point='center', fill=False, edgecolor=color, linewidth=2, alpha=0.5)
                ax.add_patch(r)
        ax.set_aspect('equal')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.legend()
        plt.show()

    def _visualize_with_pyvista(self, sensors, moving_objects, time_sample):
        pv = self.backend_lib

        try:
            plotter = pv.Plotter()

            # Add XY plane
            plane = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), i_size=600, j_size=20)
            plotter.add_mesh(plane, color="lightgray", opacity=0.5, style='wireframe')

            colors = list(mcolors.TABLEAU_COLORS.keys())
            color_map = {obj_id: colors[i % len(colors)] for i, obj_id in enumerate(moving_objects)}

            # Plot sensors
            for modality, sensor_dict in sensors.items():
                for sensor_id, sensor in sensor_dict.items():
                    loc = sensor.get_properties().get('location')
                    if loc:
                        plotter.add_mesh(pv.Sphere(radius=0.5, center=loc), color='blue', name=f'{modality} {sensor_id}')

            def update_plot(time_sample):
                time_sample = int(time_sample)
                #plotter.clear()
                plotter.add_mesh(plane, color="lightgray", opacity=0.5, style='wireframe')

                for modality, sensor_dict in sensors.items():
                    for sensor_id, sensor in sensor_dict.items():
                        loc = sensor.get_properties().get('location')
                        if loc:
                            plotter.add_mesh(pv.Sphere(radius=0.5, center=loc), color='blue', name=f'{modality} {sensor_id}')

                for obj_id, obj in moving_objects.items():
                    properties = obj.get_properties_at_time(time_sample) if time_sample is not None else obj.get_properties_at_time(0)
                    if properties:
                        loc = properties['location']
                        bb = [obj.type['length'], obj.type['width'], obj.type['height']]
                        loc[2] += obj.type['height']/2
                        color = mcolors.to_rgb(color_map[obj_id])
                        plotter.add_mesh(pv.Cube(center=loc, x_length=bb[0], y_length=bb[1], z_length=bb[2]), color=color, name=f'Object {obj_id}', opacity=0.5)

                # plotter.add_legend()
                plotter.render()

            slider = plotter.add_slider_widget(callback=update_plot, 
                                               rng=[0, 2000], 
                                               #title_opacity=0.5,
                                               #title_color="red",
                                               fmt='%.0f',
                                               #title_height=0.08,
                                               title='Time', 
                                               value=time_sample
                                               )
            plotter.show()
        except Exception as e:
            print(f"An error occurred: {e}")
