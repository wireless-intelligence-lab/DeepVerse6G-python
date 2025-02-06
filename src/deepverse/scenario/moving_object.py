import numpy as np

class MovingObject:
    """
    Represents a moving object with properties that change over time.

    Attributes:
        object_id (str or int): A unique identifier for the moving object.
        object_scene_id (list): List of scene indices where this object exists
        type (dict): A dictionary describing the type of the object (e.g., car, pedestrian).
        time (list): A list of time stamps corresponding to the object's properties.
        location (list): A list of 3D coordinates representing the object's location at each time stamp.
        angle (list): A list of the object's orientation (e.g., yaw angle) at each time stamp.
        speed (list): A list of the object's speed at each time stamp.
        acceleration (list): A list of the object's acceleration at each time stamp.
        bounding_box (list): A list of bounding box information at each time stamp.
        tx_height (list): height of transmitting antenna above ground at each time stamp
        slope (list): A list of slope values at each time stamp.
    """
    def __init__(self, object_id, type_dict):
        """
        Initializes the MovingObject object.

        Args:
            object_id (str or int): The unique identifier for the moving object.
            type_dict (dict): A dictionary describing the type of the object.
        """
        self.object_id = object_id
        self.object_scene_id = []
        self.type = type_dict

        self.time = []
        self.location = []
        self.angle = []
        self.speed = []
        self.acceleration = []
        self.bounding_box = []
        self.tx_height = []
        self.slope = []

    def add_time_sample(self, time, properties, obj_scene_idx):
        """
        Adds a new time sample to the moving object's properties.

        Args:
            time (float): The time stamp of the sample.
            properties (dict): A dictionary of properties at the given time.
                Expected keys: 'x', 'y', 'z', 'angle', 'speed', 'acceleration', 'bounds', 'tx_height', 'slope'.
            obj_scene_idx: scene index where this object exists at this time instant
        """
        self.time.append(time)
        self.object_scene_id.append(obj_scene_idx)

        self.location.append([properties['x'], properties['y'], properties['z']])
        self.angle.append(properties['angle'])
        self.speed.append(properties['speed'])
        self.acceleration.append(properties['acceleration'])
        self.bounding_box.append(properties['bounds'])
        self.tx_height.append(properties['tx_height'])
        self.slope.append(properties['slope'])


    def get_properties_at_time(self, time):
        """
        Retrieves the object's properties at a specific time.

        Args:
            time (float): The time stamp to retrieve properties for.

        Returns:
            dict or None: A dictionary of properties at the specified time, or None if the time is not found.
        """
        try:
            index = self.time.index(time)
            return {
                'time': self.time[index],
                'location': self.location[index],
                'angle': self.angle[index],
                'speed': self.speed[index],
                'acceleration': self.acceleration[index],
                'bounding_box': self.bounding_box[index],
                'tx_height': self.tx_height[index],
                'slope': self.slope[index]
            }
        except ValueError:
            return None

    def get_all_samples(self):
        """
        Retrieves all time samples for the object.

        Returns:
            dict: A dictionary containing all time samples for each property.
        """
        return {
            'time': self.time,
            'location': self.location,
            'angle': self.angle,
            'speed': self.speed,
            'acceleration': self.acceleration,
            'bounding_box': self.bounding_box,
            'tx_height': self.tx_height,
            'slope': self.slope
        }

    def __repr__(self):
        """
        Returns a string representation of the MovingObject object.

        Returns:
            str: A string representation of the object.
        """
        return f"MovingObject(id={self.object_id}, num_time_samples={len(self.time)}, time_interval={self.time[0]},{self.time[-1]})"