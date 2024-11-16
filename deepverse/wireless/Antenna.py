import numpy as np

class Antenna:
    def __init__(self, shape, rotation, FoV, spacing, **kwargs):
        """
        Initialize the Antenna object.

        Parameters:
        ----------
        shape : tuple of int
            Size of the antenna array (num_rows, num_cols).
        rotation : tuple of float
            Rotation angles (Gamma, Beta, Alpha) in degrees.
        FoV : tuple of float
            Field of View (FoV_azimuth, FoV_elevation) in degrees.
        spacing : float
            Spacing between antenna elements.
        """
        self.shape = shape
        self.rotation = rotation
        self.FoV = FoV
        self.spacing = spacing
        
        self._element_idx = self._idx_map()
        self._kd = 2 * np.pi * self.spacing
    
    def __str__(self):
        """
        Antenna summary for printing.
        """
        return (f"Antenna - Size: {self.shape} "
                f"Rot: {self.rotation} "
                f"FoV: {self.FoV} "
                f"Spacing: {self.spacing}")
    
    def array_response_vector(self, theta, phi):
        """
        Compute the array response vector for the antenna.

        Parameters:
        ----------
        theta : numpy.ndarray
            Elevation angles of the paths in radians.
        phi : numpy.ndarray
            Azimuth angles of the paths in radians.

        Returns:
        -------
        array_response : numpy.ndarray
            The computed array response vector.
        """
        gamma = 1j * self._kd * np.array([np.sin(theta) * np.cos(phi),
                                          np.sin(theta) * np.sin(phi),
                                          np.cos(theta)])

        array_response = np.exp(np.dot(self._element_idx, gamma))
        return array_response

    def _idx_map(self):
        """
        Generate the antenna channel map for the 3D antenna array.

        Returns:
        -------
        element_idx : numpy.ndarray
            The antenna channel map as a numerical matrix.
        """
        x = 1
        y, z = self.shape
        Mz_Ind, My_Ind, Mx_Ind = np.meshgrid(np.arange(z), np.arange(y), np.arange(x), indexing='ij')
        element_idx = np.stack([Mx_Ind.ravel(), My_Ind.ravel(), Mz_Ind.ravel()], axis=-1)
        return element_idx

    def is_in_FoV(self, theta, phi):
        """
        Determine if paths are within the antenna's field of view (FoV).

        Parameters:
        ----------
        theta : numpy.ndarray
            Elevation angles of the paths in radians.
        phi : numpy.ndarray
            Azimuth angles of the paths in radians.

        Returns:
        -------
        path_inclusion : numpy.ndarray
            A boolean array indicating whether each path is within the antenna's field of view.
        """
        FoV_azimuth, FoV_elevation = np.radians(self.FoV)
        FoV_azimuth, FoV_elevation = FoV_azimuth / 2, FoV_elevation / 2
        
        azimuth_inclusion = (phi >= -FoV_azimuth) & (phi <= FoV_azimuth)
        elevation_inclusion = (theta >= (np.pi/2 - FoV_elevation)) & (theta <= (np.pi/2 + FoV_elevation))
        path_inclusion = azimuth_inclusion & elevation_inclusion
        return path_inclusion

    def apply_rotation(self, theta, phi):
        """
        Rotate the given zenith and azimuth angles by specified rotation angles.

        Parameters:
        ----------
        theta : numpy.ndarray
            Initial zenith angles in radians.
        phi : numpy.ndarray
            Initial azimuth angles in radians.

        Returns:
        -------
        Theta2 : numpy.ndarray
            Rotated zenith angles in radians.
        Phi2 : numpy.ndarray
            Rotated azimuth angles in radians.
        """
        Gamma, Beta, Alpha = np.radians(self.rotation)

        cosTheta = np.cos(theta)
        sinTheta = np.sin(theta)
        cosPhiAlpha = np.cos(phi - Alpha)
        sinPhiAlpha = np.sin(phi - Alpha)
        cosBeta = np.cos(Beta)
        sinBeta = np.sin(Beta)
        cosGamma = np.cos(Gamma)
        sinGamma = np.sin(Gamma)

        Theta2 = np.arccos(cosBeta * cosGamma * cosTheta +
                                     sinTheta * (sinBeta * cosGamma * cosPhiAlpha - sinGamma * sinPhiAlpha))

        Phi2_real = cosBeta * sinTheta * cosPhiAlpha - sinBeta * cosTheta
        Phi2_imag = cosBeta * sinGamma * cosTheta + sinTheta * (sinBeta * sinGamma * cosPhiAlpha + cosGamma * sinPhiAlpha)
        Phi2 = np.angle(Phi2_real + 1j * Phi2_imag)

        return Theta2, Phi2
    
    def num_elements(self):
        return np.prod(self.shape)