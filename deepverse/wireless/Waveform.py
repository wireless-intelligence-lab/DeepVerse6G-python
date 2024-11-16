#%%
import numpy as np

from .utils import format_with_si_prefix
from . import consts as c

class Waveform:
    """
    A base class for waveform generation.
    """
    def generate_samples(self, t):
        """
        Generate waveform samples at specified time instances.
        
        Parameters:
        ----------
        t : numpy.ndarray
            Array of time instances at which to generate waveform samples.
        
        Returns:
        -------
        numpy.ndarray
            Waveform samples at the specified time instances.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

class FMCW(Waveform):
    """
    A subclass to generate Frequency Modulated Continuous Wave (FMCW) radar waveforms.
    """
    def __init__(self, n_chirps, n_samples_per_chirp, chirp_slope, Fs, f_0, T_period=None):
        """
        Initialize the FMCW waveform parameters.

        Parameters:
        ----------
        n_chirps : int
            Number of chirps in the FMCW waveform.
        n_samples_per_chirp : int
            Number of samples in each chirp.
        chirp_slope : float
            Chirp slope (Hz/s), defines the frequency change per second.
        Fs : float
            Sampling frequency in Hz.
        chirp_duration : float, optional
            Total duration of each chirp including the waiting time, in seconds.
        """
        self.n_chirps = n_chirps
        self.n_samples_per_chirp = n_samples_per_chirp
        self.Fs = Fs
        self.chirp_slope = chirp_slope
        self.f_0 = f_0
        
        # Calculate the active chirp duration
        self.T_chirp = n_samples_per_chirp / Fs
        
        # Total chirp duration including waiting time, defaults to active chirp duration if not provided
        self.T_period = T_period if T_period is not None else self.T_chirp
        self.T_frame = n_chirps * self.T_period
        
        self.time = np.arange(0, self.T_frame, 1./Fs)
        self.bandwidth = self.chirp_slope * self.T_chirp
        
    def __str__(self):
        slope_str = format_with_si_prefix(self.chirp_slope, 'Hz/s')
        fs_str = format_with_si_prefix(self.Fs, 'Hz')
        duration_str = format_with_si_prefix(self.T_period, 's')
        bandwidth_str = format_with_si_prefix(self.bandwidth, 'Hz')
        return (f"FMCW Radar Waveform: {self.n_chirps} chirps, {self.n_samples_per_chirp} samples/chirp, "
                f"slope: {slope_str}, sampling: {fs_str}, chirp duration: {duration_str},"
                f"BW: {bandwidth_str}")

    # TODO: Doppler velocity must be calculated on nonzeros - can improve computational complexity..
    def generate_samples(self, paths):
        """
        Generate FMCW baseband waveform samples.

        Returns:
        -------
        numpy.ndarray
            FMCW waveform samples.
        """     
        
        t = self.time.reshape((1, -1)) # Sampling times
        
        # Adjusted time for path and chirp
        a, tau = paths.cir(doppler_shift=False)
        
        a = a.reshape((-1, 1))
        tau = tau.reshape((-1, 1))
        doppler_vel = paths.doppler_vel.reshape((-1, 1))
        doppler_acc = paths.doppler_acc.reshape((-1, 1))
        
        velocity_term     = doppler_vel * t    / c.LIGHTSPEED 
        acceleration_term = doppler_acc * t**2 / c.LIGHTSPEED / 2. # This should be very small (may be removed)
        tau = tau + velocity_term + acceleration_term
        
        f_IF = self.chirp_slope * tau
        phi_IF = (self.f_0 + 0.5 * self.chirp_slope * tau) * tau # Second term may be removed
 
        # IF signal: P x T (chirp time samples)
        IF_signal = a * np.exp(1j * 2 * np.pi * (f_IF * t + phi_IF))
        
        return IF_signal