#!/usr/bin/env python
'''
PySpectra displays 1D data
--------------------------

The module PySpectra is usually imported by 
  import PySpectra as pysp

It exports one class and several functions: 
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

*** Applications based on PySpectra: 
$ pyspViewer.py
  successor of the FioViewer
$ pyspMonitor.py
  successor of the SardanaMonitor

*** To use PySpectra in ipython, start with 
  $ ipython --profile=PySpectra
then edit
  ~/.ipython/profile_PySpectra/startup/00-start.py
to look like 
  #!/usr/bin/env python
  import PySpectra as pysp
  # to define some PySpectra macros uncomment the following line
  #import PySpectra.ipython.startup 
then again
$ ipython --profile=PySpectra
In [1]: pysp.testCreate10()

'''
from dMgt.GQE import *
from dMgt.calc import *

import __builtin__
try:
    if __builtin__.__dict__[ 'graphicsLib'] == 'matplotlib':
        from mtpltlb.graphics import *
    else: 
        from pqtgrph.graphics import *
except: 
    __builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'
    from pqtgrph.graphics import *

from mtpltlb.graphics import createPDF

from utils import *
from definitions import *
import ipython.ifc 
