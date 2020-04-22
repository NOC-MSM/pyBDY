Troubleshooting
===============

**Always** check the PyNEMO log file. This is usually saved in the working directory of PyNEMO as nrct.log. It gives helpful information
which may help to diagnose issues. E.g. ValueErrors that are result of a THREDDS server being down and unable to provide data files.

1. pyNEMO crashing in MacOSX (Yosemite)?

*  Downgrade the scipy package to 0.15

2. How to make pyNEMO to work behind firewall/proxy?

*  Set the environment variable http_proxy. eg. in Linux export http_proxy=<proxy-server>:<proxy-port>

3. Getting this error 'Warning: Please make sure pyjnius is installed and jvm.dll/libjvm.so/libjvm.dylib is in the path' ?

*  This error is displayed when the application cannot find the java installation on the local machine. please install a java 7.x runtime from http://www.oracle.com/technetwork/java/javase/downloads/jre7-downloads-1880261.html and append the path to the library in the system path. eg. on windows SET PATH="C:\\Program Files (x86)\\Java\\jre1.7\\bin\\client"  on Linux in shell export LD_LIBRARY_PATH=/opt/java/jdk1.7.0_45/jre/lib/amd64/server:$LD_LIBRARY_PATH  in osx export DYLD_LIBRARY_PATH=/System/Library/Java/JavaVirtualMachines/jdk1.7.0_09.jdk/Contents/Home/jre/lib/server:$DYLD_LIBRARY_PATH
