import yaml
import numpy as np

# TODO: Error with numpy array - needs to be fixed
class YAMLUtils:
    @staticmethod
    def ndarray_representer(dumper, data):
        return dumper.represent_sequence('!ndarray', data.tolist())

    @staticmethod
    def range_representer(dumper, data):
        return dumper.represent_sequence('!range', list(data))

    @staticmethod
    def ndarray_constructor(loader, node):
        return (loader.construct_sequence(node)).tolist()

    @staticmethod
    def range_constructor(loader, node):
        seq = loader.construct_sequence(node)
        return range(*seq)

    @classmethod
    def register(cls):
        yaml.add_representer(np.ndarray, cls.ndarray_representer)
        yaml.add_representer(range, cls.range_representer)

        yaml.add_constructor('!ndarray', cls.ndarray_constructor)
        yaml.add_constructor('!range', cls.range_constructor)

    @staticmethod
    def safe_dump(data, stream=None, **kwargs):
        return yaml.safe_dump(data, stream, **kwargs)

    @staticmethod
    def safe_load(stream, **kwargs):
        return yaml.safe_load(stream, **kwargs)