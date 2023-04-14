# -*- coding: utf-8 -*-
"""
% --- DeepMIMO Python: A Generic Dataset for mmWave and massive MIMO ----%
% Authors: Umut Demirhan
% DeepMIMO test script
% Date: 3/19/2022
"""

import sys
import os
module_path = os.path.abspath('./src')
if module_path not in sys.path:
    sys.path.append(module_path)

import DeepVerse

#%% Load and print the default parameters

parameters = DeepVerse.default_params()
parameters['dataset_folder'] = r'C:\Users\demir\OneDrive\Documents\GitHub\DeepVerse\scenarios'
parameters['scenario'] = 'Scenario 1'

DeepVerse.generate_data(parameters)