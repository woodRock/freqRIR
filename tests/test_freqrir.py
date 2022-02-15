import unittest
import numpy as np
from freqrir.freqrir import frequency_rir
from freqrir.helper import sample_random_receiver_locations


class TestFreqrir(unittest.TestCase):
    def test_source_and_reciever_too_close(self):
        """ Test that a ValueError is raised when the source and receiver are too close together. """
        source = np.array([0, 0, 0])
        receivers = np.array([[0, 0, 0]])
        room_dimensions = np.array([5, 5, 5])
        sample_frequency = 8000
        points = 80
        frequency = 1000
        betas = [[1, 1], [1, 1], [1, 1]]
        with self.assertRaises(ValueError):
            frequency_rir(source, receivers, room_dimensions,
                          betas, points, sample_frequency, frequency)

    def test_valid_freq_rir_call(self):
        source = np.array([0, 0, 0])
        receivers = np.array([[2, 2, 2]])
        room_dimensions = np.array([5, 5, 5])
        sample_frequency = 8000
        points = 80
        frequency = 1000
        betas = [0.92] * 6
        rir = frequency_rir(receivers, source, room_dimensions,
                            betas, points, sample_frequency, frequency)

    def test_valid_freq_rir_with_receiver_point_cloud(self):
        source = np.array([1, 1, 1])
        receivers = sample_random_receiver_locations(10, 1, [3, 3, 3])
        room_dimensions = np.array([5, 5, 5])
        sample_frequency = 16000
        points = 2048
        frequency = 1000
        betas = [0.92] * 6
        rir = frequency_rir(receivers, source, room_dimensions,
                            betas, points, sample_frequency, frequency)
        print(f"Recievers: {receivers}")
        print(f"rir: {np.unique(rir)}")
