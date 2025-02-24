# base_dataset.py
import shutil
import numpy as np
class BaseDataset:
    """
    Abstract base class for datasets.
    Defines common methods that subclasses should implement.
    """
    def __init__(self, params):
        """
        Initializes the BaseDataset with parameters.

        Args:
            params (dict): A dictionary of parameters.
        """
        self.params = params

    def generate(self, batch_size):
        """
        Generates a batch of data.

        Args:
            batch_size (int): The size of the batch to generate.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method")

    def get_sample(self, device_index, sample_index):
        """
        Retrieves a data sample.

        Args:
            device_index (int): Index of the device.
            sample_index (int): Index of the sample.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method")

    def save_sample(self, path, device_index, sample_index):
        """
        Saves a data sample to a file.

        Args:
            path (str): The path to save the sample to.
            device_index (int): Index of the device.
            sample_index (int): Index of the sample.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method")

    def visualize(self, device_index, sample_index):
        """
        Visualizes a data sample.

        Args:
            device_index (int): Index of the device.
            sample_index (int): Index of the sample.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method")
    
    
class PathProviderDataset(BaseDataset):
    """
    Base class for datasets that provide data samples based on file paths.

    Attributes:
        device_type (str): The type of device (e.g., 'LiDAR', 'Camera').
        params (dict): A dictionary of parameters.
        sensors (dict): A dictionary of sensors, where keys are sensor IDs and values are sensor objects.
        sensor_id (list): A list of sensor IDs.
        num_devices (int): The number of devices.
        visualizer: An object for visualization (optional).
    """
    def __init__(self, device_type, params, sensors, visualizer=None):
        """
        Initializes the PathProviderDataset.

        Args:
            device_type (str): The type of device.
            params (dict): A dictionary of parameters.
            sensors (dict): A dictionary of sensors.
            visualizer: An object for visualization (optional).
        """
        super().__init__(params)
        self.device_type = device_type
        self.sensors = sensors
        self.sensor_id = list(self.sensors.keys())
        self.num_devices = len(self.sensors)
        self.visualizer = visualizer

    def list_sensors(self):
        return self.sensors

    def get_sample(self, device_index, sample_index):
        """
        Retrieves a data sample (file path) for a specific device and sample index.

        Args:
            device_index (int): Index of the device.
            sample_index (int): Index of the sample.

        Returns:
            str: The file path of the data sample.

        Raises:
            ValueError: If the device index is invalid.
        """
        if isinstance(sample_index, int):
            pass
        elif isinstance(sample_index, list):
            sample_index = np.array(sample_index)
        elif isinstance(sample_index, np.ndarray):
            pass
        else:
            raise TypeError('The sample_index parameter needs to be integer or list or numpy array')
        dataset_sample_index = np.array(self.params['scenes'])[sample_index]
        
        if isinstance(device_index, str):
            if device_index not in self.sensor_id:
                raise ValueError(f"Invalid sensor index: {self.device_type}")
            # Return specific device sample
            return self.sensors[device_index].files[dataset_sample_index]  # Assumes each sensor object has a 'files' attribute.
        elif isinstance(device_index, int):
            if device_index < 0 or device_index >= self.num_devices:
                raise ValueError(f"Invalid sensor index: {self.device_type}")
            # Return specific device sample
            return self.sensors[self.sensor_id[device_index]].files[dataset_sample_index]  # Assumes each sensor object has a 'files' attribute.

    def save_sample(self, path, device_index, sample_index):
        """
        Saves a data sample to a file by copying it.

        Args:
            path (str): The destination path to save the sample to.
            device_index (int): Index of the device.
            sample_index (int): Index of the sample.

        Returns:
            str: The path where the sample was saved.
        """
        shutil.copy(self.get_sample(device_index, sample_index), path)
        return path

    def visualize(self, device_index, sample_index):
        """
        Visualizes a data sample using the provided visualizer.

        Args:
            device_index (int): Index of the device.
            sample_index (int): Index of the sample.

        Raises:
            NotImplementedError: If no visualizer is provided.
        """
        if not self.visualizer:
            raise NotImplementedError("Visualizer is not provided")
        sample = self.get_sample(device_index, sample_index)
        self.visualizer.visualize(sample)

    def set_visualization_backend(self, backend):
        """
        Sets the visualization backend for the visualizer.

        Args:
            backend (str): The backend to use.
        """
        self.visualizer.set_backend(backend)


from ..visualizers import LidarVisualizer

class LiDARDataset(PathProviderDataset):
    """
    Dataset class for LiDAR data.
    """
    def __init__(self, params, sensors):
        """
        Initializes the LiDARDataset.

        Args:
            params (dict): A dictionary of parameters.
            sensors (dict): A dictionary of LiDAR sensors.
        """
        super().__init__('LiDAR', params, sensors, LidarVisualizer())
    

from ..visualizers import ImageVisualizer
class CameraDataset(PathProviderDataset):
    """
    Dataset class for Camera data.
    """
    def __init__(self, params, sensors):
        """
        Initializes the CameraDataset.

        Args:
            params (dict): A dictionary of parameters.
            sensors (dict): A dictionary of camera sensors.
        """
        super().__init__('Camera', params, sensors, ImageVisualizer())


class MobilityDataset:
    """
    Dataset class for mobility data of moving objects.
    """
    def __init__(self, params, moving_objects):
        """
        Initializes the MobilityDataset.

        Args:
            params (dict): A dictionary of parameters.
            moving_objects (dict): A dictionary of moving objects, where keys are object IDs and values are objects containing mobility information.
        """
        self.params = params
        self.objects = moving_objects

    def generate(self, batch_size):
        """
        Generates a batch of mobility data. 
        # TODO: implement this or remove if it is not used

        Args:
            batch_size (int): The size of the batch to generate.

        Raises:
            NotImplementedError: This is a placeholder, as batch generation might not be applicable to all mobility data.
        """
        raise NotImplementedError("Subclasses should implement this method")

    def get_sample(self, object_id=None, sample_index=None):
        """
        Retrieves mobility data for a specific object or all objects at a specific time index.

        Args:
            object_id (int, optional): The ID of the moving object. Defaults to None.
            sample_index (int, optional): The time index of the data sample. Defaults to None.

        Returns:
            - If object_id is specified and sample_index is None: Returns the mobility object associated with object_id.
            - If object_id and sample_index are specified: Returns the properties (e.g., position, velocity) of the object at the given time index.
            - If object_id is None and sample_index is specified: Returns a list of tuples (time, object properties) for all objects at the specified time index.
            - If both object_id and sample_index are None: Returns the entire self.objects dictionary.
        """
        if isinstance(sample_index, int):
            dataset_sample_index = np.array(self.params['scenes'])[sample_index]
        elif sample_index is None:
            dataset_sample_index = None
        else:
            raise TypeError('The sample_index parameter needs to be integer')
        
        if (object_id is not None) and dataset_sample_index is None:
            return self.objects[object_id]
        if (object_id is not None) and (dataset_sample_index is not None):
            return self.objects[object_id].get_properties_at_time(dataset_sample_index) # Assumes moving objects have a method 'get_properties_at_time'
        if object_id is None and (dataset_sample_index is not None):
            result = []
            for obj_id, samples in self.objects.items():
                result.extend([(t, obj) for t, obj in samples if t == dataset_sample_index])
            return result
        return self.objects
