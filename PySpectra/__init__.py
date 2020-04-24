#!/usr/bin/env python
'''
PySpectra displays 1D data
--------------------------
*
* Applications based on PySpectra: 
* --------------------------------
*
$ pyspViewer.py 
  successor of the FioViewer

$ pyspMonitor.py
  successor of the SardanaMonitor

$ TngGui.py
  successor of TngTool.py

*
* Send data and commands to pyspMonitor
* -------------------------------------
*
  In [1]: import PySpectra.zmqIfc
  In [2]: PySpectra.zmqIfc?
  In [3]: PySpectra.zmqIfc.toPyspMonitor?
  In [4]: PySpectra.zmqIfc.execHsh?

*
* PySpectra Python module
* -----------------------
*
Execute some examples using pyspViewer->Examples.
Afterwards you can look at the code following pyspViewer->Examples->View Code

In addition, start ipython and

  import PySpectra 
  In [1]: import PySpectra
  In [2]: import PySpectra.GQE
  In [3]: PySpectra?
  In [4]: PySpectra.GQE.Scan?
  In [5]: PySpectra.GQE.Image?

*
* PySpectra magic commands in ipython:
* -----------------------------------
* 
In [1]: import PySpectra.ipython.startup
In [2]: PySpectra.ipython.startup?

'''

import os 
#
# here we include functions like cls(), display() into the toplevel 
# PySpectra name space. Depending on the state of PYSP_USE_MATPLOTLIB
# these function are from pyqt or matplotlib.
# createPDF is a special case because it has to be available also 
# in the pqt world.
#
try:
    if os.environ["PYSP_USE_MATPLOTLIB"] == "True":
        from mtpltlb.graphics import *
    else:
        from pqtgrph.graphics import *
except: 
    from pqtgrph.graphics import *

from mtpltlb.graphics import createPDF


