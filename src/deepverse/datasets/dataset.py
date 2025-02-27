# dataset.py
import os

from ..scenario import ScenarioManager  # ScenarioManager handles scenario configuration and details.
from ..parameter.parameter_manager import ParameterManager  # ParameterManager loads and manages configuration parameters.

from .sensor_datasets import LiDARDataset
from .sensor_datasets import CameraDataset
from .sensor_datasets import MobilityDataset

from .wireless_datasets import RadarDataset
from .wireless_datasets import CommunicationDataset

from copy import deepcopy
from tqdm import tqdm
import time


class Dataset:
    """
    Main class for loading and accessing the multi-modal dataset.
    This class manages different modality-specific datasets and provides a unified interface for data access.
    """
    def __init__(self, config):
        """
        Initializes the Dataset object.

        Args:
            config_path (str): Path to the configuration file (e.g., YAML, JSON).
        """
        
        # Load Parameters
        if isinstance(config, str):
            self.param_manager = ParameterManager(config)
        elif isinstance(config, ParameterManager):
            self.param_manager = deepcopy(config)
        elif config is None:
            # Handle default parameters here (e.g., load from a default file)
            self.param_manager = ParameterManager("default_config.m") # Example
        else:
            raise TypeError("The DeepVerse6G dataset object input `config` must be a string or a ParameterManager instance.") # Raise error for invalid types
        self.params = self.param_manager.get_params()
        
        # Load Scenario
        self.scenario_path = os.path.join(self.params['dataset_folder'], self.params['scenario'])
        self.scenario = ScenarioManager(self.scenario_path)

        # Initialize modality-specific datasets based on the scenario configuration
        # TODO: Add an enumerator class, load by name and also update scenario manager to use the enumerator.
        if 'camera' in self.scenario.sensors and self.params['camera']:
            start_time = time.perf_counter()
            tqdm.write("Generating camera dataset: ⏳ In progress")
            self.camera_dataset = CameraDataset(self.params, self.scenario.sensors['camera'])
            end_time = time.perf_counter()
            tqdm.write(f"\033[F\033[KGenerating camera dataset: ✅ Completed ({(end_time-start_time):.2f}s)")
        
        if 'LiDAR' in self.scenario.sensors and self.params['lidar']:
            tqdm.write("Generating LiDAR dataset: ⏳ In progress")
            start_time = time.perf_counter()
            self.lidar_dataset = LiDARDataset(self.params, self.scenario.sensors['LiDAR'])
            end_time = time.perf_counter()
            tqdm.write(f"\033[F\033[KGenerating LiDAR dataset: ✅ Completed ({(end_time-start_time):.2f}s)")
        
        if self.params['position']:
            tqdm.write("Generating mobility dataset: ⏳ In progress")
            start_time = time.perf_counter()
            self.mobility_dataset = MobilityDataset(self.params, self.scenario.moving_objects)
            end_time = time.perf_counter()
            tqdm.write(f"\033[F\033[KGenerating mobility dataset: ✅ Completed ({(end_time-start_time):.2f}s)")
        
        if self.params['comm']['enable']:
            tqdm.write("Generating comm dataset: ⏳ In progress")
            start_time = time.perf_counter()
            self.comm_dataset = CommunicationDataset(self.param_manager.get_filtered_params('comm'))
            end_time = time.perf_counter()
            tqdm.write(f"\033[F\033[KGenerating comm dataset: ✅ Completed ({(end_time-start_time):.2f}s)")

        if self.params['radar']['enable']:
            tqdm.write("Generating radar dataset: ⏳ In progress")
            start_time = time.perf_counter()
            self.radar_dataset = RadarDataset(self.param_manager.get_filtered_params('radar'))
            end_time = time.perf_counter()
            tqdm.write(f"\033[F\033[KGenerating radar dataset: ✅ Completed ({(end_time-start_time):.2f}s)")

    def get_sample(self, modality, index=None, device_index=None, ue_idx=None, bs_idx=None, object_id=None):
        """
        Retrieves a data sample from a specific modality.

        Args:
            modality (str): The modality to retrieve data from ('cam', 'lidar', 'radar', 'comm-ue', 'comm-bs', 'loc', 'mobility').
            index (int): The index of the data sample.
            device_index (int, optional): Index of the device for 'cam' and 'lidar' modalities. Defaults to None.
            ue_idx (int, optional): Index of the User Equipment (UE) for 'radar', 'comm-ue', 'comm-bs', 'loc' and 'mobility' modalities. Defaults to None.
            bs_idx (int, optional): Index of the Base Station (BS) for 'radar', 'comm-ue', 'comm-bs', and 'loc' modalities. Defaults to None.

        Returns:
            The requested data sample (format depends on the modality).

        Raises:
            ValueError: If required arguments are missing or the modality is invalid.
        """
        if modality == 'cam':
            if device_index is None:
                raise ValueError("device_index must be specified for camera modality")
            return self.camera_dataset.get_sample(device_index, index)
        elif modality == 'lidar':
            if device_index is None:
                raise ValueError("device_index must be specified for lidar modality")
            return self.lidar_dataset.get_sample(device_index, index)
        elif modality == 'radar':
            if ue_idx is None or bs_idx is None:
                raise ValueError("ue_idx (rx bs) & bs_idx (tx bs) must be specified for radar modality")
            return self.radar_dataset.get_sample(rx_bs_idx=ue_idx, tx_bs_idx=bs_idx, sample_idx=index)
        elif modality == 'comm-ue':
            if ue_idx is None or bs_idx is None:
                raise ValueError("ue_idx & bs_idx must be specified for comm modality")
            return self.comm_dataset.get_ue_channel(ue_idx, bs_idx, time_idx=index)
        elif modality == 'comm-bs':
            if ue_idx is None or bs_idx is None:
                raise ValueError("ue_idx & bs_idx must be specified for comm modality")
            return self.comm_dataset.get_bs_channel(ue_idx, bs_idx, time_idx=index)
        elif modality == 'loc-ue':
            if ue_idx is None:
                raise ValueError("ue_idx must be specified for comm modality")
            return self.comm_dataset.get_ue_location(ue_idx, bs_idx=0, time_idx=index) # Assuming bs_idx=0 is fixed for location
        elif modality == 'loc-bs':
            if bs_idx is None:
                raise ValueError("bs_idx must be specified for comm modality")
            return self.comm_dataset.get_bs_location(bs_idx, time_idx=index) # Assuming bs_idx=0 is fixed for location
        elif modality == 'mobility':
            return self.mobility_dataset.get_sample(object_id=object_id, sample_index=index)
        else:
            raise ValueError("Invalid modality")

    def visualize(self, modality, device_index, sample_index):
        """
        Visualizes a data sample from a specific modality.

        Args:
            modality (str): The modality to visualize ('lidar' or 'cam').
            device_index (int): Index of the device for the specified modality.
            sample_index (int): The index of the data sample.

        Raises:
            ValueError: If visualization is not implemented for the given modality.
        """
        if modality == 'lidar':
            self.lidar_dataset.visualize(device_index, sample_index)
        elif modality == 'cam':
            self.camera_dataset.visualize(device_index, sample_index)
        else:
            raise ValueError("Visualization not implemented for this modality")

    def set_visualization_backend(self, modality, backend):
        """
        Sets the visualization backend for a specific modality.

        Args:
            modality (str): The modality to set the backend for ('lidar' or 'cam').
            backend (str): The visualization backend to use.

        Raises:
            ValueError: If setting the visualization backend is not supported for the given modality.
        """
        if modality == 'lidar':
            self.lidar_dataset.set_visualization_backend(backend)
        elif modality == 'cam':
            self.camera_dataset.set_visualization_backend(backend)
        else:
            raise ValueError("Setting visualization backend is not supported for this modality")

    def get_modality(self, modality):
        if modality == 'cam':
            return self.camera_dataset
        elif modality == 'lidar':
            return self.lidar_dataset
        elif modality == 'mobility':
            return self.mobility_dataset
        elif modality == 'radar':
            return self.radar_dataset
        elif modality == 'comm':
            return self.comm_dataset
        else:
            raise KeyError(f'The modality {modality} is not available.')