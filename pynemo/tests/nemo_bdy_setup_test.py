'''
Unit test for setup of nemo bdy namelist
Will be testing the reading of the file and expected settings
@author: Mr. Srikanth Nagella
'''
import unittest
from pynemo.nemo_bdy_setup import * 

import os
class Test(unittest.TestCase):


    def testReadingOfNonExistingFile(self):
        self.assertRaises(IOError,Setup,'emptynamelist.bdy')
  
    def testReadingEmptyFile(self):
        #create an empty file and load it
        fo = open("test.bdy","wb")
        fo.close()
        setup = Setup('test.bdy')   
        #test settings after reading empty file   
        self.assertEqual(setup.settings,{} ,"There are some default settings after reading empty file")
        #delete empty file
        os.remove('test.bdy')

    def testAmbigiousEntriesInFile(self):
        #create an ambigious entry in file
        fo = open('test.bdy','wb')
        fo.write("! Ambigious Entry\n")
        fo.write("ambigious = true")
        fo.close()
        
        #test
        self.assertRaises(ValueError,Setup,'test.bdy')
        
        #delete file
        os.remove('test.bdy')
        
    def testEntryWithoutSpaceOnEitherSideOfEquals(self):
        #create an  entry in file
        fo = open('test.bdy','wb')
        fo.write("! Ambigious Entry\n")
        fo.write("ln_nonambigious=true")
        fo.close()
        
        #test
        setup = Setup('test.bdy')
        self.assertEqual(setup.settings,{'nonambigious':True},"Didn't recognize valid setting")
        
        #delete file
        os.remove('test.bdy')                

    def testEntryDifferentTypeEntries(self):
        #create an  entry in file
        fo = open('test.bdy','wb')
        fo.write("! Ambigious Entry\n")
        fo.write("ln_nonambigious=false !Comment testing false logical value\n")
        fo.write("rn_floatval=10.9\n")
        fo.write("nn_floatval2 = 20.9\n")
        fo.write("!Comments in middle of file\n")
        fo.write("cn_stringval='coordinates.nc'\n")
        fo.write("sn_stringval2 = 'gregorian'\n")        
        fo.close()
                
        #test
        setup = Setup('test.bdy')
        print(setup.settings)
        self.assertEqual(setup.settings['nonambigious'],False,"Didn't recognize logical setting")
        self.assertEqual(setup.settings['floatval'],10.9,"Didn't recognize rn value in setting")
        self.assertEqual(setup.settings['floatval2'],20.9,"Didn't recongnize nn value in setting")
        self.assertEqual(setup.settings['stringval'],'coordinates.nc',"Didn't recognize cn string value in setting")
        self.assertEqual(setup.settings['stringval2'],'gregorian',"Didn't recognize sn string value in setting")
        
        #delete file
        os.remove('test.bdy')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()