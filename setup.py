"""
Setup
======== 

A `setup.py` file given in this code is required in the root directory of the project. This installs the rirbind as a library using the pip package manager. This method is preferred, as it allows us to easily install the depedency when it is run on remote machines (i.e. GitHub actions).

Pybind 
------

pybind11 is a lightweight header-only library that exposes C++ types in Python and vice versa, mainly to create Python bindings of existing C++ code. Its goals and syntax are similar to the excellent Boost.Python library by David Abrahams: to minimize boilerplate code in traditional extension modules by inferring type information using compile-time introspection.

Installation 
------------

The following command installs the `rirbind` package through pip. The packages `setuptools` and `pybind11` are both required before running the `setup.py` file.

.. code:: bash
    $ pip install pybind11 setuptools
    $ pip install --verbose . 

"""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

__version__ = "0.0.1"

ext_modules = [
    Pybind11Extension("rirbind",
                      ["freqrir/lib/rirbind.cpp"],
                      define_macros=[('VERSION_INFO', __version__)],
                      ),
]

long_description = open("README.rst").read()

setup(
    name="freqrir",
    version=__version__,
    author="Jesse Wood",
    author_email="j.r.h.wood98@gmail.com",
    url="https://github.com/woodRock/freqRIR",
    description="A room impulse response generator using pybind11",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
)
