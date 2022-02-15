"""
pyroom
======

The purpose of this example is to compared the results of the pyroomacoustics implementation to our own. We benchmark the two in terms of their exeuction time and the quality of the results. An example impulse repsonse image for both implementations for the same room setup is given below. 

.. image:: assets/pyroom.png
  :width: 400
  :alt: pyroomacoustics room impulse repsonse in time-domain.

.. image:: assets/genrrir.png
  :width: 400
  :alt: freqrir room impulse repsonse in time-domain.

The experimental setup is from (Lehmann 2008) with a point cloud added. Room dimensions :math:`[3.2, 4, 4.7]` m, source :math:`[2, 3, 2]`, reciever point cloud at center :math:`[1.1, 1, 1.2]` m and radius :math:`R_r = 1` m, sampling frequency :math:`F_s = 16` kHz, and uniform reflection coefficients :math:`\Beta = 0.92`, reverbertaion time :math:`T_{60} = 0.6` s. 

"""
import numpy as np
import matplotlib.pyplot as plt
import time
import pyroomacoustics as pra
from freqrir.helper import sample_random_receiver_locations, plot_time_rir
from freqrir.freqrir import frequency_rir
from freqrir.timerir import time_rir

# Experimental setup from (Lehmann 2008)
rt60_tgt = 0.6  # seconds (s)
room_dimensions = [3.2, 4, 2.7]  # meters (m)
e_absorption, max_order = pra.inverse_sabine(rt60_tgt, room_dimensions)
betas = [0.92] * 6  # Uniform reflection coefficients.
sample_frequency = 16000  # 16 kHz
frequency = 1000
source = [2, 3, 2]
e_absorption = 1 - np.sqrt(0.92)

py_times = []
tr_times = []
fr_times = []

# Statisical significance in results.
n_rooms = 5
for n_receivers in range(1, 5):
    for i in range(n_rooms):
        py_start = time.time()
        room = pra.ShoeBox(
            room_dimensions, fs=sample_frequency, materials=pra.Material(e_absorption), max_order=max_order,
        )
        room.add_source(source)
        receivers = sample_random_receiver_locations(
            n_receivers, 1, [1.1, 1, 1.2])
        room.add_microphone_array(list(zip(*receivers)))
        room.image_source_model()
        room.compute_rir()
        points = len(room.rir[0][0])
        rirs = [np.fft.fft(room.rir[i][0]) for i in range(n_receivers)]
        py_end = time.time()

        # tr_start = time.time()
        # rir = time_rir(receivers, source, room_dimensions, betas, points,
        #                sample_frequency, order=max_order, c=304.8)
        # rirs = [np.fft.fft(rir[i]) for i in range(n_receivers)]
        # tr_end = time.time()

        fr_start = time.time()
        rir = frequency_rir(receivers, source, room_dimensions,
                            betas, points, sample_frequency, frequency, order=max_order)
        fr_end = time.time()

        py_times.append(py_end - py_start)
        # tr_times.append(tr_end - tr_start)
        fr_times.append(fr_end - fr_start)

    print(f"n_receiv: {n_receivers}, pyroomacoustics: {np.mean(py_times)} +/- {np.std(py_times)} s, freqrir: {np.mean(fr_times)} +/- {np.std(fr_times)} s")

rir = time_rir(receivers, source, room_dimensions, betas, points,
               sample_frequency, order=max_order, c=304.8)

room.plot_rir(0)
plt.savefig("examples/assets/pyroom.png")
plot_time_rir(rir[0], points, sample_frequency, rt60_tgt,
              save="examples/assets/genrir.png")
