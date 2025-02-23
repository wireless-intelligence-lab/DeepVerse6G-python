import os
import sys

import numpy as np

sys.path.insert(0, './src')

from deepverse.parameter import ParameterManager
from deepverse.scenario import ScenarioManager
from deepverse.datasets.dataset import Dataset 

from deepverse.visualizers import ImageVisualizer, LidarVisualizer

# Create the directory if it doesn't exist
folder = 'params'
if not os.path.exists(folder):
    os.makedirs(folder)

# Path to the MATLAB configuration file
config_path = os.path.join(folder, "config.m")

# Initialize ParameterManager and load parameters
param_manager = ParameterManager(config_path)
params = param_manager.get_params()

# Print the loaded parameters
print("Loaded Parameters:")
print(params)


# Generate a dataset
dataset = Dataset(config_path)


def beam_steering_codebook(angles, num_z, num_x):
    d = 0.5
    k_z = np.arange(num_z)
    k_x = np.arange(num_x)
    
    codebook = []
    
    for beam_idx in range(angles.shape[0]):
        z_angle = angles[beam_idx, 0]
        x_angle = angles[beam_idx, 1]
        bf_vector_z = np.exp(1j * 2 * np.pi * k_z * d * np.cos(np.radians(z_angle)))
        bf_vector_x = np.exp(1j * 2 * np.pi * k_x * d * np.cos(np.radians(x_angle)))
        bf_vector = np.outer(bf_vector_z, bf_vector_x).flatten()
        codebook.append(bf_vector)
    
    return np.stack(codebook, axis=0)

# Construct beam steering codebook
num_angles = 64
x_angles = np.linspace(0, 180, num_angles + 1)[1:]
x_angles = np.flip(x_angles)
z_angles = np.full(num_angles, 90)
beam_angles = np.column_stack((z_angles, x_angles))
codebook = beam_steering_codebook(beam_angles, 1, 16)

# Apply codebook to bs-ue comm channel
beam_power = []
ue_loc = []
num_scene = len(dataset.params['scenes'])
for i in range(num_scene):
    channel = dataset.get_sample('comm-ue', index=i, bs_idx=0, ue_idx=0).coeffs
    ue_loc_ = dataset.get_sample('loc-ue', index=i, bs_idx=0, ue_idx=0)
    
    beam_power_ = (np.abs(codebook @ np.squeeze(channel, -2))**2).sum(-1)
    beam_power.append(beam_power_)

    ue_loc.append(ue_loc_)

bs_loc = dataset.get_sample('loc-bs', index=0, bs_idx=0, ue_idx=0)


print('done')