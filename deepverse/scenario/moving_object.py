import numpy as np

class MovingObject:
    def __init__(self, object_id, type_dict):
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
        return f"MovingObject(id={self.object_id}, num_time_samples={len(self.time)}, time_interval={self.time[0]},{self.time[-1]})"
    
