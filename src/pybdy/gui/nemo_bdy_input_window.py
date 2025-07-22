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
Created on 21 Jan 2015.

@author: Mr. Srikanth Nagella
"""
from PyQt5 import QtWidgets
from PyQt5.Qt import Qt

from .nemo_bdy_mask_gui import MatplotlibWidget
from .nemo_bdy_namelist_edit import NameListEditor


class InputWindow(QtWidgets.QDialog):
    """Input Window for editing pyBDY settings."""

    def __init__(self, setup):
        """Initialise the UI components."""
        super(InputWindow, self).__init__()
        # initialise NameListEditor
        self.nl_editor = NameListEditor(setup)

        # initialise MatplotlibWidget
        self.mpl_widget = MatplotlibWidget()

        # connect namelistedit to matplotlibwidget
        self.nl_editor.bathymetry_update.connect(self.mpl_widget.set_bathymetry_file)
        self.nl_editor.mask_update.connect(self.mpl_widget.save_mask_file)
        self.nl_editor.mask_settings_update.connect(self.mpl_widget.set_mask_settings)

        if setup.bool_settings["mask_file"]:
            try:  # Try to load with bathy and mask file
                self.mpl_widget.set_bathymetry_file(
                    setup.settings["bathy"], setup.settings["mask_file"]
                )
            except Exception:  # if mask file is not readable then open with bathy
                self.mpl_widget.set_bathymetry_file(setup.settings["bathy"], None)
        else:
            self.mpl_widget.set_bathymetry_file(setup.settings["bathy"], None)

        self.mpl_widget.set_mask_settings(
            float(setup.settings["mask_max_depth"]),
            float(setup.settings["mask_shelfbreak_dist"]),
        )

        splitter = QtWidgets.QSplitter(Qt.Horizontal)
        splitter.addWidget(self.nl_editor)
        splitter.addWidget(self.mpl_widget)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)
        # set the Dialog title
        self.setWindowTitle("pyBDY Settings Editor")
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))
        # show the window
        self.show()
