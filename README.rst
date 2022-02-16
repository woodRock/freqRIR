freqRIR
=======

|Documentation Status| |Python package|

Generate a room impuse response in the frequency domain.

Documentation
-------------

Read the documentation
`Docs <https://freqrir.readthedocs.io/en/latest/index.html>`__

Time domain
-----------

Plot a typical impulse repsonse for a room 80 x 12 x 100 sample lengths
long. Wall reflection coefficients were all 0.9, ceiling and floor
coefficients were 0.7. Source and receiver were at (30, 100, 40) amd
(50, 10, 60) sample periods [1].

.. figure:: ./timerir.png
   :alt: Room impulse repsonse in time-domain

   Room impulse repsonse in time-domain

Installation
------------

The python libraries necessary ro run this can be installed using
pip as follows

.. code:: bash

   $ pip install . 
   $ pip install -r requirements.txt

Testing
-------

The unit tests are located in the ``tests`` directory, they can be run
from the root directory

.. code:: bash

   $ python -m unittest discover -s tests

References
----------

1. Allen, J. B., & Berkley, D. A. (1979). Image method for efficiently
   simulating small‐room acoustics. The Journal of the Acoustical
   Society of America, 65(4), 943-950.
   `Available <https://asa.scitation.org/doi/abs/10.1121/1.382599>`__
2. Lehmann, Eric A., and Anders M. Johansson. “Prediction of energy
   decay in room impulse responses simulated with an image-source
   model.” The Journal of the Acoustical Society of America 124.1
   (2008): 269-277.
   `Available <https://asa.scitation.org/doi/full/10.1121/1.2936367>`__
3. Peterson, P. M. (1986). Simulating the response of multiple microphones 
   to a single acoustic source in a reverberant room. The Journal of the 
   Acoustical Society of America, 80(5), 1527-1529.
   `Available <https://asa.scitation.org/doi/abs/10.1121/1.394357>`__

.. |Documentation Status| image:: https://readthedocs.org/projects/freqrir/badge/?version=latest
   :target: https://freqrir.readthedocs.io/en/latest/?badge=latest
.. |Python package| image:: https://github.com/woodRock/freqRIR/actions/workflows/test.yml/badge.svg
   :target: https://github.com/woodRock/freqRIR/actions/workflows/test.yml
