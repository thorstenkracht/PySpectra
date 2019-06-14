#!/usr/bin/env python

from PyQt4 import QtCore as _QtCore
from PyQt4 import QtGui as _QtGui

import pyqtgraph as _pg
import time as _time
import os as _os
import math as _math
import numpy as _np
import PySpectra as _pysp

import datetime as _datetime
import types as _types
import psutil as _psutil

_QApp = None
_win = None

_clsFunctions = []

def _initGraphic():
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

    screen_resolution = _QApp.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    #mw = _QtGui.QMainWindow()
    if _win is None:
        _pg.setConfigOption( 'background', 'w')
        _pg.setConfigOption( 'foreground', 'k')
        #
        # <class 'pyqtgraph.graphicsWindows.GraphicsWindow'>
        #
        _win = _pg.GraphicsWindow( title="PySpectra Application")
        _win.name_TK = "graphicsWindow"
        _win.setGeometry( 30, 30, 793, int( 793./1.414))

    return (_QApp, _win)

def close(): 
    global _win
    if _win is None: 
        return

    _win.destroy()
    _win = None
    return 

def _setSizeGraphicsWindow( nScan):

    if _pysp.getWsViewportFixed(): 
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
    return 
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
    _pysp.setWsViewportFixed( True)

    return 

def cls():
    '''
    clear screen: allow for a new plot
    '''
    global _clsFunctions
    #print "pqt_graphics.cls"

    if _QApp is None: 
        _initGraphic()
    #
    # since _win.clear() does not clear all, we have to 
    # run through the prepared cls-functions
    #
    for f in _clsFunctions: 
        f()
    _clsFunctions = []

    #
    # the clear() statement cuts down this list:_win.items() to 
    # one element, <class 'pyqtgraph.graphicsItems.GraphicsLayout.GraphicsLayout'>
    #
    _win.clear()
    #_itemCrawler( _win, "after _win.clear()")

    #
    # clear the plotItems
    #
    scanList = _pysp.getScanList()
    for scan in scanList:
        if scan.mouseProxy is not None: 
            scan.mouseProxy.disconnect()
        if scan.mouseClick is not None: 
            scan.mouseClick.disconnect()
        scan.viewBox = None
        scan.plotItem = None
        scan.plotDataItem = None
        scan.lastIndex = 0

    _QApp.processEvents()
    return 
    # 
    #
    # clear the plotItems
    #
    scanList = _pysp.getScanList()
    for scan in scanList:
        if hasattr( scan, "mouseLabel"):
            if scan.mouseLabel is not None:
                del scan.mouseLabel
                scan.mouseLabel = None
        if hasattr( scan, "mouseProxy"):
            if scan.mouseProxy is not None:
                del scan.mouseProxy
                scan.mouseProxy = None
        try: 
            #
            # avoid this error: 'NoneType' object has no attribute 'removeItem'
            #
            if type( scan.plotItem) is _pg.graphicsItems.ViewBox.ViewBox and \
               scan.plotItem.scene() is None: 
                pass
            else:
                #
                # close() always throws an error
                #
                if scan.plotItem is not None: 
                    scan.plotItem.clear()
        except Exception, e: 
            print "pqt_graphic.cls: exception caught calling clear()"
            print repr( e)
            continue

        scan.viewBox = None
        scan.plotItem = None
        scan.plotDataItem = None
        scan.lastIndex = 0

    #_itemCrawler( _win, "after cls()")
    _QApp.processEvents()
    return 

_itemLevel = 0
def _itemCrawler( o, msg = None): 
    '''
    recursively crals though the items of an object
    '''
    global _itemLevel

    if msg is not None: 
        print ">>> ", msg
    _itemLevel += 1
    print " %s%d: --- type %s" % ('  ' * _itemLevel, _itemLevel, type( o))
    if type( o.items) is _types.BuiltinFunctionType:
        for item in o.items():
            if hasattr( item, "nameTK"):
                print " %s%d: Func, *** %s" % ( '  ' * _itemLevel, _itemLevel, item.nameTK)
            else:
                print " %s%d: Func, %s" % ( '  ' * _itemLevel, _itemLevel, repr( item))
            if hasattr( item, "items"):
                _itemCrawler( item)
    elif type( o.items) is _types.DictType: 
        for item in o.items.keys(): 
            if hasattr( o.items[ item], "nameTK"):
                print " %s%d: Dict, %s, *** %s" % ('  ' * _itemLevel, _itemLevel, repr( item), o.items[ item].nameTK)
            else:
                print " %s%d: Dict, %s, %s" % ('  ' * _itemLevel, _itemLevel, repr( item), repr( o.items[ item]))
            if hasattr( item, "items"):
                _itemCrawler( item)
    elif type( o.items) is _types.ListType: 
        for item in o.items: 
            if hasattr( item, "nameTK"):
                print " %s%d: List, *** %s" % ('  ' * _itemLevel, _itemLevel, item.nameTK)
            else:
                print " %s%d: List, %s" % ('  ' * _itemLevel, _itemLevel, repr( item))
            if hasattr( item, "items"):
                _itemCrawler( item)
    else: 
        print "failed to identify type", type( o.items)
    _itemLevel -= 1
    return 

def _getLayout( o): 
    for item in o.items(): 
        if type( item) == _pg.graphicsItems.GraphicsLayout.GraphicsLayout: 
            return item

def procEventsLoop():
    '''
    loops over QApp.processEvents until a <return> is entered
    '''
    print "\nPress <enter> to continue ",
    while True:
        _time.sleep(0.01)
        _QApp.processEvents()
        print "pqt_graphics.prrocLoop", _os.getenv( "DISPLAY")
        #
        # :99.0 is the DISPLAY in travis
        #
        if _os.getenv( "DISPLAY") == ":99.0": 
            break
        key = _pysp.utils.inkey()        
        if key == 10:
            break
    print ""

def processEvents(): 
    '''
    we call processEvents 2 times because after it is called
    the first time, all plots are displayed in the upper left
    corner. We don't want the mainLoop() to execute the 
    second call to processEvents
    '''
    _QApp.processEvents()
    _QApp.processEvents()

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

    if scan.lineColor.upper() == 'NONE': 
        return None

    if scan.lineColor.lower() in _pysp._colorCode: 
        clr = _pysp._colorCode[ scan.lineColor.lower()]
    else:
        clr = 'k'

    if scan.lineStyle in _pysp._lineStyle:
        stl = _pysp._lineStyle[ scan.lineStyle]
    else:
        stl = _QtCore.Qt.DashLine

    return _pg.mkPen( color = clr, width = scan.lineWidth, style = stl)

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
            if not scan.yLog:
                mY = mousePoint.y()
            else:
                mY = _math.pow( 10., mousePoint.y())
            if not scan.xLog:
                mX = mousePoint.x()
            else:
                mX = _math.pow( 10., mousePoint.x())

            scan.mouseLabel.setText( "x %g, y %g" % (mX, mY), color = 'k')
                
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
    scan.mouseLabel.nameTK = "mouseLabel"
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
    title = _pysp.getTitle()
    if title is not None:
        if not _textIsOnDisplay( title):
            _win.addLabel( title, row = 0, col = 0, colspan = 10)

    comment = _pysp.getComment()
    if comment is not None:
        if not _textIsOnDisplay( comment):
            _win.addLabel( comment, row = 1, col = 0, colspan = 10)

def _calcTextPosition( scan, xIn, yIn): 
    '''
    return the text position, taking into accout:
      - autorange
      - log scale
    '''
    
    if not scan.xLog:
            x = (scan.xMax - scan.xMin)*xIn + scan.xMin
    else:
        if scan.xMax <= 0. or scan.xMin <= 0.:
            raise ValueError( "pqt_graphics.calcTextPosition: xLog && (xMin <= 0: %g or xMax <= 0: %g" % 
                              (scan.xMin, scan.xMax))
        x = (_math.log10( scan.xMax) - _math.log10( scan.xMin))*xIn + _math.log10( scan.xMin)

    if scan.autorangeY: 
        yMax = _np.max( scan.y)
        yMin = _np.min( scan.y)
        if not scan.yLog:
            y = ( yMax - yMin)*yIn + yMin
        else:
            if yMax <= 0. or yMin <= 0.:
                raise ValueError( "pqt_graphics.calcTextPosition: yLog && (yMin <= 0: %g or yMax <= 0: %g" % 
                                  (yMin, yMax))
            y = ( _math.log10( yMax) - _math.log10( yMin))*yIn + _math.log10( yMin)
    else: 
        if scan.yMax is None: 
            scan.yMax = _np.max( scan.y)
        if scan.yMin is None: 
            scan.yMin = _np.min( scan.y)
        if not scan.yLog:
            y = ( scan.yMax - scan.yMin)*yIn + scan.yMin
        else:
            if scan.yMax <= 0. or scan.yMin <= 0.:
                raise ValueError( "pqt_graphics.calcTextPosition: yLog && (yMin <= 0: %g or yMax <= 0: %g" % 
                                  (scan.yMin, scan.yMax))
            y = ( _math.log10( scan.yMax) - _math.log10( scan.yMin))*yIn + _math.log10( scan.yMin)

    return( x, y)

def _addTexts( scan, nameList): 

    fontSize = _pysp.getFontSize( nameList)
    
    for elm in scan.textList:

        if elm.fontSize is None:
            sz = fontSize
        else:
            sz = elm.fontSize

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
        if elm.color.lower() in _pysp._colorCode:
            txt = _pg.TextItem( color=_pysp._colorCode[ elm.color.lower()], anchor = ( anchorX, anchorY))
            txt.setHtml( '<div style="font-size:%dpx;">%s</div>' % (sz, elm.text))
        else:
            txt = _pg.TextItem( color='k', anchor = ( anchorX, anchorY))
            txt.setHtml( '<div style="font-size:%dpx;">%s</div>' % ( sz, elm.text))

        if scan.textOnly:
            x = elm.x
            y = elm.y
        else:
            (x, y) = _calcTextPosition( scan, elm.x, elm.y)
            
        txt.nameTK = "text_%s" % txt
        scan.plotItem.addItem( txt)
        txt.setPos( x, y)
        txt.show()

def _setTitle( scan, nameList): 

    fontSize = _pysp.getFontSize( nameList)

    #
    # the length of the title has to be limited. Otherwise pg 
    # screws up. The plots will no longer fit into the workstation viewport
    # and the following display command, even with less scans, will 
    # also not fit into the graphics window
    #
    if len( scan.name) > _pysp._LEN_MAX_TITLE:
        tempName = "X_" + scan.name[-_pysp._LEN_MAX_TITLE:]
    else: 
        tempName = scan.name

    if _pysp.getNumberOfScansToBeDisplayed( nameList) < _pysp._MANY_SCANS:
        scan.plotItem.setTitle( title = tempName, size = '%dpx' % fontSize)
    else:
        vb = scan.plotItem.getViewBox()
        #
        # (0, 0) upper left corner, (1, 1) lower right corner
        #
        txt = _pg.TextItem( color='k', anchor = ( 1.0, 0.5))
        txt.setHtml( '<div style="font-size:%dpx;">%s</div>' % (fontSize, tempName))
        if not scan.xLog:
            x = (scan.xMax - scan.xMin)*1.0 + scan.xMin
        else:
            if scan.xMax <= 0. or scan.xMin <= 0.:
                raise ValueError( "pqt_graphics.setTitle: xLog && (xMin <= 0: %g or xMax <= 0: %g" %( scan.xMin, scan.xMax))
            x = (_math.log10( scan.xMax) - _math.log10( scan.xMin))*1.0 + _math.log10( scan.xMin)
        if scan.autorangeY: 
            y = ( _np.max( scan.y) - _np.min( scan.y))*0.85 + _np.min( scan.y)
        else: 
            if scan.yMax is None: 
                scan.yMax = _np.max( scan.y)
            if scan.yMin is None: 
                scan.yMin = _np.min( scan.y)
            if not scan.yLog:
                y = ( scan.yMax - scan.yMin)*0.85 + scan.yMin
            else:
                if scan.yMax <= 0. or scan.yMin <= 0.:
                    raise ValueError( "pqt_graphics.setTitle: yLog && (yMin <= 0: %g or yMax <= 0: %g" % (scan.yMin, scan.yMax))
                y = ( _math.log10( scan.yMax) - _math.log10( scan.yMin))*0.85 + \
                    _math.log10( scan.yMin)
        txt.setPos( x, y)
        txt.nameTK = "text_%s" % tempName
        vb.addItem( txt)

def _make_updateViews( target, scan): 
    def _func():
        scan.viewBox.setGeometry(target.plotItem.vb.sceneBoundingRect())
        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
        scan.viewBox.linkedViewChanged( target.plotItem.vb, scan.viewBox.XAxis)
        return 
    return _func

def _updateViews( target, scan): 
    scan.viewBox.setGeometry(target.plotItem.vb.sceneBoundingRect())
    
    ## need to re-update linked axes since this was called
    ## incorrectly while views had different shapes.
    ## (probably this should be handled in ViewBox.resizeEvent)
    scan.viewBox.linkedViewChanged( target.plotItem.vb, scan.viewBox.XAxis)
    return 

def _makeClsSceneFunc( scene, vb): 
    def func(): 
        scene.removeItem( vb)
        return 
    return func

def _setAutorangeForOverlaid( scan, target):
    if scan.autorangeY is False:
        if scan.yMin is None or scan.yMax is None: 
            if target.yMin is not None and target.yMax is not None: 
                scan.viewBox.setYRange( target.yMin, target.yMax)
                aY = False
            else:
                aY = True
                #raise ValueError( "pqt_graphics.display: not autorangeY and (yMin is None or yMax is None)")
        else:
            scan.viewBox.setYRange( scan.yMin, scan.yMax)
            aY = False
    else:
        aY = True

    if scan.autorangeX is False:
        if scan.xMin is None or scan.xMax is None: 
            if target.xMin is not None and target.xMax is not None: 
                scan.viewBox.setXRange( target.xMin, target.xMax)
                aX = False
            else:
                aX = True
                #raise ValueError( "pqt_graphics.display: not autorangeX and (xMin is None or xMax is None)")
        else:
            scan.viewBox.setXRange( scan.xMin, scan.xMax)
            aX = False
    else:
        aX = True
    scan.viewBox.enableAutoRange( x = aX, y = aY)
    return 

def _isNotOverlayTarget( scan): 
    '''
    returns True, if scan is the target for the overlay 
    of another scan
    '''
    scanList = _pysp.getScanList()
    for elm in scanList: 
        if elm.overlay is None: 
            continue
        if scan.name.lower() == elm.overlay.lower():
            return False
    return True
    
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
        #
        # pyqtgraph.graphicsItems.ViewBox.ViewBox.ViewBox
        #
        scan.plotItem = _win.addViewBox( row, col)
        scan.plotItem.nameTK = "viewBox_text_%s" % scan.name
        scan.plotItem.setRange( xRange = ( 0, 1), yRange = ( 0., 1.))
        _addTexts( scan, nameList)
        return 

    try:
        if scan.doty: 
            plotItem = _win.addPlot( axisItems = { 'bottom': _CAxisTime( orientation='bottom')}, 
                                     row = row, col = col, colspan = scan.colSpan) 
        else:
            #
            # <class 'pyqtgraph.graphicsItems.PlotItem.PlotItem.PlotItem'>
            #
            plotItem = _win.addPlot( row = row, col = col, colspan = scan.colSpan)
        plotItem.nameTK = "plot_%s" % scan.name

            
    except Exception, e:
        print "graphics.createPlotItem: caught exception, row", row, "col", col, "colspan", scan.colSpan
        print repr( e)
        raise ValueError( "graphics.createPlotItem, throwing exception")

    #
    # Set the default clip-to-view mode for all PlotDataItems managed by this plot. 
    # If clip is True, then PlotDataItems will attempt to draw only points within 
    # the visible range of the ViewBox.
    #
    plotItem.setClipToView( False)
    #
    # we want a closed axis box and we want tick marks 
    # at the top and right axis, but no tick mark texts
    #
    plotItem.showAxis('top')
    plotItem.getAxis('top').style[ 'showValues'] = False #  not working on Debian-8, 0.9.8-3 
    #
    # plot the right axis here, if the scan is not the target
    # of another scan which is overlaid.
    #
    if _isNotOverlayTarget( scan):
        plotItem.showAxis('right')
        plotItem.getAxis('right').style[ 'showValues'] = False #  not working on Debian-8, 0.9.8-3 
    #
    # 0.9.8-3 
    #
    if _pg.__version__ is None: 
        plotItem.getAxis('top').setTicks( [])
        if _isNotOverlayTarget( scan):
            plotItem.getAxis('right').setTicks( [])
            
    scan.plotItem = plotItem 

    scan.plotItem.showGrid( x = scan.showGridX, y = scan.showGridY)
    

    if _pysp.getNumberOfScansToBeDisplayed( nameList) <= _pysp._MANY_SCANS:
        if hasattr( scan, 'xLabel') and scan.xLabel is not None:
            scan.plotItem.setLabel( 'bottom', text=scan.xLabel)
        if hasattr( scan, 'yLabel')  and scan.yLabel is not None:
            scan.plotItem.setLabel( 'left', text=scan.yLabel)

    font=_QtGui.QFont()
    font.setPixelSize( _pysp.getTickFontSize( nameList))

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

    #
    # log scale
    # this statement has to precede the setYRange()
    #
    plotItem.setLogMode( x = scan.xLog, y = scan.yLog)

    if not arY: 
        if scan.yLog:
            #
            # if yLog, the limits have to be supplied as logs
            #
            if scan.yMax <= 0. or scan.yMin <= 0.:
                raise ValueError( "pqt_graphics.createPlotItem: yLog && (yMin <= 0: %g or yMax <= 0: %g" % (scan.yMin, scan.yMax))
            scan.plotItem.setYRange( _math.log10( scan.yMin), _math.log10(scan.yMax))
        else:
            scan.plotItem.setYRange( scan.yMin, scan.yMax)

    if not arX: 
        if scan.xLog:
            if scan.xMax <= 0. or scan.xMin <= 0.:
                raise ValueError( "pqt_graphics.createPlotItem: xLog && (xMin <= 0: %g or xMax <= 0: %g" % (scan.xMin, scan.xMax))
            scan.plotItem.setXRange( _math.log10( scan.xMin), _math.log10(scan.xMax))
        else:
            scan.plotItem.setXRange( scan.xMin, scan.xMax)

    #
    # idea: control the zoom in such a way the y-axis 
    # is re-scaled when we zoom in.
    #
    scan.plotItem.setMouseEnabled( x = True, y = True)

    _setTitle( scan, nameList)

    _addTexts( scan, nameList)

    return
    
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
    global _clsFunctions

    startTime = _time.time()

    if nameList is None:
        nameList = []

    if _QApp is None: 
        _initGraphic()
    #
    # Do not put a cls() here because it takes a lot of time, especially when
    # fast displays are done. 
    # Try /home/kracht/Misc/pySpectra/test/dMgt/testGQE.py testFillData

    #
    # see if the members of nameList arr in the scanList
    #
    for nm in nameList:
        if _pysp.getScan( nm) is None:
            raise ValueError( "graphics.display: %s is not in the scanList" % nm)

    scanList = _pysp.getScanList()
    #
    # clear the mouse things in the scan
    #
    for scan in scanList:
        if scan.mouseProxy is not None:
            scan.mouseProxy = None
            scan.mouseLabel = None

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
    nDisplay = _pysp.getNumberOfScansToBeDisplayed( nameList)
    _setSizeGraphicsWindow( nDisplay)
    _adjustFigure( nDisplay)

    #
    # set scan.nrow, scan.ncol, scan.nplot
    #
    _pysp.setScanVPs( nameList, flagDisplaySingle)

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
        #print "graphics.display.firstPass,", scan.name

        #
        # overlay? - don't create a plot for this scan. Plot it
        # in the second pass. But it is displayed, if it is the only 
        # scan or if it is the only scan mentioned in nameList
        #
        if scan.overlay is not None and not flagDisplaySingle:
            #
            # maybe the scan.overlay has beed deleted
            #
            if _pysp.getScan( scan.overlay) is None:
                scan.overlay = None
            else:
                continue

        if len( nameList) > 0: 
            if scan.name not in nameList:
                continue

        #if scan.xLog:
        #    raise ValueError( "pqt_graphic.display: no log-scale for the x-axis")
        #
        # if we re-use the  plotItem ( aka viewport ?),
        # we can use setData(), see below. That makes things much faster.
        #
        if scan.plotItem is None:
            try:
                _createPlotItem( scan, nameList)
            except ValueError, e:
                print "graphics.display", repr( e)
                print "graphics.display: exception from createPlotItem"
                return 
            if not scan.textOnly:
                if scan.symbolColor.upper() == 'NONE':
                    scan.plotDataItem = scan.plotItem.plot(pen = _getPen( scan))
                else:
                    scan.plotDataItem = scan.plotItem.plot(pen = _getPen( scan), 
                                                           symbol = scan.symbol, 
                                                           symbolPen = _pysp._colorCode[ scan.symbolColor.lower()], 
                                                           symbolBrush = _pysp._colorCode[ scan.symbolColor.lower()], 
                                                           symbolSize = scan.symbolSize)

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
        #print "graphics.display.secondPass,", scan.name
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
        target = _pysp.getScan( scan.overlay)
        if target is None or target.plotItem is None:
            raise ValueError( "pqt_graphics.display: %s tries to overlay to %s" %
                              (scan.name, scan.overlay))

        scan.plotItem = target.plotItem

        scan.viewBox = _pg.ViewBox()
        _setAutorangeForOverlaid( scan, target)
        #
        # for the overlaid scan show the right axis ...
        #
        target.plotItem.showAxis('right') 
        #
        # ... but if there are too many to be displayed, remove the tick mark labels
        #
        if nDisplay > 10: 
            target.plotItem.getAxis('right').style[ 'showValues'] = False #  not working on Debian-8, 0.9.8-3 
        #
        # the overlaid scan cannot have a log-scale. however, if
        # we don't set the log mode to false, the overlaid scan 
        # receive the log mode from the target scan
        #
        target.plotItem.getAxis('right').setLogMode( False)
        target.scene = target.plotItem.scene()
        scan.viewBox.nameTK = "viewBox_%s" % target.name
        target.scene.addItem( scan.viewBox)

        if scan.yLog or scan.xLog:
            raise ValueError( "pqt_graphic.display: no log-scale for the overlaid scan")

        target.plotItem.getAxis('right').linkToView( scan.viewBox)
        #
        # _win.clear() doesn't really work. Therefore we have to 
        # prepare a function to be called by cls()
        #
        _clsFunctions.append( _makeClsSceneFunc( target.scene, scan.viewBox))
        _updateViews( target, scan)
        #
        # link the views x-axis to another view
        #
        scan.viewBox.setXLink( target.plotItem)

        target.plotItem.vb.sigResized.connect( _make_updateViews( target, scan))
        if scan.symbolColor.upper()  == 'NONE':
            curveItem = _pg.PlotCurveItem( x = scan.x, y = scan.y, pen = _getPen( scan))
        else:
            curveItem = _pg.ScatterPlotItem( x = scan.x, y = scan.y,
                                             symbol = scan.symbol, 
                                             pen = _pysp._colorCode[ scan.symbolColor.lower()], 
                                             brush = _pysp._colorCode[ scan.symbolColor.lower()], 
                                             size = scan.symbolSize)

        curveItem.nameTK = "curve_%s" % target.name
        scan.viewBox.addItem( curveItem )
        
        scan.lastIndex = scan.currentIndex
    #
    # <class 'PyQt4.QtGui.QGraphicsGridLayout'>
    # left, top, right, bottom [pixels]
    #_win.ci.layout.setContentsMargins( 20, 0, 0, 0)
    #
    #if nDisplay >= 30:
    #    #_win.ci.layout.setContentsMargins( 20, 20, 1, 1)
    #    _win.ci.layout.setHorizontalSpacing( -30)
    #    _win.ci.layout.setVerticalSpacing( -12)
    #    pass
    #elif nDisplay >= 20:
    #    #_win.ci.layout.setContentsMargins( 20, 20, 1, 1)
    #    _win.ci.layout.setHorizontalSpacing( -40)
    #    _win.ci.layout.setVerticalSpacing( -15)
    #    pass

    _win.ci.layout.setContentsMargins( _pysp.marginLeft, _pysp.marginTop, _pysp.marginRight, _pysp.marginBottom)
    _win.ci.layout.setHorizontalSpacing( _pysp.spacingHorizontal)
    _win.ci.layout.setVerticalSpacing( _pysp.spacingVertical)
    #
    # debug scanning.py
    #
    #processEvents()
    #print "+++pqt_graph: after process events "
    #_pysp.prtc()
    processEvents()
    #print "+++pqt_graph: after process events, again "
    #_pysp.prtc()

    #print "pqt_graphics.display: time  %g" % ( _time.time() - startTime)
    #print "pqt_graphics.display: memory consumption percent %g" % p.memory_percent()
    #_itemCrawler( _win, "after display()")

    return
