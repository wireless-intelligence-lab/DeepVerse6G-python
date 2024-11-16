# dataset.py
import os

from ..scenario import ScenarioManager

from ..parameter.parameter_manager import ParameterManager

from .modality_datasets import LiDARDataset
from .modality_datasets import RadarDataset  # Assuming this is defined elsewhere
from .modality_datasets import CommunicationDataset  # Assuming this is defined elsewhere
from .modality_datasets import CameraDataset
from .modality_datasets import MobilityDataset

class Dataset:
    def __init__(self, config_path):
        # Load Parameters
        self.param_manager = ParameterManager(config_path)
        self.params = self.param_manager.get_params()
        
        # Load Scenario
        self.scenario_path = os.path.join(self.params['dataset_folder'], self.params['scenario'])
        self.scenario = ScenarioManager(self.scenario_path)
        
        # TODO: Add an enumerator class, load by name and also update scenario manager to use the enumerator.
        if 'camera' in self.scenario.sensors:
            self.camera_dataset = CameraDataset(self.params, self.scenario.sensors['camera'])
        if 'LiDAR' in self.scenario.sensors:
            self.lidar_dataset = LiDARDataset(self.params, self.scenario.sensors['LiDAR'])
        self.mobility_dataset = MobilityDataset(self.params, self.scenario.moving_objects)
        self.radar_dataset = RadarDataset(self.param_manager.get_filtered_params('radar'))
        self.comm_dataset = CommunicationDataset(self.param_manager.get_filtered_params('comm'))
    
    def get_sample(self, modality, index, device_index=None, ue_idx=None, bs_idx=None):
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
        elif modality == 'loc':
            if ue_idx is None:
                raise ValueError("ue_idx must be specified for comm modality")
            return self.comm_dataset.get_ue_location(ue_idx, bs_idx=0, time_idx=index)
        elif modality == 'mobility':
            return self.mobility_dataset.get_sample(ue_idx, sample_index=index)
        else:
            raise ValueError("Invalid modality")

    def visualize(self, modality, device_index, sample_index):
        if modality == 'lidar':
            self.lidar_dataset.visualize(device_index, sample_index)
        elif modality == 'camera':
            self.camera_dataset.visualize(device_index, sample_index)
        else:
            raise ValueError("Visualization not implemented for this modality")
    
    def set_visualization_backend(self, modality, backend):
        if modality == 'lidar':
            self.lidar_dataset.set_visualization_backend(backend)
        elif modality == 'camera':
            self.camera_dataset.set_visualization_backend(backend)
        else:
            raise ValueError("Setting visualization backend is not supported for this modality")