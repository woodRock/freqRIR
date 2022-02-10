# freqRIR 

[![Documentation Status](https://readthedocs.org/projects/freqrir/badge/?version=latest)](https://freqrir.readthedocs.io/en/latest/?badge=latest)
[![Python package](https://github.com/woodRock/freqRIR/actions/workflows/test.yml/badge.svg)](https://github.com/woodRock/freqRIR/actions/workflows/test.yml)

Generate a room impuse response in the frequency domain. 

## Documentation

Read the documentation [Docs](https://freqrir.readthedocs.io/en/latest/index.html)

## Time domain 

Plot a typical impulse repsonse for a room 80 x 12 x 100 sample lengths long. Wall reflection coefficients were all 0.9, ceiling and floor coefficients were 0.7. Source and receiver were at (30, 100, 40) amd (50, 10, 60) sample periods [1].

![Room impulse repsonse in time-domain](./timerir.png)

## References 

1. Allen, J. B., & Berkley, D. A. (1979). Image method for efficiently simulating small‐room acoustics. The Journal of the Acoustical Society of America, 65(4), 943-950. [Available](https://asa.scitation.org/doi/abs/10.1121/1.382599)
2. Lehmann, Eric A., and Anders M. Johansson. "Prediction of energy decay in room impulse responses simulated with an image-source model." The Journal of the Acoustical Society of America 124.1 (2008): 269-277. [Available](https://asa.scitation.org/doi/full/10.1121/1.2936367)