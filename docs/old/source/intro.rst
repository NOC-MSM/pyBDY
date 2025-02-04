Introduction
============


The NRCT is a tool to set up the lateral boundary conditions for a regional `NEMO <http://www.nemo-ocean.eu>`_
model configuration.  The tool is written in Python, largely within the
`Anaconda <https://store.continuum.io/cshop/anaconda/>`_ environment to aid
wider distribution and to facilitate development.  In their current form these
tools are by no means generic and polished, but it is hoped will form a foundation
from which something more formal can be developed. The following sections provide a quick-start guide with
worked examples to help the user get up and running with the tool.

The tool essentially uses geographical and depth information from the source
data (e.g. a global ocean simulation) and destination simulation (i.e. the
proposed regional NEMO model configuration) to determine which source points are required
for data extraction. This is done using a kdtree approximate nearest neighbour
algorithm. The idea behind this targetted method is that it provides a generic
method of interpolation for any flavour of ocean model in order to set up a
regional NEMO model configuration.  At present (alpha release) the tools do not
contain many options, but those that exist are accessed either through a NEMO style
namelist or a convient GUI.
