import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from . freqrir import frequency_rir


def sample_random_receiver_locations(n, radius, offset=[0, 0, 0]):
    """ Sample n random receiver locations within the volume of a point cloud with center offset.

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
    return np.array([x, y, z])


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

    This method generates a density plot for the distances from the offset. The purpose of this method is to verify that the distances are being generated with a uniformly distributed magnitude from the offset.

    Args:
        r (Array-like) : Array of reciever locations. 
        offset (list[float]) : Offset from origin for center of point cloud. Default is [0, 0, 0] (origin).

    Returns:
        d (Array-like) : Array of distances.
    """
    ds = [np.linalg.norm(np.array([rx, ry, rz]) - np.array(offset))
          for rx, ry, rz in zip(*r)]
    sns.displot(ds)
    plt.xlabel("distance")
    plt.ylabel("density")
    plt.savefig("reciever_distances_from_origin.png")
    return ds


source = np.array([30, 100, 40])
receiver = np.array([50, 10, 60])
room_dimensions = np.array([80, 120, 100])
betas = np.reshape([0.9, 0.9, 0.9, 0.9, 0.7, 0.7], (3, 2))
sampling_frequency = 8000
frequency = 1000  # Hz
points = 2048

# rir = frequency_rir(receiver, source, room_dimensions,
#                     betas, points, sampling_frequency, frequency)

radius = 1
n = 1000
offset = [2, 2, 2]
r = sample_random_receiver_locations(n, radius, offset)
plot_recievers(r, projection='3d')
plot_recievers(r, projection='2d')
[x, y, z] = r
offset = [0, 0, 0]
ds = distance_from_offset(r, offset)

print(r)
