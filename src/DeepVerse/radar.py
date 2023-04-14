# -*- coding: utf-8 -*-
"""
DeepMIMOv2 Python Implementation

Description: MIMO channel generator

Authors: Umut Demirhan, Ahmed Alkhateeb
Date: 12/10/2021
"""

import DeepMIMO.consts as c
import numpy as np
from tqdm import tqdm
import types
from DeepVerse.antenna_func import AntennaPattern, array_response, array_response_phase, ant_indices, rotate_angles

# Generates common parameters first. The output is a numpy matrix.
def generate_radar_signal(raydata, params, tx_ant_params, rx_ant_params):
    
    chirp_params = params[c.PARAMSET_RADAR][c.PARAMSET_CHIRP]
    kd_tx = 2*np.pi*tx_ant_params[c.PARAMSET_ANT_SPACING]
    kd_rx = 2*np.pi*rx_ant_params[c.PARAMSET_ANT_SPACING]
    Ts = 1./generate_radar_signal[c.PARAMSET_CHIRP_FS]

    T_PRI = chirp_params[c.PARAMSET_CHIRP_NS]/chirp_params[c.PARAMSET_CHIRP_FS]

    antennapattern = AntennaPattern(tx_pattern = tx_ant_params[c.PARAMSET_ANT_RAD_PAT], rx_pattern = rx_ant_params[c.PARAMSET_ANT_RAD_PAT])

    M_tx = np.prod(tx_ant_params[c.PARAMSET_ANT_SHAPE])
    ant_tx_ind = ant_indices(tx_ant_params[c.PARAMSET_ANT_SHAPE])
    
    M_rx = np.prod(rx_ant_params[c.PARAMSET_ANT_SHAPE])
    ant_rx_ind = ant_indices(rx_ant_params[c.PARAMSET_ANT_SHAPE])
    
    for i in tqdm(range(len(raydata)), desc='Generating radar signal'):
        
        if raydata[i][c.OUT_PATH_NUM]==0:
            continue
        
        
        dod_theta, dod_phi = rotate_angles(rotation = tx_ant_params[c.PARAMSET_ANT_ROTATION],
                                  theta = raydata[i][c.OUT_PATH_DOD_THETA],
                                  phi = raydata[i][c.OUT_PATH_DOD_PHI])
        
        doa_theta, doa_phi = rotate_angles(rotation = rx_ant_params[c.PARAMSET_ANT_ROTATION][i],
                                  theta = raydata[i][c.OUT_PATH_DOA_THETA],
                                  phi = raydata[i][c.OUT_PATH_DOA_PHI])
        
        array_response_TX = array_response(ant_ind = ant_tx_ind, 
                                           theta = dod_theta, 
                                           phi = dod_phi, 
                                           kd = kd_tx)
        
        array_response_RX = array_response(ant_ind = ant_rx_ind, 
                                           theta =  doa_theta, 
                                           phi = doa_phi,
                                           kd = kd_rx)
        
        power = antennapattern.apply(power = raydata[i][c.OUT_PATH_RX_POW], 
                                     doa_theta = doa_theta, 
                                     doa_phi = doa_phi, 
                                     dod_theta = dod_theta, 
                                     dod_phi = dod_phi)
        
        delay_normalized = raydata[i][c.OUT_PATH_TOA]/Ts
        delay_normalized[delay_normalized>(chirp_params[c.PARAMSET_CHIRP_NS]-1)] = (chirp_params[c.PARAMSET_CHIRP_NS]-1)
    
        power[delay_normalized>(chirp_params[c.PARAMSET_CHIRP_NS]-1)] = 0

        #
        IF_sampling_mat = np.zeros((chirp_params[c.PARAMSET_CHIRP_NS], params[c.PARAMSET_RADAR][c.PARAMSET_NUM_PATHS]));
        for ll in range(num_paths):
            IF_sampling_mat[np.arange(np.ceil(delay_normalized[ll]), chirp_params[c.PARAMSET_CHIRP_NS]), ll] = 1

        # Time indices
        time_fast = Ts*np.arange(chirp_params[c.PARAMSET_CHIRP_NS])
        time_slow = time_fast + np.arange(chirp_params[c.PARAMSET_CHIRP_NS])*T_PRI
        
        # Phase shift terms of IF signal
        Tau3_rt = raydata[i][c.OUT_PATH_DOPPLER_ACC]*(time_slow**2)/(2*c.LIGHTSPEED)
        Tau2_rt = raydata[i][c.OUT_PATH_DOPPLER_VEL]*time_slow/c.LIGHTSPEED
        Tau_rt = delay_normalized*Ts + Tau2_rt + Tau3_rt

        extra_phase = np.exp(1j*np.deg2rad(raydata[i][c.OUT_PATH_PHASE]));
        phase_terms = np.exp(1j*2*np.pi*( params[c.PARAMSET_SCENARIO_PARAMS_CF]*Tau_rt - chirp_params[c.PARAMSET_CHIRP_S]*(Tau_rt**2)/2 + chirp_params[c.PARAMSET_CHIRP_S]*time_fast*Tau_rt))
        IF_mat = np.sqrt(power)*np.conj(extra_phase)*phase_terms*IF_sampling_mat
        
        IF_signal = np.sum(array_response_RX[:, np.newaxis, np.newaxis, :, np.newaxis] * array_response_TX[np.newaxis, :, np.newaxis, :, np.newaxis] * IF_mat[np.newaxis, np.newaxis, :, :, :], axis=3)
        IF_signal = np.reshape(IF_signal, (M_rx, M_tx, chirp_params[c.PARAMSET_CHIRP_NS], chirp_params[c.PARAMSET_CHIRP_NC]))

    return IF_signal