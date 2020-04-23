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
    the function PySpectra.zmqIfc.toPyspMonitor()
    communicates with the pyspMonitor via ZMQ

# TngGui.py
  successor of TngToog.py
*
* To use PySpectra from Python:
* -----------------------------
*
Look at some examples using pyspViewer->Examples then
view the code pyspViewer->Examples->View Code

In addition, start ipython and

  import PySpectra 
  In [1]: import PySpectra
  In [2]: PySpectra?
  In [3]: dir( PySpectra) 
  In [4]: PySpectra.GQE.Scan?
*
* To use PySpectra in ipython:
* ----------------------------
* Create a profile: 

  $ ipython --profile=PySpectra
  In [1]: exit

Then edit the startup file: 
  ~/.ipython/profile_PySpectra/startup/00-start.py
to look like 
  #!/usr/bin/env python
  # PySpectra macros
  import PySpectra.ipython.startup 

then again
$ ipython --profile=PySpectra
In [1]: create t1
In [2]: display
In [3]: o = PySpectra.GQE.getGqe( "t1")
In [4]: dir( o)

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


