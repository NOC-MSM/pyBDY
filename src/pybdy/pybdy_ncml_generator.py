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
Created on 2 Jul 2015.

The main application object for hosting the pybdy ncml editor.
Used for development purposes to display the ncml editor dialog.

@author: Shirley Crompton, UK Science and Technology Facilities Council
"""
import logging
import sys

from PyQt5.QtWidgets import QApplication

from .gui import nemo_ncml_generator as ncml_generator

# Logging set to info
logging.basicConfig(level=logging.INFO)


def main():
    """
    Command line execution method.

    Notes
    -----
    Checks the input arguments and passes on to method to open the ncml generator window.
    """
    app = QApplication(sys.argv)
    ncml_generator.Ncml_generator(None)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
