import numpy as np
from . helper import distance_for_permutations, sample_period_to_meters
import rirbind as rb


def frequency_rir(receivers, source, room_dimensions, betas, points, sample_frequency, frequency, c=304.8, T=1E-4, order=-1):
    """
    Calculate room impulse response in the frequency domain.

    Args:
        receiver (list[float] with shape (3,)) : Reciever location in sample periods (s).
        source (list[float] with shape(3,)) : Source location in sample periods (s).
        room_dimensions (list[float] with shape (3,)) : Room dimensions in sample periods (s).
        betas (float np-array with shape (3,2)) : Absorbtion coefficients. Walls: left, right, front, back, floor, ceiling.
        points (int) :  Number of points, which determines precisions of bins.
        sample_frequency (float) : Sampling frequency or sampling rate (Hz).
        frequency (float) : Frequency of interest (Hz).
        c (float, optional) : Speed of sound (m/s). Defaults to 304.8 m/s (i.e. 1 ft/ms) (Allen 1979).
        T (float, optional) : Sampling period (s). Defaults to 1E-4 s (i.e. 0.1 ms) (Allen 1979).
        order (int, optional) : Maximum order of reflections. Defaults to -1 (i.e. all reflections).

    Returns:
        pressure (complex) : A pressure wave in the frequency domain.

    Raises:
        ValueError : If source and receiver are too close together (i.e. within 0.5 sampling periods).
    """
    for receiver in receivers:
        source_receiver_distance = np.linalg.norm(receiver-source)
        if (source_receiver_distance < 0.5):
            raise ValueError("Source and reciever are too close to eachother.")

    direction = 'o'  # Omni-directional source.
    angle = [0, 0]  # No angle.
    isHighPass = 1  # High-pass filter is applied or not.
    nDimensions = 3  # 2d or 3d.

    rir = rb.freq_rir(c, sample_frequency, frequency, receivers, source,
                      room_dimensions, betas, angle, isHighPass, nDimensions, order, points, direction)

    return rir
