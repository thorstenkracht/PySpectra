#!/usr/bin/env python
'''
here are the definitions used in various python files of the project

  - this file is importet by PySpectra/__init__.py
  - programm refere to the variables like pysp.definitions.MANY_GQES
  - we avoid _MANY_GQES because this variable appear under pysp.definitions
    and is thus well hidden
'''
#
#
# if there are more scans than MANY_GQES the x- and y-labels
# are suppressed and the title is moved into the plot
#
from PyQt4 import QtCore as _QtCore
from PyQt4 import QtGui as _QtGui
MANY_GQES = 20
VERY_MANY_GQES = 30

FONT_SIZE_NORMAL = 14
FONT_SIZE_SMALL = 12       # number of scans > MANY_GQES
FONT_SIZE_VERY_SMALL = 10    # number of scans > VERY_MANY_GQES

TICK_FONT_SIZE_NORMAL = 12
TICK_FONT_SIZE_SMALL = 10        # number of scans > MANY_GQES
TICK_FONT_SIZE_VERY_SMALL = 8    # number of scans > VERY_MANY_GQES

LEN_MAX_TITLE = 25
#
# used by pqt_graphics
#
marginLeft = 10
marginTop = 20
marginRight = 40
marginBottom = 20
spacingHorizontal = -30
spacingVertical = -15

dataFormats = [ 'fio', 'dat', 'iint', 'nxs']

BLUE_MOVING = "#a0b0ff"
RED_ALARM = "#ff8080"
GREEN_OK = "#70ff70"
#
# the arrays are needed to put the colors and the 
# styles into a well-defined order
#
colorArr = [ 
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

colorDct = { 
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

lineWidthDct = { 
    '1.0': 0,
    '1.2': 1,
    '1.4': 2,
    '1.6': 3,
    '1.8': 4,
    '2.0': 5,
    '2.5': 6,
    '3.0': 7,
}

lineWidthArr = [ 
    '1.0', 
    '1.2',
    '1.4',
    '1.6',
    '1.8',
    '2.0',
    '2.5',
    '3.0',
]
#
# the generic line styles: SOLID, DASHED, DOTTED, DASHDOTTED
#
lineStyleArr = [ 
    'SOLID', 
    'DASHED', 
    'DOTTED', 
    'DASHDOTTED', 
]

lineStyleDct = { 
    'SOLID': 0, 
    'DASHED': 1,
    'DOTTED': 2,
    'DASHDOTTED': 3,
}
#
# pyqtgraph
#
colorCode = { 
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
symbolArr = [ 
    'o', 
    's',
    'd',
    '+',
]
symbolDct = { 
    'o': 0,
    's': 1, 
    'd': 2, 
    '+': 3, 
}
symbolDctFullName = { 
    'o': 'Circle',
    's': 'Square', 
    'd': 'Diamond', 
    '+': 'Plus', 
}
symbolSizeDct = { 
    '1': 0,
    '3': 1,
    '5': 2,
    '8': 3,
    '10': 4,
    '15': 5,
    '25': 6,
    '35': 7,
}

symbolSizeArr = [ 
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
# pyqtgraph
#
lineStylePQT = { 
    'SOLID': _QtCore.Qt.SolidLine,
    'DASHED': _QtCore.Qt.DashLine,
    'DOTTED': _QtCore.Qt.DotLine,
    'DASHDOTTED': _QtCore.Qt.DashDotLine,
}

colorMaps = [ 
    'binary', 'blackwhite', 'flag', 'Greys', 'Greys_r', 'Blues', 'Greens', 'Reds',
    'prism', 'gist_earth', 'terrain',
    'gnuplot2', 'CMRmap',
    'rainbow', 'jet', 'nipy_spectral', 
    'hsv',
    'Spectral', 
] 

moduloList = [ -1, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
maxIterList = [ 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
