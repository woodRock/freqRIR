import unittest
import time
import numpy as np
import pyroomacoustics as pra
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
        """ Test a valid call of the frequency rir generator."""
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
        """ Test a valid call of the frequency rir generator with a receiver point cloud."""
        source = np.array([1, 1, 1])
        receivers = sample_random_receiver_locations(10, 1, [3, 3, 3])
        room_dimensions = np.array([5, 5, 5])
        sample_frequency = 16000
        points = 2048
        frequency = 1000
        betas = [0.92] * 6
        rir = frequency_rir(receivers, source, room_dimensions,
                            betas, points, sample_frequency, frequency)

    def test_faster_than_pyroom(self):
        """ Test that the frequency rir generator is faster than pyroomacoustics. """
        rt60_tgt = 0.6  # seconds (s)
        room_dimensions = [3.2, 4, 2.7]  # meters (m)
        e_absorption, max_order = pra.inverse_sabine(rt60_tgt, room_dimensions)
        betas = [0.92] * 6  # Uniform reflection coefficients.
        sample_frequency = 16000  # 16 kHz
        frequency = 1000
        source = [2, 3, 2]
        e_absorption = 1 - np.sqrt(0.92)  # \Alpha = 1 - \Beta^2

        py_times = []
        fr_times = []

        max_receivers = 5
        n_rooms = 5
        for n_receivers in range(1, max_receivers):
            for _ in range(n_rooms):
                py_start = time.time()
                room = pra.ShoeBox(
                    room_dimensions, fs=sample_frequency,
                    materials=pra.Material(e_absorption), max_order=max_order,
                )
                room.add_source(source)
                receivers = sample_random_receiver_locations(
                    n_receivers, 1, [1.1, 1, 1.2])
                room.add_microphone_array(list(zip(*receivers)))
                room.image_source_model()
                room.compute_rir()
                points = len(room.rir[0][0])
                rirs = [np.fft.fft(room.rir[i][0]) for i in range(n_receivers)]
                py_end = time.time()

                fr_start = time.time()
                rir = frequency_rir(receivers, source, room_dimensions,
                                    betas, points, sample_frequency,
                                    frequency, order=max_order)
                fr_end = time.time()

                py_times.append(py_end - py_start)
                fr_times.append(fr_end - fr_start)

            py_time, py_std = np.mean(py_times),  np.std(py_times)
            fr_time, fr_std = np.mean(fr_times), np.std(fr_times)
            msg = f"Faster than alternative: {round(fr_time, 2)} s ± {round(fr_std,2)} s (freqrir) < {round(py_time,2)} s ± {round(py_std,2)} s (pyroom)"
            self.assertLess(fr_time, py_time, msg)
