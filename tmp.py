# %% [markdown]
# ## Imports

# %%
import os
import sys

import numpy as np

sys.path.insert(0, './src')

from deepverse import ParameterManager
from deepverse.scenario import ScenarioManager
from deepverse import Dataset 

from deepverse.visualizers import ImageVisualizer, LidarVisualizer

# %% [markdown]
# ## Parameter reading

# %%
# Create the directory if it doesn't exist
folder = 'D:/Deepverse_data/scenarios/O1/param'
if not os.path.exists(folder):
    os.makedirs(folder)

# Path to the MATLAB configuration file
config_path = os.path.join(folder, "config_py.m")

# Initialize ParameterManager and load parameters
param_manager = ParameterManager(config_path)
params = param_manager.get_params()

# # Print the loaded parameters
print("Loaded Parameters:")
print(params)

# %% [markdown]
# ## Generate a dataset

# %%
# Generate a dataset
dataset = Dataset(config_path)

# %% [markdown]
# ## Access samples

# %% [markdown]
# ### Access camera sample

# %%
camera_sample = dataset.get_sample('cam', index=0, device_index="unit1_cam1")  # Get sample from camera 1
print(camera_sample)

# %% [markdown]
# ### Access LiDAR sample

# %%
lidar_sample = dataset.get_sample('lidar', index=0, device_index="unit1_lidar1")  # Get sample from LiDAR 1
print(lidar_sample)

# %% [markdown]
# ### Access radar sample

# %%
# radar_sample = dataset.get_sample('radar', index=0, bs_idx=0, ue_idx=0)
# There is no UE, it is the bs_tx_idx=bs_idx and bs_rx_idx=ue_idx
# Channel can be reached with:
# radar_sample.coeffs
# ------- Some print examples ----------
# print(radar_sample)
# print(radar_sample.paths)
# print(radar_sample.waveform)
# print(radar_sample.tx_antenna)
# print(radar_sample.rx_antenna)

# %% [markdown]
# ### Access BS-UE channel sample

# %%
# comm_sample = dataset.get_sample('comm-ue', index=0, bs_idx=0, ue_idx=0)
# # Channel can be reached with:
# comm_sample.coeffs
# # ------- Some print examples ----------
# print(comm_sample)
# print(comm_sample.paths)
# print(comm_sample.LoS_status)
# print(comm_sample.tx_antenna)
# print(comm_sample.rx_antenna)

# %% [markdown]
# ### Access BS-BS channel sample

# %%
comm_bs2bs_sample = dataset.get_sample('comm-bs', index=0, bs_idx=0, ue_idx=0)
# Channel can be reached with:
comm_bs2bs_sample.coeffs
# ------- Some print examples ----------
print(comm_bs2bs_sample)
print(comm_bs2bs_sample.paths)
print(comm_bs2bs_sample.LoS_status)
print(comm_bs2bs_sample.tx_antenna)
print(comm_bs2bs_sample.rx_antenna)

# %% [markdown]
# ### Access location and mobility sample

# %%
# Access bs location sample
bs_location = dataset.get_sample('loc-bs', index=0, bs_idx=0)
print(bs_location)

# Access user location sample
# ue_location = dataset.get_sample('loc-ue', index=0, ue_idx=0)
# print(ue_location)

# Access user mobility sample
mobility = dataset.get_sample('mobility', index=0, ue_idx=0)
print(mobility)

# %% [markdown]
# ## Visualization test

# %%
# Visualizing scenario
# Set visualization backend for scenario and visualize samples

dataset.scenario.visualizer.set_backend('pyvista')
dataset.scenario.visualize()

# # For demonstration, let's just show how you would generate and process batches
# for batch in dataset.generate_batches():
#     # Process or save the batch
#     pass

# %%
# Visualizing camera data
# Set visualization backend for camera and visualize samples

for backend in ImageVisualizer.supported_backends:
    print(f'Image Backend {backend}')
    dataset.set_visualization_backend('cam', backend)
    dataset.visualize('cam', 'unit1_cam1', 0)

# %%
# Visualizing LiDAR data
# Set visualization backend for lidar and visualize samples
for backend in LidarVisualizer.supported_backends:
    print(f'Lidar Backend {backend}')
    dataset.set_visualization_backend('lidar', backend)
    dataset.visualize('lidar', 'unit1_lidar1', 0)

# %% [markdown]
# ## Plot BS beam power and user position

# %% [markdown]
# ### Simple beam-steering codebook

# %%
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

# %% [markdown]
# ### Apply beam-steering codebook to channels

# %%
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

# %% [markdown]
# ### Plot video

# %%

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Create figure and axes
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# fig.subplots_adjust(hspace=0.5)

# Initialize plots
axes[0].scatter(bs_loc[0], bs_loc[1], color='b', label='BS')
ue_scatter = axes[0].scatter([0], [0], color='g', label='UE')
axes[0].set_xlim([-100, 100])
axes[0].set_ylim([0, 120])
axes[0].set_xlabel('x (m)')
axes[0].set_ylabel('y (m)')
axes[0].legend()
axes[0].axis('equal')
axes[0].grid(True)

line, = axes[1].plot(range(1, num_angles + 1), 10 * np.log10(beam_power[0]))
axes[1].set_xlim([1, num_angles])
axes[1].set_ylim([-120, -80])
axes[1].set_xlabel('Beam index')
axes[1].set_ylabel('Beam power (dB)')
axes[1].grid(True)

fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15)



# Update function for animation
def update(i):
    ue_scatter.set_offsets([ue_loc[i][0], ue_loc[i][1]])  # Update UE location
    line.set_data(range(1, num_angles + 1), 10 * np.log10(beam_power[i]))  # Update beam power
    return ue_scatter, line

# Create animation
ani = FuncAnimation(fig, update, frames=num_scene, interval=100, blit=True)

# Display the animation in Jupyter Notebook
from IPython.display import HTML
HTML(ani.to_jshtml(default_mode="once"))


