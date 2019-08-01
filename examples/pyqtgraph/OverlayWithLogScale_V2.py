#!/usr/bin/env python
#
# the data are in log mode but the right axis description 
# starts at -3 instead of e.g. 0.001 
#
#
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import time, sys
plotItem = None
viewBox = None

def updateViews():
    global plotItem, viewBox
    viewBox.setGeometry(plotItem.vb.sceneBoundingRect())
    viewBox.linkedViewChanged(plotItem.vb, viewBox.XAxis)

def main(): 
    global plotItem, viewBox
    pg.setConfigOption( 'background', 'w')
    pg.setConfigOption( 'foreground', 'k')
    app = pg.mkQApp()

    # data
    x = np.linspace( -5, 5, 101)
    (a, mu, sigma) = ( 1, -1., 1.)
    y1 = a/(sigma*np.sqrt(2.*np.pi))*np.exp( -(x-mu)**2/(2*sigma**2))
    (a, mu, sigma) = ( 150, 0.5, 0.7)
    y2 = a/(sigma*np.sqrt(2.*np.pi))*np.exp( -(x-mu)**2/(2*sigma**2))

    win = pg.GraphicsWindow( title = "2 Plots")
    win.clear()

    plotItem = win.addPlot()
    print type( plotItem)
    #plotItem.setLogMode( x = False, y = True)
    #plotItem.setYRange( -2, 1)

    plotItem.getAxis('left').setLabel('axis1', color='#ff0000')
    plotItem.getAxis('right').setLabel('axis2', color='#0000ff')
    plotItem.getAxis('top').setLabel('The overlaid plot has a log scale', color='#0000ff')
    plotItem.getAxis('bottom').setLabel('position', color='#0000ff')
    
    # create a new ViewBox, link the right axis to its coordinate system
    viewBox = pg.ViewBox()
    plotItem.showAxis('right')
    plotItem.showAxis('top')
    plotItem.scene().addItem(viewBox)
    plotItem.getAxis('right').linkToView(viewBox)
    #
    # link the viewbox x-axis to plotItem
    #
    viewBox.setXLink(plotItem)

    plotItem.addItem( pg.PlotDataItem( x, y1, pen = 'r'))
    #
    # PlotCurveItem() has no setLogMode()
    #
    #dataItem = pg.PlotCurveItem( x = x, y = y2, pen = 'b')
    dataItem = pg.PlotDataItem( x, y2, pen = 'b')
    #plotItem.setLogMode( x = False, y = True)
    dataItem.setLogMode( False, True)
    viewBox.addItem( dataItem)
    viewBox.setYRange( -3, 2)

    plotItem.vb.sigResized.connect(updateViews)

    app.processEvents()
    time.sleep(0.1)
    app.processEvents()

    print "Prtc ",
    sys.stdin.readline()
    
if __name__ == '__main__':
    main()


