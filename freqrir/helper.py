import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


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

    Examples:
        >>> distance_for_permutations(np.array([0,0,0]), np.array([1,1,1]), np.array([5,5,5]), np.array([0,0,0]))[0]
        1.7320508075688772 # Take the first element of the list.
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


def meters_to_sample_periods(x, sample_rate, c=304.8):
    """ Convert a measurement from meters to sample periods.

    Args:
        x (float): A measurement in meters (m).
        c (float): Speed of sound (m/s). Defaults to 304.8 m/s (i.e. 1 ft/ms).
        T (float): Sampling period (s). Defaults to 1E-4 s (i.e. 0.1 ms).

    Returns:
        x (float): A measurement in sample periods (s).

    Examples:
        >>> meters_to_sample_periods(3.048, 8000) # 1.2 meters (m)
        80 # sample periods (s)
    """
    sample_period = 1 / sample_rate
    x = x / (c * sample_period)
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


def sample_random_receiver_locations(n, radius, offset=[0, 0, 0]):
    """ Sample a random reciever location from within a spherical point cloud.

    Args:
        n (int) : number of receiver locations to sample.
        radius (float) : radius of the point cloud.
        offset (list[float], optional) : offset from origin for center of point cloud. Default is [0, 0, 0] (origin).

    Returns:
        r (Array-like) : Array of reciever locations.
    """
    x_off, y_off, z_off = offset
    theta = np.random.uniform(0, 2 * np.pi, n)
    phi = np.random.uniform(0, np.pi, n)
    radius = np.random.uniform(0, radius, n)
    x = radius * np.sin(theta) * np.cos(phi) + x_off
    y = radius * np.sin(theta) * np.sin(phi) + y_off
    z = radius * np.cos(theta) + z_off
    r = np.array([x, y, z])
    return [np.array(x) for x in zip(*r)]


def plot_recievers(r, projection='2d'):
    """ Plot the reciever locations.

    Args:
        r (Array-like) : Array of reciever locations.
        projection (str) : Projection of the reciever locations. Default is 2d.
    """
    [x, y, z] = r
    fig = plt.figure()
    if projection == '3d':
        ax = fig.add_subplot(111, projection=projection)
        ax.scatter(x, y, z)
    else:
        ax = fig.add_subplot(111)
        ax.scatter(x, y)
    plt.title('Reciever Locations')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.savefig(f"receiver_locations-{projection}.png")
    plt.show()


def distance_from_offset(r, offset=[0, 0, 0]):
    """ Compute the distances for the reciever locations from the offset.

    This method generates a density plot for the distances from the offset. The purpose of this method is to verify that the distances are being generated with a uniformly distributed magnitude from the offset (i.e. the center of the point cloud).

    Args:
        r (Array-like) : Array of reciever locations.
        offset (list[float]) : Offset from origin for center of point cloud. Default is [0, 0, 0] (origin).

    Returns:
        d (Array-like) : Array of distances.
    """
    ds = [np.linalg.norm(np.array([rx, ry, rz]) - np.array(offset))
          for rx, ry, rz in zip(*r)]
    sns.displot(ds)
    plt.title("Density plot for distance from offset")
    plt.xlabel("distance from offset (m)")
    plt.ylabel("density")
    plt.savefig("reciever_distances_from_origin.png")
    return ds


def plot_time_rir(rir, points, f, rt60, save=None):
    """
    Plot room impulse repsonse in the time domain.

    Args:
        rir (list[complex]) : A pressure wave in the frequency domain.
        points (int): The number of points.
        rt60 (float): The reverberation time (RT60) of the room.
        f (int) : Sampling rate (Hz)
        save (str, optional) : Save the plot to a file.
    """
    # length = points / 8  # Length of sample (ms)
    t = np.linspace(0, rt60, points)
    plt.figure(figsize=(4, 4))
    plt.stem(t, rir, 'b', markerfmt=" ", basefmt="-b")
    plt.xlabel("Time (s)")
    plt.ylabel("Pressure (Pa)")
    plt.grid()
    # plt.ylim(-1, 1)
    plt.xlim(0, rt60)  # Show until 1 second
    plt.text(0.5, 0.9, "Impulse Response", horizontalalignment='center',
             verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.1, f"{points} points \n{f//1000} kHz sampling rate",
             horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    if save:
        plt.savefig(save, dpi=300)
    plt.show()


def plot_frequency_rir(rir, points, frequency, save=None):
    """
    Plot room impulse repsonse in the frequency domain.

    Args:
        rir (list[complex]) : A pressure wave in the frequency domain.
        points (int): The number of points.
        frequency (int) : Sampling rate (Hz)
        save (str, optional) : Path to save file to. Defaults to None.
    """
    fs = np.linspace(0, frequency, points)
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
        plt.savefig(save, dpi=300)
    plt.show()
