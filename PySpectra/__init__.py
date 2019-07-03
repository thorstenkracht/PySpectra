#!/usr/bin/env python
'''
PySpectra displays 1D data
--------------------------

The module PySpectra is usually imported by 

  import PySpectra as pysp

The interface
Scan()              a class returning a scan object
antiderivative()    calculate the Stammfunktion
cls()               clear the screen graphics window
createPDF()         create a PDF file
delete()            delete all or selected scans
derivative()        calculate the derivative
display()           display all or selected scans
getComment()        return the comment
getScan()           return a scan object
getScanList()       return the list of the scans
getTitle()          return the title
launchGui()         launches the Gui
overlay( src, trgt) plot src in the viewport of trgt
procEventsLoop()    loop over QApp.processEvents until a <return> is entered
processEvents()     call QApp.processEvents()
read()              read .fio or .dat files
setComment()        set the comment 
setTitle()          set the title
setWsViewPort()     set the size of the graphics window
show()              print the scans
ssa()               simple scan analysis
write()             create a .fio file
yToMinusY()         change the sign of the y-values

*
* Default plot parameters for pyqtgraph
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
$ pyspViewer.py
  successor of the FioViewer
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

#from PyQt4 import QtCore as _QtCore
#from PyQt4 import QtGui as _QtGui

from dMgt.GQE import *
from dMgt.calc import *
from examples.exampleCode import *

import os as _os 
try:
    if _os.environ["PYSP_USE_MATPLOTLIB"] == "True":
        from mtpltlb.graphics import *
    else:
        from pqtgrph.graphics import *
except: 
    from pqtgrph.graphics import *

#import __builtin__
#try:
#    if __builtin__.__dict__[ 'graphicsLib'] == 'matplotlib':
#    else: 
#        from pqtgrph.graphics import *
#except: 
#    __builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'
#    from pqtgrph.graphics import *

from mtpltlb.graphics import createPDF
from utils import *
import ipython.ifc 
import definitions
