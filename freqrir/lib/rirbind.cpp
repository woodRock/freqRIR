#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // This is required for more complex type casts between C++ and Python (i.e. std::vector<double> to list)
#include <pybind11/complex.h>

/*
Program     : Room Impulse Response Generator

Description : Computes the response of an acoustic source to one or more
			  microphones in a reverberant room using the image method [1,2].

			  [1] J.B. Allen and D.A. Berkley,
			  Image method for efficiently simulating small-room acoustics,
			  Journal Acoustic Society of America, 65(4), April 1979, p 943.

			  [2] P.M. Peterson,
			  Simulating the response of multiple microphones to a single
			  acoustic source in a reverberant room, Journal Acoustic
			  Society of America, 80(5), November 1986.

Author      : dr.ir. E.A.P. Habets (ehabets@dereverberation.org)

Version     : 2.1.20141124

History     : 1.0.20030606 Initial version
			  1.1.20040803 + Microphone directivity
						   + Improved phase accuracy [2]
			  1.2.20040312 + Reflection order
			  1.3.20050930 + Reverberation Time
			  1.4.20051114 + Supports multi-channels
			  1.5.20051116 + High-pass filter [1]
						   + Microphone directivity control
			  1.6.20060327 + Minor improvements
			  1.7.20060531 + Minor improvements
			  1.8.20080713 + Minor improvements
			  1.9.20090822 + 3D microphone directivity control
			  2.0.20100920 + Calculation of the source-image position
							 changed in the code and tutorial.
							 This ensures a proper response to reflections
							 in case a directional microphone is used.
			  2.1.20120318 + Avoid the use of unallocated memory
			  2.1.20140721 + Fixed computation of alpha
			  2.1.20141124 + The window and sinc are now both centered
							 around t=0

Copyright (C) 2003-2014 E.A.P. Habets, The Netherlands.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/
#include "rirbind.h"

#define _USE_MATH_DEFINES
#include <cmath>

#include <limits>
#include <cstdlib>
#include <iostream>
#include <complex>

#define ROUND(x) ((x) >= 0 ? (long)((x) + 0.5) : (long)((x)-0.5))

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

template <typename T>
inline const T sinc(T const &x)
{
	return (x == 0) ? 1 : std::sin(x) / x;
}

double sim_microphone(double x, double y, double z, double *angle, char mtype)
{
	if (mtype == 'b' || mtype == 'c' || mtype == 's' || mtype == 'h')
	{
		double gain, vartheta, varphi, rho;

		// Polar Pattern         rho
		// ---------------------------
		// Bidirectional         0
		// Hypercardioid         0.25
		// Cardioid              0.5
		// Subcardioid           0.75
		// Omnidirectional       1

		switch (mtype)
		{
		case 'b':
			rho = 0;
			break;
		case 'h':
			rho = 0.25;
			break;
		case 'c':
			rho = 0.5;
			break;
		case 's':
			rho = 0.75;
			break;
		};

		vartheta = acos(z / sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2)));
		varphi = atan2(y, x);

		gain = sin(M_PI / 2 - angle[1]) * sin(vartheta) * cos(angle[0] - varphi) + cos(M_PI / 2 - angle[1]) * cos(vartheta);
		gain = rho + (1 - rho) * gain;

		return gain;
	}
	else
	{
		return 1;
	}
}

std::vector<std::vector<double>> time_rir(double c, double fs, const std::vector<std::vector<double>> &rr, const std::vector<double> &ss, const std::vector<double> &LL, const std::vector<double> &beta_input, const std::vector<double> &orientation, int isHighPassFilter, int nDimension, int nOrder, int nSamples, char microphone_type)
{
	// | Room Impulse Response Generator                                  |\n"
	// |                                                                  |\n"
	// | Computes the response of an acoustic source to one or more       |\n"
	// | microphones in a reverberant room using the image method [1,2].  |\n"
	// |                                                                  |\n"
	// | Author    : dr.ir. Emanuel Habets (ehabets@dereverberation.org)  |\n"
	// |                                                                  |\n"
	// | Version   : 2.1.20141124                                         |\n"
	// |                                                                  |\n"
	// | Copyright (C) 2003-2014 E.A.P. Habets, The Netherlands.          |\n"
	// |                                                                  |\n"
	// | [1] J.B. Allen and D.A. Berkley,                                 |\n"
	// |     Image method for efficiently simulating small-room acoustics,|\n"
	// |     Journal Acoustic Society of America,                         |\n"
	// |     65(4), April 1979, p 943.                                    |\n"
	// |                                                                  |\n"
	// | [2] P.M. Peterson,                                               |\n"
	// |     Simulating the response of multiple microphones to a single  |\n"
	// |     acoustic source in a reverberant room, Journal Acoustic      |\n"
	// |     Society of America, 80(5), November 1986.                    |\n"
	// --------------------------------------------------------------------\n\n"
	// function [h, beta_hat] = rir_generator(c, fs, r, s, L, beta, nsample,\n"
	//  mtype, order, dim, orientation, hp_filter);\n\n"
	// Input parameters:\n"
	//  c           : sound velocity in m/s.\n"
	//  fs          : sampling frequency in Hz.\n"
	//  r           : M x 3 array specifying the (x,y,z) coordinates of the\n"
	//                receiver(s) in m.\n"
	//  s           : 1 x 3 vector specifying the (x,y,z) coordinates of the\n"
	//                source in m.\n"
	//  L           : 1 x 3 vector specifying the room dimensions (x,y,z) in m.\n"
	//  beta        : 1 x 6 vector specifying the reflection coefficients\n"
	//                [beta_x1 beta_x2 beta_y1 beta_y2 beta_z1 beta_z2] or\n"
	//                beta = reverberation time (T_60) in seconds.\n"
	//  nsample     : number of samples to calculate, default is T_60*fs.\n"
	//  mtype       : [omnidirectional, subcardioid, cardioid, hypercardioid,\n"
	//                bidirectional], default is omnidirectional.\n"
	//  order       : reflection order, default is -1, i.e. maximum order.\n"
	//  dim         : room dimension (2 or 3), default is 3.\n"
	//  orientation : direction in which the microphones are pointed, specified using\n"
	//                azimuth and elevation angles (in radians), default is [0 0].\n"
	//  hp_filter   : use 'false' to disable high-pass filter, the high-pass filter\n"
	//                is enabled by default.\n\n"
	// Output parameters:\n"
	//  h           : M x nsample matrix containing the calculated room impulse\n"
	//                response(s).\n"
	//  beta_hat    : In case a reverberation time is specified as an input parameter\n"
	//                the corresponding reflection coefficient is returned.\n\n");

	// Load parameters
	int nMicrophones = rr.size();
	double beta[6];
	double angle[2];
	double reverberation_time;

	if (beta_input.size() == 1)
	{
		double V = LL[0] * LL[1] * LL[2];
		double S = 2 * (LL[0] * LL[2] + LL[1] * LL[2] + LL[0] * LL[1]);
		reverberation_time = beta_input[0];
		if (reverberation_time != 0)
		{
			double alfa = 24 * V * log(10.0) / (c * S * reverberation_time);
			// if (alfa > 1)
			// 	mexErrMsgTxt("Error: The reflection coefficients cannot be calculated using the current "
			// 	             "room parameters, i.e. room size and reverberation time.\n           Please "
			// 	             "specify the reflection coefficients or change the room parameters.");
			for (int i = 0; i < 6; i++)
				beta[i] = sqrt(1 - alfa);
		}
		else
		{
			for (int i = 0; i < 6; i++)
				beta[i] = 0;
		}
	}
	else
	{
		for (int i = 0; i < 6; i++)
			beta[i] = beta_input[i];
	}

	// 3D Microphone orientation (optional)
	if (orientation.size())
	{
		angle[0] = orientation[0];
		angle[1] = orientation[1];
	}
	else
	{
		angle[0] = 0;
		angle[1] = 0;
	}

	// Room Dimension (optional)
	// if (nDimension != 2 && nDimension != 3)
	//     mexErrMsgTxt("Invalid input arguments! (9)");
	if (nDimension == 2)
	{
		beta[4] = 0;
		beta[5] = 0;
	}

	// Reflection order (optional)
	if (nOrder < -1)
	{
		// mexErrMsgTxt("Invalid input arguments! (8)");
	}

	// Number of samples (optional)
	if (nSamples == -1)
	{
		if (beta_input.size() > 1)
		{
			double V = LL[0] * LL[1] * LL[2];
			double alpha = ((1 - pow(beta[0], 2)) + (1 - pow(beta[1], 2))) * LL[1] * LL[2] +
						   ((1 - pow(beta[2], 2)) + (1 - pow(beta[3], 2))) * LL[0] * LL[2] +
						   ((1 - pow(beta[4], 2)) + (1 - pow(beta[5], 2))) * LL[0] * LL[1];
			reverberation_time = 24 * log(10.0) * V / (c * alpha);
			if (reverberation_time < 0.128)
				reverberation_time = 0.128;
		}
		nSamples = (int)(reverberation_time * fs);
	}

	// Create output vector
	std::vector<std::vector<double>> imp(nMicrophones);
	for (int idxMicrophone = 0; idxMicrophone < nMicrophones; idxMicrophone++)
		imp[idxMicrophone].resize(nSamples);

	// Temporary variables and constants (high-pass filter)
	const double W = 2 * M_PI * 100 / fs; // The cut-off frequency equals 100 Hz
	const double R1 = exp(-W);
	const double B1 = 2 * R1 * cos(W);
	const double B2 = -R1 * R1;
	const double A1 = -(1 + R1);
	double X0;
	double *Y = new double[3];

	// Temporary variables and constants (image-method)
	const double Fc = 1;				  // The cut-off frequency equals fs/2 - Fc is the normalized cut-off frequency.
	const int Tw = 2 * ROUND(0.004 * fs); // The width of the low-pass FIR equals 8 ms
	const double cTs = c / fs;
	double *LPI = new double[Tw];
	double *r = new double[3];
	double *s = new double[3];
	double *L = new double[3];
	double Rm[3];
	double Rp_plus_Rm[3];
	double refl[6];
	double fdist, dist;
	double gain;
	double b, d; // Beta absorbtion coefficient, distance.
	int startPosition;
	int n1, n2, n3;
	int q, j, k;
	int mx, my, mz;
	int n;

	s[0] = ss[0] / cTs;
	s[1] = ss[1] / cTs;
	s[2] = ss[2] / cTs;
	L[0] = LL[0] / cTs;
	L[1] = LL[1] / cTs;
	L[2] = LL[2] / cTs;

	for (int idxMicrophone = 0; idxMicrophone < nMicrophones; idxMicrophone++)
	{
		// [x_1 x_2 ... x_N y_1 y_2 ... y_N z_1 z_2 ... z_N]
		r[0] = rr[idxMicrophone][0] / cTs;
		r[1] = rr[idxMicrophone][1] / cTs;
		r[2] = rr[idxMicrophone][2] / cTs;

		n1 = (int)ceil(nSamples / (2 * L[0]));
		n2 = (int)ceil(nSamples / (2 * L[1]));
		n3 = (int)ceil(nSamples / (2 * L[2]));

		// Generate room impulse response
		for (mx = -n1; mx <= n1; mx++)
		{
			refl[0] = pow(beta[1], std::abs(mx));
			Rm[0] = 2 * mx * L[0];
			for (my = -n2; my <= n2; my++)
			{
				refl[1] = pow(beta[3], std::abs(my));
				Rm[1] = 2 * my * L[1];
				for (mz = -n3; mz <= n3; mz++)
				{
					refl[2] = pow(beta[5], std::abs(mz));
					Rm[2] = 2 * mz * L[2];
					for (q = 0; q <= 1; q++)
					{
						Rp_plus_Rm[0] = (1 - 2 * q) * s[0] - r[0] + Rm[0];
						for (j = 0; j <= 1; j++)
						{
							Rp_plus_Rm[1] = (1 - 2 * j) * s[1] - r[1] + Rm[1];
							for (k = 0; k <= 1; k++)
							{
								Rp_plus_Rm[2] = (1 - 2 * k) * s[2] - r[2] + Rm[2];
								dist = sqrt(pow(Rp_plus_Rm[0], 2) + pow(Rp_plus_Rm[1], 2) + pow(Rp_plus_Rm[2], 2));
								if (std::abs(2 * mx - q) + std::abs(2 * my - j) + std::abs(2 * mz - k) <= nOrder || nOrder == -1)
								{
									fdist = floor(dist);
									if (fdist < nSamples)
									{
										// Only compute when necessary.
										refl[3] = pow(beta[0], std::abs(mx - q)) * refl[0];
										refl[4] = pow(beta[2], std::abs(my - j)) * refl[1];
										refl[5] = pow(beta[4], std::abs(mz - k)) * refl[2];
										b = refl[4] * refl[5] * refl[6]; // Absorbtion coefficient.
										d = dist * cTs;					 // Distance in meters (s)
										gain = sim_microphone(Rp_plus_Rm[0], Rp_plus_Rm[1], Rp_plus_Rm[2], angle, microphone_type) * b / (4 * M_PI * d);

										for (n = 0; n < Tw; n++)
											LPI[n] = 0.5 * (1 - cos(2 * M_PI * ((n + 1 - (dist - fdist)) / Tw))) * Fc * sinc(M_PI * Fc * (n + 1 - (dist - fdist) - (Tw / 2)));

										startPosition = (int)fdist - (Tw / 2) + 1;
										for (n = 0; n < Tw; n++)
											if (startPosition + n >= 0 && startPosition + n < nSamples)
												imp[idxMicrophone][startPosition + n] += gain * LPI[n];
									}
								}
							}
						}
					}
				}
			}
		}

		// 'Original' high-pass filter as proposed (Allen 1979).
		if (isHighPassFilter == 1)
		{
			for (int idx = 0; idx < 3; idx++)
			{
				Y[idx] = 0;
			}
			for (int idx = 0; idx < nSamples; idx++)
			{
				X0 = imp[idxMicrophone][idx];
				Y[2] = Y[1];
				Y[1] = Y[0];
				Y[0] = B1 * Y[1] + B2 * Y[2] + X0;
				imp[idxMicrophone][idx] = Y[0] + A1 * Y[1] + R1 * Y[2];
			}
		}
	}

	delete[] Y;
	delete[] LPI;
	delete[] r;
	delete[] s;
	delete[] L;

	return imp;
}

std::vector<std::complex<double>> freq_rir(double c, double fs, double f, const std::vector<std::vector<double>> &rr, const std::vector<double> &ss, const std::vector<double> &LL, const std::vector<double> &beta_input, const std::vector<double> &orientation, int isHighPassFilter, int nDimension, int nOrder, int nSamples, char microphone_type)
{
	// | Room Impulse Response Generator                                  |\n"
	// |                                                                  |\n"
	// | Computes the response of an acoustic source to one or more       |\n"
	// | microphones in a reverberant room using the image method [1,2].  |\n"
	// |                                                                  |\n"
	// | Author    : dr.ir. Emanuel Habets (ehabets@dereverberation.org)  |\n"
	// |                                                                  |\n"
	// | Version   : 2.1.20141124                                         |\n"
	// |                                                                  |\n"
	// | Copyright (C) 2003-2014 E.A.P. Habets, The Netherlands.          |\n"
	// |                                                                  |\n"
	// | [1] J.B. Allen and D.A. Berkley,                                 |\n"
	// |     Image method for efficiently simulating small-room acoustics,|\n"
	// |     Journal Acoustic Society of America,                         |\n"
	// |     65(4), April 1979, p 943.                                    |\n"
	// |                                                                  |\n"
	// | [2] P.M. Peterson,                                               |\n"
	// |     Simulating the response of multiple microphones to a single  |\n"
	// |     acoustic source in a reverberant room, Journal Acoustic      |\n"
	// |     Society of America, 80(5), November 1986.                    |\n"
	// --------------------------------------------------------------------\n\n"
	// function [h, beta_hat] = rir_generator(c, fs, r, s, L, beta, nsample,\n"
	//  mtype, order, dim, orientation, hp_filter);\n\n"
	// Input parameters:\n"
	//  c           : sound velocity in m/s.\n"
	//  fs          : sampling frequency in Hz.\n"
	// 	f			: frequency variable in Hz \n"
	//  r           : M x 3 array specifying the (x,y,z) coordinates of the\n"
	//                receiver(s) in m.\n"
	//  s           : 1 x 3 vector specifying the (x,y,z) coordinates of the\n"
	//                source in m.\n"
	//  L           : 1 x 3 vector specifying the room dimensions (x,y,z) in m.\n"
	//  beta        : 1 x 6 vector specifying the reflection coefficients\n"
	//                [beta_x1 beta_x2 beta_y1 beta_y2 beta_z1 beta_z2] or\n"
	//                beta = reverberation time (T_60) in seconds.\n"
	//  nsample     : number of samples to calculate, default is T_60*fs.\n"
	//  mtype       : [omnidirectional, subcardioid, cardioid, hypercardioid,\n"
	//                bidirectional], default is omnidirectional.\n"
	//  order       : reflection order, default is -1, i.e. maximum order.\n"
	//  dim         : room dimension (2 or 3), default is 3.\n"
	//  orientation : direction in which the microphones are pointed, specified using\n"
	//                azimuth and elevation angles (in radians), default is [0 0].\n"
	//  hp_filter   : use 'false' to disable high-pass filter, the high-pass filter\n"
	//                is enabled by default.\n\n"
	// Output parameters:\n"
	//  h           : M x nsample matrix containing the calculated room impulse\n"
	//                response(s).\n"
	//  beta_hat    : In case a reverberation time is specified as an input parameter\n"
	//                the corresponding reflection coefficient is returned.\n\n");

	// Load parameters
	int nMicrophones = rr.size();
	double beta[6];
	double angle[2];
	double reverberation_time;

	if (beta_input.size() == 1)
	{
		double V = LL[0] * LL[1] * LL[2];
		double S = 2 * (LL[0] * LL[2] + LL[1] * LL[2] + LL[0] * LL[1]);
		reverberation_time = beta_input[0];
		if (reverberation_time != 0)
		{
			double alfa = 24 * V * log(10.0) / (c * S * reverberation_time);
			for (int i = 0; i < 6; i++)
				beta[i] = sqrt(1 - alfa);
		}
		else
		{
			for (int i = 0; i < 6; i++)
				beta[i] = 0;
		}
	}
	else
	{
		for (int i = 0; i < 6; i++)
			beta[i] = beta_input[i];
	}

	// 3D Microphone orientation (optional)
	if (orientation.size())
	{
		angle[0] = orientation[0];
		angle[1] = orientation[1];
	}
	else
	{
		angle[0] = 0;
		angle[1] = 0;
	}

	if (nDimension == 2)
	{
		beta[4] = 0;
		beta[5] = 0;
	}

	// Reflection order (optional)
	if (nOrder < -1)
	{
		// mexErrMsgTxt("Invalid input arguments! (8)");
	}

	// Number of samples (optional)
	if (nSamples == -1)
	{
		if (beta_input.size() > 1)
		{
			double V = LL[0] * LL[1] * LL[2];
			double alpha = ((1 - pow(beta[0], 2)) + (1 - pow(beta[1], 2))) * LL[1] * LL[2] +
						   ((1 - pow(beta[2], 2)) + (1 - pow(beta[3], 2))) * LL[0] * LL[2] +
						   ((1 - pow(beta[4], 2)) + (1 - pow(beta[5], 2))) * LL[0] * LL[1];
			reverberation_time = 24 * log(10.0) * V / (c * alpha);
			if (reverberation_time < 0.128)
				reverberation_time = 0.128;
		}
		nSamples = (int)(reverberation_time * fs);
	}

	// Output array.
	std::vector<std::complex<double>> imp(nMicrophones);

	// Temporary variables and constants (image-method)
	const std::complex<double> i(0, 1);					// i = sqrt(-1)
	const double w = 2 * M_PI * f;						// Frequency variable in radians.
	double t, d, b;										// Time delay (s), distance (m), absortion coefficient.
	std::complex<double> attenuation, time_shift, gain; // Attenuation factor A(.) and time delay T(.), product of A(.) x T(.),
	const double cTs = c / fs;							// Conversion term: Speed of sound (c) * Sample periods (T) = Speed of sound (c) / Sample frequency (fs).
	double *r = new double[3];
	double *s = new double[3];
	double *L = new double[3];
	double Rm[3];
	double Rp_plus_Rm[3];
	double refl[6];		// Absorption coefficient
	double fdist, dist; // Distance between source and receiver, meters and seconds, respectively.

	int n1, n2, n3; // Image order +/- range along x, y, and z axes.
	int q, j, k;	// Integer vector triplet.
	int mx, my, mz; // Image order index along the x,y,z axis.

	// Convert measurements from meters to sample periods.
	s[0] = ss[0] / cTs;
	s[1] = ss[1] / cTs;
	s[2] = ss[2] / cTs;
	L[0] = LL[0] / cTs;
	L[1] = LL[1] / cTs;
	L[2] = LL[2] / cTs;

	for (int idxMicrophone = 0; idxMicrophone < nMicrophones; idxMicrophone++)
	{
		// [x_1 x_2 ... x_N y_1 y_2 ... y_N z_1 z_2 ... z_N]
		// Convert measurements from meters to sample periods.
		r[0] = rr[idxMicrophone][0] / cTs;
		r[1] = rr[idxMicrophone][1] / cTs;
		r[2] = rr[idxMicrophone][2] / cTs;

		// Order of reflections in each axis.
		n1 = (int)ceil(nSamples / (2 * L[0]));
		n2 = (int)ceil(nSamples / (2 * L[1]));
		n3 = (int)ceil(nSamples / (2 * L[2]));

		// Generate room impulse response
		for (mx = -n1; mx <= n1; mx++)
		{
			refl[0] = pow(beta[1], std::abs(mx));
			Rm[0] = 2 * mx * L[0];
			for (my = -n2; my <= n2; my++)
			{
				refl[1] = pow(beta[3], std::abs(my));
				Rm[1] = 2 * my * L[1];
				for (mz = -n3; mz <= n3; mz++)
				{
					refl[2] = pow(beta[5], std::abs(mz));
					Rm[2] = 2 * mz * L[2];
					for (q = 0; q <= 1; q++)
					{
						Rp_plus_Rm[0] = (1 - 2 * q) * s[0] - r[0] + Rm[0];
						for (j = 0; j <= 1; j++)
						{
							Rp_plus_Rm[1] = (1 - 2 * j) * s[1] - r[1] + Rm[1];
							for (k = 0; k <= 1; k++)
							{
								Rp_plus_Rm[2] = (1 - 2 * k) * s[2] - r[2] + Rm[2];
								dist = sqrt(pow(Rp_plus_Rm[0], 2) + pow(Rp_plus_Rm[1], 2) + pow(Rp_plus_Rm[2], 2));
								if (std::abs(2 * mx - q) + std::abs(2 * my - j) + std::abs(2 * mz - k) <= nOrder || nOrder == -1)
								{
									fdist = floor(dist);  // Time delay sample periods (s).
									if (fdist < nSamples) // Check impulse will reach the source within the sample length.
									{
										// Only compute when necessary.
										refl[3] = pow(beta[0], std::abs(mx - q)) * refl[0];
										refl[4] = pow(beta[2], std::abs(my - j)) * refl[1];
										refl[5] = pow(beta[4], std::abs(mz - k)) * refl[2];
										b = refl[3] * refl[4] * refl[5]; // Absorption coefficient.
										d = dist * cTs;					 // Distance in meters (m).
										t = d / c;						 // Time delay in seconds (s).
										attenuation = sim_microphone(Rp_plus_Rm[0], Rp_plus_Rm[1], Rp_plus_Rm[2], angle, microphone_type) * b / (4 * M_PI * d);
										time_shift = exp(-i * w * t);
										gain = attenuation * time_shift;
										imp[idxMicrophone] = imp[idxMicrophone] + gain;
									}
								}
							}
						}
					}
				}
			}
		}
	}

	// Clean up memory.
	delete[] r;
	delete[] s;
	delete[] L;

	return imp;
}

// 2022-02-12: Jesse Wood
// This compiles the c++ code for the rir generator into a shared library that is accessible through python.
// To compile this code run:
//
// ```bash
// c++ -O3 -Wall -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) rirbind.cpp -o rirbind$(python3-config --extension-suffix)
// ```
//
// Examples:
// ```bash
// $ python3
// >>> import rirbind
// >>> rirbind.time_rir(343.0, 16000, [[1,1,1]], [1,2,2], [3,3,3], [0.9]*6, [0,0], 1, 3 , -1, 2048, 'o')
// >>> rirbind.freq_rir(343.0, 16000, 1000, [[1,1,1]], [1,2,2], [3,3,3], [0.9]*6, [0,0], 1, 3 , -1, 2048, 'o')
// ```
//

PYBIND11_MODULE(rirbind, m)
{
	m.doc() = "Computes the response of an acoustic source to one or more microphones in a reverberant room using the image method [1,2]."; // optional module docstring
	m.def("time_rir", &time_rir, "A function that computes a room impulse repsonse in the time domain.");
	m.def("freq_rir", &freq_rir, "A function that computes a room impulse repsonse in the frequency domain.");
}