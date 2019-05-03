#!/usr/bin/env python

from PyQt4 import QtCore as _QtCore
from PyQt4 import QtGui as _QtGui

#
# if there are more scans than MANY_SCANS the x- and y-labels
# are suppressed and the title is moved into the plot
#
_MANY_SCANS = 20
_VERY_MANY_SCANS = 30

_FONT_SIZE_NORMAL = 14
_FONT_SIZE_SMALL = 12         # number of scans > MANY_SCANS
_FONT_SIZE_VERY_SMALL = 10    # number of scans > VERY_MANY_SCANS

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

