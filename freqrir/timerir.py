import numpy as np
from helper import distance_for_permutations, plot_frequency_rir, plot_time_rir


def time_rir(receiver, source, room_dimensions, betas, points):
    """ 
    Calculate room impulse response in the time domain. 

    Args:
        receiver (list[float]) : Reciever 
        source (list[float]) : Source
        room_dimensions (list[float]) : Room dimensions 
        betas (list[float]) : Absorbtion coefficients. Walls: left, front, floor, right, back, ceiling.
        points (int) :  Number of points, which determines precisions of bins. 

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

    N1 = int(np.ceil(points / (room_dimensions[0]*2)))
    N2 = int(np.ceil(points / (room_dimensions[1]*2)))
    N3 = int(np.ceil(points / (room_dimensions[2]*2)))

    for NX in range(-N1, N1+1):
        for NY in range(-N2, N2+1):
            for NZ in range(-N3, N3+1):
                vector_triplet = np.array([NX, NY, NZ])
                DELP = distance_for_permutations(
                    receiver, source, room_dimensions, vector_triplet)
                # Image index for 8 image sources reflection (and original).
                IO = 0
                for L in range(0, 2):
                    for J in range(0, 2):
                        for K in range(0, 2):
                            IO += 1
                            # Impulse delay times 8, time (ms).
                            ID = int(np.ceil(DELP[IO-1]) + .5)
                            FDM1 = ID
                            ID += 1

                            # Cascade break
                            if (ID > points):
                                break

                            GID = betas[0][0]**(np.abs(NX-L))
                            GID *= betas[1][0]**(np.abs(NX))
                            GID *= betas[0][1]**(np.abs(NY-J))
                            GID *= betas[1][1]**(np.abs(NY))
                            GID *= betas[0][2]**(np.abs(NZ-K))
                            GID *= betas[1][2]**(np.abs(NZ))
                            GID /= FDM1
                            pressures[ID-1] = pressures[ID-1] + GID

                        # Cascade break
                        if (ID > points):
                            break
                    # Cascade break
                    if (ID > points):
                        break

    pressures = high_pass_filter(pressures, points)
    # Convert from sample periods to proper units.
    pressures = 2 * C * T * np.array(pressures)
    return pressures


def high_pass_filter(pressures, points):
    """ 
    High-pass digital filter to wierd behaviour at low frequencies (i.e. 100 Hz). 

    Args:
        pressures (list[complex]) : Pressure wave in the time domain. 
        points (int) : The number of points.

    Returns: 
        pressures (list[complex]): Pressure wave with frequencies below cutoff removed.
    """

    F = 100.  # Cut-off (Hz)
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
    for I in range(0, NPTS):
        X0 = pressures[I]
        pressures[I] = Y0 + A1 * Y1 + A2 * Y2
        Y2 = Y1
        Y1 = Y0
        Y0 = B1 * Y1 + B2 * Y2 + X0
    return pressures


if __name__ == "__main__":

    # All measuresments are given in terms of sample periods (i.e. ΔR = cT) (Allen 1979)
    RL = np.array([80, 120, 100])
    R0 = np.array([30, 100, 40])
    R = np.array([50, 10, 60])
    B = np.reshape([0.9, 0.9, 0.7, 0.9, 0.9, 0.7], (2, 3))

    C = 330  # (Beranek 1954, Allen 1979)
    T = 0.1  # Sampling period (ms)
    F = 8000  # Sampling rate (Hz)
    NPTS = 2048  # Number of points.

    rir = time_rir(R, R0, RL, B, NPTS)
    plot_time_rir(rir, NPTS, F)
    fft_rir = np.fft.fft(rir)
    plot_frequency_rir(fft_rir, NPTS, F)
