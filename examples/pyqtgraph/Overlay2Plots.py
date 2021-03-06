#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Demonstrates a way to put multiple axes around a single plot. 

(This will eventually become a built-in feature of PlotItem)

"""
#import initExample ## Add path to library (just for examples; you do not need this)

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
p1 = None
p2 = None
pw = None

## Handle view resizing 
def updateViews():
    ## view has resized; update auxiliary views to match
    global p1, p2
    p2.setGeometry(p1.vb.sceneBoundingRect())
    
    ## need to re-update linked axes since this was called
    ## incorrectly while views had different shapes.
    ## (probably this should be handled in ViewBox.resizeEvent)
    p2.linkedViewChanged(p1.vb, p2.XAxis)


def main(): 
    global p1, p2, pw
    pg.mkQApp()

    pw = pg.PlotWidget()
    pw.show()
    pw.setWindowTitle('pyqtgraph example: MultiplePlotAxes')
    p1 = pw.plotItem
    p1.setLabels(left='axis 1')
    
    ## create a new ViewBox, link the right axis to its coordinate system
    p2 = pg.ViewBox()
    p2.setYRange( -10., 200)
    p1.showAxis('right')
    p1.scene().addItem(p2)
    #
    # Link this axis to a ViewBox, causing its displayed range to 
    # match the visible range of the view.
    #
    p1.getAxis('right').linkToView(p2)
    #
    # link the views x-axis to another view
    #
    p2.setXLink(p1)
    p1.getAxis('right').setLabel('axis2', color='#0000ff')

    updateViews()
    p1.vb.sigResized.connect(updateViews)
    
    p1.plot([1,2,4,8,16,32])
    p2.addItem(pg.PlotCurveItem([10,20,40,80,40,20], pen='b'))

    
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    main()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
