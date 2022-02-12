"""
Pyroom Comparison
=================

The purpose of this example is to compared the results of the pyroomacoustics implementation to our own. We benchmark the two in terms of their exeuction time and the quality of the results. An example impulse repsonse image for both implementations for the same room setup is given below. 

.. image:: assets/pyroom.png
  :width: 400
  :alt: pyroomacoustics room impulse repsonse in time-domain.

.. image:: assets/genrrir.png
  :width: 400
  :alt: freqrir room impulse repsonse in time-domain.


"""
import matplotlib.pyplot as plt
import pyroomacoustics as pra
from freqrir.helper import sample_random_receiver_locations, plot_time_rir
from freqrir.timerir import time_rir
import numpy as np

# Experimental setup from (Lehmann 2008)
rt60_tgt = 0.6  # seconds (s)
room_dim = [3.2, 4, 2.7]  # meters (m)
e_absorption, max_order = pra.inverse_sabine(rt60_tgt, room_dim)
betas = [0.92] * 6  # Uniform reflection coefficients.
sample_frequency = 16000  # 16 kHz
source = [2, 3, 2]
n_rooms = 1
n_receivers = 1

e_absorption = np.sqrt(1 - 0.92)

for i in range(n_rooms):
    room = pra.ShoeBox(
        room_dim, fs=sample_frequency, materials=pra.Material(e_absorption), max_order=max_order,
    )
    room.add_source(source)
    mic_locs = sample_random_receiver_locations(
        n_receivers, 1, [1.1, 1, 1.2])  # list of(x, y, z) tuples.
    # mic_locs = [np.array((1.1, 1, 1.2))]
    room.add_microphone_array(list(zip(*mic_locs)))
    room.image_source_model()
    room.compute_rir()
    points = len(room.rir[0][0])
    rir = time_rir(mic_locs, source, room_dim,
                   betas, points, sample_frequency, order=max_order)


room.plot_rir(0)
plt.savefig("examples/rir/assets/pyroom.png")
plot_time_rir(rir[0], points, sample_frequency, rt60_tgt,
              save="examples/rir/assets/genrir.png")
