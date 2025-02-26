import os
import sys

import numpy as np
from scipy.io import savemat

# sys.path.insert(0, './src')
from src.deepverse import ParameterManager
from src.deepverse import Dataset

d_path = '//129.219.30.20/d' # "D:/"
scenario_names = ["DT1", "DT31", "I1", "O1", "Carla-Town01", "Carla-Town05"]
# scenario_names = ["DT1"]

for scenario_name in scenario_names:

    # Create the directory if it doesn't exist
    folder = f'{d_path}/Deepverse_data/scenarios/{scenario_name}/param'
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Path to the MATLAB configuration file
    config_path = os.path.join(folder, "config_py.m")

    # Initialize ParameterManager and load parameters
    param_manager = ParameterManager(config_path)
    # Set scene to 1000, this is the 1001-th scene and corresponds to the scene_1000 in wireless folder
    # The scene needs to be set to 1001 in matlab to match the result
    param_manager.params['scenes'] = [1000]

    dataset = Dataset(param_manager)

    
    cam_id = 'unit3_cam1' if scenario_name=='I1' else 'unit1_cam1'
    camera_sample = dataset.get_sample('cam', index=0, device_index=cam_id)  # Get sample from camera 1
    lidar_sample = dataset.get_sample('lidar', index=0, device_index="unit1_lidar1")  # Get sample from LiDAR 1
    radar_sample = dataset.get_sample('radar', index=0, bs_idx=0, ue_idx=0).coeffs
    comm_sample = dataset.get_sample('comm-ue', index=0, bs_idx=0, ue_idx=0).coeffs
    comm_bs2bs_sample = dataset.get_sample('comm-bs', index=0, bs_idx=0, ue_idx=0).coeffs
    bs_location = dataset.get_sample('loc-bs', index=0, bs_idx=0)
    ue_location = dataset.get_sample('loc-ue', index=0, ue_idx=0)
    object_id = 21 if scenario_name=='O1' else 0
    mobility = dataset.get_sample('mobility', index=0, object_id=object_id)
    

    mat_data = {
        'camera_sample': camera_sample,
        'lidar_sample': lidar_sample,
        'radar_sample': radar_sample,
        'comm_sample': comm_sample,
        'comm_bs2bs_sample': comm_bs2bs_sample,
        'bs_location': bs_location,
        'ue_location': ue_location,
        'mobility': mobility
    }

    save_path = f'debug_data/{scenario_name}_debug_data_py.mat'
    print(f'Saving to: {save_path}')
    savemat(save_path, mat_data)