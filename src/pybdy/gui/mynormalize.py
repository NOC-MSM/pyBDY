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


# The Normalize class is largely based on code provided by Sarah Graves.

import matplotlib.cbook as cbook
import numpy as np
import numpy.ma as ma
from matplotlib.colors import Normalize


class MyNormalize(Normalize):
    """A Normalize class for imshow that allows different stretching functions for astronomical images."""

    def __init__(
        self, stretch="linear", exponent=5, vmid=None, vmin=None, vmax=None, clip=False
    ):
        """
        Initialise an APLpyNormalize instance.

        Optional Keyword Arguments:

            *vmin*: [ None | float ]
                Minimum pixel value to use for the scaling.

            *vmax*: [ None | float ]
                Maximum pixel value to use for the scaling.

            *stretch*: [ 'linear' | 'log' | 'sqrt' | 'arcsinh' | 'power' ]
                The stretch function to use (default is 'linear').

            *vmid*: [ None | float ]
                Mid-pixel value used for the log and arcsinh stretches. If
                set to None, a default value is picked.

            *exponent*: [ float ]
                if self.stretch is set to 'power', this is the exponent to use.

            *clip*: [ True | False ]
                If clip is True and the given value falls outside the range,
                the returned value will be 0 or 1, whichever is closer.
        """
        if vmax < vmin:
            raise Exception("vmax should be larger than vmin")

        # Call original initalization routine
        Normalize.__init__(self, vmin=vmin, vmax=vmax, clip=clip)

        # Save parameters
        self.stretch = stretch
        self.exponent = exponent

        if stretch == "power" and np.equal(self.exponent, None):
            raise Exception("For stretch=='power', an exponent should be specified")

        if np.equal(vmid, None):
            if stretch == "log":
                if vmin > 0:
                    self.midpoint = vmax / vmin
                else:
                    raise Exception(
                        "When using a log stretch, if vmin < 0, then vmid has to be specified"
                    )
            elif stretch == "arcsinh":
                self.midpoint = -1.0 / 30.0
            else:
                self.midpoint = None
        else:
            if stretch == "log":
                if vmin < vmid:
                    raise Exception(
                        "When using a log stretch, vmin should be larger than vmid"
                    )
                self.midpoint = (vmax - vmid) / (vmin - vmid)
            elif stretch == "arcsinh":
                self.midpoint = (vmid - vmin) / (vmax - vmin)
            else:
                self.midpoint = None

    def __call__(self, value, clip=None):
        # read in parameters
        exponent = self.exponent

        # ORIGINAL MATPLOTLIB CODE

        if clip is None:
            clip = self.clip

        if cbook.iterable(value):
            vtype = "array"
            val = ma.asarray(value).astype(np.float)
        else:
            vtype = "scalar"
            val = ma.array([value]).astype(np.float)

        self.autoscale_None(val)
        vmin, vmax = self.vmin, self.vmax
        if vmin > vmax:
            raise ValueError("minvalue must be less than or equal to maxvalue")
        elif vmin == vmax:
            return 0.0 * val
        else:
            if clip:
                mask = ma.getmask(val)
                val = ma.array(np.clip(val.filled(vmax), vmin, vmax), mask=mask)
            result = (val - vmin) * (1.0 / (vmax - vmin))

            # CUSTOM APLPY CODE

            # Keep track of negative values
            negative = result < 0.0

            if self.stretch == "linear":
                pass

            elif self.stretch == "log":
                result = ma.log10(result * (self.midpoint - 1.0) + 1.0) / ma.log10(
                    self.midpoint
                )

            elif self.stretch == "sqrt":
                result = ma.sqrt(result)

            elif self.stretch == "arcsinh":
                result = ma.arcsinh(result / self.midpoint) / ma.arcsinh(
                    1.0 / self.midpoint
                )

            elif self.stretch == "power":
                result = ma.power(result, exponent)

            else:
                raise Exception("Unknown stretch in APLpyNormalize: %s" % self.stretch)

            # Now set previously negative values to 0, as these are
            # different from true NaN values in the FITS image
            result[negative] = -np.inf

        if vtype == "scalar":
            result = result[0]

        return result

    def inverse(self, value):
        # ORIGINAL MATPLOTLIB CODE

        if not self.scaled():
            raise ValueError("Not invertible until scaled")

        vmin, vmax = self.vmin, self.vmax

        # CUSTOM APLPY CODE

        if cbook.iterable(value):
            val = ma.asarray(value)
        else:
            val = value

        if self.stretch == "linear":
            pass

        elif self.stretch == "log":
            val = (ma.power(10.0, val * ma.log10(self.midpoint)) - 1.0) / (
                self.midpoint - 1.0
            )

        elif self.stretch == "sqrt":
            val = val * val

        elif self.stretch == "arcsinh":
            val = self.midpoint * ma.sinh(val * ma.arcsinh(1.0 / self.midpoint))

        elif self.stretch == "power":
            val = ma.power(val, (1.0 / self.exponent))

        else:
            raise Exception("Unknown stretch in APLpyNormalize: %s" % self.stretch)

        return vmin + val * (vmax - vmin)
