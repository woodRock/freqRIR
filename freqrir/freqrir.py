import numpy as np
from helper import distance_for_permutations, meters_to_sample_periods, sample_period_to_meters


def frequency_rir(receiver, source, room_dimensions, betas, points, frequency, c=304.8, T=1E-4):
    """ 
    Calculate room impulse response in the frequency domain. 

    Args:
        receiver (list[float]) : Reciever location in sample periods (s).
        source (list[float]) : Source location in sample periods (s).
        room_dimensions (list[float]) : Room dimensions in sample periods (s).
        betas (list[float]) : Absorbtion coefficients. Walls: left, front, floor, right, back, ceiling.
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

    N1 = int(np.ceil(points / (room_dimensions[0]*2)))
    N2 = int(np.ceil(points / (room_dimensions[1]*2)))
    N3 = int(np.ceil(points / (room_dimensions[2]*2)))

    image_count = 0

    for NX in range(-N1, N1+1):
        for NY in range(-N2, N2+1):
            for NZ in range(-N3, N3+1):
                vector_triplet = np.array([NX, NY, NZ])
                DELP = distance_for_permutations(
                    receiver, source, room_dimensions, vector_triplet)
                IO = 0
                for L in range(0, 2):
                    for J in range(0, 2):
                        for K in range(0, 2):
                            # Distance in sample periods
                            id = DELP[IO]
                            # id = DELP[IO]
                            # Distance in meters d(u,l).
                            d = sample_period_to_meters(id)
                            T = d / c  # Time delay T(.) (ms).

                            if (id > points):
                                break

                            image_count += 1

                            # Attenuation factor A(.).
                            A = betas[0][0]**(np.abs(NX-L))
                            A *= betas[1][0]**(np.abs(NX))
                            A *= betas[0][1]**(np.abs(NY-J))
                            A *= betas[1][1]**(np.abs(NY))
                            A *= betas[0][2]**(np.abs(NZ-K))
                            A *= betas[1][2]**(np.abs(NZ))
                            A /= 4 * np.pi * d

                            pressure += A * np.exp(- 1j * w * T)
                            IO += 1
                        if (id > points):
                            break
                    if (id > points):
                        break
    print(f"Image count: {image_count}")
    return pressure


if __name__ == "__main__":
    # All measuresments are given in terms of sample periods (i.e. ΔR = cT) (Allen 1979)
    source = np.array([30, 100, 40])
    receiver = np.array([50, 10, 60])
    room_dimensions = np.array([80, 120, 100])
    betas = np.reshape([0.9, 0.9, 0.7, 0.9, 0.9, 0.7], (2, 3))
    frequency = 1000  # Hz
    points = 2048

    rir = frequency_rir(receiver, source, room_dimensions,
                        betas, points, frequency)
    print(rir)
