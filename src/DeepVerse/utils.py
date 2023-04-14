# -*- coding: utf-8 -*-
"""
DeepMIMOv2 Python Implementation

Description: Utilities

Authors: Umut Demirhan, Ahmed Alkhateeb
Date: 12/10/2021
"""

import time
import numpy as np

# Sleep between print and tqdm displays
def safe_print(text, stop_dur=0.3):
    print(text)
    time.sleep(stop_dur)


# MAT data is loaded as a structured array
# The function for conversion to dictionary
def structured_arr_to_dict(arr):
    if np.ndim(arr) == 0:
        if arr.dtype.names == None:
            return arr.item()
        # accessing by int does *not* work when arr is a zero-dimensional array!
        return {k: structured_arr_to_dict(arr[k]) for k in arr.dtype.names}
    return [structured_arr_to_dict(v) for v in arr]
