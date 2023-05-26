"""
Created on 2 Jul 2015.

@author: Shirley Crompton, UK Science and Technology Facilities Council
"""
import logging
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot


class Ncml_tab(QtWidgets.QWidget):
    """Tab contents to define child aggregation."""

    def __init__(self, tabName):
        """Initialise the UI components."""
        super(Ncml_tab, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.var = tabName  # tabName is used to determine the set of netcdf variables to process
        # print self.var
        # self.value_dict = {} # to capture the user inputs

        # no params yet, may be allow user to predefine an input ncml for edit????
        self.initUI()

    def initUI(self):
        QtWidgets.QToolTip.setFont(QtGui.QFont("SansSerif", 11))
        self.varStackedWidget = QtWidgets.QStackedWidget()
        # variable chooser combobox
        combo_vars = []
        if self.var == "Tracer":
            combo_vars = ["temperature", "salinity"]  # votemper, vosaline
            self.votemper = ncml_variable("temperature", "votemper")
            self.vosaline = ncml_variable("salinity", "vosaline")
            self.varStackedWidget.addWidget(self._addStackWidget("votemper"))
            self.varStackedWidget.addWidget(self._addStackWidget("vosaline"))
            # debug
        #            print 'Tracer has ' + str(self.varStackedWidget.count())
        elif self.var == "Ice":
            combo_vars = [
                "ice thickness",
                "leads fraction",
                "snow thickness",
            ]  #'iicethic,ileadfra,isnowthi
            self.iicethic = ncml_variable("ice_thickness", "iicethic")
            self.ileadfra = ncml_variable("leads_fraction", "ileadfra")
            self.isnowthi = ncml_variable("snow_thickness", "isnowthi")
            self.varStackedWidget.addWidget(self._addStackWidget("iicethic"))
            self.varStackedWidget.addWidget(self._addStackWidget("ileadfra"))
            self.varStackedWidget.addWidget(self._addStackWidget("isnowthi"))
        #            print 'Ice has ' + str(self.varStackedWidget.count())
        elif self.var == "Dynamics":
            combo_vars = [
                "zonal velocity",
                "meridian velocity",
                "sea surface height",
            ]  # vozocrtx, vomecrty, sossheig
            self.vozocrtx = ncml_variable("zonal_velocity", "vozocrtx")
            self.vomecrty = ncml_variable("meridian_velocity", "vomecrty")
            self.sossheig = ncml_variable("sea_surface_height", "sossheig")
            self.varStackedWidget.addWidget(self._addStackWidget("vozocrtx"))
            self.varStackedWidget.addWidget(self._addStackWidget("vomecrty"))
            self.varStackedWidget.addWidget(self._addStackWidget("sossheig"))
        #            print 'Dynamics has ' + str(self.varStackedWidget.count())
        elif self.var == "Grid":
            combo_vars = [
                "depth at T points",
                "depth at W points",
                "number of wet levels",
                "vertical scale factor at T points",
                "vertical scale factor at U points",
                "vertical scale factor at V points",
            ]  # gdept,gdepw,mbathy
            self.gdept = ncml_variable("depth_at_t_points", "gdept")
            self.gdepw = ncml_variable("depth_at_w_points", "gdepw")
            self.mbathy = ncml_variable("number_of_wet_levels", "mbathy")
            self.e3t = ncml_variable("vertical_scale_factors_at_t_points", "e3t")
            self.e3u = ncml_variable("vertical_scale_factors_at_u_points", "e3u")
            self.e3v = ncml_variable("vertical_scale_factors_at_v_points", "e3v")
            self.varStackedWidget.addWidget(self._addStackWidget("gdept"))
            self.varStackedWidget.addWidget(self._addStackWidget("gdepw"))
            self.varStackedWidget.addWidget(self._addStackWidget("mbathy"))
            self.varStackedWidget.addWidget(self._addStackWidget("e3t"))
            self.varStackedWidget.addWidget(self._addStackWidget("e3u"))
            self.varStackedWidget.addWidget(self._addStackWidget("e3v"))
        #            print 'Grid has ' + str(self.varStackedWidget.count())
        elif self.var == "Ecosysem":
            pass  # nitrate, silicate
        self.varStackedWidget.setCurrentIndex(
            0
        )  # we rely on the stacked tab index to be the same as the combo box
        # combo box
        self.var_combo = QtWidgets.QComboBox()
        self.var_combo.addItems(combo_vars)
        self.var_combo.setEditable(False)
        self.var_combo.setCurrentIndex(0)
        # the value if not saved is cached during the session, we can wait until the add button is pressed
        self.var_combo.currentIndexChanged.connect(
            lambda var_name=self.var: self.src_combo_changed(var_name)
        )
        self.var_combo.currentIndexChanged.connect(self.setWidgetStack)
        # label
        var_label = QtWidgets.QLabel("Variable")
        # set layout
        stacked_hBox = QtWidgets.QHBoxLayout()
        stacked_hBox.setContentsMargins(5, 5, 5, 5)
        stacked_hBox.setSpacing(50)  # spacing between items
        stacked_hBox.setAlignment(QtCore.Qt.AlignLeft)
        stacked_hBox.addWidget(var_label)
        stacked_hBox.addWidget(self.var_combo)
        #
        vBoxLayout = QtWidgets.QVBoxLayout()
        vBoxLayout.addLayout(stacked_hBox)
        vBoxLayout.addWidget(self.varStackedWidget)
        #
        grp_box = QtWidgets.QGroupBox(None)
        grp_box.setLayout(vBoxLayout)

        """
        :TODO Need to add the override time gui widgets
        """

        """
        button bar
        """
        # reset button
        reset_btn = QtWidgets.QPushButton("Reset")
        reset_btn.setToolTip("Reset fields to previously saved values")
        add_btn = QtWidgets.QPushButton("Add")
        add_btn.setDefault(True)
        add_btn.setToolTip("Add the current definition to the NcML")
        # connect up with events
        reset_btn.clicked.connect(self.reset_tab)
        add_btn.clicked.connect(self.add_tab)

        btn_hBox = QtWidgets.QHBoxLayout(None)
        btn_hBox.setContentsMargins(5, 5, 5, 5)
        btn_hBox.setSpacing(10)
        btn_hBox.setAlignment(QtCore.Qt.AlignCenter)
        btn_hBox.addWidget(reset_btn)
        btn_hBox.addWidget(add_btn)

        # build the contents
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 5, 5)
        vbox.addWidget(grp_box)
        vbox.addLayout(btn_hBox)

    """
    create the stacked widget for each nemo variable
    """

    def _addStackWidget(self, old_name=""):
        self.varWidget = QtWidgets.QWidget()
        # self.varWidget.setObjectName(objName)
        varLayout = QtWidgets.QGridLayout()
        varLayout.setSpacing(20)

        # labels
        src_label = QtWidgets.QLabel("Source directory*")
        cbox_label = QtWidgets.QLabel("Includes subdirs")
        regex_label = QtWidgets.QLabel("Regular expression")
        old_name_label = QtWidgets.QLabel("Existing variable name*")
        # input textboxs
        self.varWidget.src_tedit = (
            QtWidgets.QLineEdit()
        )  # input widgets need to be attached to the stacked widget itself
        self.varWidget.src_tedit.setToolTip(
            "either remote OPeNDAP server or local file absolute path"
        )
        self.varWidget.src_tedit.returnPressed.connect(self.src_tedit_edited)

        self.varWidget.cbox = QtWidgets.QCheckBox()
        self.varWidget.cbox.setCheckable(True)
        self.varWidget.cbox.setChecked(False)
        self.varWidget.cbox.setToolTip("includes subdirectories")
        self.varWidget.regex_tedit = QtWidgets.QLineEdit()
        self.varWidget.regex_tedit.setToolTip(
            "see http://www.unidata.ucar.edu/software/thredds/current/netcdf-java/ncml/AnnotatedSchema4.html#regexp"
        )
        self.varWidget.old_name_tedit = QtWidgets.QLineEdit()
        self.varWidget.old_name_tedit.setToolTip("variable name in data file")
        self.varWidget.old_name_tedit.setText(old_name)

        varLayout.addWidget(src_label, 1, 0, 1, 1)
        varLayout.addWidget(self.varWidget.src_tedit, 1, 1, 1, 3)
        varLayout.addWidget(cbox_label, 2, 0, 1, 1)
        varLayout.addWidget(self.varWidget.cbox, 2, 1, 1, 1)
        varLayout.addWidget(regex_label, 2, 2, 1, 1)
        varLayout.addWidget(self.varWidget.regex_tedit, 2, 3, 1, 1)
        varLayout.addWidget(old_name_label, 3, 0, 1, 1)
        varLayout.addWidget(self.varWidget.old_name_tedit, 3, 1, 1, 3)

        self.varWidget.setLayout(varLayout)
        return self.varWidget

    """
    synchronise stack widget display with combo box value changed callback
    """

    @pyqtSlot()
    def setWidgetStack(self):
        self.varStackedWidget.setCurrentIndex(self.var_combo.currentIndex())

    """
    variable combo box value changed callback
    """

    @pyqtSlot()
    def src_combo_changed(self, var_name):
        # not sure why the current text is prefixed by the index : eg 0temperature
        # print 'src_combo_value_changed to :
        #  ' + str(var_name) +  unicode(str(self.var_combo.currentText())).encode('utf_8')
        pass

    @pyqtSlot()
    def src_tedit_edited(self):
        src_tedit_input = self.varStackedWidget.currentWidget().src_tedit.text()
        #        print 'src_edit text edited : ', src_tedit_input
        # validate the input now
        if not str(src_tedit_input).startswith("http"):
            if not os.path.isabs(src_tedit_input):  # assumes local file
                QtWidgets.QMessageBox.critical(
                    self,
                    "Something is wrong",
                    "source directory must be an absolute path!",
                    QtWidgets.QMessageBox.Ok,
                    QtWidgets.QMessageBox.Ok,
                )
                self.varStackedWidget.currentWidget().src_tedit.clear()
            if not os.path.exists(src_tedit_input):
                QtWidgets.QMessageBox.critical(
                    self,
                    "Something is wrong",
                    "source directory does not exist!",
                    QtWidgets.QMessageBox.Ok,
                    QtWidgets.QMessageBox.Ok,
                )
                self.varStackedWidget.currentWidget().src_tedit.clear()

    """
    reset button pushed callback.  The widgets are reset to default values
    """

    @pyqtSlot()
    def reset_tab(self):
        # current screen value is not saved until the add button is pressed
        # reset only reset the screen values, not the cached values
        if self.var_combo.currentText() == "temperature":
            #            print 'reset button is pushed, temperature ....'
            self.resetValues(self.votemper)
        elif self.var_combo.currentText() == "salinity":
            self.resetValues(self.vosaline)
        elif self.var_combo.currentText() == "ice thickness":
            self.resetValues(self.iicethic)
        elif self.var_combo.currentText() == "leads fraction":
            self.resetValues(self.ileadfra)
        elif self.var_combo.currentText() == "snow thickness":
            self.resetValues(self.isnowthi)
        elif self.var_combo.currentText() == "zonal velocity":
            self.resetValues(self.vozocrtx)
        elif self.var_combo.currentText() == "meridian velocity":
            self.resetValues(self.vomecrty)
        elif self.var_combo.currentText() == "sea surface height":
            self.resetValues(self.sossheig)
        elif self.var_combo.currentText() == "depth at T points":
            self.resetValues(self.gdept)
        elif self.var_combo.currentText() == "depth at W points":
            self.resetValues(self.gdepw)
        elif self.var_combo.currentText() == "number of wet levels":
            self.resetValues(self.mbathy)
        elif self.var_combo.currentText() == "vertical scale factor at T points":
            self.resetValues(self.e3t)
        elif self.var_combo.currentText() == "vertical scale factor at U points":
            self.resetValues(self.e3u)
        elif self.var_combo.currentText() == "vertical scale factor at V points":
            self.resetValues(self.e3v)

    """
    reset the stacked widget values
    """

    def resetValues(self, currentValues=None):
        # 'in resetValues ....'
        if currentValues is None:
            # self.var_combo.setCurrentIndex(0)    #we don't reset this, as this is the key
            self.varStackedWidget.currentWidget().src_tedit.clear()
            self.varStackedWidget.currentWidget().regex_tedit.clear()
            self.varStackedWidget.currentWidget().old_name_tedit.clear()
            self.varStackedWidget.currentWidget().cbox.setChecked(False)
        else:
            # print('name : ' + currentValues.name + ', src: ' + currentValues.src +
            #       ', regex: ' +  currentValues.regex + ', old_name: ' + currentValues.old_name)
            # self.var_combo.setCurrentIndex(0)
            self.varStackedWidget.currentWidget().src_tedit.setText(currentValues.src)
            self.varStackedWidget.currentWidget().regex_tedit.setText(
                currentValues.regex
            )
            self.varStackedWidget.currentWidget().old_name_tedit.setText(
                currentValues.old_name
            )
            self.varStackedWidget.currentWidget().cbox.setChecked(currentValues.subdirs)

    """
    add button pushed call back
    """

    @pyqtSlot()
    def add_tab(self):
        # first validate the src tab is not null
        if (
            self.varStackedWidget.currentWidget().src_tedit.text() is None
            or self.varStackedWidget.currentWidget().src_tedit.text() == ""
            or self.varStackedWidget.currentWidget().old_name_tedit.text() is None
            or self.varStackedWidget.currentWidget().old_name_tedit.text() == ""
        ):
            QtWidgets.QMessageBox.critical(
                self,
                "Something is wrong",
                "source directory and existing variable name cannot be blank!",
                QtWidgets.QMessageBox.Ok,
                QtWidgets.QMessageBox.Ok,
            )
        else:
            """
            if not str(target).startsWith(unicode('http').encode('utf-8')):
                if os.path.exists(os.path.normpath(target)) == False:
                    QMessageBox.critical(self, unicode('Something is wrong').encode('utf-8'),
                      unicode('source directory does not exist!').encode('utf-8'),
                      QMessageBox.Ok, QMessageBox.Ok)
                    return #breakout now
            """
            # print type(self.var) = str
            # effort to speed string entry up: on the first entry of the src directory
            # go populate other variables as they're most likely to
            # be in the same directory.

            if self.var == "Tracer":
                if self.var_combo.currentText() == "temperature":
                    if self._sameValues(self.votemper):
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.votemper.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.votemper.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        self.votemper.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.votemper.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.votemper.regex = ""  # blank it over
                else:  # can only be salinity
                    if self._sameValues(self.vosaline):
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.vosaline.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.vosaline.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        self.vosaline.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.vosaline.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.vosaline.regex = ""
                if self.votemper.src == "":
                    self.votemper.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(0).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                if self.vosaline.src == "":
                    self.vosaline.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(1).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
            elif self.var == "Ice":  # iicethic,ileadfra,isnowthi
                if self.var_combo.currentText() == "ice thickness":
                    if self._sameValues(self.iicethic):
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.iicethic.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.iicethic.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.iicethic.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.iicethic.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.iicethic.regex = ""
                elif self.var_combo.currentText() == "leads fraction":
                    if self._sameValues(self.ileadfra):
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.ileadfra.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.ileadfra.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.ileadfra.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.ileadfra.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.ileadfra.regex = ""
                else:
                    if self._sameValues(self.isnowthi):  # snow thickness
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.isnowthi.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.isnowthi.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.isnowthi.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.isnowthi.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.isnowthi.regex = ""
                if self.iicethic.src == "":
                    self.iicethic.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(0).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                if self.ileadfra.src == "":
                    self.ileadfra.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(1).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                if self.isnowthi.src == "":
                    self.isnowthi.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(2).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
            elif self.var == "Dynamics":
                if self.var_combo.currentText() == "zonal velocity":
                    if self._sameValues(self.vozocrtx):
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.vozocrtx.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.vozocrtx.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.vozocrtx.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.vozocrtx.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.vozocrtx.regex = ""
                elif self.var_combo.currentText() == "meridian velocity":
                    if self._sameValues(self.vomecrty):
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.vomecrty.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.vomecrty.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.vomecrty.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.vomecrty.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.vomecrty.regex = ""
                elif self.var_combo.currentText() == "sea surface height":
                    if self._sameValues(self.sossheig):  # sea surface height
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.sossheig.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.sossheig.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.sossheig.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.sossheig.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.sossheig.regex = ""
                if self.vozocrtx.src == "":
                    self.vozocrtx.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(0).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                if self.vomecrty.src == "":
                    self.vomecrty.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(1).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                if self.sossheig.src == "":
                    self.sossheig.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(2).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
            elif self.var == "Grid":
                if self.var_combo.currentText() == "depth at T points":
                    if self._sameValues(self.gdept):
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.gdept.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.gdept.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.gdept.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.gdept.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.gdept.regex = ""
                elif self.var_combo.currentText() == "depth at W points":
                    if self._sameValues(self.gdepw):
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.gdepw.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.gdepw.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.gdepw.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.gdepw.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.gdepw.regex = ""
                elif self.var_combo.currentText() == "number of wet levels":
                    if self._sameValues(self.mbathy):  # sea surface height
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.mbathy.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.mbathy.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.mbathy.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.mbathy.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.mbathy.regex = ""
                elif (
                    self.var_combo.currentText() == "vertical scale factor at T points"
                ):
                    if self._sameValues(self.e3t):  # sea surface height
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.e3t.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.e3t.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.e3t.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.e3t.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.e3t.regex = ""
                elif (
                    self.var_combo.currentText() == "vertical scale factor at U points"
                ):
                    if self._sameValues(self.e3u):  # sea surface height
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.e3u.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.e3u.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.e3u.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.e3u.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.e3u.regex = ""
                elif (
                    self.var_combo.currentText() == "vertical scale factor at V points"
                ):
                    if self._sameValues(self.e3v):  # sea surface height
                        QtWidgets.QMessageBox.information(
                            self,
                            "For information",
                            "No changes have been made!",
                            QtWidgets.QMessageBox.Ok,
                            QtWidgets.QMessageBox.Ok,
                        )
                    else:
                        self.e3v.src = self._convertSrc(
                            self.varStackedWidget.currentWidget().src_tedit.text()
                        )
                        self.e3v.subdirs = (
                            self.varStackedWidget.currentWidget().cbox.isChecked()
                        )
                        self.e3v.old_name = (
                            self.varStackedWidget.currentWidget().old_name_tedit.text()
                        )
                        if (
                            self.varStackedWidget.currentWidget().regex_tedit.text()
                            is not None
                            or self.varStackedWidget.currentWidget().regex_tedit.text()
                            != ""
                        ):
                            self.e3v.regex = (
                                self.varStackedWidget.currentWidget().regex_tedit.text()
                            )
                        else:
                            self.e3v.regex = ""
                if self.gdept.src == "":
                    self.gdept.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(0).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                if self.gdepw.src == "":
                    self.gdepw.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(1).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                if self.mbathy.src == "":
                    self.mbathy.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(2).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                if self.e3t.src == "":
                    self.e3t.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(3).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                if self.e3u.src == "":
                    self.e3u.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(4).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                if self.e3v.src == "":
                    self.e3v.src = self._convertSrc(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )
                    self.varStackedWidget.widget(5).src_tedit.setText(
                        self.varStackedWidget.currentWidget().src_tedit.text()
                    )

    """
    convert the target folder into NcMl required format
    """

    def _convertSrc(self, thepath):
        # print 'thepath before trimming ', thepath
        fpath = str(
            thepath.trimmed()
        )  # 24Aug15 trimmed whitespaces at both end of QString and then cast to string
        # print 'thepath after trimming and casting ', fpath
        # make sure thatit is an absolute path and prefixed with file:/ and uses / file separator
        if fpath.startswith("http:/"):
            target = fpath  # do nothing
        elif fpath.startswith("file:/"):
            temp = os.path.normpath(fpath[6:])
            #            print 'normal path : ', temp
            target = str(
                "file:/" + str(os.path.abspath(temp)).replace("\\", "/")
            ).encode("utf-8")
        else:  # should be local file but not prefixed by file:/  we still check for absolute path
            #            print 'normal path : ', os.path.normpath(fpath)
            target = str(
                "file:/" + str(os.path.abspath(fpath)).replace("\\", "/")
            ).encode("utf-8")

        #       if not str(target).endswith('/'):
        #           target = target + '/'

        return target

    """
    compare the gui cached values with the stored values
    """

    def _sameValues(self, ncml_var):
        # print('before state - variable: ' + ncml_var.name + ', src: ' + ncml_var.src
        #      + ', regex: ' +  ncml_var.regex + ', old_name: ' + ncml_var.old_name)
        target = self._convertSrc(
            self.varStackedWidget.currentWidget().src_tedit.text()
        )

        if (
            target == ncml_var.src
            and self.varStackedWidget.currentWidget().old_name_tedit.text() is not None
            and self.varStackedWidget.currentWidget().old_name_tedit.text()
            == ncml_var.old_name
            and self.varStackedWidget.currentWidget().regex_tedit.text() is not None
            and self.varStackedWidget.currentWidget().regex_tedit.text()
            == ncml_var.regex
            and self.varStackedWidget.currentWidget().cbox.isChecked()
            == ncml_var.subdirs
        ):
            return True
        else:
            return False


"""
convenient class to hold the user input for each variable
"""


class ncml_variable(object):
    """convenient class to hold the values for a ncml variable."""

    def __init__(self, varName, old_name=""):
        # print 'created ncml_variable object : ' + varName
        self.name = varName
        self.src = ""
        self.regex = ""
        self.old_name = old_name
        self.subdirs = False
