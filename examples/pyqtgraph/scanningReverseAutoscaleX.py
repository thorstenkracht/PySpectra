#!/usr/bin/env python
#
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import time
import pyqtgraph.functions as fn

win = None

def display():
    global win
    xMin = 0
    xMax = 50
    xDelta = 0.05
    x = np.arange( xMin, xMax, xDelta)
    x = x[::-1]
    t = np.tan(x)

    app = QtGui.QApplication.instance()
    if app is None:
        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')
        app = pg.mkQApp()
    
    if win is None:
        win = pg.GraphicsWindow( title="Scan the Tango Function")
    win.clear()

    #win.setBackground( QtGui.QBrush(QtGui.QColor(240,240,240)))   

    win.addLabel( "A figure containing one plot", row = 1, col = 1)
    tan = win.addPlot( row=2, col=1)
    tan.showGrid( x = True, y = True)
    tan.setTitle( title = "The tan() Function")
    tan.setLabel( 'left', 'tan')
    tan.setLabel( 'bottom', 'phase')
    tan.enableAutoRange( x = True, y = True)
    #tan.setXRange( xMin - 0.25, xMax + 0.25)
    tan.plot = tan.plot( pen = (0, 0, 255))

    #tan.clear()
    for i in range( len(x)):
        tan.plot.setData( x = x[0:i], y = t[0:i])
        app.processEvents()

if __name__ == "__main__":
    display()
