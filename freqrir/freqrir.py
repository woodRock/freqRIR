import numpy as np
from helper import distance_for_permutations, meters_to_sample_periods, sample_period_to_meters


def frequency_rir(receiver, source, room_dimensions, betas, points, frequency, c=304.8, T=1E-4):
    """ 
    Calculate room impulse response in the frequency domain. 

    Args:
        receiver (list[float] with shape (3,)) : Reciever location in sample periods (s).
        source (list[float] with shape(3,)) : Source location in sample periods (s).
        room_dimensions (list[float] with shape (3,)) : Room dimensions in sample periods (s).
        betas (float np-array with shape (3,2)) : Absorbtion coefficients. Walls: left, right, front, back, floor, ceiling.
        points (int) :  Number of points, which determines precisions of bins. 

        c (float, optional) : Speed of sound (m/s). Defaults to 304.8 m/s (i.e. 1 ft/ms) (Allen 1979).
        T (float, optional) : Sampling period (s). Defaults to 1E-4 s (i.e. 0.1 ms) (Allen 1979).

    Returns:
        pressure (complex) : A pressure wave in the frequency domain.

    Raises:
        ValueError : If source and receiver are too close together (i.e. within 0.5 sampling periods).
    """

    source_receiver_distance = np.linalg.norm(receiver-source)
    if (source_receiver_distance < 0.5):
        raise ValueError("Source and receiver are too close to eachother.")

    w = 2 * np.pi * frequency
    pressure = 0 + 0j

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
                io = 0
                for l in range(0, 2):
                    for j in range(0, 2):
                        for k in range(0, 2):
                            io += 1
                            # Distance in sample periods
                            id = delp[io-1]
                            # Distance in meters d(u,l).
                            d = sample_period_to_meters(id)
                            T = d / c  # Time delay T(.) (ms).

                            id += 1

                            if (id > points):
                                continue

                            image_count += 1

                            # Attenuation factor A(.).
                            A = betas[0][0]**(np.abs(nx-l))
                            A *= betas[0][1]**(np.abs(nx))
                            A *= betas[1][0]**(np.abs(ny-j))
                            A *= betas[1][1]**(np.abs(ny))
                            A *= betas[2][0]**(np.abs(nz-k))
                            A *= betas[2][1]**(np.abs(nz))
                            A /= 4 * np.pi * d

                            pressure += A * np.exp(- 1j * w * T)

    print(f"Image count: {image_count}")
    return pressure


if __name__ == "__main__":
    # All measuresments are given in terms of sample periods (i.e. ΔR = cT) (Allen 1979)
    source = np.array([30, 100, 40])
    receiver = np.array([50, 10, 60])
    room_dimensions = np.array([80, 120, 100])
    betas = np.reshape([0.9, 0.9, 0.9, 0.9, 0.7, 0.7], (3, 2))
    frequency = 1000  # Hz
    points = 2048

    rir = frequency_rir(receiver, source, room_dimensions,
                        betas, points, frequency)
    print(rir)
