# -*- coding: utf-8 -*-
"""
DeepVerse 6G Python Implementation

Description: Antenna Functions

Authors: Umut Demirhan, Ahmed Alkhateeb
Date: 3/16/2022
"""

import DeepVerse.consts as c
import numpy as np

def array_response(ant_ind, theta, phi, kd):        
    gamma = array_response_phase(theta, phi, kd)
    return np.exp(ant_ind@gamma.T)
    
def array_response_phase(theta, phi, kd):
    gamma_x = 1j*kd*np.sin(theta)*np.cos(phi)
    gamma_y = 1j*kd*np.sin(theta)*np.sin(phi)
    gamma_z = 1j*kd*np.cos(theta)
    return np.vstack([gamma_x, gamma_y, gamma_z]).T
 
def ant_indices(panel_size):
    gamma_x = np.tile(np.arange(panel_size[0]), panel_size[1]*panel_size[2])
    gamma_y = np.tile(np.repeat(np.arange(panel_size[1]), panel_size[0]), panel_size[2])
    gamma_z = np.repeat(np.arange(panel_size[2]), panel_size[0]*panel_size[1])
    return np.vstack([gamma_x, gamma_y, gamma_z]).T

def rotate_angles(rotation, theta, phi): # Input all degrees - output radians
    theta = np.deg2rad(theta)
    phi = np.deg2rad(phi)

    if rotation is not None:
        rotation = np.deg2rad(rotation)
    
        sin_alpha = np.sin(phi - rotation[2])
        sin_beta = np.sin(rotation[1])
        sin_gamma = np.sin(rotation[0])
        cos_alpha = np.cos(phi - rotation[2])
        cos_beta = np.cos(rotation[1])
        cos_gamma = np.cos(rotation[0])
        
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        
        theta = np.arccos(cos_beta*cos_gamma*cos_theta 
                              + sin_theta*(sin_beta*cos_gamma*cos_alpha-sin_gamma*sin_alpha)
                              )
        phi = np.angle(cos_beta*sin_theta*cos_alpha-sin_beta*cos_theta 
                           + 1j*(cos_beta*sin_gamma*cos_theta 
                                 + sin_theta*(sin_beta*sin_gamma*cos_alpha + cos_gamma*sin_alpha))
                           )
    return theta, phi


class AntennaPattern():
    def __init__(self, tx_pattern, rx_pattern):
        # Initialize TX Pattern
        if tx_pattern in c.PARAMSET_ANT_RAD_PAT_VALS:
            if tx_pattern == c.PARAMSET_ANT_RAD_PAT_VALS[0]:
                self.tx_pattern_fn = None
            else:
                tx_pattern = tx_pattern.replace('-', '_')
                tx_pattern = 'pattern_' + tx_pattern
                self.tx_pattern_fn = globals()[tx_pattern]
        else:
            raise NotImplementedError('The given \'%s\' antenna radiation pattern is not applicable.' % tx_pattern)
        
        
        # Initialize RX Pattern
        if rx_pattern in c.PARAMSET_ANT_RAD_PAT_VALS:
            if rx_pattern == c.PARAMSET_ANT_RAD_PAT_VALS[0]:
                self.rx_pattern_fn = None
            else:
                rx_pattern = rx_pattern.replace('-', '_')
                rx_pattern = 'pattern_' + rx_pattern
                self.rx_pattern_fn = globals()[rx_pattern]
        else:
            raise NotImplementedError('The given \'%s\' antenna radiation pattern is not applicable.' % rx_pattern)
    
    def apply(self, power, doa_theta, doa_phi, dod_theta, dod_phi):
        pattern = 1.
        if self.tx_pattern_fn is not None:
            pattern *= self.tx_pattern_fn(dod_theta, dod_phi)
        if self.rx_pattern_fn is not None:
            pattern *= self.rx_pattern_fn(doa_theta, doa_phi)
            
        return power * pattern

def pattern_halfwave_dipole(theta, phi):
    max_gain = 1.6409223769 # Half-wave dipole maximum directivity
    theta_nonzero = theta.copy()
    zero_idx = theta_nonzero==0
    theta_nonzero[zero_idx] = 1e-4 # Approximation of 0 at limit
    pattern = max_gain * np.cos((np.pi/2)*np.cos(theta))**2 / np.sin(theta)**2
    pattern[zero_idx] = 0
    return pattern
    
