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
        
        
        M_tx = self.tx_antenna.num_elements()
        M_rx = self.rx_antenna.num_elements()

        channel = np.zeros((M_rx, M_tx, len(self.subcarriers)), dtype=np.csingle)

        # Antenna Array
        array_response_TX = self.tx_antenna.array_response_vector(self.paths.DoD_theta, self.paths.DoD_phi)
        array_response_RX = self.rx_antenna.array_response_vector(self.paths.DoA_theta, self.paths.DoA_phi)
        array_response = array_response_RX[:, None, :] * array_response_TX[None, :, :]
        # Reshaping to 2D for matrix multiplication
        N_tx, N_rx = self.tx_antenna.num_elements(), self.rx_antenna.num_elements()
        array_response = array_response.reshape((N_rx*N_tx, -1))

        # Channel Impulse Response
        a, tau = self.paths.cir(doppler_shift=self.doppler_shift)
        a, tau = a.reshape((-1, 1)), tau.reshape((-1, 1))
        
        path_const = a * np.exp(-1j * 2 * np.pi * tau * self.subcarrier_freq) / np.sqrt(self.total_subcarriers)
        
        channel = array_response @ path_const
        channel = channel.reshape((N_tx, N_rx, -1))

        self.coeffs = channel

# class TimeDomainChannel(Channel):
#     def __init__(self, tx_antenna, rx_antenna, paths, carrier_freq, bandwidth, params):
#         """
#         Initialize the TimeDomainChannel object.

#         Parameters:
#         ----------
#         tx_antenna : Antenna object
#             Transmitting antenna object.
#         rx_antenna : Antenna object
#             Receiving antenna object.
#         paths : list of dict
#             List containing the path parameters for each path.
#         carrier_freq : float
#             Carrier frequency in Hz.
#         bandwidth : float
#             Bandwidth in Hz.
#         params : dict
#             Dictionary containing the simulation parameters.
#         """
#         super().__init__(tx_antenna, rx_antenna, paths, carrier_freq, bandwidth)
#         self.params = params

#     def generate(self):
#         """
#         Generate the time-domain MIMO channel based on the paths.

#         Returns:
#         -------
#         channel : numpy.ndarray
#             Generated MIMO channel.
#         LoS_status : numpy.ndarray
#             Line-of-sight status for each path.
#         """
#         M_tx = self.tx_antenna.num_elements()
#         M_rx = self.rx_antenna.num_elements()

#         channel = np.zeros((len(self.paths), M_rx, M_tx, self.params['NUM_PATHS']), dtype=np.csingle)
#         LoS_status = np.zeros((len(self.paths)), dtype=np.int8) - 2

#         for i in tqdm(range(len(self.paths)), desc='Generating channels'):
#             if self.paths[i]['PATH_NUM'] == 0:
#                 LoS_status[i] = -1
#                 continue

#             array_response_TX = self.tx_antenna.array_response_vector(self.paths[i]['DOD_THETA'], self.paths[i]['DOD_PHI'])
#             self.rx_antenna.rotation = self.paths[i]['ROTATION']
#             array_response_RX = self.rx_antenna.array_response_vector(self.paths[i]['DOA_THETA'], self.paths[i]['DOA_PHI'])

#             channel[i, :, :, :self.paths[i]['PATH_NUM']] = array_response_RX[:, None, :] * array_response_TX[None, :, :] * (np.sqrt(self.paths[i]['RX_POW']) * np.exp(1j * np.deg2rad(self.paths[i]['PHASE'])))[None, None, :]

#         return channel, LoS_status

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
                                       self.waveform.n_samples_per_chirp, self.waveform.n_chirps))

        self.coeffs = IF_signal
    
    # # TODO: Frequency domain implementation
    # def generate_channel_coeffs_freq(self):
    #     """
    #     Generate the FMCW radar signal based on the paths, in frequency domain.

    #     Returns:
    #     -------
    #     IF_signal : numpy.ndarray
    #         Intermediate Frequency (IF) signal for FMCW radar.
    #     """
    #     Fs = self.params['Fs']
    #     Ts = 1 / Fs
    #     T_PRI = self.params['T_PRI']
    #     N_chirp = self.params['N_chirp']
    #     N_samples = self.params['N_samples']
    #     light_speed = c.LIGHTSPEED  # Speed of light in vacuum

    #     if self.paths.num_paths() == 0:
    #         return np.zeros((self.rx_antenna.num_elements(), self.tx_antenna.num_elements(), N_samples, N_chirp), dtype=np.complex64)

    #     # Define time and frequency vectors
    #     time = np.arange(N_samples) * Ts
    #     frequency = np.fft.fftfreq(N_samples, Ts)

    #     # Initialize IF signal array
    #     IF_signal = np.zeros((self.rx_antenna.num_elements(), self.tx_antenna.num_elements(), N_samples, N_chirp), dtype=np.complex64)

    #     for chirp in range(N_chirp):
    #         # Compute the frequency modulation due to each chirp
    #         time_slow = time + chirp * T_PRI
    #         phase_shift = 2 * np.pi * self.paths.doppler_shift[:, None] * time_slow  # Doppler shift phase
    #         frequency_shift = self.paths.doppler_shift[:, None] * time_slow / light_speed  # Doppler frequency shift

    #         # Compute channel response for each path
    #         path_response = np.exp(-1j * phase_shift)
    #         path_response *= np.exp(-1j * 2 * np.pi * frequency[:, None] * self.paths.ToA)  # Time delay in frequency domain
    #         path_response *= np.sqrt(self.paths.power[:, None])  # Scale by path power

    #         # Aggregate response across all paths
    #         channel_response = np.sum(path_response, axis=0)

    #         # Transform to time domain to get the IF signal for this chirp
    #         IF_signal[:, :, :, chirp] = np.fft.ifft(channel_response)

    #     return IF_signal