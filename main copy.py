# main.py
#%%
import os
import sys

import numpy as np

sys.path.insert(0, './src')

from deepverse import ParameterManager
from deepverse.scenario import ScenarioManager
from deepverse import Dataset 

from deepverse.visualizers import ImageVisualizer, LidarVisualizer

    
#%% Parameter reading
# Create the directory if it doesn't exist
folder = 'params'
if not os.path.exists(folder):
    os.makedirs(folder)

# Path to the MATLAB configuration file
config_path = os.path.join(folder, "config.m")

# Initialize ParameterManager and load parameters
param_manager = ParameterManager(config_path)
params = param_manager.get_params()

# # Print the loaded parameters
print("Loaded Parameters:")
print(params)

#%% Parameter Test
# # Modify parameters as needed
# params['batch_size'] = np.arange(64).tolist()
#params['scenes']


# # Save the modified parameters back to a new MATLAB file
# new_matlab_config_path = os.path.join(folder, 'new_config.m')
# param_manager.save_params(new_matlab_config_path)
# print(f"Modified parameters saved to {new_matlab_config_path}")

# # Save the modified parameters to a JSON file
# new_json_config_path = os.path.join(folder, 'new_config.json')
# param_manager.save_params(new_json_config_path)
# print(f"Modified parameters saved to {new_json_config_path}")

# # Save the modified parameters to a YAML file
# new_yaml_config_path = os.path.join(folder, 'new_config.yaml')
# param_manager.save_params(new_yaml_config_path)
# print(f"Modified parameters saved to {new_yaml_config_path}")

#%% Visualization Tests
# Initialize Dataset with the new MATLAB config file (assuming Dataset class is defined)
dataset = Dataset(config_path)
dataset.scenario.visualizer.set_backend('pyvista')
dataset.scenario.visualize()
# # For demonstration, let's just show how you would generate and process batches
# for batch in dataset.generate_batches():
#     # Process or save the batch
#     pass

#%%
camera_sample = dataset.get_sample('cam', index=2, device_index=1)  # Get sample from camera 1
print(camera_sample)

# Example of retrieving specific samples and visualizing them (assuming Dataset methods are defined)
lidar_sample = dataset.get_sample('lidar', index=5, device_index=1)  # Get sample from LiDAR 1
print(lidar_sample)

#%%
radar_sample = dataset.get_sample('radar', index=1, bs_idx=0, ue_idx=0)
# There is no UE, it is the bs_tx_idx=bs_idx and bs_rx_idx=ue_idx
# Channel can be reached with:
# radar_sample.coeffs
# ------- Some print examples ----------
# print(radar_sample)
# print(radar_sample.paths)
# print(radar_sample.waveform)
# print(radar_sample.tx_antenna)
# print(radar_sample.rx_antenna)

#%%
comm_sample = dataset.get_sample('comm-ue', index=1, bs_idx=0, ue_idx=1)
# Channel can be reached with:
# comm_sample.coeffs
# ------- Some print examples ----------
# print(comm_sample)
# print(comm_sample.paths)
# print(comm_sample.LoS_status)
# print(comm_sample.tx_antenna)
# print(comm_sample.rx_antenna)

#%%
comm_bs2bs_sample = dataset.get_sample('comm-bs', index=1, bs_idx=0, ue_idx=0) 

#%%
location = dataset.get_sample('loc', index=1, ue_idx=0)

#%%
mobility = dataset.get_sample('mobility', index=1, ue_idx=0)
print(mobility)

#%%
# # %% Set visualization backend for camera and visualize samples
# for backend in ImageVisualizer.supported_backends:
#     print(f'Image Backend {backend}')
#     dataset.set_visualization_backend('camera', backend)
#     dataset.visualize('camera', 1, 2)

# #%% Set visualization backend for lidar and visualize samples
# for backend in LidarVisualizer.supported_backends:
#     print(f'Lidar Backend {backend}')
#     dataset.set_visualization_backend('lidar', backend)
#     dataset.visualize('lidar', 1, 2)
