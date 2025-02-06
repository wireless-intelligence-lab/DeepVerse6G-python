class Sensor:
    """
    Base class for representing a sensor.

    Attributes:
        sensor_id (str): A unique identifier for the sensor.
        properties (dict): A dictionary of sensor properties.
        files (list): A list of file paths associated with the sensor's data.
    """
    def __init__(self, sensor_id, properties, files):
        """
        Initializes the Sensor object.

        Args:
            sensor_id (str): The unique identifier for the sensor.
            properties (dict): A dictionary of sensor properties.
            files (list): A list of file paths associated with the sensor's data.
        """
        self.sensor_id = sensor_id
        self.properties = properties
        self.files = files

    def __repr__(self):
        """
        Returns a string representation of the Sensor object.

        Returns:
            str: A string representation of the sensor.
        """
        return f"Sensor(id={self.sensor_id}, properties={self.properties}, files={len(self.files)} files)"

    def get_files(self):
        """
        Returns the list of files associated with the sensor.

        Returns:
            list: A list of file paths.
        """
        return self.files

    def get_properties(self):
        """
        Returns the dictionary of sensor properties.

        Returns:
            dict: A dictionary of sensor properties.
        """
        return self.properties


class CameraSensor(Sensor):
    """
    Represents a camera sensor, inheriting from the Sensor class.

    Attributes:
        rotation (dict or tuple): The rotation of the camera (e.g., Euler angles, quaternion).
        location (dict or tuple): The location of the camera in 3D space.
        fov (float or dict): The field of view of the camera.
    """
    def __init__(self, sensor_id, properties, files):
        """
        Initializes the CameraSensor object.

        Args:
            sensor_id (str): The unique identifier for the camera sensor.
            properties (dict): A dictionary of camera sensor properties, including 'rotation', 'location', and 'FoV'.
            files (list): A list of file paths associated with the camera sensor's data (e.g., image files).
        """
        super().__init__(sensor_id, properties, files)
        self.rotation = properties.get('rotation')
        self.location = properties.get('location')
        self.fov = properties.get('FoV')

    def __repr__(self):
        """
        Returns a string representation of the CameraSensor object.

        Returns:
            str: A string representation of the camera sensor.
        """
        return (f"CameraSensor(id={self.sensor_id}, rotation={self.rotation}, location={self.location}, "
                f"FoV={self.fov}, files={len(self.files)} files)")


class LidarSensor(Sensor):
    """
    Represents a LiDAR sensor, inheriting from the Sensor class.

    Attributes:
        location (dict or tuple): The location of the LiDAR sensor in 3D space.
        fov (float or dict): The field of view of the LiDAR sensor.
    """
    def __init__(self, sensor_id, properties, files):
        """
        Initializes the LidarSensor object.

        Args:
            sensor_id (str): The unique identifier for the LiDAR sensor.
            properties (dict): A dictionary of LiDAR sensor properties, including 'location' and 'FoV'.
            files (list): A list of file paths associated with the LiDAR sensor's data (e.g., point cloud files).
        """
        super().__init__(sensor_id, properties, files)
        self.location = properties.get('location')
        self.fov = properties.get('FoV')

    def __repr__(self):
        """
        Returns a string representation of the LidarSensor object.

        Returns:
            str: A string representation of the LiDAR sensor.
        """
        return (f"LidarSensor(id={self.sensor_id}, location={self.location}, "
                f"FoV={self.fov}, files={len(self.files)} files)")