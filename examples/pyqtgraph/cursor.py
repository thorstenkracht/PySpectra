#!/usr/bin/env python
#

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import time, sys

plot = None
label = None

def mouseMoved(evt):
    mousePoint = plot.vb.mapSceneToView(evt[0])
    label.setText( "x %g, y %g" % (mousePoint.x(), mousePoint.y()), color = 'k')
    label.setPos( mousePoint.x(), mousePoint.y())

def mouseClicked(event):
    mousePoint = plot.vb.mapSceneToView(event[0].scenePos())
    print "Clicked: %g, %g" % (mousePoint.x(), mousePoint.y())

def display():
    global plot
    global label
    xMin = 0
    xMax = 10
    xDelta = 0.1
    x = np.arange( xMin, xMax, xDelta)
    t = np.tan(x)

    pg.setConfigOption( 'background', 'w')
    pg.setConfigOption( 'foreground', 'k')
    app = pg.mkQApp()
    
    win = pg.GraphicsWindow( title="Scan the Tango Function")
    win.clear()

    win.addLabel( "Demo for mouse moves and mouse clicks", row = 1, col = 1)

    plot = win.addPlot( row=2, col=1) 

    plot.showGrid( x = True, y = True)
    plot.setLabel( 'left', 'tan')
    plot.setLabel( 'bottom', 'phase')
    plot.enableAutoRange( x = False, y = True)
    plot.setXRange( xMin, xMax)

    proxy1 = pg.SignalProxy( plot.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
    proxy = pg.SignalProxy( plot.scene().sigMouseClicked, rateLimit=60, slot=mouseClicked)

    plot.plot( x, t, pen=( 0, 0, 255))

    label = pg.TextItem( "cursor", color='b', anchor = (0, 1.0))
    plot.addItem( label)
    label.setPos( x[0], t[0])

    print "Use Ctrl-C to exit"
    while True:
        time.sleep(0.01)
        app.processEvents()
    
if __name__ == "__main__":
    display()
