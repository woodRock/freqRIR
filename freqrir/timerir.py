import numpy as np
from helper import distance_for_permutations, plot_time_rir


def time_rir(receiver, source, room_dimensions, betas, points, sample_frequency, c=304.8):
    """
    Calculate room impulse response in the time domain.

    Args:
        receiver (list[float] with shape (3,)) : Reciever location in sample periods (s).
        source (list[float] with shape(3,)) : Source location in sample periods (s).
        room_dimensions (list[float] with shape (3,)) : Room dimensions in sample periods (s).
        betas (float np-array with shape (3,2)) : Absorbtion coefficients. Walls: left, right, front, back, floor, ceiling.
        points (int) :  Number of points, which determines precisions of bins.
        sample_frequency (float) : Sampling frequency or sampling rate (Hz).
        c (float, optional) : Speed of sound (m/s). Defaults to 304.8 m/s (i.e. 1 ft/ms) (Allen 1979).

    Returns:
        pressures (list[complex]) : A pressure wave in the time domain.

    Raises:
        ValueError : If source and receiver are too close together (i.e. within 0.5 sampling periods).
    """

    pressures = [0] * points
    source_receiver_distance = np.linalg.norm(receiver-source)
    if (source_receiver_distance < 0.5):
        pressures[0] = 1
        raise ValueError("Source and reciever are too close to eachother.")

    n1 = int(np.ceil(points / (room_dimensions[0]*2)))
    n2 = int(np.ceil(points / (room_dimensions[1]*2)))
    n3 = int(np.ceil(points / (room_dimensions[2]*2)))

    image_count = 0

    for nx in range(-n1, n1+1):
        for ny in range(-n2, n2+1):
            for nz in range(-n3, n3+1):
                vector_triplet = np.array([nx, ny, nz])
                delp = distance_for_permutations(
                    receiver, source, room_dimensions, vector_triplet)
                # Image index for 8 image sources reflection (and original).
                io = 0
                for l in range(0, 2):
                    for j in range(0, 2):
                        for k in range(0, 2):
                            io += 1
                            # Impulse delay times 8, time (ms).
                            id = int(np.ceil(delp[io-1]) + .5)

                            fdm1 = id
                            id += 1

                            if (id > points):
                                continue

                            image_count += 1

                            gid = betas[0][0]**(np.abs(nx-l))
                            gid *= betas[0][1]**(np.abs(nx))
                            gid *= betas[1][0]**(np.abs(ny-j))
                            gid *= betas[1][1]**(np.abs(ny))
                            gid *= betas[2][0]**(np.abs(nz-k))
                            gid *= betas[2][1]**(np.abs(nz))
                            gid /= fdm1
                            pressures[id-1] = pressures[id-1] + gid

    pressures = high_pass_filter(pressures, points, sample_frequency)
    pressures = np.array(pressures)
    print(f"Image count: {image_count}")
    return pressures


def high_pass_filter(pressures, points, sample_frequency):
    """
    High-pass digital filter to wierd behaviour at low frequencies (i.e. 100 Hz).

    Args:
        pressures (list[complex]) : Pressure wave in the time domain.
        points (int) : The number of points.
        sample_frequency (float) : Sampling frequency or sampling rate (Hz).
    Returns:
        pressures (list[complex]): Pressure wave with frequencies below cutoff removed.
    """

    F = 0.01 * sample_frequency  # 0.01 of the sampling frequency (Allen 1979).
    W = 2 * np.pi * F  # Frequency variable (radians).
    T = 1E-4  # Time (s)
    R1 = np.exp(-W*T)
    R2 = R1
    B1 = 2. * R1 * np.cos(W * T)
    B2 = -R1 * R1
    A1 = -(1. + R2)
    A2 = R2
    Y1 = 0
    Y2 = 0
    Y0 = 0
    for I in range(0, points):
        X0 = pressures[I]
        pressures[I] = Y0 + A1 * Y1 + A2 * Y2
        Y2 = Y1
        Y1 = Y0
        Y0 = B1 * Y1 + B2 * Y2 + X0
    return pressures


if __name__ == "__main__":
    # All measuresments are given in terms of sample periods (i.e. ΔR = cT) (Allen 1979)
    room_dimensions = np.array([80, 120, 100])
    source = np.array([30, 100, 40])
    receiver = np.array([50, 10, 60])
    betas = np.reshape([0.9, 0.9, 0.9, 0.9, 0.7, 0.7], (3, 2))
    points = 2048
    sample_frequency = 8000  # Sampling rate (Hz)
    rir = time_rir(receiver, source, room_dimensions,
                   betas, points, sample_frequency)
    plot_time_rir(rir, points, sample_frequency, save=True)
