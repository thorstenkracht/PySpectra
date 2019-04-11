#!/usr/bin/env python

from PyQt4 import QtCore as _QtCore
from PyQt4 import QtGui as _QtGui

#from pyqtgraph.Qt import QtCore as _QtCore
#from pyqtgraph.Qt import QtGui as _QtGui
#from taurus.external.qt import QtGui as _QtGui
#from taurus.external.qt import QtCore as _QtCore
#from taurus.qt.qtgui.application import TaurusApplication 

import pyqtgraph as _pg
import time as _time
import os as _os
import math as _math
import numpy as _np
import PySpectra.dMgt.GQE as _GQE
import PySpectra.utils as _utils
import PySpectra.definitions as _defs
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
        _QApp = _QtGui.QApplication([])
        #_QApp = TaurusApplication( [])

    screen_resolution = _QApp.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    #+++mw = _QtGui.QMainWindow()
    if _win is None:
        _pg.setConfigOption( 'background', 'w')
        _pg.setConfigOption( 'foreground', 'k')
        #
        # <class 'pyqtgraph.graphicsWindows.GraphicsWindow'>
        #
        _win = _pg.GraphicsWindow( title="PySpectra Application")
        _win.setGeometry( 30, 30, 793, int( 793./1.414))

    return (_QApp, _win)

def _setSizeGraphicsWindow( nScan):

    if _GQE.getWsViewportFixed(): 
        return 

    if nScan > 10:
        #factor = 0.625
        factor = 0.7
    elif nScan > 4: 
        factor = 0.5
    else: 
        factor = 0.35 # 1920 -> 680

    geo = _win.geometry()

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
    size: DINA4, DINA4P, DINA3, DINA3P
    '''
    if size is None:
        return 

    if size.upper() == "DINA4" or size.upper() == "DINA4L": 
        w = 29.7
        h = 21
    elif size.upper() == "DINA4P": 
        w = 21
        h = 29.7
    elif size.upper() == "DINA5" or size.upper() == "DINA5L": 
        w = 21
        h = 14.85
    elif size.upper() == "DINA5P": 
        w = 14.85
        h = 21.0
    elif size.upper() == "DINA6" or size.upper() == "DINA6L": 
        w = 14.85
        h = 10.5
    elif size.upper() == "DINA6P": 
        w = 10.5
        h = 14.85
    else:
        raise ValueError( "graphics.setWsViewport: no valid size, %s" % size)

    #
    # 3778: pixel per meter (spectra)
    #
    wPixel = w*3778./100. 
    hPixel = h*3778./100.
    #print "graphics.setWsViewport", wPixel, hPixel
    _win.setGeometry( 30, 30, int(wPixel), int(hPixel))
    _QApp.processEvents()
    _GQE.setWsViewportFixed( True)

    return 

def cls():
    '''
    clear screen: allow for a new plot
    '''
    #print "pqt_graphics.cls"

    if _QApp is None: 
        initGraphic()
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

    if scan.color.lower() in _defs.colorCode: 
        clr = _defs.colorCode[ scan.color.lower()]
    else:
        clr = 'k'

    if scan.style in _defs.style:
        stl = _defs.style[ scan.style]
    else:
        stl = _QtCore.Qt.DashLine

    return _pg.mkPen( color = clr, width = scan.width, style = stl)


def _make_cb_mouseMoved( scan):
    '''
    return a callback function for the moveMouse signal
    '''
    def mouseMoved(evt):
        #print " mouseMoved, evt[0]", scan.name, repr( evt[0])
        m = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        mousePoint = scan.plotItem.vb.mapSceneToView(evt[0])
        #print " scene", repr( evt[0]), "view", repr( mousePoint)
        if scan.doty:
            now = _datetime.datetime.now()
            year = now.year
            x = mousePoint.x()
            if x < 0: 
                x += 365.
                year = year - 1
            a = _doty2datetime( x, year)
            #
            # with zooming ...
            #
            if a.month < 1: 
                a.month = 1
            if a.month > 12: 
                a.month = 12
            xStr = "%s %d, %02d:%02d" % (m[ a.month - 1], a.day, a.hour, a.minute)

            scan.mouseLabel.setText( "x %s, y %g" % (xStr, mousePoint.y()), color = 'k')
        else:
            scan.mouseLabel.setText( "x %g, y %g" % (mousePoint.x(), mousePoint.y()), color = 'k')
        scan.mouseLabel.setPos( mousePoint.x(), mousePoint.y())
        scan.mouseLabel.show()
    return mouseMoved

def _make_cb_mouseClicked( scan):
    '''
    return a callback function for the mouseClicked signal
    '''
    def mouseClicked(evt):
        mousePoint = scan.plotItem.vb.mapSceneToView(evt[0].scenePos())
        scan.move( mousePoint.x())
    return mouseClicked

def _prepareMouse( scan):
    scan.mouseProxy = _pg.SignalProxy( scan.plotItem.scene().sigMouseMoved, 
                                       rateLimit=60, slot=_make_cb_mouseMoved( scan))
    scan.mouseClick = _pg.SignalProxy( scan.plotItem.scene().sigMouseClicked, 
                                       rateLimit=60, slot=_make_cb_mouseClicked( scan))
    scan.mouseLabel = _pg.TextItem( "cursor", color='b', anchor = (0, 1.0))
    scan.plotItem.addItem( scan.mouseLabel)
    scan.mouseLabel.hide()
    return 


def _textIsOnDisplay( textStr):
    '''
    searches the list of Items to see whether textStr exists already
    '''
    for item in _win.items():
        if type( item) is _pg.graphicsItems.LabelItem.LabelItem: 
            if textStr == item.text:
                return True

    return False

def _adjustFigure( nDisplay): 
    '''
    used for matplotlib
    '''
    return 

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
                        #print "pqt_graphics.isCellTaken (%d, %d) %s" % (row, col, elm.text)
                        pass
                    else: 
                        #print "pqt_graphics.isCellTaken (%d, %d) %s " % (row, col, repr( elm))
                        pass
                argout = True
                break
            else:
                argout = False
                break
    return argout

def _displayTitleComment():
    '''
    display title and comment.
    - title is over comment
    - colspan is infinity
    '''
    title = _GQE.getTitle()
    if title is not None:
        if not _textIsOnDisplay( title):
            _win.addLabel( title, row = 0, col = 0, colspan = 10)

    comment = _GQE.getComment()
    if comment is not None:
        if not _textIsOnDisplay( comment):
            _win.addLabel( comment, row = 1, col = 0, colspan = 10)

def _addTexts( scan, nameList): 

    if _GQE.getNumberOfScansToBeDisplayed( nameList) <= _defs.MANY_SCANS:
        fontSize = _defs.FONT_SIZE_NORMAL
    else: 
        fontSize = _defs.FONT_SIZE_SMALL
    
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
        #txt = _pg.TextItem( elm.text, color=elm.color, anchor = ( anchorX, anchorY))
        if elm.color.lower() in _defs.colorCode:
            #txt = _pg.TextItem( elm.text, color=_defs.colorCode[ elm.color.lower()], anchor = ( anchorX, anchorY))
            txt = _pg.TextItem( color=_defs.colorCode[ elm.color.lower()], anchor = ( anchorX, anchorY))
            txt.setHtml( '<div style="font-size:%dpx;">%s</div>' % (fontSize, elm.text))
        else:
            #txt = _pg.TextItem( elm.text, color='k', anchor = ( anchorX, anchorY))
            txt = _pg.TextItem( color='k', anchor = ( anchorX, anchorY))
            txt.setHtml( '<div style="font-size:%dpx;">%s</div>' % ( fontSize, elm.text))

        if scan.textOnly:
            x = elm.x
            y = elm.y
        else:
            x = (scan.xMax - scan.xMin)*elm.x + scan.xMin
            y = ( _np.max( scan.y) - _np.min( scan.y))*elm.y + _np.min( scan.y)
            
        scan.plotItem.addItem( txt)
        txt.setPos( x, y)
        txt.show()

def _setTitle( scan, nameList): 
    if _GQE.getNumberOfScansToBeDisplayed( nameList) <= _defs.MANY_SCANS:
        fontSize = _defs.FONT_SIZE_NORMAL
    else: 
        fontSize = _defs.FONT_SIZE_SMALL
    #
    # the length of the title has to be limited. Otherwise pg 
    # screws up. The plots will no longer fit into the workstation viewport
    # and the following display command, even with less scans, will 
    # also not fit into the graphics window
    #
    lenMax = 15
    if len( _GQE._scanList) > 15: 
        lenMax = 12

    if len( scan.name) > lenMax:
        tempName = "X_" + scan.name[-lenMax:]
    else: 
        tempName = scan.name

    if _GQE.getNumberOfScansToBeDisplayed( nameList) <= _defs.MANY_SCANS:
        scan.plotItem.setTitle( title = tempName, size = '%dpx' % fontSize)
    else:
        vb = scan.plotItem.getViewBox()
        #txt = _pg.TextItem( tempName, color='k', anchor = ( 1.0, 0.5))
        txt = _pg.TextItem( color='k', anchor = ( 1.0, 0.5))
        txt.setHtml( '<div style="font-size:%dpx;">%s</div>' % (fontSize, tempName))
        x = (scan.xMax - scan.xMin)*0.95 + scan.xMin
        if scan.autorangeY: 
            y = ( _np.max( scan.y) - _np.min( scan.y))*0.85 + _np.min( scan.y)
        else: 
            if scan.yMax is None: 
                scan.yMax = _np.max( scan.y)
            if scan.yMin is None: 
                scan.yMin = _np.min( scan.y)
            y = ( scan.yMax - scan.yMin)*0.85 + scan.yMin
            
        txt.setPos( x, y)
        vb.addItem( txt)

def _extractData( scan): 
    '''
    the arrays scan.xExtract and scan.yExtract are produced.
    they contain those data which are between yMin and yMax.
    this way be bypass the pyqtgraph issue: limits are not respected
    for logarithmic plots.
    '''

    if scan.yLog is False:
        scan.xExtract = scan.x[:(scan.currentIndex + 1)]
        scan.yExtract = scan.y[:(scan.currentIndex + 1)]
        return 

    condition = _np.copy( scan.y[:(scan.currentIndex + 1)])

    if scan.yMin is None or scan.yMax is None:
        for i in range( scan.currentIndex + 1): 
            if scan.y[i] > 0.:
                condition[i] = True
            else:
                condition[i] = False
        scan.xExtract = _np.extract( condition, scan.x[:(scan.currentIndex + 1)])
        scan.yExtract = _np.extract( condition, scan.y[:(scan.currentIndex + 1)])
        return 


    for i in range( scan.currentIndex + 1): 
        if scan.y[i] >= scan.yMin and scan.y[i] <= scan.yMax and scan.y[i] > 0.:
            condition[i] = True
        else:
            condition[i] = False

    scan.xExtract = _np.extract( condition, scan.x[:(scan.currentIndex + 1)])
    scan.yExtract = _np.extract( condition, scan.y[:(scan.currentIndex + 1)])

    return 

def _createPlotItem( scan, nameList):            
    '''
    create a plotItem, aka viewport (?) with title, axis descriptions and texts
    '''
    #
    # (nrow, ncol, nplot) -> (row, col)
    #
    # (1, 1, 1) -> (0, 0)
    #
    # (2, 2, 1) -> (0, 0)
    # (2, 2, 2) -> (0, 1)
    # (2, 2, 3) -> (1, 0)
    # (2, 2, 4) -> (1, 1)
    #
    #print "graphics.createPlotItem", scan.name, repr( scan.at)
    #print "graphics.createPlotItem, nrow", scan.nrow, "ncol", scan.ncol, \
    #    "nplot", scan.nplot
    row = int( _math.floor(float( scan.nplot - 1)/float(scan.ncol)))
    col = int( scan.nplot - 1 - row*scan.ncol)
    #print "graphics.createPlotItem, row", row, "col", col
    #
    # take title and comment into account
    #
    row += 2
    
    if _isCellTaken( row, col):
        raise ValueError( "graphics.createPlotItem: cell (%d, %d) is already taken" % ( row, col))
    #
    # the textContainer
    #
    if scan.textOnly:
        plotItem = _win.addViewBox( row, col)
        plotItem.setRange( xRange = ( 0, 1), yRange = ( 0., 1.))
        scan.plotItem = plotItem
        _addTexts( scan, nameList)
        return plotItem

    try:
        if scan.doty: 
            plotItem = _win.addPlot( axisItems = { 'bottom': _CAxisTime( orientation='bottom')}, 
                                     row = row, col = col, colspan = scan.colSpan) 
        else:
            #
            # <class 'pyqtgraph.graphicsItems.PlotItem.PlotItem.PlotItem'>
            #
            plotItem = _win.addPlot( row = row, col = col, colspan = scan.colSpan)
            
    except Exception, e:
        print "graphics.createPlotItem: caught exception, row", row, "col", col, "colspan", scan.colSpan
        print repr( e)
        raise ValueError( "graphics.createPlotItem, throwing exception")


    plotItem.showAxis('top')
    plotItem.getAxis('top').setTicks( [])
    plotItem.showAxis('right')
    #plotItem.getAxis('right').setTicks( [])
    plotItem.getAxis( 'right').showValues = False
    
    scan.plotItem = plotItem 

    scan.plotItem.showGrid( x = scan.showGridX, y = scan.showGridY)
    
    _setTitle( scan, nameList)

    if _GQE.getNumberOfScansToBeDisplayed( nameList) <= _defs.MANY_SCANS:
        if hasattr( scan, 'xLabel'):
            scan.plotItem.setLabel( 'bottom', text=scan.xLabel)
        if hasattr( scan, 'yLabel'):
            scan.plotItem.setLabel( 'left', text=scan.yLabel)
    else: 
        font=_QtGui.QFont()
        font.setPixelSize( _defs.FONT_SIZE_SMALL)

        plotItem.getAxis("bottom").tickFont = font
        plotItem.getAxis("left").tickFont = font
    #
    # autoscale
    #
    arX = scan.autorangeX
    arY = scan.autorangeY

    if scan.yMin is None or scan.yMax is None:
        arY = True

    #
    # problem: autorange needs padding != 0
    #
    scan.plotItem.enableAutoRange( x = arX, y = arY)

    if not arY: 
        scan.plotItem.setYRange( scan.yMin, scan.yMax)

    if not arX: 
        scan.plotItem.setXRange( scan.xMin, scan.xMax)


    #
    # log scale
    #
    plotItem.setLogMode( x = scan.xLog, y = scan.yLog)

    #
    # idea: control the zoom in such a way the y-axis 
    # is re-scaled when we zoom in.
    #
    scan.plotItem.setMouseEnabled( x = True, y = True)

    _addTexts( scan, nameList)

    return scan.plotItem

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
    #print "pqt_graphics.display", repr( nameList)
    #
    # don't want to check for nameListis None below
    #
    if nameList is None:
        nameList = []

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
    nDisplay = _GQE.getNumberOfScansToBeDisplayed( nameList)
    _setSizeGraphicsWindow( nDisplay)
    _adjustFigure( nDisplay)

    #
    # set scan.nrow, scan.ncol, scan.nplot
    #
    _utils._setScanVPs( nameList, flagDisplaySingle)

    #
    # _displayTitleComment() uses (0,0) and (1, 0)
    # this has to follow setScanVPs because this function
    # might execute a cls()
    #
    _displayTitleComment()
    
    #_allocateViewBox()
    #
    # --- first pass: run through the scans in scanList and display 
    #     non-overlaid scans
    #
    for scan in scanList:
        print "graphics.display.firstPass,", scan.name

        #
        # overlay? - don't create a plot for this scan. Plot it
        # in the second pass. But it is displayed, if it is the only 
        # scan or if it is the only scan mentioned in nameList
        #
        if scan.overlay is not None and not flagDisplaySingle:
            #
            # maybe the scan.overlay has beed deleted
            #
            if _GQE.getScan( scan.overlay) is None:
                scan.overlay = None
            else:
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
                scan.plotItem = _createPlotItem( scan, nameList)
            except ValueError, e:
                print "graphics.display", repr( e)
                print "graphics.display: exception from createPlotItem"
                return 
            if not scan.textOnly:
                scan.plotDataItem = scan.plotItem.plot(pen = _getPen( scan))

        if scan.textOnly:
            continue
        #
        # check, if there is something to display
        # 
        if scan.lastIndex == scan.currentIndex:
            continue

        #print "graphics.display, plotting %s currentIndex %d len: %d" % (scan.name, scan.currentIndex, len( scan.x)) 
        #
        # pyqtgraph cannot respect limits for log-scales
        #
        if scan.yLog:
            _extractData( scan)
            scan.plotDataItem.setData( scan.xExtract, scan.yExtract)
        else:
            scan.plotDataItem.setData( scan.x[:(scan.currentIndex + 1)], 
                                       scan.y[:(scan.currentIndex + 1)])
        #
        # keep track of what has already been displayed
        #
        scan.lastIndex = scan.currentIndex
        if flagDisplaySingle: 
            _prepareMouse( scan)

    #
    # --- second pass: display overlaid scans
    #
    for scan in scanList:
        print "graphics.display.secondPass,", scan.name
        if scan.name == "hasfpgm1_pl":
            print "secondPass", scan.name, scan.x, scan.y
        #
        # if only one scan is displayed, there is no overlay
        #
        if len( nameList) == 1:
            break
        #
        # textContainers are not overlaid
        #
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
        if target is None:
            raise ValueError( "pqt_graphics.display: %s tries to overlay to %s" %
                              (scan.name, scan.overlay))

        scan.plotItem = target.plotItem

        if scan.yLog:
            print "+++pqt_graphics.display, yLog", scan.name
            _extractData( scan)
            scan.plotDataItem.setData( scan.xExtract, scan.yExtract)
            target.plotItem.plot( scan.xExtract,
                                  scan.yExtract,
                                  pen = _getPen( scan))
        else:
            target.plotItem.plot( scan.x[:(scan.currentIndex + 1)], 
                                  scan.y[:(scan.currentIndex + 1)], 
                                  pen = _getPen( scan))

        scan.lastIndex = scan.currentIndex

    processEvents()

    return
