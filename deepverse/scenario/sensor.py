class Sensor:
    def __init__(self, sensor_id, properties, files):
        self.sensor_id = sensor_id
        self.properties = properties
        self.files = files

    def __repr__(self):
        return f"Sensor(id={self.sensor_id}, properties={self.properties}, files={len(self.files)} files)"

    def get_files(self):
        return self.files

    def get_properties(self):
        return self.properties


class CameraSensor(Sensor):
    def __init__(self, sensor_id, properties, files):
        super().__init__(sensor_id, properties, files)
        self.rotation = properties.get('rotation')
        self.location = properties.get('location')
        self.fov = properties.get('FoV')

    def __repr__(self):
        return (f"CameraSensor(id={self.sensor_id}, rotation={self.rotation}, location={self.location}, "
                f"FoV={self.fov}, files={len(self.files)} files)")


class LidarSensor(Sensor):
    def __init__(self, sensor_id, properties, files):
        super().__init__(sensor_id, properties, files)
        self.location = properties.get('location')
        self.fov = properties.get('FoV')

    def __repr__(self):
        return (f"LidarSensor(id={self.sensor_id}, location={self.location}, "
                f"FoV={self.fov}, files={len(self.files)} files)")
