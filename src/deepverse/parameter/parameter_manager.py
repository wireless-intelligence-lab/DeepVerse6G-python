# parameter_manager.py
import os
import re

# Loading/Writing Different types
import json
from .json_utils import DeepVerseJSONEncoder, DeepVerseJSONDecoder

from .yaml_utils import YAMLUtils
YAMLUtils.register() # Register custom YAML handlers

from .matlab_utils import matlab_dump, matlab_load

# TODO: Default parameters to be added!!!

class ParameterManager:
    """
    Manages the parameters for the dataset generation process by loading them from a configuration file.
    Supports multiple formats including JSON and YAML.

    Attributes:
        config_path (str): The path to the configuration file.
        params (dict): The parameters loaded from the configuration file.
    """
    
    loaders = {
        'json': ['.json'],
        'yaml': ['.yaml', '.yml'],
        'matlab': ['.m']
    }

    def __init__(self, config_path):
        """
        Initializes the ParameterManager with the specified configuration file path.

        Args:
            config_path (str): The path to the configuration file.
        """
        self.config_path = config_path
        self.params = self.load_params()


    def _get_method(self, method_type, file_extension):
        """
        Returns the appropriate method (load or save) based on the file extension.

        Args:
            method_type (str): The type of method, 'load' or 'save'.
            file_extension (str): The file extension.

        Returns:
            function: The method corresponding to the file extension.
        """
        for format, extensions in self.loaders.items():
            if file_extension in extensions:
                return getattr(self, f"_{method_type}_params_{format}")
        return None

    def get_params(self):
        """
        Returns the loaded parameters.

        Returns:
            dict: The parameters loaded from the configuration file.
        """
        return self.params

    def get_filtered_params(self, extra_key, selected_keys = ['basestations', 'dataset_folder', 'scenario', 'scenes']):
        # Create a new dictionary with selected keys
        
        filtered_params = {key: self.params[key] for key in selected_keys if key in self.params}
        
        # Add the contents of the 'extra_key' dictionary if it exists and is a dict
        if extra_key in self.params and isinstance(self.params[extra_key], dict):
            filtered_params.update(self.params[extra_key])
        else:
            # If the extra_key is not a dictionary, add it as is
            filtered_params[extra_key] = self.params.get(extra_key)
        
        return filtered_params

    def load_params(self):
        """
        Loads the parameters from the configuration file.

        Returns:
            dict: The parameters loaded from the configuration file.

        Raises:
            ValueError: If the file extension is not supported.
        """
        _, file_extension = os.path.splitext(self.config_path)
        load_method = self._get_method('load', file_extension)
        if load_method:
            return load_method()
        else:
            raise ValueError(f"Unsupported file format. Please use one of {self.get_supported_extensions()}.")

    def _load_params_json(self):
        """
        Loads the parameters from a JSON file.

        Returns:
            dict: The parameters loaded from the JSON file.
        """
        with open(self.config_path, 'r') as file:
            params = json.load(file, cls=DeepVerseJSONDecoder)
        return params

    def _load_params_yaml(self):
        """
        Loads the parameters from a YAML file.

        Returns:
            dict: The parameters loaded from the YAML file.
        """
        with open(self.config_path, 'r') as file:
            params = YAMLUtils.safe_load(file)
        return params
    
    def _load_params_matlab(self):
        """
        Loads the parameters from a MATLAB (.m) file.

        Returns:
            dict: The parameters loaded from the MATLAB file.
        """
        with open(self.config_path, 'r') as file:
            params = matlab_load(file)
        return params
            
    def save_params(self, save_path):
        """
        Saves the current parameters to the specified file path in the first supported format.

        Args:
            save_path (str): The path where the parameters should be saved.

        Raises:
            ValueError: If the file extension is not supported.
        """
        _, file_extension = os.path.splitext(save_path)
        save_method = self._get_method('save', file_extension)
        if save_method:
            save_method(save_path)
        else:
            raise ValueError(f"Unsupported file format. Please use one of {self.get_supported_extensions()}.")

    def _save_params_json(self, save_path):
        """
        Saves the current parameters to a JSON file.

        Args:
            save_path (str): The path where the parameters should be saved.
        """
        with open(save_path, 'w') as file:
            json.dump(self.params, file, cls=DeepVerseJSONEncoder, indent=4)

    def _save_params_yaml(self, save_path):
        """
        Saves the current parameters to a YAML file.

        Args:
            save_path (str): The path where the parameters should be saved.
        """
        with open(save_path, 'w') as file:
            YAMLUtils.safe_dump(self.params, file)

    def _save_params_matlab(self, save_path):
        """
        Saves the current parameters to a MATLAB (.m) file.

        Args:
            save_path (str): The path where the parameters should be saved.
        """
        with open(save_path, 'w') as file:
            matlab_dump(self.params, file)
        
    @classmethod
    def get_supported_extensions(cls):
        """
        Returns a list of all supported file extensions.

        Returns:
            list: A list of supported file extensions.
        """
        extensions = []
        for ext_list in cls.loaders.values():
            extensions.extend(ext_list)
        return extensions