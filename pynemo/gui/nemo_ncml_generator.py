'''
Created on 6 Aug 2015

@author: Shirley Crompton, UK Science and Technology Facilities Council
'''
import logging
import os
import xml.etree.ElementTree as ET
from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from . import nemo_ncml_tab_widget
from thredds_crawler.crawl import Crawl

class Ncml_generator(QtWidgets.QDialog):
    '''
    Gui editor to capture user input for the purpose of generating NCML representation of pynemo source datasets.
    '''

    def __init__(self, basefile):
        '''
        Initialises the UI components
        '''
        super(Ncml_generator, self).__init__()     # no params yet, may be allow user to predefine an input ncml for edit???? 
        #Logging for class
        self.logger = logging.getLogger(__name__)   #logger config'ed in pynemo_exe.py
        
        if not basefile:
            testpath, file_name = os.path.split(__file__)
            self.baseFile = os.path.join(testpath,'base.ncml')
        else:
            self.baseFile = basefile
            print('ncml baseFile : ', str(self.baseFile))
        
        self.filename = None # store the output file pointer      
        self.initUI()
        
        
    def initUI(self):
        QtWidgets.QToolTip.setFont(QtGui.QFont('SansSerif', 11))
        '''
        vbox is the top container
        '''
        #the 
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 5, 5)
        
        '''
        top panel for output file
        '''
        top_outfile_label = QtWidgets.QLabel('Output filename')
        self.top_outfile_name = QtWidgets.QLineEdit()    #location is pre-defined
        self.top_outfile_name.setToolTip('Define output file')
        self.top_outfile_name.returnPressed.connect(self.get_fname_input)
        
        top_outfile_button = QtWidgets.QPushButton('Select file')
        top_outfile_button.clicked.connect(self.get_fname)
        
        top_grpBox = QtWidgets.QGroupBox('Define output file', None)
        top_grid = QtWidgets.QGridLayout(top_grpBox)
        top_grid.setVerticalSpacing(5)
        top_grid.setHorizontalSpacing(10)
        top_grid.addWidget(top_outfile_label, 1, 0)
        top_grid.addWidget(self.top_outfile_name, 1, 1)
        top_grid.addWidget(top_outfile_button, 1,2, QtCore.Qt.AlignRight)
        
        '''
        middle panel for tab folder
        '''
        self.tabWidget = QtWidgets.QTabWidget()
        self.tracer_tab = nemo_ncml_tab_widget.Ncml_tab("Tracer")
        self.tracer_tab.setEnabled(False)
        self.dynamic_tab = nemo_ncml_tab_widget.Ncml_tab("Dynamics")
        self.dynamic_tab.setEnabled(False)
        self.ice_tab = nemo_ncml_tab_widget.Ncml_tab("Ice")
        self.ice_tab.setEnabled(False)
        self.ecosys_tab = nemo_ncml_tab_widget.Ncml_tab("Ecosystem")
        self.ecosys_tab.setEnabled(False)
        self.grid_tab = nemo_ncml_tab_widget.Ncml_tab("Grid")
        self.grid_tab.setEnabled(False)
                
        self.tabWidget.addTab(self.tracer_tab, "Tracer")
        self.tabWidget.addTab(self.dynamic_tab, "Dynamics")
        self.tabWidget.addTab(self.ice_tab, "Ice")
        self.tabWidget.addTab(self.ecosys_tab, "Ecosystem") # should be disabled
        self.tabWidget.addTab(self.grid_tab, "Grid") # should be disabled
        self.tabWidget.setMovable(False)
#        if self.tabWidget.widget(self.tabWidget.currentIndex()).isEnabled() is True:
        
#       self.connect(self.tabWidget, SIGNAL('currentChanged(int)'),self.enable_btn_update)
        self.tabWidget.currentChanged.connect(lambda: self.enable_btn_update(enable_btn))
        '''
        button bar
        '''
        go_btn = QtWidgets.QPushButton('Generate')
        go_btn.setToolTip('Add all variable definitions before generating NcML file.')
        cancel_btn = QtWidgets.QPushButton('Cancel')
        enable_btn = QtWidgets.QPushButton('Enable Tab')
        #layout button bar        
        btn_hBox = QtWidgets.QHBoxLayout(None)
        btn_hBox.setContentsMargins(5, 5, 5, 5)
        btn_hBox.setSpacing(10)
        btn_hBox.setAlignment(QtCore.Qt.AlignRight)
        btn_hBox.addWidget(enable_btn)
        btn_hBox.addWidget(cancel_btn)
        btn_hBox.addWidget(go_btn)
        
        go_btn.clicked.connect(self.generate)
        cancel_btn.clicked.connect(self.close)
        enable_btn.clicked.connect(lambda: self.enable_tab(enable_btn))
#       enable_btn.clicked.connect(self.enable_tab)
        
        '''
        Assemble the top layout container
        '''
        vbox.addWidget(top_grpBox)
        vbox.addWidget(self.tabWidget)
        vbox.addLayout(btn_hBox)
        
        #self.setLayout(grp_box)        
        self.setWindowIcon(QtGui.QIcon('/Users/jdha/anaconda/lib/python2.7/site-packages/pynemo-0.2-py2.7.egg/pynemo/gui/nemo_icon.png'))    #doesn't work       
        self.setWindowTitle("PyNEMO NcML Generator")
        self.resize(650,300)
        
        #has to change the default focus to stop the output file QTextedit to trigger the widget in focus when enter is pressed.  Not sure why this happens???
        self.tabWidget.setFocus()
        #show the window
        self.show()
        
    
    '''
    file picker call back for output file input field
    '''
    @pyqtSlot()
    def get_fname(self):
        # When you call getOpenFileName, a file picker dialog is created
        # and if the user selects a file, it's path is returned, and if not
        # (ie, the user cancels the operation) None is returned
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Select output file', '', selectedFilter='*.ncml')
        if fname:
            self.filename = fname #returns a QString
            self.top_outfile_name.setText(str(fname))
            #print 'the output file is set to : ' + self.filename
    '''
    output file text box call back handler
    '''
    @pyqtSlot()
    def get_fname_input(self):
        self.filename = self.top_outfile_name.text()
        #print 'the output file is manually set to : ' + self.filename
    '''
    call back to handle the generate button pressed
    '''
    @pyqtSlot()
    def enable_btn_update(self, enable_btn):
        if self.tabWidget.widget(self.tabWidget.currentIndex()).isEnabled() is True:
            enable_btn.setText('Disable Tab')
        else:
            enable_btn.setText('Enable Tab')
    '''
    call back to handle the generate button pressed
    '''
    @pyqtSlot()
    def enable_tab(self,enable_btn):
#   def enable_tab(self):
        #validate output file
        if self.tabWidget.widget(self.tabWidget.currentIndex()).isEnabled() is True:
            self.tabWidget.widget(self.tabWidget.currentIndex()).setEnabled(False)
            enable_btn.setText('Enable Tab')
        else:
            self.tabWidget.widget(self.tabWidget.currentIndex()).setEnabled(True)
            enable_btn.setText('Disable Tab')

    '''
    call back to handle the generate button pressed
    '''
    @pyqtSlot()
    def generate(self):
        #validate output file
        if self.filename is None or self.filename == "":
            if self.top_outfile_name.text() is None or self.top_outfile_name.text() == "":
                QtWidgets.QMessageBox.critical(self, 'Something is wrong', 'No output file specified!', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                return
            else:
                self.filename = self.top_outfile_name.text()
            
        if(os.path.exists(os.path.dirname(str(self.filename)))) == False:
            #if os.path.dirname(os.path.dirname(os.path.exists(os.path.normpath(str(self.filename))))) == False:
            QtWidgets.QMessageBox.critical(self, 'Something is wrong', 'Invalid output directory!  Cannot generate file!', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            #print 'invalid target directory!  Cannot generate.'
            return
            
                
        #validate if all the variables are defined, use the mandatory src field as a proxy
        # also need to check that the tab is active

        tabsList = []
        if self.tracer_tab.isEnabled() is True:
            if self.tracer_tab.votemper.src != ""  and \
               self.tracer_tab.vosaline.src != "" :
                tabsList.extend([self.tracer_tab.votemper, self.tracer_tab.vosaline])
            else:
                QtWidgets.QMessageBox.information(self, 'Something is wrong', 'Not all the variables under the tracer tab have been defined!', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)


        if self.ice_tab.isEnabled() is True:
            if self.ice_tab.ileadfra.src != ""  and \
               self.ice_tab.iicethic.src != ""  and \
               self.ice_tab.isnowthi.src != "" :
                tabsList.extend([self.ice_tab.iicethic, self.ice_tab.ileadfra, self.ice_tab.isnowthi])
            else:
                QtWidgets.QMessageBox.information(self, 'Something is wrong', 'Not all the variables under the ice tab have been defined!', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

        if self.dynamic_tab.isEnabled() is True:
            if self.dynamic_tab.vozocrtx.src != ""  and \
               self.dynamic_tab.vozocrtx.src != ""  and \
               self.dynamic_tab.sossheig.src != "" :
                tabsList.extend([self.dynamic_tab.vozocrtx, self.dynamic_tab.vomecrty, self.dynamic_tab.sossheig])
            else:
                QtWidgets.QMessageBox.information(self, 'Something is wrong', 'Not all the variables under the dynamics tab have been defined!', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

        if self.grid_tab.isEnabled() is True:
            if self.grid_tab.gdept.src != ""    and \
               self.grid_tab.gdepw.src != ""    and \
               self.grid_tab.mbathy.src != ""   and \
               self.grid_tab.e3t.src != ""      and \
               self.grid_tab.e3u.src != ""      and \
               self.grid_tab.e3v.src != "" :
                tabsList.extend([self.grid_tab.gdept, self.grid_tab.gdepw, self.grid_tab.mbathy, self.grid_tab.e3t, self.grid_tab.e3u, self.grid_tab.e3v])
            else:
                QtWidgets.QMessageBox.information(self, 'Something is wrong', 'Not all the variables under the grid tab have been defined!', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

        try:
            self.generateNcML(tabsList) #go ahead and do it
        except:
            raise

        QtWidgets.QMessageBox.information(self, 'Success.', 'NcML file generated.', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    '''
    Function to generates the NcML text and write it to the user defined output file
    '''
    def generateNcML(self, tabsList):
        #first open the default base file
        ns = '{http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2}'
        self.tree = self._parseNcml()
        self.root = self.tree.getroot()
        #create a netcdf element for each tab variable
        for tab in tabsList:
            netcdfE = ET.Element(ns+'netcdf') #src directory is converted to the correct format when added/
            if str(tab.src).startswith("http:") or str(tab.src).startswith("https:"):
                #Its url so use thredds crawler to get the urls
                urls = self.url_trawler(tab.src,str(tab.regex))
                aggE = ET.Element(ns+'aggregation', name=str(tab.name), type='joinExisting', dimName='time_counter') #tab.name already encoded                
                for nc_url in urls:
                    tcNetcdf = ET.Element(ns+'netcdf', location=str(nc_url))
                    aggE.append(tcNetcdf)
                netcdfE.append(aggE)
            else:
                scanE = ET.Element(ns+'scan', location=str(tab.src), regExp=str(tab.regex))
                if tab.subdirs == True:
                    scanE.set('subdirs', 'true')
                aggE = ET.Element(ns+'aggregation', name=str(tab.name), type='joinExisting', dimName='time_counter') #tab.name already encoded
                aggE.append(scanE)
                netcdfE.append(aggE)
            self.root[0].append(netcdfE)    #add the new netcdf element to the top aggregation 
            
            #deal with variable name change TODO put this into a loop?
            if tab.old_name is not None and tab.old_name != "":
                vname = 'variable'
                #v is None          
                if tab.name == 'temperature' and tab.old_name != 'votemper':
                    v = ET.Element(ns+vname, name='votemper', orgName = str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'salinity' and tab.old_name != 'vosaline':
                    v = ET.Element(ns+vname, name='vosaline', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'ice_thickness' and tab.old_name != 'iicethic':
                    v = ET.Element(ns+vname, name='iicethic', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'leads_fraction' and tab.old_name != 'ileadfra':
                    v = ET.Element(ns+vname, name='ileadfra', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'snow_thickness' and tab.old_name != 'isnowthi':
                    v = ET.Element(ns+vname, name='isnowthi', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'zonal_velocity' and tab.old_name != 'vozocrtx':
                    v = ET.Element(ns+vname, name='vozocrtx', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'meridian_velocity' and tab.old_name != 'vomecrty':
                    v = ET.Element(ns+vname, name='vomecrty', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'sea_surface_height' and tab.old_name != 'sossheig':
                    v = ET.Element(ns+vname, name='sossheig', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'depth_at_t_points' and tab.old_name != 'gdept':
                    v = ET.Element(ns+vname, name='gdept', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'depth_at_w_points' and tab.old_name != 'gdepw':
                    v = ET.Element(ns+vname, name='gdepw', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'number_of_wet_levels' and tab.old_name != 'mbathy':
                    v = ET.Element(ns+vname, name='mbathy', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'vertical_scale_factors_at_t_points' and tab.old_name != 'e3t':
                    v = ET.Element(ns+vname, name='e3t', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'vertical_scale_factors_at_u_points' and tab.old_name != 'e3u':
                    v = ET.Element(ns+vname, name='e3u', orgName =  str(tab.old_name))
                    self.root.append(v)
                elif tab.name == 'vertical_scale_factors_at_v_points' and tab.old_name != 'e3v':
                    v = ET.Element(ns+vname, name='e3v', orgName =  str(tab.old_name))
                    self.root.append(v)
                   
        #write ncml to file
        try:
            self.indent(self.root, 0)   #24Aug15 format the xml for pretty printing
            self.tree.write(self.filename, encoding='utf-8')
        except IOError as xxx_todo_changeme:
            (errno, strerror) = xxx_todo_changeme.args
            self.logger.error("I/O error({0}): {1}".format(errno, strerror))
        except:
            self.logger.error('Error generating ncml file')
            raise
             
    '''
    Function to retrieve the NcML file template
    '''
    def _parseNcml(self):
        try:
            parser = ET.XMLParser(encoding="utf-8")
            tree = ET.parse(self.baseFile, parser=parser)
            return tree
        except ET.ParseError as v:
                row, column = v.position
                print("error on row", row, "column", column, ":", v)
                
    '''
    Function to format xml.  Based on code provided by http://effbot.org/zone/element-lib
    '''
    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i     
    
    """
        This method trawls throught the url with a given expression and returns the
        list of urls that match the expression 
    """
    def url_trawler(self, url, expr):
        if url.endswith(".xml"):
            c = Crawl(url, select=[expr])
        elif url.endswith("/"): # we'll try and add catalog.xml as the user may have just provided a directory
            c = Crawl(url+"catalog.xml", select=[expr])
        else:                   # we'll try and add catalog.xml as the user may have just provided a directory
            c = Crawl(url+"/catalog.xml", select=[expr])
        urls = [s.get("url") for d in c.datasets for s in d.services if s.get("service").lower()=="opendap"]
        return urls
