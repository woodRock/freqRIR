import unittest
import numpy as np
from freqrir.timerir import time_rir


class TestTimerir(unittest.TestCase):
    def test_source_and_reciever_too_close(self):
        """ Test that a ValueError is raised when the source and receiver are too close together. """
        source = np.array([0, 0, 0])
        receiver = np.array([0, 0, 0])
        room_dimensions = np.array([5, 5, 5])
        sample_frequency = 8000
        points = 2048
        betas = np.array([[1, 1], [1, 1], [1, 1]])
        with self.assertRaises(ValueError):
            time_rir(source, receiver, room_dimensions,
                     betas, points, sample_frequency)
