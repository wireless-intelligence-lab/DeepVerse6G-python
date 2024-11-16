# tests/test_base_visualizer.py
import unittest
from visualizers import BaseVisualizer

class TestBaseVisualizer(unittest.TestCase):
    def setUp(self):
        self.visualizer = BaseVisualizer()

    def test_set_backend_invalid(self):
        with self.assertRaises(ValueError):
            self.visualizer.set_backend('invalid_backend')

    def test_set_backend_valid(self):
        self.visualizer.supported_backends = ['valid_backend']
        self.visualizer.set_backend('valid_backend')
        self.assertEqual(self.visualizer.backend, 'valid_backend')

    def test_visualize_file_not_found(self):
        self.visualizer.supported_backends = ['valid_backend']
        self.visualizer.set_backend('valid_backend')
        with self.assertRaises(FileNotFoundError):
            self.visualizer.visualize('non_existent_path')

if __name__ == '__main__':
    unittest.main()