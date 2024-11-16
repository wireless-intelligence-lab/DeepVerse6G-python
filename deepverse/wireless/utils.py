# -*- coding: utf-8 -*-
"""
DeepMIMOv3 Python Implementation

Description: Utilities

Authors: Umut Demirhan, Ahmed Alkhateeb
Date: 12/10/2021
"""

import time
import numpy as np

from . import consts as c

################################# Internal ####################################

# Sleep between print and tqdm displays
def safe_print(text, stop_dur=0.3):
    print(text)
    time.sleep(stop_dur)
        
# Determine active paths with the given configurations
# (For OFDM, only the paths within DS are activated)
class PathVerifier:
    def __init__(self, params):
        self.params = params
        if self.params[c.PARAMSET_FDTD]: # IF OFDM
            Ts = 1 / (params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_BW]*c.PARAMSET_OFDM_BW_MULT)
            self.FFT_duration = params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_SC_NUM] * Ts
            self.max_ToA = 0
            self.path_ratio_FFT = []
    
    def verify_path(self, ToA, power):
        if self.params[c.PARAMSET_FDTD]: # OFDM CH
            m_toa = np.max(ToA)
            self.max_ToA = max(self.max_ToA, m_toa)
            
            if m_toa > self.FFT_duration:
                violating_paths = ToA > self.FFT_duration
                self.path_ratio_FFT.append( sum(power[violating_paths])/sum(power) )
                        
    def notify(self):
        if self.params[c.PARAMSET_FDTD]: # IF OFDM
            avg_ratio_FFT = 0
            if len(self.path_ratio_FFT) != 0:
                avg_ratio_FFT = np.mean(self.path_ratio_FFT)*100
                
            if self.max_ToA > self.FFT_duration and avg_ratio_FFT >= 1.:
                safe_print('ToA of some paths of %i channels with an average total power of %.2f%% exceed the useful OFDM symbol duration and are clipped.' % (len(self.path_ratio_FFT), avg_ratio_FFT))
            



################################## For User ###################################

def dbm2pow(val):
    return 10 ** (val/10 - 3)

def OFDM_subcarrier_frequency(bandwidth, sampled_subcarriers, total_subcarriers):
    """
    Calculate the OFDM subcarrier frequencies.

    Parameters:
    ----------
    bandwidth : float
        Total bandwidth of the OFDM system.
    sampled_subcarriers : np.ndarray or list
        Array or list of indices of the sampled subcarriers.
    total_subcarriers : int
        Total number of subcarriers in the OFDM system.

    Returns:
    -------
    np.ndarray
        Frequencies of the sampled subcarriers.
    """
    # Calculate the bandwidth of each subcarrier
    subcarrier_bw = bandwidth / total_subcarriers

    # Shift the sampled subcarriers to be centered around zero
    sampled_subcarriers = np.array(sampled_subcarriers, dtype=float)
    # sampled_subcarriers -= np.floor(total_subcarriers / 2.)

    # Calculate the frequencies of the sampled subcarriers
    frequencies = subcarrier_bw * sampled_subcarriers

    return frequencies

def format_with_si_prefix(value, unit):
    """
    Print the numerical value with an appropriate SI prefix and specified unit.
    
    Parameters:
    ----------
    value : float
        Numerical value to be formatted.
    unit : str
        The unit of the value (e.g., 'Hz', 'm', 'g', etc.).
        
    Returns:
    -------
    str
        Formatted string representing the value with an appropriate SI prefix.
    """
    # Define the prefixes and corresponding powers of ten
    prefixes = [
        (1e12, 'T'),  # Tera
        (1e9, 'G'),   # Giga
        (1e6, 'M'),   # Mega
        (1e3, 'k'),   # Kilo
        (1, ''),      # Base unit
        (1e-3, 'm'),  # Milli
        (1e-6, 'µ'),  # Micro
        (1e-9, 'n'),  # Nano
        (1e-12, 'p')  # Pico
    ]
    
    # Determine the most suitable prefix
    for factor, prefix in prefixes:
        if abs(value) >= factor:
            return f"{value / factor:.3f} {prefix}{unit}"

    return f"{value} {unit}"  # In case the value is extremely small
