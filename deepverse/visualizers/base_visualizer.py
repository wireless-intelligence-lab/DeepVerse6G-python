# base_visualizer.py
import os

class BaseVisualizer:
    """
    Base class for visualizers that provides common functionality for setting backends 
    and checking file existence before visualization.

    Attributes:
        supported_backends (list): List of supported backend names.
        backend (str): The currently selected backend.
        backend_lib (module): The library module corresponding to the selected backend.
        visualization_method (function): The method used for visualization with the selected backend.
    """
    supported_backends = []  # List of supported backends

    def __init__(self):
        """
        Initializes the BaseVisualizer with no backend set.
        """
        self.backend = None  # Selected backend
        self.backend_lib = None  # Library corresponding to the backend
        self.visualization_method = None  # Method to visualize using the selected backend
    
    def set_backend(self, backend):
        """
        Sets the backend for visualization.

        Args:
            backend (str): The name of the backend to set.

        Raises:
            ValueError: If the backend is not supported.
        """
        if backend not in self.supported_backends:
            raise ValueError(f"Unsupported backend. Choose from {self.supported_backends}")
        self.backend = backend
        self.backend_lib = None
        
        # Get the method corresponding to the selected backend
        method_name = f"_visualize_with_{self.backend}"
        self.visualization_method = getattr(self, method_name, None)
        
        if self.visualization_method is None:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def visualize(self, file_path):
        """
        Visualizes the file using the selected backend.

        Args:
            file_path (str): The path to the file to visualize.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")
        # Call the method to visualize the file
        self.visualization_method(file_path)