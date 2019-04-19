'''
Created on 21 Jan 2015

@author: Mr. Srikanth Nagella
'''
# pylint: disable=E1103
# pylint: disable=no-name-in-module
# pylint: disable=E1002
from PyQt4 import QtGui
from .nemo_bdy_namelist_edit import NameListEditor
from .nemo_bdy_mask_gui import MatplotlibWidget
from PyQt4.QtGui import QSizePolicy
from PyQt4.Qt import Qt

class InputWindow(QtGui.QDialog):
    '''
    Input Window for editing pyNEMO settings
    '''

    def __init__(self, setup):
        '''
        Initialises the UI components
        '''
        super(InputWindow, self).__init__()
        #initialise NameListEditor
        self.nl_editor = NameListEditor(setup)

        #initialise MatplotlibWidget
        self.mpl_widget = MatplotlibWidget()

        #connect namelistedit to matplotlibwidget
        self.nl_editor.bathymetry_update.connect(self.mpl_widget.set_bathymetry_file)
        self.nl_editor.mask_update.connect(self.mpl_widget.save_mask_file)
        self.nl_editor.mask_settings_update.connect(self.mpl_widget.set_mask_settings)

        if setup.bool_settings['mask_file']: 
            try: #Try to load with bathy and mask file
                self.mpl_widget.set_bathymetry_file(setup.settings['bathy'], setup.settings['mask_file'])
            except: # if mask file is not readable then open with bathy
                self.mpl_widget.set_bathymetry_file(setup.settings['bathy'],None)
        else:
            self.mpl_widget.set_bathymetry_file(setup.settings['bathy'],None)

        self.mpl_widget.set_mask_settings(float(setup.settings['mask_max_depth']), float(setup.settings['mask_shelfbreak_dist']))

        splitter = QtGui.QSplitter(Qt.Horizontal)
        splitter.addWidget(self.nl_editor)
        splitter.addWidget(self.mpl_widget)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)
        #set the Dialog title
        self.setWindowTitle("PyNEMO Settings Editor")
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))        
        #show the window
        self.show()
