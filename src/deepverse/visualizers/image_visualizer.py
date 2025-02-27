from .base_visualizer import BaseVisualizer

class ImageVisualizer(BaseVisualizer):
    """
    Visualizer class for images that supports multiple backends including Pillow, Matplotlib, OpenCV, Plotly, and Dash.

    Attributes:
        supported_backends (list): List of supported backend names.
        backend (str): The currently selected backend.
        backend_lib (module): The library module corresponding to the selected backend.
        visualization_method (function): The method used for visualization with the selected backend.
    """
    supported_backends = ['pillow', 'matplotlib', 'opencv', 'plotly']  # Supported backends for image visualization

    def __init__(self, backend='pillow'):
        """
        Initializes the ImageVisualizer with the specified backend.

        Args:
            backend (str): The name of the backend to use for visualization. Default is 'pillow'.
        """
        super().__init__()
        # self.set_backend(backend)  # Set the default backend

    def set_backend(self, backend):
        """
        Sets the backend for image visualization and loads the corresponding library.

        Args:
            backend (str): The name of the backend to set.

        Raises:
            ValueError: If the backend is not supported.
        """
        super().set_backend(backend)  # Call the base method to set the backend
        if backend == 'pillow':
            import PIL
            self.backend_lib = PIL
        elif backend == 'matplotlib':
            import matplotlib.pyplot as plt
            self.backend_lib = plt
        elif backend == 'opencv':
            import cv2
            self.backend_lib = cv2
        elif backend == 'plotly':
            import plotly.graph_objects as go
            self.backend_lib = go

    def _visualize_with_pillow(self, image_path):
        """
        Visualizes an image using the Pillow backend.

        Args:
            image_path (str): The path to the image file.
        """
        img = self.backend_lib.Image.open(image_path)
        img.show()

    def _visualize_with_matplotlib(self, image_path):
        """
        Visualizes an image using the Matplotlib backend.

        Args:
            image_path (str): The path to the image file.
        """
        img = self.backend_lib.imread(image_path)
        self.backend_lib.imshow(img)
        self.backend_lib.axis('off')
        self.backend_lib.show()

    def _visualize_with_opencv(self, image_path):
        """
        Visualizes an image using the OpenCV backend.

        Args:
            image_path (str): The path to the image file.
        """
        img = self.backend_lib.imread(image_path)
        self.backend_lib.imshow('Image', img)
        
        # Use a loop to wait until the window is closed
        while True:
            # Wait for 1 ms and check for window close event
            if self.backend_lib.getWindowProperty('Image', self.backend_lib.WND_PROP_VISIBLE) < 1:
                break
            self.backend_lib.waitKey(1)
            
        self.backend_lib.destroyAllWindows()

    def _visualize_with_plotly(self, image_path):
        """
        Visualizes an image using the Plotly backend.

        Args:
            image_path (str): The path to the image file.
        """
        import numpy as np
        from PIL import Image

        img = Image.open(image_path)
        img_array = np.array(img)

        fig = self.backend_lib.Figure(data=[self.backend_lib.Image(z=img_array)])
        fig.show()
