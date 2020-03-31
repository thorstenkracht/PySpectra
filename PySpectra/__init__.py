#!/usr/bin/env python
'''
PySpectra displays 1D data
--------------------------

The module PySpectra is usually imported by 

  import PySpectra as pysp
The interface
Scan()              a class returning a scan object
Image()             a class returning an image object
antiderivative()    calculate the Stammfunktion
cls()               clear the screen graphics window
createPDF()         create a PDF file
delete()            delete all or selected scans
derivative()        calculate the derivative
display()           display all or selected scans
getComment()        return the comment
getGqe()            return a scan/mesh object
getGqeList()        return the list of the scans/meshes
getTitle()          return the title
info()              print information about scans
launchGui()         launches the Gui
list()              print the list of scans
overlay( src, trgt) plot src in the viewport of trgt
procEventsLoop()    loop over QApp.processEvents until a <return> is entered
processEvents()     call QApp.processEvents()
read()              read .fio or .dat files
setComment()        set the comment 
setTitle()          set the title
setWsViewPort()     set the size of the graphics window
show()              print the list of scans
ssa()               simple scan analysis
write()             create a .fio file
yToMinusY()         change the sign of the y-values

*
* Default plot parameters for pyqtgraph
* in PySpectra.definitions
*
Space around the plots
  marginLeft
  marginTop
  marginRight
  marginBottom
Between the plots: 
  spacingHorizontal 
  spacingVertical 
*
* Applications based on PySpectra: 
*
$ pyspViewer.py [-m]
  successor of the FioViewer
  -m for matplotlib
$ pyspMonitor.py
  successor of the SardanaMonitor
*
* To use PySpectra in ipython, start with 
*
  $ ipython --profile=PySpectra

then edit
  ~/.ipython/profile_PySpectra/startup/00-start.py

to look like 
  #!/usr/bin/env python
  #__builtin__.__dict__[ 'graphicsLib'] = 'matplotlib'
  __builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'
  import PySpectra as pysp
  # PySpectra macros
  import PySpectra.ipython.startup 

then again
$ ipython --profile=PySpectra
In [1]: create t1
In [2]: display
In [3]: dir( pysp.t1)
*
* To use PySpectra from Python:
*
Look at some examples using pyspViewer->Examples then
view the code pyspViewer->Examples->View Code

In addition, start ipython and

  import PySpectra as pysp
  In [1]: import PySpectra as pysp
  In [2]: pysp?
  In [3]: dir( pysp) 
  In [4]: pysp.Scan?

Select the graphics library by before importing PySpectra
  import os
  os.environ["PYSP_USE_MATPLOTLIB"] = "True"
  import PySpectra as pysp

'''

import os as _os 
#
# here we include functions like cls(), display() into the toplevel 
# PySpectra name space. Depending on the state of PYSP_USE_MATPLOTLIB
# these function are from pyqt or matplotlib.
# createPDF is a special case because it has to be available also 
# in the pqt world.
#
try:
    if _os.environ["PYSP_USE_MATPLOTLIB"] == "True":
        from mtpltlb.graphics import *
    else:
        from pqtgrph.graphics import *
except: 
    from pqtgrph.graphics import *

from mtpltlb.graphics import createPDF


