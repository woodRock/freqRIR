import numpy as np
from helper import distance_for_permutations


def frequency_rir(receiver, source, room_dimensions, betas, points, frequency):
    """Generate a room impulse response in the frequency domain. 

    :param receiver: The location of the receiver in the room.
    :type receiver: array-like of shape (3,)
    :param source: array-like of shape (3,)
    :type source: Location of the source in the room.
    :param room_dimensions: Dimensions of the room.
    :type room_dimensions: array-like of shape (3,)
    :param betas: Absorbtion coefficients of the walls.
    :type betas: array-like of shape (2,3)
    :param points: Number of points to use for the frequency response.
    :type points: int
    :param frequency: Frequency to sample at (i.e. 1000 Hz).
    :type frequency: int
    :raises ValueError: Source and reciever are too close to each other (i.e. within 0.5 sample periods).
    :return: The pressure wave at a given frequency.
    :rtype: float
    """

    source_receiver_distance = np.linalg.norm(receiver-source)
    if (source_receiver_distance < 0.5):
        raise ValueError("Source and receiver are too close to eachother.")

    w = 2 * np.pi * frequency
    pressure = 0 + 0j

    N1 = int(np.ceil(points / (room_dimensions[0]*2)))
    N2 = int(np.ceil(points / (room_dimensions[1]*2)))
    N3 = int(np.ceil(points / (room_dimensions[2]*2)))

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
                            IO += 1
                            d = DELP[IO-1]  # Distance d(u,l).
                            T = d / C  # Time delay T(.) (ms).

                            if (d > points):
                                break

                            # Attenuation factor A(.).
                            A = betas[0][0]**(np.abs(NX-L))
                            A *= betas[1][0]**(np.abs(NX))
                            A *= betas[0][1]**(np.abs(NY-J))
                            A *= betas[1][1]**(np.abs(NY))
                            A *= betas[0][2]**(np.abs(NZ-K))
                            A *= betas[1][2]**(np.abs(NZ))
                            A /= 4 * np.pi * d

                            pressure += A * np.exp(- 1j * w * T)
                        if (d > points):
                            break
                    if (d > points):
                        break
    return pressure


if __name__ == "__main__":
    # All measuresments are given in terms of sample periods (i.e. ΔR = cT) (Allen 1979)
    room_dimensions = np.array([80, 120, 100])
    source = np.array([30, 100, 40])
    receiver = np.array([50, 10, 60])
    betas = np.reshape([0.9, 0.9, 0.7, 0.9, 0.9, 0.7], (2, 3))

    C = 1000  # Speed of sound (Beranek 1954, Allen 1979)
    T = 0.1  # Sampling period (ms)
    frequency = 1000  # Frequency variable (Hz)
    points = 2048  # Number of points.

    rir = frequency_rir(receiver, source, room_dimensions,
                        betas, points, frequency)
    rir * C * T
