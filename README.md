
The toplevel help can be found by

In [1]: import PySpectra as pysp

In [2]: pysp?



PySpectra displays 1D data
--------------------------

The module PySpectra is usually imported by 
  import PySpectra as pysp

It exports one class and several functions: 
Scan()              a class returning a scan object
Text()              a class returning a text object, called from Scan()
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

*** Default plot parameters for pyqtgraph
Space around the plots
  marginLeft
  marginTop
  marginRight
  marginBottom
Between the plots: 
  spacingHorizontal 
  spacingVertical 

*** Applications based on PySpectra: 
$ pyspViewer.py
  successor of the FioViewer
$ pyspMonitor.py
  successor of the SardanaMonitor

*** To use PySpectra from Python:

Look at some examples using pyspViewer->Examples then
view the code pyspViewer->Examples->View Code

In addition, start ipython and

  import PySpectra as pysp
  In [1]: import PySpectra as pysp
  In [2]: pysp?
  In [3]: dir( pysp) 
  In [4]: pysp.Scan?

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



