import matplotlib.pyplot as plt
import numpy as np

def frequency_rir(receiver, source, room_dimensions, betas, points, frequency):
    """ 
    Calculate room impulse response in the frequency domain. 

    Args:
        receiver (list[float]) : Reciever location.
        source (list[float]) : Source location.
        room_dimensions (list[float]) : Room dimensions.
        betas (list[float]) : Absorbtion coefficients. Walls: left, front, floor, right, back, ceiling.
        points (int) :  Number of points, which determines precisions of bins. 

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

def plot_time_rir(rir, points, f):
    """ 
    Plot room impulse repsonse in the time domain. 

    Args:
        rir (list[complex]) : A pressure wave in the frequency domain. 
        points (int): The number of points. 
        f (int) : Sampling rate (Hz)
    """

    length = points / 8  # Length of sample (ms)
    t = np.linspace(0, length, points)
    plt.figure(figsize=(4, 4))
    plt.stem(t, rir, 'b', markerfmt=" ", basefmt="-b")
    plt.xlabel("Time (ms)")
    plt.ylabel("Pressure (Pa)")
    plt.grid()
    plt.ylim(-1, 1)
    plt.xlim(0, length)
    plt.text(0.5, 0.9, "Impulse Response", horizontalalignment='center',
             verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.1, f"{points} points \n{f//1000} kHz sampling rate",
             horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.show()


def plot_frequency_rir(rir, points, f):
    """ 
    Plot room impulse repsonse in the frequency domain. 

    Args:
        rir (list[complex]) : A pressure wave in the frequency domain. 
        points (int): The number of points. 
        f (int) : Sampling rate (Hz)
    """

    fs = np.linspace(0, F, 2048)
    plt.figure(figsize=(4, 4))
    plt.stem(fs, rir, 'b', markerfmt=" ", basefmt="-b")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Pressure (Pa)")
    plt.grid()
    plt.xlim(0, F)
    plt.text(0.5, 0.9, "Impulse Response", horizontalalignment='center',
             verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.1, f"{points} points \n{f//1000} kHz sampling rate",
             horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.show()


def distance_for_permutations(receiver, source, room_dimensions, vector_triplet):
    """ 
    Computes the distances between the reciever and the eight image source permutations. 

    Args:
        receiver (list[float]): Reciever. 
        source (list[float]): Source. 
        room_dimensions (list[float]): Room dimensions. 
        vector_triplet (list[float]): Vector triplet (n,l,m) (Allen 1979).

    Returns:
        distances (list[float]): The distances between the reciever and the eight image source permutations.
    """
    # Add in mean radius to eight vectors to get total delay.
    r2l = 2 * np.array(room_dimensions) * np.array(vector_triplet)
    distances = []
    for l in range(-1, 2, 2):
        for j in range(-1, 2, 2):
            for k in range(-1, 2, 2):
                rp = np.array(receiver) + \
                    np.array([l, j, k]) * np.array(source)
                d = np.linalg.norm(r2l - rp)
                distances.append(d)
    return distances


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
