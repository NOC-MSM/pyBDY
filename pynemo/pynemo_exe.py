'''
Entry for the project

@author: Mr. Srikanth Nagella
'''

import sys, getopt
import profile
import logging

# Logging set to info
logging.basicConfig(level=logging.INFO)
import time
def main():
    """ Main function which checks the command line parameters and
        passes them to the profile module for processing """

    setup_file = ''
    mask_gui = False
    try:
        opts, dummy_args = getopt.getopt(sys.argv[1:], "h:s:d:g", ["help","setup=","download_cmems=","mask_gui"])
    except getopt.GetoptError:
        print "usage: pynemo -g -s -d <namelist.bdy> "
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print "usage: pynemo [-g] -s -d <namelist.bdy> "
            print "       -g (optional) will open settings editor before extracting the data"
            print "       -s <bdy filename> file to use"
            print "       -d (optional) will download CMEMS data using provided bdy file"
            sys.exit()
        elif opt in ("-s", "--setup"):
            setup_file = arg
        elif opt in("-g", "--mask_gui"):
            mask_gui = True
        elif opt in ("-d", "--download_cmems"):
            print "downloading from CMEMS repository....."
            setup_file = arg
            t0 = time.time()
            profile.download_cmems(setup_file)
            t1 = time.time()
            print "CMEMS download time: %s" % (t1 - t0)
            sys.exit(0)
    if setup_file == "":
        print "usage: pynemo [-g] -s <namelist.bdy> "
        sys.exit(2)

    #Logger
    #logger = logging.getLogger(__name__)
    t0 = time.time()
    profile.process_bdy(setup_file, mask_gui)
    t1 = time.time()
    print "Execution Time: %s" % (t1-t0)

if __name__ == "__main__":
    main()
