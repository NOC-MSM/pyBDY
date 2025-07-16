# ===================================================================
# Copyright 2025 National Oceanography Centre
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
# ===================================================================

"""
Created on Tue Mar 04 14:045:00 2025.

@author James Harle
@author Benjamin Barton
"""

# External imports
import matplotlib.pyplot as plt
import numpy as np

# Internal imports


def synth_sco(bathy, n_zlevel, theta=3, b=0.5):
    """
    Generate sigma vertical coordinates for gdep.

    This uses the original default NEMO s-coordinate stretching
    [Madec et al., 1996].

    Parameters
    ----------
    bathy (np.array)   : bathymetry for calculating the sigma levels
                         (postive down)
    n_zlevel (int)     : number of z levels required
    theta (int)        : surface control parameter (0<=theta<=20)
    b (int)            : bottom control parameter  (0<=b<=1)

    Returns
    -------
    gdept (np.array)       : sigma depth levels on t levels points
    gdepw (np.array)       : sigma depth levels on w levels points
    """
    k = np.arange(n_zlevel).astype(int)
    s = -k / (n_zlevel - 1)
    s_min = 0
    c_s = (np.tanh(theta * (s + b)) - np.tanh(theta * b)) / (2 * np.sinh(theta))
    c_s = c_s / c_s[-1]

    b_shape = bathy.T.shape
    c_s = np.tile(c_s, b_shape + (1,)).T
    t_shape = [len(c_s)]
    for i in range(len(b_shape)):
        t_shape.append(1)
    t_shape = tuple(t_shape)
    bathy = np.tile(bathy, t_shape)

    gdepw = s_min + (c_s * (bathy - s_min))
    gdept = gdepw.copy()
    gdept[:-1, ...] = 0.5 * (gdepw[:-1, ...] + gdepw[1:, ...])
    gdept[-1, ...] = gdepw[-1, ...] + (gdepw[-1, ...] - gdept[-2, ...])

    return gdept, gdepw


def synth_zco(max_depth, n_zlevel):
    """
    Generate zco vertical coordinates for gdep.

    Parameters
    ----------
    max_depth (int)    : maximum depth level
    n_zlevel (int)     : number of z levels required

    Returns
    -------
    gdept (np.array)   : zco depth levels on t levels points
    gdepw (np.array)   : zco depth levels on w levels points
    """
    gdepw = np.linspace(0, max_depth, num=n_zlevel)
    gdept = gdepw.copy()
    gdept[:-1, ...] = 0.5 * (gdepw[:-1, ...] + gdepw[1:, ...])
    gdept[-1, ...] = gdepw[-1, ...] + (gdepw[-1, ...] - gdept[-2, ...])
    return gdept, gdepw


if __name__ == "__main__":
    zt, zw = synth_sco(np.array([[50, 60], [40, 55.5]]), 20)
    plt.plot(zt.reshape(len(zt), -1))
    plt.show()
