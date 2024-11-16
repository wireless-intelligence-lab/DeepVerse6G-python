import os
import yaml
import scipy.io
import numpy as np
from .sensor import Sensor, CameraSensor, LidarSensor
from .moving_object import MovingObject
from ..visualizers.scene_visualizer import SceneVisualizer
from natsort import natsorted

class ScenarioManager:
    
    def __init__(self, scenario_path):
        self.scenario_path = scenario_path
        self.config = self.load_config()
        
        self.sensors = self.process_sensors()
        self.moving_objects = self.process_moving_objects()
        
        self.visualizer = SceneVisualizer()

    def set_visualization_backend(self, backend):
        self.visualizer.set_backend(backend)
        
    def load_config(self):
        config_path = os.path.join(self.scenario_path, 'scenario.yaml')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def process_sensors(self):
        sensor_data = {}
        for modality in self.config['modalities']:
            modality_name = modality['name']
            if 'object' not in modality_name: # Do not process objects
                modality_path = os.path.join(self.scenario_path, modality['path'])
                sensors = modality.get('sensors', [])
                if os.path.exists(modality_path):
                    sensor_data[modality_name] = self.get_sensor_objects(modality_name, modality_path, sensors)
                else:
                    print(f"Warning: {modality_path} does not exist.")
        return sensor_data

    def get_sensor_objects(self, modality_name, modality_path, sensors):
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
        moving_objects_data = {}
        movement_modality = next((mod for mod in self.config['modalities'] if 'object' in mod['name']), None)
        if movement_modality:
            mat_path = os.path.join(self.scenario_path, movement_modality['path'])
            if os.path.exists(mat_path):
                mat_data = scipy.io.loadmat(mat_path, simplify_cells=True)
                object_types = mat_data['object_info']
                time_samples = mat_data['scene']
                for t, sample in enumerate(time_samples):
                    if isinstance(sample['objects'], dict): # If there is only one object, it takes dictionary- due to matlab loading function
                        sample['objects'] = [sample['objects']]
                        
                    for obj_scene_idx, obj in enumerate(sample['objects']):  # assuming 'objects' is the key
                        object_id = obj['id']
                        if object_id not in moving_objects_data:
                            # Find the object properties from the list of types dictionary
                            for object_type in object_types:
                                if obj['type'] == object_type['id']:
                                    break
                            # Initialize the MovingObject with the corresponding ID
                            moving_objects_data[object_id] = MovingObject(object_id, object_type)
                        # Add time samples to the object
                        moving_objects_data[object_id].add_time_sample(t, obj, obj_scene_idx)

            else:
                print(f"Warning: {mat_path} does not exist.")
        return moving_objects_data

    def get_files_in_directory(self, directory):
        files = []
        for root, _, filenames in os.walk(directory):
            # Add file paths to the file list
            for filename in filenames:
                files.append(os.path.join(root, filename))
        files = natsorted(files)
        return files

    def get_modality_data(self, modality_name):
        return self.sensors.get(modality_name, {})

    def visualize(self, time_sample=None):
        self.visualizer.visualize(self.sensors, self.moving_objects, time_sample)