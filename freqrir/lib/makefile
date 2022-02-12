makefile: rirbind.cpp
	c++ -O3 -Wall -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) rirbind.cpp -o rirbind$(python3-config --extension-suffix)
