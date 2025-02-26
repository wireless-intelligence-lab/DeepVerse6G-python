import numpy as np
from tqdm import tqdm

from . import consts as c
from .utils import OFDM_subcarrier_frequency
from .Paths import Paths

class Channel:
    def __init__(self, tx_antenna, rx_antenna, paths, carrier_freq, bandwidth):
        """
        Initialize the Channel object.

        Parameters:
        ----------
        tx_antenna : Antenna object
            Transmitting antenna object.
        rx_antenna : Antenna object
            Receiving antenna object.
        paths : list of dict
            List containing the path parameters for each path.
        carrier_freq : float
            Carrier frequency in Hz.
        bandwidth : float
            Bandwidth in Hz.
        """
        self.tx_antenna = tx_antenna
        self.rx_antenna = rx_antenna
        self.carrier_freq = carrier_freq
        self.bandwidth = bandwidth

        self.paths = paths
        
        self.coeffs = None
        self.LoS_status = -1
        
    def generate(self):
        """
        Generate the MIMO channel based on the paths.

        Returns:
        -------
        channel : numpy.ndarray
            Generated MIMO channel.
        LoS_status : numpy.ndarray
            Line-of-sight status for each path.
        """
        raise NotImplementedError("Subclasses should implement this method")

    def __str__(self):
        """
        String representation of the Channel object for printing.
        
        Returns:
        -------
        str
            Formatted string with the Channel information.
        """
        info = (
            f"Channel Information:\n"
            f"-------------------\n"
            f"Transmitting Antenna: {self.tx_antenna}\n"
            f"Receiving Antenna: {self.rx_antenna}\n"
            f"Carrier Frequency: {self.carrier_freq} Hz\n"
            f"Bandwidth: {self.bandwidth} Hz\n"
            f"Paths: {self.paths}\n"
            f"Channel Coefficients: {self.coeffs}\n"
            f"Line-of-Sight Status: {self.LoS_status}\n"
        )
        
        return info

class OFDMChannel(Channel):
    def __init__(self, tx_antenna, rx_antenna, paths, carrier_freq, bandwidth, num_subcarriers, select_subcarriers, rx_filter, params, doppler_shift=False):
        """
        Initialize the OFDMChannel object.

        Parameters:
        ----------
        tx_antenna : Antenna object
            Transmitting antenna object.
        rx_antenna : Antenna object
            Receiving antenna object.
        paths : list of dict
            List containing the path parameters for each path.
        carrier_freq : float
            Carrier frequency in Hz.
        bandwidth : float
            Bandwidth in Hz.
        params : dict
            Dictionary containing the simulation parameters.
        """
        super().__init__(tx_antenna, rx_antenna, paths, carrier_freq, bandwidth)
        self.total_subcarriers = num_subcarriers
        self.subcarriers = select_subcarriers
        self.rx_filter = rx_filter
        self.doppler_shift = doppler_shift
        
        self.subcarrier_freq = OFDM_subcarrier_frequency(self.bandwidth, self.subcarriers, self.total_subcarriers).reshape((1, -1))
        
        self.params = params

    def generate(self):
        """
        Generate the OFDM MIMO channel based on the paths.

        Returns:
        -------
        channel : numpy.ndarray
            Generated MIMO channel.
        LoS_status : numpy.ndarray
            Line-of-sight status for each path.
        """
        
        if self.paths.num_paths() == 0:
            return
        
        
        N_tx = self.tx_antenna.num_elements()
        N_rx = self.rx_antenna.num_elements()

        channel = np.zeros((N_rx, N_tx, len(self.subcarriers)), dtype=np.csingle)

        # Antenna Array
        array_response_TX = self.tx_antenna.array_response_vector(self.paths.DoD_theta, self.paths.DoD_phi)
        array_response_RX = self.rx_antenna.array_response_vector(self.paths.DoA_theta, self.paths.DoA_phi)
        array_response = array_response_RX[:, None, :] * array_response_TX[None, :, :]
        
        # Reshaping to 2D for matrix multiplication
        array_response = array_response.reshape((N_rx*N_tx, -1))

        # Channel Impulse Response
        a, tau = self.paths.cir(doppler_shift=self.doppler_shift)
        a, tau = a.reshape((-1, 1)), tau.reshape((-1, 1))
        
        path_const = a * np.exp(-1j * 2 * np.pi * tau * self.subcarrier_freq) / np.sqrt(self.total_subcarriers)
        
        channel = array_response @ path_const
        channel = channel.reshape((N_rx, N_tx, -1))

        self.coeffs = channel


#%%
class RadarChannel(Channel):
    def __init__(self, tx_antenna, rx_antenna, paths, carrier_freq, waveform, params):
        """
        Initialize the FMCWChannel object.

        Parameters:
        ----------
        tx_antenna : Antenna object
            Transmitting antenna object.
        rx_antenna : Antenna object
            Receiving antenna object.
        paths : list of dict
            List containing the path parameters for each path.
        carrier_freq : float
            Carrier frequency in Hz.
        params : dict
            Dictionary containing the simulation parameters.
        """
        super().__init__(tx_antenna, rx_antenna, paths, carrier_freq, bandwidth=None)
        self.waveform = waveform
        self.params = params

    def generate(self):
        """
        Generate the FMCW radar signal based on the paths.

        Returns:
        -------
        IF_signal : numpy.ndarray
            Intermediate Frequency (IF) signal for FMCW radar.
        """
        array_response_TX = self.tx_antenna.array_response_vector(self.paths.DoD_theta, self.paths.DoD_phi)
        array_response_RX = self.rx_antenna.array_response_vector(self.paths.DoA_theta, self.paths.DoA_phi)
        
        # Reshaping to 2D for matrix multiplication
        array_response = array_response_RX[:, None, :] * array_response_TX[None, :, :]
        N_tx, N_rx = self.tx_antenna.num_elements(), self.rx_antenna.num_elements()
        array_response = array_response.reshape((N_rx*N_tx, -1))
        
        IF_signal = self.waveform.generate_samples(self.paths) # P x T
        
        # Sum over paths
        IF_signal = array_response @ IF_signal
        
        # N_rx x N_tx x N_chirps x N_time
        IF_signal = IF_signal.reshape((N_rx, N_tx, 
                                       self.waveform.n_chirps,
                                       self.waveform.n_samples_per_chirp))
        IF_signal = np.swapaxes(IF_signal, -1, -2)

        self.coeffs = IF_signal
    
    