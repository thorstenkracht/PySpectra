#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
ViewBox is the general-purpose graphical container that allows the user to 
zoom / pan to inspect any area of a 2D coordinate system. 

This unimaginative example demonstrates the constrution of a ViewBox-based
plot area with axes, very similar to the way PlotItem is built.
"""


## Add path to library (just for examples; you do not need this)
#import initExample

## This example uses a ViewBox to create a PlotWidget-like interface

#from scipy import random
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.setWindowTitle('pyqtgraph example: ViewBox')
mw.show()
mw.resize(800, 600)

gv = pg.GraphicsView()
mw.setCentralWidget(gv)
layout = QtGui.QGraphicsGridLayout()
layout.setHorizontalSpacing(0)
layout.setVerticalSpacing(0)

vb = pg.ViewBox()

p1 = pg.PlotDataItem()
vb.addItem(p1)

tItem = pg.TextItem( "ein test", color = 'w')
tItem.setPos( 1.0, 20.0)
vb.addItem( tItem)

layout.addItem(vb, 0, 1)
gv.centralWidget.setLayout(layout)


xScale = pg.AxisItem(orientation='bottom', linkView=vb)
layout.addItem(xScale, 1, 1)
yScale = pg.AxisItem(orientation='left', linkView=vb)
layout.addItem(yScale, 0, 0)

xScale.setLabel(text="<span style='color: #ff0000; font-weight: bold'>X</span> <i>Axis</i>", units="s")
yScale.setLabel('Y Axis', units='V')

x = np.linspace( 0, 100, 1000.)
y = np.linspace( 0, 100, 1000.)
p1.setData( y = y, x = x)
vb.autoRange()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
