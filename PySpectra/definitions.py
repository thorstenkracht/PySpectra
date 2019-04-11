#!/usr/bin/env python

from taurus.external.qt import QtCore as _QtCore

FONT_SIZE_NORMAL = 14
FONT_SIZE_SMALL = 12    # number of scans > MANY_SCANS

dataFormats = [ 'fio', 'dat', 'iint']

_BLUE_MOVING = "#a0b0ff"
_RED_ALARM = "#ff8080"
_GREEN_OK = "#70ff70"
#
# the arrays are needed to put the colors and the 
# styles into a well-defined order
#
colorArr = [ 'RED', 
             'GREEN',
             'BLUE',
             'YELLOW',
             'CYAN',
             'MAGENTA',
             'BLACK']

colorDct = { 'RED': 0, 
             'GREEN': 1, 
             'BLUE': 2, 
             'YELLOW': 3,
             'CYAN': 4,
             'MAGENTA': 5,
             'BLACK': 6}


widthDct = { '1.0': 0,
             '1.2': 1,
             '1.4': 2,
             '1.6': 3,
             '1.8': 4,
             '2.0': 5,
         }

widthArr = [ '1.0', 
             '1.2',
             '1.4',
             '1.6',
             '1.8',
             '2.0']

styleArr = [ 'SOLID', 
             'DASHED', 
             'DOTTED', 
             'DASHDOTTED', 
             'DASHDOTDOTTED']

styleDct = { 'SOLID': 0, 
             'DASHED': 1,
             'DOTTED': 2,
             'DASHDOTTED': 3,
             'DASHDOTDOTTED': 4
         }
#
# pyqtgraph
#
colorCode = { 'red': 'r', 
        'blue': 'b',
        'green': 'g',
        'cyan': 'c',
        'magenta': 'm',
        'yellow': 'y',
        'black': 'k',
}
#
# matplotlib
#
style = { 'SOLID': _QtCore.Qt.SolidLine,
          'DASHED': _QtCore.Qt.DashLine,
          'DOTTED': _QtCore.Qt.DotLine,
          'DASHDOTTED': _QtCore.Qt.DashDotLine,
          'DASHDOTDOTTED': _QtCore.Qt.DashDotDotLine,
}

#
# if there are more scans than MANY_SCANS the x- and y-labels
# are suppressed and the title is moved into the plot
#
MANY_SCANS = 20
