# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

"""
Created on Thu Feb 13 18:03:00 2025.

@author James Harle
@author Benjamin Barton
"""

# External imports
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

# Internal imports


def temperature_profile(
    depth: Union[xr.DataArray, float]
) -> Union[xr.DataArray, float]:
    """
    Temperature (in °C) at a given depth (in meters).

    Parameters
    ----------
        depth (DataArray or float): Depth in meters (0 to 6000).

    Returns
    -------
        DataArray or float: Temperature in °C.
    """
    depth = xr.DataArray(depth) if not isinstance(depth, xr.DataArray) else depth
    # Smooth temperature profile with a thermocline
    surface_temp = 20
    deep_temp = -2
    thermocline_depth = 1000  # Depth of the thermocline
    scale_depth = 200  # Sharpness of the thermocline transition
    temperature = deep_temp + (surface_temp - deep_temp) / (
        1 + np.exp((depth - thermocline_depth) / scale_depth)
    )
    return temperature


def salinity_profile(depth: Union[xr.DataArray, float]) -> Union[xr.DataArray, float]:
    """
    Salinity (in PSU) at a given depth (in meters).

    Parameters
    ----------
        depth (DataArray or float): Depth in meters (0 to 6000).

    Returns
    -------
        DataArray or float: Salinity in PSU.
    """
    depth = xr.DataArray(depth) if not isinstance(depth, xr.DataArray) else depth
    # Smooth salinity profile using an exponential model
    surface_salinity = 34.5
    deep_salinity = 32.7
    scale_depth = 1500  # Characteristic depth for salinity stabilization
    salinity = deep_salinity - (deep_salinity - surface_salinity) * np.exp(
        -depth / scale_depth
    )
    return salinity


if __name__ == "__main__":
    # Generate depth array
    depths = xr.DataArray(np.linspace(0, 6000, 1000), dims=["depth"], name="depth")

    # Compute profiles
    temperatures = temperature_profile(depths)
    salinities = salinity_profile(depths)

    # Plot profiles
    fig, ax1 = plt.subplots(figsize=(6, 8))

    ax1.plot(temperatures, depths, label="Temperature (°C)", color="red")
    ax1.set_xlabel("Temperature (°C)", color="red")
    ax1.set_xlim(-3, 25)
    ax1.set_ylim(6000, 0)
    ax1.invert_yaxis()
    ax1.tick_params(axis="x", labelcolor="red")

    ax2 = ax1.twiny()
    ax2.plot(salinities, depths, label="Salinity (PSU)", color="blue")
    ax2.set_xlabel("Salinity (PSU)", color="blue")
    ax2.set_xlim(30, 35)
    ax2.tick_params(axis="x", labelcolor="blue")

    # Add legends and title
    fig.suptitle("Typical Ocean Temperature and Salinity Profiles")
    plt.show()
