import matplotlib.pyplot as plt
import numpy as np


def sample_period_to_meters(x, sample_rate, c=304.8):
    """ Convert a measurement from sample periods to meters.

    Args:
        x (float): A measurement in sample periods.
        sample_rate (int): Sampling rate (Hz).
        c (float): Speed of sound (m/s). Defaults to 304.8 m/s (i.e. 1 ft/ms).

    Returns:
        x (float): A measurement in meters (m).

    Examples:
        >>> sample_period_to_meters(80, 8000) # 80 sample periods (s) at 8 kHZ
        3.048 # meters (m)
    """
    sample_period = 1 / sample_rate
    x = x * c * sample_period
    return x


def meters_to_sample_periods(x, c=304.8, T=1E-4):
    """ Convert a measurement from meters to sample periods.

    Args:
        x (float): A measurement in meters (m).
        c (float): Speed of sound (m/s). Defaults to 304.8 m/s (i.e. 1 ft/ms).
        T (float): Sampling period (s). Defaults to 1E-4 s (i.e. 0.1 ms).

    Returns:
        x (float): A measurement in sample periods (s).

    Examples:
        >>> meters_to_sample_periods(1.2) # 1.2 meters (m)
        39.370078740157474 # sample periods (s)
    """
    x = x / (c * T)
    return x


def sample_period_to_feet(x, sample_frequency, c=1000):
    """ Convert a measurement from sample periods to meters.

    Args:
        x (float): A measurement in sample periods.
        sample_frequency (int): Sampling rate (Hz). 
        c (float, optional): Speed of sound (ft/s). Defaults to 1000 ft/ms (i.e. 304.8 m/s SI).

    Returns:
        x (float): A measurement in meters (feet).

    Examples:
        >>> sample_period_to_feet(80,8000) # 80 sample periods (s)
        10 # ft
    """
    sample_period = (1 /
                     sample_frequency)
    x = x * c * sample_period
    return x


def distance_for_permutations(receiver, source, room_dimensions, vector_triplet):
    """
    Computes the distances between the reciever and the eight image source permutations.

    Args:
        receiver (list[float]): Reciever position.
        source (list[float]): Source position.
        room_dimensions (list[float]): Room dimensions.
        vector_triplet (list[float]): Vector triplet (n,l,m) (Allen 1979).

    Returns:
        distances (list[float] with shape (8,)): The distances between the reciever and the eight image source permutations.
    """
    # Add in mean radius to eight vectors to get total delay.
    r2l = 2 * np.array(vector_triplet) * np.array(room_dimensions)
    distances = []
    for l in range(-1, 2, 2):
        for j in range(-1, 2, 2):
            for k in range(-1, 2, 2):
                # l == j == j == -1 is the original source position.
                rp = receiver + np.array([l, j, k]) * source
                d = np.linalg.norm(r2l - rp)
                distances.append(d)
    return distances


def plot_time_rir(rir, points, f, save=False):
    """
    Plot room impulse repsonse in the time domain.

    Args:
        rir (list[complex]) : A pressure wave in the frequency domain.
        points (int): The number of points.
        f (int) : Sampling rate (Hz)
        save (bool) : Whether to save the plot.
    """

    length = points / 8  # Length of sample (ms)
    t = np.linspace(0, length, points)
    plt.figure(figsize=(4, 4))
    plt.stem(t, rir, 'b', markerfmt=" ", basefmt="-b")
    plt.xlabel("Time (ms)")
    plt.ylabel("Pressure (Pa)")
    plt.grid()
    # plt.ylim(-1, 1)
    plt.xlim(0, length)
    plt.text(0.5, 0.9, "Impulse Response", horizontalalignment='center',
             verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.1, f"{points} points \n{f//1000} kHz sampling rate",
             horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    if save:
        plt.savefig(f"timerir.png", dpi=300)
    plt.show()


def plot_frequency_rir(rir, points, frequency, save=False):
    """
    Plot room impulse repsonse in the frequency domain.

    Args:
        rir (list[complex]) : A pressure wave in the frequency domain.
        points (int): The number of points.
        frequency (int) : Sampling rate (Hz)
        save (bool) : Whether to save the plot.
    """

    fs = np.linspace(0, frequency, 2048)
    plt.figure(figsize=(4, 4))
    plt.stem(fs, rir, 'b', markerfmt=" ", basefmt="-b")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Pressure (Pa)")
    plt.grid()
    plt.xlim(0, frequency)
    plt.text(0.5, 0.9, "Impulse Response", horizontalalignment='center',
             verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.1, f"{points} points \n{frequency//1000} kHz sampling rate",
             horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    if save:
        plt.savefig(f"freqrir.png", dpi=300)
    plt.show()
