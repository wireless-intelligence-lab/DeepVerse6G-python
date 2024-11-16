import json
import numpy as np

# TODO: To be updated to print lists in the same line

class DeepVerseJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, range):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    
class DeepVerseJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "__ndarray__" in dct:
            return np.array(dct["__ndarray__"])
        elif "__range__" in dct:
            return range(*dct["__range__"])
        return dct