#!/usr/bin/env python

# -*- coding: utf-8 -*-

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import time, sys
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

    pg.setConfigOption( 'background', 'w')
    pg.setConfigOption( 'foreground', 'k')   
    app = pg.mkQApp()

    win = pg.GraphicsWindow( title="Overlay 2 plots")
    win.clear()

    win.addLabel( "First plot has log scale", row = 1, col = 1, colspan = 10)
    win.addLabel( "A comment", row = 2, col = 1, colspan = 10)

    plotItem = win.addPlot( row = 3, col = 1)
    plotItem.setLabels(left='axis 1')
    
    ## create a new ViewBox, link the right axis to its coordinate system
    viewBox = pg.ViewBox()
    
    plotItem.showAxis('top')
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

    plotDataItem = plotItem.plot()
    plotDataItem.setData( x, y)
    
    dataItem = pg.PlotDataItem( x, y2, pen = '#00ffff')
    dataItem.setLogMode( False, False)
    viewBox.addItem( dataItem)

    plotItem.setLogMode( x = False, y = True)

    viewBox.enableAutoRange( x = True, y = True)
    #viewBox.setXRange( -5, 5)
    #viewBox.setYRange( -10, 1)


    updateViews()
    plotItem.vb.sigResized.connect(updateViews)
    
    app.processEvents()
    time.sleep(0.1)
    app.processEvents()

    print "Prtc ",
    sys.stdin.readline()
    
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':

    main()

