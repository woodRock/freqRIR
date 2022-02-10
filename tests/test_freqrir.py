import unittest
import numpy as np
from freqrir.freqrir import frequency_rir


class TestFreqrir(unittest.TestCase):
    def test_source_and_reciever_too_close(self):
        """ Test that a ValueError is raised when the source and receiver are too close together. """
        source = np.array([0, 0, 0])
        receiver = np.array([0, 0, 0])
        room_dimensions = np.array([5, 5, 5])
        sample_frequency = 8000
        points = 80
        frequency = 1000
        betas = [[1, 1], [1, 1], [1, 1]]
        with self.assertRaises(ValueError):
            frequency_rir(source, receiver, room_dimensions,
                          betas, points, sample_frequency, frequency)
