"""
This example creates a room with reverberation time specified by inverting Sabine's formula.
This results in a reverberation time slightly longer than desired.
The simulation is pure image source method.
The audio sample with the reverb added is saved back to `examples/samples/guitar_16k_reverb.wav`.
"""
import matplotlib.pyplot as plt
import numpy as np

import pyroomacoustics as pra

if __name__ == "__main__":
    # The desired reverberation time and dimensions of the room
    rt60_tgt = 0.3  # seconds
    fs = 16000

    n_rooms = 1000
    n_receivers = 5
    max_order = 1

    for i in range(n_rooms):
        room_dim = [10, 7.5, 3.5]  # meters

        # We invert Sabine's formula to obtain the parameters for the ISM simulator
        e_absorption, _ = pra.inverse_sabine(rt60_tgt, room_dim)

        room = pra.ShoeBox(
            room_dim, fs=fs, materials=pra.Material(e_absorption), max_order=max_order
        )
        room.add_source([2.5, 3.73, 1.76])

        mic_locs = np.random.uniform(1, 3, (3, n_receivers))
        room.add_microphone_array(mic_locs)
        room.image_source_model()
        room.compute_rir()

    rir_1_0 = room.rir[1][0]
    print(f"points {len(rir_1_0)}")

    plot = False
    if plot:
        plt.figure()
        rir_1_0 = room.rir[1][0]

        plt.subplot(2, 1, 1)
        plt.plot(np.arange(len(rir_1_0)) / room.fs, rir_1_0)
        plt.title("The RIR from source 0 to mic 1")
        plt.xlabel("Time [s]")

        plt.tight_layout()
        plt.savefig("pyroom_rir.png")
        plt.show()
