import os
import yaml
import scipy.io
import numpy as np
from .sensor import Sensor, CameraSensor, LidarSensor
from .moving_object import MovingObject
from ..visualizers.scene_visualizer import SceneVisualizer
from natsort import natsorted

class ScenarioManager:
    """
    Manages the loading and processing of a scenario, including sensor data and moving object information.
    """

    def __init__(self, scenario_path):
        """
        Initializes the ScenarioManager with the path to the scenario directory.

        Args:
            scenario_path (str): The path to the scenario directory.
        """
        self.scenario_path = scenario_path
        self.config = self.load_config()

        self.sensors = self.process_sensors()
        self.moving_objects = self.process_moving_objects()

        self.visualizer = SceneVisualizer()

    def set_visualization_backend(self, backend):
        """
        Sets the visualization backend for the scene visualizer.

        Args:
            backend (str): The name of the visualization backend to use.
        """
        self.visualizer.set_backend(backend)

    def load_config(self):
        """
        Loads the scenario configuration from a YAML file.

        Returns:
            dict: The scenario configuration as a dictionary.
        """
        config_path = os.path.join(self.scenario_path, 'param', 'scenario.yaml')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def process_sensors(self):
        """
        Processes the sensor data based on the scenario configuration.

        Returns:
            dict: A dictionary containing sensor data for each modality.
        """
        sensor_data = {}
        for modality in self.config['modalities']:
            modality_name = modality['name']
            if 'object' not in modality_name:  # Do not process objects as sensors
                modality_path = os.path.join(self.scenario_path, modality['path'])
                sensors = modality.get('sensors', [])
                if os.path.exists(modality_path):
                    sensor_data[modality_name] = self.get_sensor_objects(modality_name, modality_path, sensors)
                else:
                    print(f"Warning: {modality_path} does not exist.")
        return sensor_data

    def get_sensor_objects(self, modality_name, modality_path, sensors):
        """
        Creates sensor objects (CameraSensor, LidarSensor, or Sensor) for a given modality.

        Args:
            modality_name (str): The name of the modality.
            modality_path (str): The path to the modality directory.
            sensors (list): A list of sensor configurations.

        Returns:
            dict: A dictionary of sensor objects, where keys are sensor IDs and values are the corresponding Sensor objects.
        """
        sensor_objects = {}
        for sensor in sensors:
            sensor_id = sensor['id']
            sensor_path = os.path.join(modality_path, sensor_id)
            properties = sensor.get('properties', {})
            if os.path.exists(sensor_path):
                files = self.get_files_in_directory(sensor_path)
                if modality_name == 'camera':
                    sensor_objects[sensor_id] = CameraSensor(sensor_id, properties, files)
                elif modality_name == 'lidar':
                    sensor_objects[sensor_id] = LidarSensor(sensor_id, properties, files)
                else:
                    sensor_objects[sensor_id] = Sensor(sensor_id, properties, files)
            else:
                print(f"Warning: {sensor_path} does not exist.")
        return sensor_objects

    def process_moving_objects(self):
        """
        Processes the moving object data from a MATLAB file.

        Returns:
            dict: A dictionary of MovingObject instances, where keys are object IDs and values are the corresponding MovingObject instances.
        """
        moving_objects_data = {}
        movement_modality = next((mod for mod in self.config['modalities'] if 'object' in mod['name']), None)
        if movement_modality:
            mat_path = os.path.join(self.scenario_path, movement_modality['path'])
            if os.path.exists(mat_path):
                mat_data = scipy.io.loadmat(mat_path, simplify_cells=True)
                object_types = mat_data['object_info']  # Information about each object type
                time_samples = mat_data['scene']  # Time samples with object data
                object_types = object_types if isinstance(object_types, list) else [object_types]
                time_samples = time_samples if isinstance(time_samples, list) else [time_samples]
                for t, sample in enumerate(time_samples):
                    # Handle cases where 'objects' might be a single dictionary instead of a list
                    if isinstance(sample['objects'], dict):
                        sample['objects'] = [sample['objects']]

                    for obj_scene_idx, obj in enumerate(sample['objects']):  # Iterate through objects at each time step
                        object_id = obj['id']
                        if object_id not in moving_objects_data:
                            # Find the object type information based on object ID from the mat file
                            for object_type in object_types:
                                if obj['type'] == object_type['id']:
                                    break
                            # Initialize the MovingObject with the corresponding ID and type
                            moving_objects_data[object_id] = MovingObject(object_id, object_type)
                        # Add time samples to the object
                        moving_objects_data[object_id].add_time_sample(t, obj, obj_scene_idx)

            else:
                print(f"Warning: {mat_path} does not exist.")
        return moving_objects_data

    def get_files_in_directory(self, directory):
        """
        Retrieves a sorted list of all files within a directory and its subdirectories.

        Args:
            directory (str): The path to the directory.

        Returns:
            list: A sorted list of file paths.
        """
        files = []
        for root, _, filenames in os.walk(directory):
            # Add file paths to the file list
            for filename in filenames:
                files.append(os.path.join(root, filename))
        files = natsorted(files)  # Sort the files naturally
        files = np.array(files)
        return files

    def get_modality_data(self, modality_name):
        """
        Retrieves the sensor data for a specific modality.

        Args:
            modality_name (str): The name of the modality.

        Returns:
            dict: The sensor data for the specified modality, or an empty dictionary if the modality is not found.
        """
        return self.sensors.get(modality_name, {})

    def visualize(self, time_sample=None):
        """
        Visualizes the scenario using the SceneVisualizer.

        Args:
            time_sample (int, optional): The time sample to visualize. If None, the entire scenario is visualized (if supported by the visualizer).
        """
        self.visualizer.visualize(self.sensors, self.moving_objects, time_sample)