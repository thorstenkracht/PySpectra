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

*** To use PySpectra from Python:

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

from PyQt4 import QtCore as _QtCore
from PyQt4 import QtGui as _QtGui

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

#+++
#
# if there are more scans than MANY_SCANS the x- and y-labels
# are suppressed and the title is moved into the plot
#
_MANY_SCANS = 20
_VERY_MANY_SCANS = 30

FONT_SIZE_NORMAL = 14
FONT_SIZE_SMALL = 12       # number of scans > MANY_SCANS
FONT_SIZE_VERY_SMALL = 10    # number of scans > VERY_MANY_SCANS

TICK_FONT_SIZE_NORMAL = 12
TICK_FONT_SIZE_SMALL = 10        # number of scans > MANY_SCANS
TICK_FONT_SIZE_VERY_SMALL = 8    # number of scans > VERY_MANY_SCANS

_LEN_MAX_TITLE = 25
#
# used by pqt_graphics
#
marginLeft = 10
marginTop = 20
marginRight = 40
marginBottom = 20
spacingHorizontal = -30
spacingVertical = -15

_dataFormats = [ 'fio', 'dat', 'iint']

_BLUE_MOVING = "#a0b0ff"
_RED_ALARM = "#ff8080"
_GREEN_OK = "#70ff70"
#
# the arrays are needed to put the colors and the 
# styles into a well-defined order
#
_lineColorArr = [ 
    'RED', 
    'GREEN',
    'BLUE',
    'YELLOW',
    'CYAN',
    'MAGENTA',
    'BLACK',
    'WHITE', 
    'NONE', 
]

_lineColorDct = { 
    'RED': 0, 
    'GREEN': 1, 
    'BLUE': 2, 
    'YELLOW': 3,
    'CYAN': 4,
    'MAGENTA': 5,
    'BLACK': 6,
    'WHITE': 7,
    'NONE': 8,
}

_lineWidthDct = { 
    '1.0': 0,
    '1.2': 1,
    '1.4': 2,
    '1.6': 3,
    '1.8': 4,
    '2.0': 5,
    '2.5': 6,
    '3.0': 7,
}

_lineWidthArr = [ 
    '1.0', 
    '1.2',
    '1.4',
    '1.6',
    '1.8',
    '2.0',
    '2.5',
    '3.0',
]

_lineStyleArr = [ 
    'SOLID', 
    'DASHED', 
    'DOTTED', 
    'DASHDOTTED', 
]

_lineStyleDct = { 
    'SOLID': 0, 
    'DASHED': 1,
    'DOTTED': 2,
    'DASHDOTTED': 3,
}
#
# pyqtgraph
#
_colorCode = { 
    'red': 'r', 
    'blue': 'b',
    'green': 'g',
    'cyan': 'c',
    'magenta': 'm',
    'yellow': 'y',
    'black': 'k',
    'white': 'w',
    'none': 'w',
}
#
# matplotlib: 
#  '.' 	point marker
#  ',' 	pixel marker
#  'o' 	circle marker
#  'v' 	triangle_down marker
#  '^' 	triangle_up marker
#  '<' 	triangle_left marker
#  '>' 	triangle_right marker
#  '1' 	tri_down marker
#  '2' 	tri_up marker
#  '3' 	tri_left marker
#  '4' 	tri_right marker
#  's' 	square marker
#  'p' 	pentagon marker
#  '*' 	star marker
#  'h' 	hexagon1 marker
#  'H' 	hexagon2 marker
#  '+' 	plus marker
#  'x' 	x marker
#  'D' 	diamond marker
#  'd' 	thin_diamond marker
#  '|' 	vline marker
#  '_' 	hline marker
#
# pyqtgraph
#  'o' 	circle marker
#  't' 	triangle
#  'd' 	diamond
#  '+' 	plus marker
#
_symbolArr = [ 
    'o', 
    's',
    'd',
    '+',
]
_symbolDct = { 
    'o': 0,
    's': 1, 
    'd': 2, 
    '+': 3, 
}
_symbolDctFullName = { 
    'o': 'Circle',
    's': 'Square', 
    'd': 'Diamond', 
    '+': 'Plus', 
}
_symbolSizeDct = { 
    '1': 0,
    '3': 1,
    '5': 2,
    '8': 3,
    '10': 4,
    '15': 5,
    '25': 6,
    '35': 7,
}

_symbolSizeArr = [ 
    '1', 
    '3',
    '5',
    '8',
    '10',
    '15',
    '25',
    '35',
]
#
# matplotlib
#
_lineStyle = { 
    'SOLID': _QtCore.Qt.SolidLine,
    'DASHED': _QtCore.Qt.DashLine,
    'DOTTED': _QtCore.Qt.DotLine,
    'DASHDOTTED': _QtCore.Qt.DashDotLine,
    'DASHDOTDOTTED': _QtCore.Qt.DashDotDotLine,
}
