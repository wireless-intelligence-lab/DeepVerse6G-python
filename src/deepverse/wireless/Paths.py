import numpy as np

from . import consts as c

class Paths:
    def __init__(self, path_dict, carrier_freq, max_num_path=None):
        """
        Initialize the Paths object.

        Parameters:
        ----------
        DoD_theta : list or np.ndarray
            List or array of departure angles in the theta direction.
        DoD_phi : list or np.ndarray
            List or array of departure angles in the phi direction.
        DoA_theta : list or np.ndarray
            List or array of arrival angles in the theta direction.
        DoA_phi : list or np.ndarray
            List or array of arrival angles in the phi direction.
        ToA : list or np.ndarray
            List or array of times of arrival.
        power : list or np.ndarray
            List or array of path powers.
        phase : list or np.ndarray
            List or array of path phases.
        Doppler_vel : list or np.ndarray, optional
            List or array of Doppler velocities (default is None).
        Doppler_acc : list or np.ndarray, optional
            List or array of Doppler accelerations (default is None).
        """
        if max_num_path is None:
            max_num_path = len(np.array(path_dict['power']))
        self.power = np.array(path_dict['power'])[:max_num_path]
        self.phase = np.array(path_dict['phase'])[:max_num_path]
        self.ToA = np.array(path_dict['ToA'])[:max_num_path]
        
        self.DoD_theta = np.radians(np.array(path_dict['DoD_theta']))[:max_num_path]
        self.DoD_phi = np.radians(np.array(path_dict['DoD_phi']))[:max_num_path]
        self.DoA_theta = np.radians(np.array(path_dict['DoA_theta']))[:max_num_path]
        self.DoA_phi = np.radians(np.array(path_dict['DoA_phi']))[:max_num_path]
        
        if 'Doppler_vel' in path_dict.keys() and path_dict['Doppler_vel'] is not None:
            self.doppler_vel = np.array(path_dict['Doppler_vel'])[:max_num_path]
            self.doppler_acc = np.array(path_dict['Doppler_acc'])[:max_num_path]
        else:  
            self.doppler_vel = np.zeros_like(self.DoA_phi)[:max_num_path]
            self.doppler_acc = np.zeros_like(self.DoA_phi)[:max_num_path]
            
        # Other parameters
        # Make sure they are not np.ndarray for not being filtered
        self.carrier_freq = carrier_freq
        self.wavelength = self.carrier_freq / c.LIGHTSPEED
        
        self.antenna_applied = False
        
    def __str__(self):
        """
        Paths summary for printing.
        """
        return (f"Paths:\n"
                f"DoD_theta: {self.DoD_theta}\n"
                f"DoD_phi: {self.DoD_phi}\n"
                f"DoA_theta: {self.DoA_theta}\n"
                f"DoA_phi: {self.DoA_phi}\n"
                f"ToA: {self.ToA}\n"
                f"Power: {self.power}\n"
                f"Phase: {self.phase}\n"
                f"Doppler_vel: {self.doppler_vel}\n"
                f"Doppler_acc: {self.doppler_acc}")

    def cir(self, doppler_shift=False):
        a = np.sqrt(self.power) * np.exp(1j*np.radians(self.phase))
        
        if doppler_shift and self.doppler_vel is not None:
            a = self.apply_doppler(a)
            
        return a, self.ToA
    
    def apply_doppler(self, a):
        a *= np.exp(-1j * 2 * np.pi * self.ToA*(self.doppler_vel + self.ToA*self.doppler_acc/2) / self.wavelength)
        return a
    
    def num_paths(self):
        return len(self.power)
    
    def apply_antenna_parameters(self, TX_antenna, RX_antenna):
        if self.antenna_applied:
            raise RuntimeError('Antennas are already applied to the read ray-tracing parameters.')
        else:
            # Assume full inclusion if FoV is None
            in_TX_FoV = np.ones_like(self.DoD_theta, dtype=bool)  # Default to all True
            in_RX_FoV = np.ones_like(self.DoA_theta, dtype=bool)  # Default to all True
            
            if TX_antenna.rotation is not None:
                self.DoD_theta, self.DoD_phi = TX_antenna.apply_rotation(self.DoD_theta, self.DoD_phi)
            if RX_antenna.rotation is not None:
                self.DoA_theta, self.DoA_phi = RX_antenna.apply_rotation(self.DoA_theta, self.DoA_phi)
                
                
            if TX_antenna.FoV is not None:
                in_TX_FoV = TX_antenna.is_in_FoV(self.DoD_theta, self.DoD_phi)
            if RX_antenna.FoV is not None:
                in_RX_FoV = RX_antenna.is_in_FoV(self.DoA_theta, self.DoA_phi) 
            in_FoV = in_TX_FoV & in_RX_FoV
            self.apply_FoV_filter(in_FoV)

            self.antenna_applied = True
            return self
        
    def apply_FoV_filter(self, FoV_filter):
        """
        Apply a Field of View (FoV) filter to the applicable attributes of the class instance.

        Parameters:
        ----------
        FoV_filter : numpy.ndarray
            A boolean array where True values indicate the elements that should be retained.
        
        Notes:
        -----
        This method directly modifies the attributes of the instance by applying the FoV filter to
        every attribute that is an instance of a numpy.ndarray. Attributes not being numpy.ndarrays are
        not affected.
        """
        for key, array in self.__dict__.items():
            if isinstance(array, np.ndarray):  # Ensure it's a NumPy array
                self.__dict__[key] = array[FoV_filter]  # Apply the filter