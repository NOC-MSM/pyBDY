'''
This file contains all the logged errors from MOTU client, these are added over time. The MOTU client is prone to errors
that only may need a restart to complete. To add an error the key needs to be the error code returned by MOTU,
this is ususally a number or set of numbers. The dictionary entry is an explantion of the error. Only the key is checked
so make sure it is written correctly.
'''

# errors that are worth retrying download, e,g, error in netcdfwriter finish
MOTU_retry = {'004-27': 'Error in NetcdfWriter finish'}
# errors that are not worth retrying e.g. cmems network is down
MOTU_critical = {'50': 'Network Down'}
# FTP specific errors
FTP_retry = {'999': 'add ftp retry errors here' }
FTP_critical = {'999': 'add ftp critical errors here' }