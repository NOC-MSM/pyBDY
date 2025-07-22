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
Created on 7 Jan 2015.

@author: Mr. Srikanth Nagella
"""
import getopt
import sys

from PyQt5 import QtWidgets

from . import nemo_bdy_setup
from .gui.nemo_bdy_input_window import InputWindow


def open_settings_window(fname):
    """
    Start a Qt application.

    Notes
    -----
    This method gives the user the option to pick a namelist.bdy file to edit.
    Once user selects it it will open a dialog box where users can edit the parameters.
    """
    app = QtWidgets.QApplication(sys.argv)
    if fname is None:
        fname = QtWidgets.QFileDialog.getOpenFileName(None, "Open file")

    setup = nemo_bdy_setup.Setup(fname)  #'../../data/namelisttest.bdy')
    ex = InputWindow(setup)
    ex.nl_editor.btn_cancel.clicked.connect(lambda: sys.exit(0))
    return app.exec_(), ex.mpl_widget.mask


def open_settings_dialog(setup):
    """
    Start the settings window using the setup settings provided in the input.

    Notes
    -----
    On clicking the cancel button it doesn't shutdown the applicaiton but carries on with the execution.
    """
    app = QtWidgets.QApplication(sys.argv)
    ex = InputWindow(setup)
    ex.nl_editor.btn_cancel.clicked.connect(app.quit)
    return app.exec_(), ex.mpl_widget.mask


def main():
    """
    Command line execution method.

    Checks the input arguments and passes on to method to open the settings window.
    """
    setup_file = None
    try:
        opts, dummy_args = getopt.getopt(sys.argv[1:], "hs:", ["help", "setup="])
    except getopt.GetoptError:
        print("usage: pybdy_settings_editor -s <namelist.bdy> ")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("usage: pybdy_settings_editor -s <namelist.bdy> ")
            sys.exit()
        elif opt in ("-s", "--setup"):
            setup_file = arg
    sys.exit(open_settings_window(setup_file))


if __name__ == "__main__":
    main()
