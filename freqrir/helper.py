import matplotlib.pyplot as plt
import numpy as np

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