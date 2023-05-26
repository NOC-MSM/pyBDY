Usage
=====
There are two tools available in pyNEMO. They are described in detail below.

pynemo
------

This command line tool reads a BDY file, extracts boundary data and prepares
the data for a NEMO simulation. The bdy file is a plain text file containing
key value pairs. Please look at the sample `namelist.bdy
<http://ccpforge.cse.rl.ac.uk/gf/project/pynemo/scmsvn/?action=browse&path=%2Ftrunk%2FPython%2Fdata%2Fnamelist.bdy&view=markup>`_
file, which shares common syntax with the NEMO simulation namelist input file.

.. note:: Directory paths in bdy file can be relative or absolute.
          The application picks the relative path from the current working
          directory.

Syntax for pynemo command is

::

   > pynemo [-g] -s <bdy file>

For help

::

   > pynemo -h
   > usage: pynemo [-g] -s <namelist.bdy>
   >        -g (optional) will open settings editor before extracting the data
   >        -s <bdy filename> file to use

Example comamnd

::

   > pynemo -g -s namelist.bdy


pynemo_settings_editor
----------------------

This tool will open a window where you can edit the mask and change the values of bdy parameters.

Syntax for pynemo_settings_editor command is

::

   > pynemo_settings_editor [-s <bdy filename>]

.. note:: If no file name is specified then a file dialog box will open to select a file.

For help

::

   > pynemo_settings_editor -h
   > usage: pynemo_settings_editor -s <namelist.bdy>

Example:

::

   pynemo_settings_editor -s namelist.bdy
