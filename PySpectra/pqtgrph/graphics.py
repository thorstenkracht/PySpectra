#!/usr/bin/env python

#from pyqtgraph.Qt import QtCore as _QtCore
#from pyqtgraph.Qt import QtGui as _QtGui
from taurus.external.qt import QtGui as _QtGui
from taurus.external.qt import QtCore as _QtCore
from taurus.qt.qtgui.application import TaurusApplication 

import pyqtgraph as _pg
import time as _time
import os as _os
import math as _math
import numpy as _np
import PySpectra.dMgt.GQE as _GQE
import HasyUtils as _HasyUtils
import datetime as _datetime

_QApp = None
_win = None

def initGraphic():
    '''
    haso107d1: 1920 x 1200
    spectra: 640 x 450 def., A4:  680 x 471 
    '''
    global _QApp, _win

    if _QApp is not None: 
        return (_QApp, _win)

    _QApp = _QtGui.QApplication.instance()
    if _QApp is None:
        #_QApp = _QtGui.QApplication([])
        _QApp = TaurusApplication( [])

    #+++mw = _QtGui.QMainWindow()
    if _win is None:
        _pg.setConfigOption( 'background', 'w')
        _pg.setConfigOption( 'foreground', 'k')
        _win = _pg.GraphicsWindow( title="PySpectra Application")
        #_win.setGeometry( 30, 30, 680, int( 680./1.414))
        _win.setGeometry( 30, 30, 750, int( 750./1.414))

    return (_QApp, _win)

def close(): 
    global _win, _QApp
    if _win is None:
        return 
    cls()
    _win.close()
    _win = None
    _QApp = None
    return 

def _setSizeGraphicsWindow( nScan):

    if nScan > 10:
        factor = 0.625
    elif nScan > 4: 
        factor = 0.5
    else: 
        factor = 0.35 # 1920 -> 680

    geo = _win.geometry()
    #print "current geo", repr( geo), geo.width(), geo.height()

    geoScreen = _QtGui.QDesktopWidget().screenGeometry(-1)
    widthNew = int( geoScreen.width()*factor)
    heightNew = int( widthNew/1.414)
    if widthNew > geoScreen.width(): 
        widthNew = geoScreen.width() - 60
    if heightNew > geoScreen.height(): 
        heightNew = geoScreen.height() - 60
    if widthNew > geo.width() or heightNew > geo.height():
        #print "set-geo, new", widthNew, heightNew, "curr", geo.width(), geo.height()
        _win.setGeometry( 30, 30, widthNew, heightNew)

def setWsViewport( size = None):
    '''
    the workstation viewport is the graphics window
    '''
    if size is None:
        return 

    if size == "DINA4" or size == "DINA4L": 
        pass
    elif size == "DINA4P": 
        pass
    else:
        raise ValueError( "graphics.setWsViewport: no valid size, %s" % size)

    return 

def cls():
    '''
    clear screen: allow for a new plot
    '''
    #print "graphics.cls"
    if _QApp is None:
        return 
    if _win is None:
        return
    #
    # the clear() statement cuts down this list:_win.items() to 
    # one element, <class 'pyqtgraph.graphicsItems.GraphicsLayout.GraphicsLayout'>
    #
    _win.clear()
    #
    # remove all items from the layout
    #
    ##_win.items()[0].clear()
    #
    # Bug in pyqtgraph? have to set currentRow and currentCol
    # explicitly to 0.
    #
    ##_win.items()[0].currentRow = 0
    ##_win.items()[0].currentCol = 0

    #
    # clear the plotItems
    #
    scanList = _GQE.getScanList()
    for i in range( len( scanList)):
        if hasattr( scanList[i], "mouseLabel"):
            if scanList[i].mouseLabel is not None:
                del scanList[i].mouseLabel
                scanList[i].mouseLabel = None
        if hasattr( scanList[i], "mouseProxy"):
            if scanList[i].mouseProxy is not None:
                del scanList[i].mouseProxy
                scanList[i].mouseProxy = None

        scanList[i].plotItem = None
        scanList[i].plotDataItem = None
        scanList[i].lastIndex = 0

    _QApp.processEvents()

def listGraphicsItems(): 
    '''
    debugging tool
    '''
    return 
    for item in _win.items():
        print "item:", type( item)
        #if type( item) == _QtGui.QGraphicsTextItem:
        #    print "text", dir( item)

def _doty2datetime(doty, year = None):
    """
    Convert the fractional day-of-the-year to a datetime structure.
    The default year is the current year.

    Example: 
      a = doty2datetime( 28.12)
      m = [ 'Jan', 'Feb', 'Mar', 'Aptr', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      print "%s %d, %02d:%02d" % (m[ a.month - 1], a.day, a.hour, a.minute)
      --> Jan 29, 02:52
    """
    if year is None:
        now = _datetime.datetime.now()
        year = now.year
    dotySeconds = doty*24.*60.*60
    boy = _datetime.datetime(year, 1, 1)
    return boy + _datetime.timedelta(seconds=dotySeconds)

class _CAxisTime( _pg.AxisItem):
    ''' 
    Formats axis label to human readable time.
    '''
    def tickStrings(self, values, scale, spacing):
        strns = []
        m = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        now = _datetime.datetime.now()
        year = now.year
        for x in values:
            yearTemp = year
            if x < 0: 
                x += 365.
                yearTemp = year - 1
            try:
                a = _doty2datetime( x, yearTemp)
                #
                # with zooming the 
                #
                if a.month < 1: 
                    a.month = 1
                if a.month > 12: 
                    a.month = 12
                strns.append( "%s %d, %02d:%02d" % (m[ a.month - 1], a.day, a.hour, a.minute))
            except ValueError:  # Windows can't handle dates before 1970
                strns.append('')
        return strns

def _getPen( scan):
    col = { 'red': 'r', 
            'blue': 'b',
            'green': 'g',
            'cyan': 'c',
            'magenta': 'm',
            'yellow': 'y',
            'black': 'k',
            }
    style = { 'solidLine': _QtCore.Qt.SolidLine,
              'dashLine': _QtCore.Qt.DashLine,
              'dotLine': _QtCore.Qt.DotLine,
              'dashDotLine': _QtCore.Qt.DashDotLine,
              'dashDotDotLine': _QtCore.Qt.DashDotDotLine,
          }

    if scan.color in col: 
        clr = col[ scan.color]
    else:
        clr = 'k'

    if scan.style in style:
        stl = style[ scan.style]
    else:
        stl = _QtCore.Qt.DashLine

    return _pg.mkPen( color = clr, width = scan.width, style = stl)


def _make_cb_mouseMoved( scan):
    '''
    return a callback function for the moveMouse signal
    '''
    def mouseMoved(evt):
        mousePoint = scan.plotItem.vb.mapSceneToView(evt[0])
        #print "+++ scene", repr( evt[0]), "view", repr( mousePoint)
        scan.mouseLabel.setText( "x %g, y %g" % (mousePoint.x(), mousePoint.y()), color = 'k')
        scan.mouseLabel.setPos( mousePoint.x(), mousePoint.y())
        scan.mouseLabel.show()
    return mouseMoved

def _prepareMouse( scan):
    scan.mouseProxy = _pg.SignalProxy( scan.plotItem.scene().sigMouseMoved, 
                                  rateLimit=60, slot=_make_cb_mouseMoved( scan))
    scan.mouseLabel = _pg.TextItem( "cursor", color='b', anchor = (0, 1.0))
    scan.plotItem.addItem( scan.mouseLabel)
    scan.mouseLabel.hide()

def _isCellTaken( row, col):
    '''
    returns True, if there is already a plotItem in (row, col)
    '''
    argout = False
    for item in _win.items():
        if isinstance( item, _pg.graphicsItems.GraphicsLayout.GraphicsLayout):
            if item.getItem( row, col) is not None:
                for elm in item.items:
                    if type( elm) == _pg.graphicsItems.LabelItem.LabelItem:
                        print "graphics.isCellTaken (%d, %d) %s" % (row, col, elm.text)
                    else: 
                        #print "graphics.isCellTaken (%d, %d) %s " % (row, col, repr( elm))
                        pass
                argout = True
                break
            else:
                argout = False
                break
    return argout

def _createPlotItem( scan, row = 0, col = 0):            
    '''
    create a plotItem, aka viewport (?) with title, axis descriptions and texts
    '''
    #
    #print "graphics.createPlotItem", scan.name, row, col
    #
    #
    #
    if _isCellTaken( row, col):
        raise ValueError( "graphics.createPlotItem: cell (%d, %d) is already taken" % ( row, col))

    try:
        if scan.doty: 
            plotItem = _win.addPlot( axisItems = { 'bottom': _CAxisTime( orientation='bottom')}, 
                                     row = row, col = col, colspan = scan.colSpan) 
        else:
            plotItem = _win.addPlot( row = row, col = col, colspan = scan.colSpan) 
    except Exception, e:
        print "graphics.createPlotItem: caught exception, row", row, "col", col, "colspan", scan.colSpan
        print repr( e)
        raise ValueError( "graphics.createPlotItem, throwing exception")

    plotItem.showGrid( x = True, y = True)
    
    #
    # the length of the title has to be limited. Otherwise pg 
    # screws up. The plots will no longer fit into the workstation viewport
    # and the following display command, even with less scans, will 
    # also not fit into the graphics window
    #
    lenMax = 15
    if len( _GQE.getScanList()) > 15: 
        lenMax = 12

    if len( scan.name) > lenMax:
        tempName = "X_" + scan.name[-lenMax:]
    else: 
        tempName = scan.name

    plotItem.setTitle( title = tempName)

    if hasattr( scan, 'xLabel'):
        plotItem.setLabel( 'bottom', text=scan.xLabel)
    if hasattr( scan, 'yLabel'):
        plotItem.setLabel( 'left', text=scan.yLabel)

    arX = scan.autorangeX
    arY = scan.autorangeY

    if scan.yMin is None:
        arY = True
    else:
        if not scan.autorangeY: 
            arY = False

    #print "graphics.createPlotItem", scan.name, "autorange x, y", arX, arY
    
    plotItem.enableAutoRange( x = arX, y = arY)

    if not arY: 
        plotItem.setYRange( scan.yMin, scan.yMax)
    #
    # idea: control the zoom in such a way the y-axis 
    # is re-scaled when we zoom in.
    #
    plotItem.setMouseEnabled( x = True, y = True)

    if not arX: 
        plotItem.setXRange( scan.xMin, scan.xMax, padding=0)

    for elm in scan.textList:
        if elm.hAlign == 'left':
            anchorX = 0
        elif elm.hAlign == 'right':
            anchorX = 1
        elif elm.hAlign == 'center':
            anchorX = 0.5
        if elm.vAlign == 'top':
            anchorY = 0
        elif elm.vAlign == 'bottom':
            anchorY = 1
        elif elm.vAlign == 'center':
            anchorY = 0.5
        txt = _pg.TextItem( elm.text, color=elm.color, anchor = ( anchorX, anchorY))
        x = (scan.xMax - scan.xMin)*elm.x + scan.xMin
        y = ( _np.max( scan.y) - _np.min( scan.y))*elm.y + _np.min( scan.y)
        #txt.setParentItem( plotItem.getViewBox())
        #txt.setPos( 20, 20)
        plotItem.addItem( txt)
        txt.setPos( x, y)
        txt.show()

    return plotItem

def _textIsOnDisplay( textStr):
    '''
    searches the list of Items to see whether textStr exists already
    '''
    for item in _win.items():
        if type( item) is _pg.graphicsItems.LabelItem.LabelItem: 
            if textStr == item.text:
                return True

    return False

def display( nameList = None):
    '''
    display one or more or all scans

    Parameters
    ----------
    None: 
          display all scans
    Name: string
          a list of scans to be displayed

    Example
    -------
    PySpectra.display( [ 's1', 's2'])
      display scans s1 and s2
    PySpectra.display()
      display all scans

    Module: PySpectra.graphics.<graphLib>.graphics.py
    '''
    #
    # don't want to check for nameList is None below
    #
    if nameList is None:
        nameList = []

    #print "graphics.displaY, nameList", repr( nameList)

    if _QApp is None: 
        initGraphic()

    #
    # Do not put a cls() here because it takes a lot of time, especially when
    # fast displays are done. 
    # Try /home/kracht/Misc/pySpectra/test/dMgt/testGQE.py testFillData

    #
    # see if the members of nameList arr in the scanList
    #
    for nm in nameList:
        if _GQE.getScan( nm) is None:
            raise ValueError( "graphics.display: %s is not in the scanList" % nm)

    scanList = _GQE.getScanList()
    #
    # clear the mouse things in the scan
    #
    for i in range( len( scanList)):
        if scanList[i].mouseProxy is not None:
            scanList[i].mouseProxy = None
            scanList[i].mouseLabel = None

    #
    # find out whether only one scan will be displayed 
    # in this case the mouse-cursor will be activated
    #
    flagDisplaySingle = False
    if len( nameList) == 1 or len( scanList) == 1:
        flagDisplaySingle = True

    #
    # adjust the graphics window to the number of displayed scans
    #
    _setSizeGraphicsWindow( _GQE.getNumberOfScansToBeDisplayed( nameList))
    lenTemp = len( scanList) - _GQE.getNoOverlaid()
    ncol = _math.floor( _math.sqrt( lenTemp) + 0.5)
    col = 0
    row = 0
    title = _GQE.getTitle()
    if title is not None:
        if not _textIsOnDisplay( title):
            _win.addLabel( title, row = row, col = 0, rowspan = 1, 
                           colspan = int( ncol))
        row += 1
    
    comment = _GQE.getComment()
    if comment is not None:
        if not _textIsOnDisplay( comment):
            _win.addLabel( comment, row = row, col = 0, 
                           rowspan = 1, colspan = int( ncol))
        row += 1
    #
    # --- first pass: run through the scans in scanList and display 
    #     non-overlaid scans
    #
    for i in range( len( scanList)):

        #
        # 'scan' is a copy
        #
        scan = scanList[i]
        #print "graphics.display.firstPass,", scan.name, scan.lastIndex, scan.currentIndex
        #
        # overlay? - don't create a plot for this scan. Plot it
        # in the second pass. But it is displayed, if it is the only 
        # scan or if it is the only scan mentioned in nameList
        #
        if scan.overlay is not None and not flagDisplaySingle:
            continue

        if len( nameList) > 0: 
            if scan.name not in nameList:
                continue
        #
        # if we re-use the  plotItem ( aka viewport ?),
        # we can use setData(), see below. That makes things much faster.
        #
        if scan.plotItem is None:
            try:
                scan.plotItem = _createPlotItem( scan, row, col)
            except ValueError, e:
                print "graphics.display", repr( e)
                print "graphics.display: exception from createPlotItem"
                return 
            scan.plotDataItem = scan.plotItem.plot( name = scan.name, pen = _getPen( scan))

        #
        # check, if there is something to display
        # 
        if scan.lastIndex == scan.currentIndex:
            col += scan.colSpan
            if col >= ncol:
                col = 0
                row += 1
            continue

        #
        # modify the scan 
        #
        scanList[i].plotItem = scan.plotItem
        #print "graphics.display, plotting %s currentIndex %d len: %d" % (scan.name, scan.currentIndex, len( scan.x)) 
        scan.plotDataItem.setData( scan.x[:(scan.currentIndex + 1)], 
                                   scan.y[:(scan.currentIndex + 1)])
        #
        # keep track of what has already been displayed
        #
        scan.lastIndex = scan.currentIndex
        if flagDisplaySingle: 
            _prepareMouse( scan)

        col += scan.colSpan
        if col >= ncol:
            col = 0
            row += 1
    #
    # --- second pass: display overlaid scans
    #
    for i in range( len( scanList)):
        #
        # if only one scan is displayed, there is no overlay
        #
        if len( nameList) == 1:
            break
        #
        # 'scan' is a copy
        #
        scan = scanList[i]
        if scan.overlay is None:
            continue

        #
        # check, if theren is something to display
        #
        if scan.lastIndex == scan.currentIndex:
            continue
        
        if len( nameList) > 0 and scan.name not in nameList:
            continue
        target = _GQE.getScan( scan.overlay)
        scan.plotItem = target.plotItem
        #
        # modify the overlaid scan 
        #
        scanList[i].plot = scan.plotItem

        target.plotItem.setTitle( title ="%s and %s" % (target.name, scan.name))

        target.plotItem.plot( scan.x[:(scan.currentIndex + 1)], 
                              scan.y[:(scan.currentIndex + 1)], 
                              pen = _getPen( scan))
        scan.lastIndex = scan.currentIndex
        if scan.yMin is None:
            scan.plotItem.enableAutoRange( x = False, y = True)
        else:
            scan.plotItem.setYRange( scan.yMin, scan.yMax)
        scan.plotItem.setXRange( scan.xMin, scan.xMax)

    #_QApp.processEvents()
    #
    # except for the first display command in a session, 
    # all graphics plots, which have been displayed before
    # appear in the upper left corner of the graphics screen
    #
    #_time.sleep(0.1)
    #
    # /usr/lib/python2.7/dist-packages/pyqtgraph/graphicsItems/AxisItem.py L.818
    # crashed because len( textRects) == 0
    #
    _QApp.processEvents()
    return

def procEventsLoop():
    print "\nPress <return> to continue ",
    while True:
        _time.sleep(0.01)
        _QApp.processEvents()
        key = _HasyUtils.inkey()        
        if key == 10:
            break
    print ""

def processEvents(): 
    _QApp.processEvents()
