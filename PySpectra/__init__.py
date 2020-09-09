#!/usr/bin/env python
'''
PySpectra displays 1D and 2D data
---------------------------------
*
* Applications based on PySpectra: 
* --------------------------------
*
$ pyspMonitor.py
  - listens to a Sardana Door and displays the 1D data
  - receives data and commands sent by HasyUtils.toPyspMonitor()
    The fact that toPyspMonitor() is part of HasyUtils and 
    not PySpectra is due to: toPyspMonitor() should also be
    called from Macros, Macros live in the MacroServer, the
    Python3 MacroServer imports PyQt5 whereas PySpectra imports
    PyQt4 producing a conflict related to QObject
  - has the displayCounters feature, see the Sardana/Spock/Taurus at DESY manual
  - uses the SignalCounter to display the a signal during mesh scans.

$ TngGui.py
  gives access to various parts of our Tango/Sardana environment

$ pyspViewer.py 
  displays 1D data from ASCII (.fio, .dat,. iint) and .nxs files

*
* Send data and commands to pyspMonitor
* -------------------------------------
*
  In [1]: import PySpectra, HasyUtils
  In [2]: HasyUtils.toPyspMonitor?
  In [3]: PySpectra.toPyspLocal?

*
* PySpectra Python interface in general
* -------------------------------------
*
Start by executing some examples using pyspViewer->Examples.
Afterwards you see how it was done by looking at the code
  pyspViewer->Examples->View Code

In addition, all PySpectra functions and modules are python-documented

  import PySpectra 
  In [1]: import PySpectra
  In [2]: PySpectra?
  In [3]: PySpectra.Scan?
  In [4]: PySpectra.Image?

*
* PySpectra magic commands in ipython:
* -----------------------------------
*  
In [1]: import PySpectra.ipython.startup
In [2]: PySpectra.ipython.startup?

'''

#
# here we include functions like cls(), display() into the toplevel 
# PySpectra name space. Depending on the state of PYSP_USE_MATPLOTLIB
# these function are from pyqt or matplotlib.
# createPDF is a special case because it has to be available also 
# in the pqt world.
#
#import os 
#try:
#    if os.environ["PYSP_USE_MATPLOTLIB"] == "True":
#        from mtpltlb.graphics import *
#    else:
#        from pqtgrph.graphics import *
#except: 
#    from pqtgrph.graphics import *
 
from .pqtgrph.graphics import *
from .mtpltlb.graphics import createPDF

from PySpectra.GQE import *
from PySpectra.ipython.ifc import *
from PySpectra.zmqIfc import *

