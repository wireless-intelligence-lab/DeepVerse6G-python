# -*- coding: utf-8 -*-
"""
DeepMIMOv2 Python Implementation

Description: Parameters file

Authors: Umut Demirhan, Ahmed Alkhateeb
Date: 12/10/2021
"""

import numpy as np
import DeepVerse.consts as c


def default_params():
    params = {
        c.PARAMSET_DATASET_FOLDER: './Raytracing_scenarios',
        c.PARAMSET_SCENARIO: 'O1_60',

        # Active Basestation IDs
        c.PARAMSET_ACTIVE_BS: np.array([1]),

        # Dynamic scenario scene selection
        c.PARAMSET_DYNAMIC: np.array([1000, 1001]),

        c.PARAMSET_POSITION: {
            c.PARAMSET_ACTIVE: True,
        },
        c.PARAMSET_LIDAR: {
            c.PARAMSET_ACTIVE: True,
        },
        c.PARAMSET_CAMERA: {
            c.PARAMSET_ACTIVE: True,
            c.PARAMSET_IDX: np.array([1, 2, 3])
        },
        
        c.PARAMSET_COMM: {
            c.PARAMSET_ACTIVE: True,

            # Maximum # of paths to be loaded
            c.PARAMSET_NUM_PATHS: 5,

            # Subsampling
            c.PARAMSET_USER_ROW_SUBSAMP: 1,
            c.PARAMSET_USER_SUBSAMP: 1,

            # BS Antenna Parameters
            c.PARAMSET_ANT_BS: {
                # Antenna dimensions in X - Y - Z
                c.PARAMSET_ANT_SHAPE: np.array([1, 8, 4]),
                c.PARAMSET_ANT_SPACING: 0.5,
                # c.PARAMSET_ANT_ROTATION: np.array([0, 0, 0]), # Rotation around X - Y - Z axes
                # 'omni-directional'
                c.PARAMSET_ANT_RAD_PAT: c.PARAMSET_ANT_RAD_PAT_VALS[0]
            },

            # UE Antenna Parameters
            c.PARAMSET_ANT_UE: {
                # Antenna dimensions in X - Y - Z
                c.PARAMSET_ANT_SHAPE: np.array([1, 4, 2]),
                c.PARAMSET_ANT_SPACING: 0.5,
                # c.PARAMSET_ANT_ROTATION: np.array([0, 0, 0]) # Rotation around X - Y - Z axes
                # 'omni-directional'
                c.PARAMSET_ANT_RAD_PAT: c.PARAMSET_ANT_RAD_PAT_VALS[0]
            },

            c.PARAMSET_BS2BS: 1,
            c.PARAMSET_DOPPLER: 0,
            c.PARAMSET_FDTD: 1,
            # OFDM if 1
            # Time domain if 0.
            # In time domain, the channel of
            # RX antennas x TX antennas x Number of available paths is generated.
            # Each matrix of RX ant x TX ant represent the response matrix of that path.

            # OFDM Parameters
            c.PARAMSET_OFDM: {
                c.PARAMSET_OFDM_SC_NUM: 512,  # Number of total subcarriers

                c.PARAMSET_OFDM_SC_LIM: 64,  # Take first subcarriers
                c.PARAMSET_OFDM_SC_SAMP: 1,  # Sample the subcarriers
                # The selected subcarriers are given by range(0, subcarriers_limit, subcarriers_sampling)

                c.PARAMSET_OFDM_BW: 0.05,  # GHz

                # Receive Low Pass / ADC Filter
                # 0: No Filter - Delta Function
                # 1: Ideal (Rectangular) Low Pass Filter - Sinc Function
                c.PARAMSET_OFDM_LPF: 0
            }
        },
        
        c.PARAMSET_RADAR: {
            c.PARAMSET_ACTIVE: True,
            c.PARAMSET_NUM_PATHS: 5,

            # TX Antenna Parameters
            c.PARAMSET_ANT_TX: {
                # Antenna dimensions in X - Y - Z
                c.PARAMSET_ANT_SHAPE: np.array([1, 1, 4]),
                c.PARAMSET_ANT_SPACING: 0.5,
                # c.PARAMSET_ANT_ROTATION: np.array([0, 0, 0]), # Rotation around X - Y - Z axes
                # 'omni-directional'
                c.PARAMSET_ANT_RAD_PAT: c.PARAMSET_ANT_RAD_PAT_VALS[0]
            },

            # RX Antenna Parameters
            c.PARAMSET_ANT_RX: {
                # Antenna dimensions in X - Y - Z
                c.PARAMSET_ANT_SHAPE: np.array([1, 1, 2]),
                c.PARAMSET_ANT_SPACING: 0.5,
                # c.PARAMSET_ANT_ROTATION: np.array([0, 0, 0]), # Rotation around X - Y - Z axes
                # 'omni-directional'
                c.PARAMSET_ANT_RAD_PAT: c.PARAMSET_ANT_RAD_PAT_VALS[0]
            },

            c.PARAMSET_CHIRP: {
                c.PARAMSET_CHIRP_FS: 15e6,
                c.PARAMSET_CHIRP_S: 15e12,
                c.PARAMSET_CHIRP_NS: 512,
                c.PARAMSET_CHIRP_NC: 128
            }
        }
    }
    return params
