import unittest
import numpy as np
from freqrir.helper import sample_period_to_meters, meters_to_sample_periods, sample_period_to_feet, distance_for_permutations


class TestUnitConversions(unittest.TestCase):
    def test_sample_period_to_meters(self):
        """ Test conversion from sample periods to meters. """
        s = sample_period_to_meters(80, 8000)
        assert s == 3.048, "Sample period to meters conversion failed. {s} != 3.048 m"

    def test_meters_to_sample_periods(self):
        """ Test conversion from meters to sample periods. """
        m = meters_to_sample_periods(
            3.048, 8000)
        assert m == 80, f"meters_to_sample_periods() failed. {m} != 80 sample periods"

    def test_sample_period_to_feet(self):
        """ Test conversion from sample periods to feet. """
        f = sample_period_to_feet(80, 8000)
        assert f == 10, "Sample period to feet conversion failed. {f} != 10 ft"


class TestDistanceForPermuations(unittest.TestCase):
    def test_distance_for_permutations(self):
        """ Test the distance is calculated correctly for permutations of an image source. """
        room_dimensions = np.array([5, 5, 5])
        vector_triplet = np.array([0, 0, 0])  # original room.
        source = np.array([0, 0, 0])  # origin
        receiver = np.array([1, 1, 1])  # 1 meter away from origin

        d = distance_for_permutations(
            receiver, source, room_dimensions, vector_triplet)
        first = d[0]  # distance from origin to receiver
        assert len(
            d) == 8, "Eight permutations of an image source including the orignal."
        assert first == np.sqrt(
            3), f"Distance between source (at the origin) and reciever (at unit distance) was  {first} != np.sqrt(3)"
        assert np.argmin(
            d) == 0, "First distance should be the shortest distance."


if __name__ == '__main__':
    unittest.main()
