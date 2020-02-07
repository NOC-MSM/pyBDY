'''
Created on 7 Jan 2015

@author: Mr. Srikanth Nagella
'''
# pylint: disable=E1103
# pylint: disable=no-name-in-module
from PyQt5 import QtGui, QtWidgets

from .gui.nemo_bdy_input_window import InputWindow
from . import nemo_bdy_setup

import sys, getopt

def open_settings_window(fname):
    """ Main method which starts a Qt application and gives user
    an option to pick a namelist.bdy file to edit. Once user selects it
    it will open a dialog box where users can edit the parameters"""
    app = QtWidgets.QApplication(sys.argv)
    if fname is None:
        fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file')

    setup = nemo_bdy_setup.Setup(fname)#'../../data/namelisttest.bdy')
    ex = InputWindow(setup)
    ex.nl_editor.btn_cancel.clicked.connect(lambda: sys.exit(0))
    return app.exec_(), ex.mpl_widget.mask

def open_settings_dialog(setup):
    """ This method is to start the settings window using the setup settings provided
    in the input. On clicking the cancel button it doesn't shutdown the applicaiton
    but carries on with the execution"""
    app = QtWidgets.QApplication(sys.argv)
    ex = InputWindow(setup)
    ex.nl_editor.btn_cancel.clicked.connect(app.quit)
    return app.exec_(), ex.mpl_widget.mask

def main():
    """ Command line execution method which check the input arguments and passes on to
    method to open the settings window"""
    setup_file = None
    try:
        opts, dummy_args = getopt.getopt(sys.argv[1:], "hs:", ["help", "setup="])
    except getopt.GetoptError:
        print("usage: pynemo_settings_editor -s <namelist.bdy> ")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("usage: pynemo_settings_editor -s <namelist.bdy> ")
            sys.exit()
        elif opt in ("-s", "--setup"):
            setup_file = arg
    sys.exit(open_settings_window(setup_file))

if __name__ == '__main__':
    main()
