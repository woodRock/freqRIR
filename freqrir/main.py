import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from . freqrir import frequency_rir, frequency_rir_m
from . helper import meters_to_sample_periods


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


source = np.array([30, 100, 40])
betas = np.reshape([0.9, 0.9, 0.9, 0.9, 0.7, 0.7], (3, 2))
sample_frequency = 8000
frequency = 1000  # Hz
points = 783
radius = 1  # Meter
offset = [2, 2, 2]

n_rooms = 10
n_receivers = 5
order = 1
data = []

r = sample_random_receiver_locations(n_receivers, radius, offset)
room_dimensions = np.random.uniform(100, 300, (n_rooms, 3))

for i in range(n_rooms):
    room_dimension = room_dimensions[i]
    rir = frequency_rir_m(r, source, room_dimension,
                          betas, points, sample_frequency, frequency, order=order)
    data.append((r, rir))
