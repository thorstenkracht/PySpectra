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
plotItem = None
viewBox = None
pw = None

## Handle view resizing 
def updateViews():
    ## view has resized; update auxiliary views to match
    global plotItem, viewBox
    viewBox.setGeometry(plotItem.vb.sceneBoundingRect())
    
    ## need to re-update linked axes since this was called
    ## incorrectly while views had different shapes.
    ## (probably this should be handled in ViewBox.resizeEvent)
    viewBox.linkedViewChanged(plotItem.vb, viewBox.XAxis)


def main(): 
    global plotItem, viewBox, pw

    (xMin, xMax, xDelta) = (-5, 5, 0.1)
    x = np.arange( xMin, xMax, xDelta)
    mu = 0.
    sigma = 1.
    y = 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (x - mu)**2 / (2 * sigma**2))

    mu = 1.0
    sigma = 0.7
    y2 = 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (x - mu)**2 / (2 * sigma**2))
    
    pg.mkQApp()

    pw = pg.PlotWidget()
    pw.show()
    pw.setWindowTitle('pyqtgraph example: MultiplePlotAxes')

    plotItem = pw.plotItem
    plotItem.setLabels(left='axis 1')
    
    ## create a new ViewBox, link the right axis to its coordinate system
    viewBox = pg.ViewBox()
    
    plotItem.showAxis('right')
    plotItem.scene().addItem(viewBox)
    #
    # Link this axis to a ViewBox, causing its displayed range to 
    # match the visible range of the view.
    #
    plotItem.getAxis('right').linkToView(viewBox)
    #
    # link the views x-axis to another view
    #
    viewBox.setXLink(plotItem)
    plotItem.getAxis('right').setLabel('axis2', color='#00ffff')

    updateViews()
    plotItem.vb.sigResized.connect(updateViews)

    plotDataItem = plotItem.plot()
    plotDataItem.setData( x, y)
    
    dataItem = pg.PlotDataItem( x, y2, pen = '#00ffff')
    dataItem.setLogMode( False, True)
    viewBox.addItem( dataItem)

    plotItem.setLogMode( x = False, y = True)
    
    viewBox.setXRange( -5, 5)
    viewBox.setYRange( -10, 1)

    
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    main()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
