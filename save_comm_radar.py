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

    param_manager.params['scenes'] = list(range(1000, 1010))
    # param_manager.params['radar']['enable'] = False

    dataset = Dataset(param_manager)

    comm_sample_all = []
    comm_bs2bs_sample_all = []
    radar_sample_all = []
    bs_location_all = []
    ue_location_all = []

    for i in range(len(param_manager.params['scenes'])):
        comm_sample = dataset.get_sample('comm-ue', index=i, bs_idx=0, ue_idx=0).coeffs
        comm_bs2bs_sample = dataset.get_sample('comm-bs', index=i, bs_idx=0, ue_idx=0).coeffs
        radar_sample = dataset.get_sample('radar', index=i, bs_idx=0, ue_idx=0).coeffs

        bs_location = dataset.get_sample('loc-bs', index=i, bs_idx=0)
        ue_location = dataset.get_sample('loc-ue', index=i, ue_idx=0)

        comm_sample_all.append(comm_sample)
        comm_bs2bs_sample_all.append(comm_bs2bs_sample)
        radar_sample_all.append(radar_sample)
        bs_location_all.append(bs_location)
        ue_location_all.append(ue_location)
    
    comm_sample_all = np.stack(comm_sample_all, 0)
    comm_bs2bs_sample_all = np.stack(comm_bs2bs_sample_all, 0)
    bs_location_all = np.stack(bs_location_all, 0)
    ue_location_all = np.stack(ue_location_all, 0)

    mat_data = {
        'comm_sample': comm_sample_all,
        'comm_bs2bs_sample': comm_bs2bs_sample_all,
        'radar_sample': radar_sample_all,
        'bs_location': bs_location_all,
        'ue_location': bs_location_all,
    }

    save_path = f'debug_data_comm_radar/{scenario_name}_debug_data_py.mat'
    print(f'Saving to: {save_path}')
    savemat(save_path, mat_data)