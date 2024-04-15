"""
Editor for namelist.bdy file.

@author: Mr. Srikanth Nagella
"""
import ast

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QMessageBox, QToolTip


class NameListEditor(QtWidgets.QWidget):
    """GUI for the Namelist file options."""

    new_settings = (
        {}
    )  # temporary variable to store the settings as they are changed in the GUI
    bathymetry_update = pyqtSignal(
        str, str
    )  # fires when there are changes to the settings
    mask_update = pyqtSignal(str)  # fires when there mask data to be saved is fired
    mask_settings_update = pyqtSignal(
        float, float
    )  # fires when there is mask settings update

    def __init__(self, setup):
        """Initialise the constructor for setting up the gui using the settings."""
        super(NameListEditor, self).__init__()
        self.settings = setup.settings
        self.bool_settings = setup.bool_settings
        self.setup = setup
        self.init_ui()

    def init_ui(self):
        """Initialise the UI components of the GUI."""
        client = QtWidgets.QWidget(self)
        # Create the Layout to Grid
        grid = QtWidgets.QGridLayout()

        # Loop through the settings and create widgets for each setting
        index = 0
        for setting in self.settings:
            # initialises setting Widget
            label = QtWidgets.QLabel(setting)
            qlabel = QtWidgets.QPushButton("")
            qlabel.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxQuestion)
            )
            if type(self.settings[setting]).__name__ in [
                "str",
                "float",
                "double",
                "int",
                "time",
                "dict",
            ]:
                text = QtWidgets.QLineEdit(self)
                text.setText(str(self.settings[setting]))
                text.textChanged.connect(
                    lambda value=setting, var_name=setting: self.label_changed(
                        value, var_name
                    )
                )
                if setting in self.bool_settings:
                    chkbox = QtWidgets.QCheckBox(self)
                    chkbox.setChecked(self.bool_settings[setting])
                    chkbox.stateChanged.connect(
                        lambda value=setting, var_name=setting: self.state_changed(
                            value, var_name
                        )
                    )
                    grid.addWidget(chkbox, index, 0)

            elif type(self.settings[setting]).__name__ == "bool":
                text = QtWidgets.QComboBox(self)
                text.insertItem(0, "True")
                text.insertItem(1, "False")
                if self.settings[setting]:
                    text.setCurrentIndex(0)
                else:
                    text.setCurrentIndex(1)
                text.currentIndexChanged.connect(
                    lambda value=setting, var_name=setting: self.combo_index_changed(
                        value, var_name
                    )
                )

            grid.addWidget(label, index, 1)
            grid.addWidget(text, index, 2)
            qlabel.clicked.connect(
                lambda widget=qlabel, str_val=self.setup.variable_info[
                    setting
                ]: QToolTip.showText(QCursor.pos(), str_val)
            )
            grid.addWidget(qlabel, index, 3)
            if setting in self.setup.variable_info:
                qlabel.setToolTip(self.setup.variable_info[setting])
            index = index + 1

        client.setLayout(grid)
        # scrollbars
        scroll_area = QtWidgets.QScrollArea(self)
        # scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(client)

        # save cancel buttons
        btn_widget = QtWidgets.QWidget(self)
        hbox_layout = QtWidgets.QHBoxLayout(self)
        btn_save = QtWidgets.QPushButton("Save")
        btn_save.clicked.connect(self._btn_save_callback)
        self.btn_cancel = QtWidgets.QPushButton("Close")
        self.btn_cancel.clicked.connect(self._btn_cancel_callback)
        hbox_layout.addWidget(btn_save)
        hbox_layout.addWidget(self.btn_cancel)
        btn_widget.setLayout(hbox_layout)

        box_layout = QtWidgets.QVBoxLayout(self)
        box_layout.addWidget(scroll_area)
        box_layout.addWidget(btn_widget)
        btn_widget.setMaximumWidth(400)
        scroll_area.setMaximumWidth(400)
        self.setLayout(box_layout)
        # show the window
        self.show()

    def label_changed(self, value, name):
        """Run callback when the text is changed in the text box."""
        self.new_settings[name] = str(value).encode("utf_8")

    def combo_index_changed(self, value, name):
        """
        Run callback for the dropdown in the settings.

        Notes
        -----
        Run callback when the True/False dropdown for the settings,
          which has a boolean value, is changed.
        """
        if value == 0:
            self.new_settings[name] = True
        else:
            self.new_settings[name] = False

    def state_changed(self, state, name):
        """
        Run callback when the check box state is changed.

        Notes
        -----
        This updates the bool_setting.
        """
        if state == QtCore.Qt.Checked:
            self.bool_settings[name] = True
        else:
            self.bool_settings[name] = False

    def _btn_save_callback(self):
        """
        Run callback when save button is clicked.

        Notes
        -----
        This method writes takes the settings values in
        GUI and write them back to file.
        """
        # copy the the modified values to settings and call the setup save
        for setting in self.new_settings:
            if (type(self.settings[setting]).__name__ == "dict") & (
                type(self.new_settings[setting]).__name__ != "dict"
            ):
                self.new_settings[setting] = ast.literal_eval(
                    self.new_settings[setting]
                )
            self.settings[setting] = self.new_settings[setting]

        self.setup.settings = self.settings
        try:
            self.setup.write()  # write settings back to file
            QMessageBox.information(self, "pyBDY", "Setting saved to file")
        except Exception:
            QMessageBox.information(
                self,
                "pyBDY",
                "Error while saving the settings file, please check the permissions",
            )

        try:
            # only emit the saving of mask file if the mask file name is set and boolean value is set
            if (
                self.settings["mask_file"] is not None
                and self.bool_settings["mask_file"]
            ):
                self.mask_update.emit(self.settings["mask_file"])
        except KeyError:
            QMessageBox.information(
                self, "pyBDY", "Set mask_file key in the setting .bdy file"
            )

        try:
            self.mask_settings_update.emit(
                float(self.settings["mask_max_depth"]),
                float(self.settings["mask_shelfbreak_dist"]),
            )
        except KeyError:
            print("Set the mask setting mask_max_depth and mask_shelfbreak_dist")

        if self.bool_settings["mask_file"]:
            self.bathymetry_update.emit(
                self.settings["bathy"], self.settings["mask_file"]
            )

    def _btn_cancel_callback(self):
        """Run callback when cancel button is clicked."""
        self.close()
