#!/usr/bin/env python

from PyQt4 import QtCore, QtGui

import pyqtgraph as _pg
import matplotlib as _mpl
import time as _time
import os as _os
import math as _math
import numpy as _np
from matplotlib import cm
import datetime as _datetime
import types as _types
import psutil as _psutil
import PySpectra.dMgt.GQE as _gqe
import PySpectra.misc.utils as _utils
import PySpectra.misc.tangoIfc as _tangoIfc
import PySpectra.definitions as _definitions

_QApp = None
_graphicsWindow = None
_myScene = None
_clsFunctions = []

def _initGraphic():
    '''
    haso107d1: 1920 x 1200
    spectra: 640 x 450 def., A4:  680 x 471 
    '''
    global _QApp, _graphicsWindow

    if _QApp is not None and _graphicsWindow is not None: 
        return (_QApp, _graphicsWindow)

    _QApp = QtGui.QApplication.instance()
    if _QApp is None:
        _QApp = QtGui.QApplication([])

    screen_resolution = _QApp.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    if _graphicsWindow is None:
        _pg.setConfigOption( 'background', 'w')
        _pg.setConfigOption( 'foreground', 'k')
        _graphicsWindow = _pg.GraphicsWindow( title="PySpectra Application (PQT)")
        _graphicsWindow.setGeometry( 30, 30, 793, int( 793./1.414))
    return (_QApp, _graphicsWindow)

def getGraphicsWindowHeight(): 
    return _graphicsWindow.geometry().height()

def clear( scan): 
    '''
    the clear() is executed here to ensure that _graphicsWindow is still alive
    '''
    if _graphicsWindow is None: 
        return 
    #
    # clear.__doc__: 'Remove all items from the ViewBox'
    #
    scan.plotItem.clear()
    return 

def close(): 
    global _graphicsWindow
    global _clsFunctions
    global _myScene

    if _graphicsWindow is None: 
        return

    _graphicsWindow.destroy()
    _graphicsWindow = None

    _myScene = None

    _clsFunctions = []

    return 

def _setSizeGraphicsWindow( nGqe):

    if _gqe.getWsViewportFixed(): 
        return 

    if nGqe > 10:
        #factor = 0.625
        factor = 0.7
    elif nGqe > 4: 
        factor = 0.5
    else: 
        factor = 0.35 # 1920 -> 680

    geo = _graphicsWindow.geometry()

    geoScreen = QtGui.QDesktopWidget().screenGeometry(-1)
    widthNew = int( geoScreen.width()*factor)
    heightNew = int( widthNew/1.414)
    if widthNew > geoScreen.width(): 
        widthNew = geoScreen.width() - 60
    if heightNew > geoScreen.height(): 
        heightNew = geoScreen.height() - 60
    if widthNew > geo.width() or heightNew > geo.height():
        #print "set-geo, new", widthNew, heightNew, "curr", geo.width(), geo.height()
        _graphicsWindow.setGeometry( 30, 30, widthNew, heightNew)
    return 

def setWsViewport( size = None):
    '''
    size: DINA4, DINA4P, DINA4S, DINA5, DINA5P, DINA5S, DINA6, DINA6L, DINA6S
    '''
    if size is None:
        return 

    if _QApp is None: 
        _initGraphic()

    if size.upper() == "DINA4" or size.upper() == "DINA4L": 
        w = 29.7
        h = 21
    elif size.upper() == "DINA4P": 
        w = 21
        h = 29.7
    elif size.upper() == "DINA4S": 
        w = 29.7
        h = 29.7
    elif size.upper() == "DINA5" or size.upper() == "DINA5L": 
        w = 21
        h = 14.85
    elif size.upper() == "DINA5P": 
        w = 14.85
        h = 21.0
    elif size.upper() == "DINA5S": 
        w = 21.0
        h = 21.0
    elif size.upper() == "DINA6" or size.upper() == "DINA6L": 
        w = 14.85
        h = 10.5
    elif size.upper() == "DINA6P": 
        w = 10.5
        h = 14.85
    elif size.upper() == "DINA6S": 
        w = 14.85
        h = 14.85
    else:
        raise ValueError( "graphics.setWsViewport: no valid size, %s" % size)

    #
    # 3778: pixel per meter (spectra)
    # DINA5S: 793.38, 793.38
    # DINA6S: 561, 561
    #
    wPixel = w*3778./100. 
    hPixel = h*3778./100.
    #print( "graphics.setWsViewport", wPixel, hPixel)
    _graphicsWindow.setGeometry( 30, 30, int(wPixel), int(hPixel))
    _QApp.processEvents()
    _gqe.setWsViewportFixed( True)

    return 

def cls():
    '''
    clear screen: allow for a new plot
    '''
    global _clsFunctions
    global _myScene

    if _QApp is None or _graphicsWindow is None: 
        _initGraphic()

    #
    # since _graphicsWindow.clear() does not clear all, we have to 
    # run through the prepared cls-functions
    # the problem was visible when one runs through the 
    # pyspViewer examples
    #
    for f in _clsFunctions: 
        try: 
            f()
        except Exception as e: 
            print( "pqtgraphics.cls, clsFunctions, error %s" % repr( e))
    _clsFunctions = []
    #
    # gqe.mousePrepared: needed because we can have several display() 
    # calls without cls()
    #
    gqeList = _gqe.getGqeList()
    for gqe in gqeList:
        gqe.mousePrepared = False

    if _myScene is not None: 
        _myScene.sigMouseClicked.disconnect()
        _myScene.sigMouseMoved.disconnect()
        _myScene = None
    #
    # the clear() statement cuts down this list:_graphicsWindow.items() to 
    # one element, <class 'pyqtgraph.graphicsItems.GraphicsLayout.GraphicsLayout'>
    #
    _graphicsWindow.clear()

    #_itemCrawler( _graphicsWindow, "after _graphicsWindow.clear()")

    #
    # clear the plotItems
    #
    gqeList = _gqe.getGqeList()
    for gqe in gqeList:
        #
        # this is necessary because createPDF() might hasv been called before
        #
        if gqe.plotItem is None: 
            continue
        if type( gqe) == _gqe.Scan:
            if gqe.labelArrowMotorCurrent is not None: 
                _graphicsWindow.scene().removeItem( gqe.labelArrowMotorCurrent)
                gqe.labelArrowMotorCurrent = None
            if gqe.arrowMotorCurrent is not None: 
                _graphicsWindow.scene().removeItem( gqe.arrowMotorCurrent)
                gqe.arrowMotorCurrent = None
            if gqe.arrowMotorSetPoint is not None: 
                _graphicsWindow.scene().removeItem( gqe.arrowMotorSetPoint)
                gqe.arrowMotorCurrent = None
            if gqe.infLineLeft is not None: 
                gqe.plotItem.removeItem( gqe.infLineLeft)
                gqe.infLineLeft = None
            if gqe.infLineRight is not None: 
                gqe.plotItem.removeItem( gqe.infLineRight)
                gqe.infLineRight = None
            if gqe.infLineMouseX is not None: 
                gqe.plotItem.removeItem( gqe.infLineMouseX)
                gqe.infLineMouseX = None
            if gqe.infLineMouseY is not None: 
                gqe.plotItem.removeItem( gqe.infLineMouseY)
                gqe.infLineMouseY = None
            if gqe.plotDataItem is not None: 
                try: 
                    gqe.plotItem.removeItem( gqe.plotDataItem)
                except Exception as e: 
                    print( "pqtgraph.cls: trouble removing gqe.plotDataItem, %s " % repr( type( gqe.plotDataItem)))
                    print( "pqtgraph.cls: type plotItem %s " % repr( type( gqe.plotItem)))
                    print( repr( e))
                gqe.plotDataItem = None

            gqe.lastIndex = 0
        gqe.viewBox = None
        gqe.plotItem = None

        if type( gqe) == _gqe.Image:
            gqe.img = None

    #
    # _QApp.processEvents() must not follow a _graphicsWindow.clear(). 
    # Otherwise all plots are displayed in the upper left corner
    # before they are moves to the correct final positions
    #
    #_QApp.processEvents()
    return 

def _getLayout( o): 
    for item in o.items(): 
        if type( item) == _pg.graphicsItems.GraphicsLayout.GraphicsLayout: 
            return item

def procEventsLoop( timeOut = None):
    '''
    loops over QApp.processEvents until a <return> is entered
    '''
    if timeOut is None:
        print "\nPress <enter> to continue ",
    startTime = _time.time()
    while True:
        _time.sleep(0.01)
        _QApp.processEvents()
        if timeOut is not None:
            if (_time.time() - startTime) > timeOut: 
                break
        #
        # :99.0 is the DISPLAY in travis
        #
        if _os.getenv( "DISPLAY") == ":99.0": 
            break
        key = _utils.inkey()        
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
    _QApp.processEvents()


def _addInfLineMouse( gqe): 
    '''
    create the mouse cross-hair 
    '''

    if gqe.infLineMouseX is not None: 
        return 

    if not gqe.xLog: 
        gqe.infLineMouseX = _pg.InfiniteLine( movable=True, angle=90, label='x={value:g}', 
                                              pen = _pg.mkPen( color = (0, 0, 0)), 
                                              labelOpts={'position': 0.1, 
                                                         'color': (0,0,000), 
                                                         'movable': True})
    else: 
        gqe.infLineMouseX = _pg.InfiniteLine( movable=True, angle=90, 
                                              pen = _pg.mkPen( color = (0, 0, 0)))

    if not gqe.yLog:
        gqe.infLineMouseY = _pg.InfiniteLine( movable=True, angle=0, label='y={value:g}', 
                                              pen = _pg.mkPen( color = (0, 0, 0)), 
                                              labelOpts={'position':0.1, 'color': (0,0,0), 'movable': True})
    else: 
        gqe.infLineMouseY = _pg.InfiniteLine( angle=0, 
                                              pen = _pg.mkPen( color = (0, 0, 0)))

    gqe.plotItem.addItem( gqe.infLineMouseX)
    gqe.plotItem.addItem( gqe.infLineMouseY)
    gqe.infLineMouseX.hide()
    gqe.infLineMouseY.hide()

    mIndex = int( gqe.currentIndex*0.5)
    if not gqe.xLog: 
        gqe.infLineMouseX.setPos( gqe.x[mIndex])
    else: 
        gqe.infLineMouseX.setPos( _math.log10( gqe.x[mIndex]))
    if not gqe.yLog: 
        gqe.infLineMouseY.setPos( gqe.y[mIndex])
    else: 
        gqe.infLineMouseY.setPos( _math.log10( gqe.y[mIndex]))

    return 

def _addArrowsMotor( gqe, nameList): 
    '''
    the arrows pointing to the current position and the setpoint
    '''

    if gqe.arrowMotorCurrent is not None: 
        return 
    #
    # if called from a pure graphics application the position arrow in not created
    #
    if gqe.motorNameList is None:
        return 

    #
    # there are no motor position arrows for MCA GQEs
    #
    if gqe.flagMCA: 
        return 

    gqe.arrowMotorCurrent = _pg.ArrowItem( angle=270, pen = _pg.mkPen( color = (0, 0, 255)))
    gqe.arrowMotorSetPoint = _pg.ArrowItem( angle=270, pen = _pg.mkPen( color = (255, 0, 0)),
                                            brush = _pg.mkBrush( color = (255, 0, 0)))
    #
    # anchor, (0, 0) -> upper left
    #
    gqe.labelArrowMotorCurrent = _pg.TextItem( color='k', anchor = ( 0.5, 2.))
    fontSize = _gqe.getFontSize( nameList)
    gqe.labelArrowMotorCurrent.setHtml( '<div style="font-size:%dpx;">%s</div>' % (fontSize, "n.n."))
    #
    # the arrows are added to the GraphicsWindow to use pixel coordinates (?)
    #
    _graphicsWindow.scene().addItem( gqe.arrowMotorSetPoint)
    _graphicsWindow.scene().addItem( gqe.arrowMotorCurrent)
    _graphicsWindow.scene().addItem( gqe.labelArrowMotorCurrent)

    #gqe.plotItem.addItem( gqe.arrowMotorSetPoint)
    # gqe.plotItem.addItem( gqe.arrowMotorCurrent)
    #gqe.plotItem.addItem( gqe.labelArrowMotorCurrent)

    gqe.arrowMotorCurrent.hide()
    gqe.arrowMotorSetPoint.hide()
    gqe.labelArrowMotorCurrent.hide()
    return 

def _addVLines( gqe): 
    '''
    the vertical lines
    '''
    if gqe.infLineLeft is not None:
        return 

    gqe.infLineLeft = _pg.InfiniteLine(movable=True, angle=90, label='x={value:g}', 
                                    labelOpts={'position':0.1, 'color': (0,0,0), 'movable': True})
    gqe.infLineRight = _pg.InfiniteLine(movable=True, angle=90, label='x={value:g}', 
                                    labelOpts={'position':0.1, 'color': (0,0,0), 'movable': True})
    lIndex = int( gqe.currentIndex*0.25)
    rIndex = int( gqe.currentIndex*0.75)
    gqe.plotItem.addItem( gqe.infLineLeft)
    gqe.plotItem.addItem( gqe.infLineRight)
    gqe.infLineLeft.setPos( gqe.x[lIndex])
    gqe.infLineRight.setPos( gqe.x[rIndex])

    return 

def _addInfiniteLines( gqe, nameList): 

    #
    # if we are called from the moveMotor() widget, the scan 
    # is extended. No need to re-create the cross-hair
    #
    if gqe.infLineMouseX is not None: 
        return 

    if gqe.doty:
        return 

    _addInfLineMouse( gqe)

    _addArrowsMotor( gqe, nameList)
    
    if gqe.flagDisplayVLines:
        _addVLines( gqe)
    return 

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

class _CAxisImageX( _pg.AxisItem):
    ''' 
    Formats axis label to human readable time.
    '''
    def tickStrings(self, values, scale, spacing):
        strns = []
        gqe = self.gqe
        for ix in values:
            if hasattr( gqe, 'xMin'): 
                x = float(ix)/float( gqe.width)*(gqe.xMax - gqe.xMin) + gqe.xMin
                strns.append( "%g" % x)
            else: 
                strns.append( "%g" % ix)

        return strns

class _CAxisImageY( _pg.AxisItem):
    ''' 
    Formats axis label for a image
    '''
    def tickStrings(self, values, scale, spacing):
        strns = []
        gqe = self.gqe
        for ix in values:
            if hasattr( gqe, 'yMin'): 
                x = float(ix)/float( gqe.height)*(gqe.yMax - gqe.yMin) + gqe.yMin
                strns.append( "%g" % x)
            else: 
                strns.append( "%g" % ix)

        return strns

def _getPen( scan):

    if scan.lineColor.upper() == 'NONE': 
        return None

    if scan.lineColor.lower() in _definitions.colorCode: 
        clr = _definitions.colorCode[ scan.lineColor.lower()]
    else:
        clr = 'k'

    if scan.lineStyle in _definitions.lineStylePQT:
        stl = _definitions.lineStylePQT[ scan.lineStyle]
    else:
        stl = QtCore.Qt.DashLine

    return _pg.mkPen( color = clr, width = scan.lineWidth, style = stl)

def _make_cb_mouseMoved( gqe):
    '''
    return a callback function for the moveMouse signal
    '''
    def mouseMoved(evt):
        #print " mouseMoved, evt[0]", scan.name, repr( evt[0])
        m = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        #
        # scan.plotItem can be None, if we created a PDF file. In this
        # can scan.plotItem was used by matplotlib. It is cleared when 
        # matplotlib is closed and it has no meaning in the pyqt world
        # anyhow
        #
        if gqe.plotItem is None:
            return 
        #
        # still it is possible that gqe.plotItem has been created
        # by matplotlib. 
        #
        if gqe.plotItem.__class__.__name__ != 'PlotItem':
            return 

        mousePoint = gqe.plotItem.vb.mapSceneToView(evt)

        #
        # it is an image
        #
        if type( gqe) == _gqe.Image: 
            mY = mousePoint.y()
            mX = mousePoint.x()
            if mY >= gqe.height: 
                mY = gqe.height - 1
            if mX >= gqe.width: 
                mX = gqe.width - 1
            tX = mX/float( gqe.width)*(gqe.xMax - gqe.xMin) + gqe.xMin
            tY = mY/float( gqe.height)*(gqe.yMax - gqe.yMin) + gqe.yMin
            gqe.mouseLabel.setText( "x %g, y %g, val %g " % (tX, tY, gqe.data[int(mX)][int(mY)]), color = 'w')
            gqe.mouseLabel.setPos( mousePoint.x(), mousePoint.y())
            gqe.mouseLabel.show()
            if gqe.cb_mouseLabel: 
                gqe.cb_mouseLabel( tX, tY, gqe.data[int(mX)][int(mY)])
            return 
            
        #
        # x is day-of-the year
        #
        if gqe.doty:
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

            gqe.mouseLabel.setText( "x=%s, y=%g" % (xStr, mousePoint.y()), color = 'k')
            gqe.mouseLabel.setPos( mousePoint.x(), mousePoint.y())
            gqe.mouseLabel.show()
            return 
        

        #
        # SCAN, linear or log 
        #
        if not gqe.yLog:
            mY = mousePoint.y()
        else:
            mY = _math.pow( 10., mousePoint.y())
        if not gqe.xLog:
            mX = mousePoint.x()
        else:
            mX = _math.pow( 10., mousePoint.x())
        #
        # getIndex() may throw an exception, if the x-values
        # are not ordered
        #
        try: 
            index = gqe.getIndex( mX)
        except Exception as err: 
            #print( "pqtgraphic.mouseMoved: %s" % repr( err))
            gqe.infLineMouseX.hide()
            gqe.infLineMouseY.hide()
            return 
        #
        # do not show the infinite lines, if the mouse is outside the window
        #
        if mX < gqe.xMin or mX > gqe.xMax or \
           mY < gqe.getYMin() or mY > gqe.getYMax():
            gqe.infLineMouseX.hide()
            gqe.infLineMouseY.hide()
            return 
        else: 
            gqe.infLineMouseX.show()
            gqe.infLineMouseY.show()

        if not gqe.xLog:
            gqe.infLineMouseX.setPos( gqe.x[index])
        else: 
            try: 
                gqe.infLineMouseX.setPos( _math.log10( gqe.x[index]))
            except: 
                pass
        if not gqe.yLog:
            gqe.infLineMouseY.setPos( gqe.y[index])
        else: 
            try: 
                gqe.infLineMouseY.setPos( _math.log10( gqe.y[index]))
            except: 
                pass

        if gqe.cb_mouseLabel: 
            gqe.cb_mouseLabel( gqe.x[ index], gqe.y[ index])
            
        if gqe.xLog or gqe.yLog: 
            if gqe.xLog and gqe.yLog: 
                gqe.mouseLabel.setText( "x=%g, y=%g" % ( gqe.x[ index], gqe.y[index]))
                try: 
                    gqe.mouseLabel.setPos( mousePoint.x(), _math.log10( gqe.y[index]))
                except: 
                    pass
                if index > gqe.currentIndex/2.: 
                    gqe.mouseLabel.setAnchor((1, 1))
                else:
                    gqe.mouseLabel.setAnchor((0, 1))
            elif gqe.yLog: 
                gqe.mouseLabel.setText( "y=%g" % (gqe.y[index]))
                try: 
                    gqe.mouseLabel.setPos( mousePoint.x(), _math.log10( gqe.y[index]))
                except: 
                    pass
                if index > gqe.currentIndex/2.: 
                    gqe.mouseLabel.setAnchor((1, 1))
                else:
                    gqe.mouseLabel.setAnchor((0, 1))
            elif gqe.xLog: 
                if index > gqe.currentIndex/2.: 
                    gqe.mouseLabel.setAnchor((1, 1))
                else:
                    gqe.mouseLabel.setAnchor((0, 1))
                gqe.mouseLabel.setText( "x=%g" % (gqe.x[index]))
                try: 
                    gqe.mouseLabel.setPos( _math.log10( gqe.x[index]), mousePoint.y())
                except: 
                    pass

            gqe.mouseLabel.show()
        return 
    return mouseMoved

def _make_cb_mouseClicked( gqe):
    '''
    return a callback function for the mouseClicked signal
    '''
    def mouseClicked(evt):

        #print( "+++pqtgraphics.mouseClicked: %s" % repr( evt.scenePos()))
        
        # left mouse button
        if evt.button() == 1: 
            #
            # scenePos() are pixel values
            #
            mousePoint = gqe.plotItem.vb.mapSceneToView(evt.scenePos())
            if type( gqe) == _gqe.Scan:
                if mousePoint.y() < gqe.getYMin() or \
                   mousePoint.y() > gqe.getYMax(): 
                    return 
                try: 
                    index = gqe.getIndex( mousePoint.x())
                except Exception as err: 
                    print( "pqtgraphics.mouseClicked %s" % repr( err))
                    return 
                _tangoIfc.move( gqe, gqe.x[ index])
            elif type( gqe) == _gqe.Image:
                if gqe.flagZooming: 
                    return 
                _tangoIfc.move( gqe, mousePoint.x(), mousePoint.y())
        # middle button
        elif evt.button() == 4: 
            mousePoint = gqe.plotItem.vb.mapSceneToView(evt.scenePos())
            if type( gqe) == _gqe.Image:
                gqe.shift( mousePoint.x(), mousePoint.y())
            return

    return mouseClicked

def _prepareMouse( gqe):
    '''
    see display() for some remarks about setting of the mouse/cursor
    '''
    global _myScene

    if gqe.mousePrepared: 
        return 

    if _myScene is None: 
        _myScene = gqe.plotItem.scene()
        _myScene.sigMouseMoved.connect( _make_cb_mouseMoved( gqe))
        _myScene.sigMouseClicked.connect( _make_cb_mouseClicked( gqe))
    #
    # the scene object seems to be fixed for an entrire session
    #
    #_clsFunctions.append( gqe.plotItem.scene().sigMouseClicked.disconnect)
    #_clsFunctions.append( gqe.plotItem.scene().sigMouseMoved.disconnect)
    #
    # the mouseLabel.hide() call messes up the x-scale, so we plot only a ' '
    #

    if type(gqe) == _gqe.Scan:
        if gqe.xLog or gqe.yLog or gqe.doty: 
            gqe.mouseLabel = _pg.TextItem( ".", color='k', anchor = (1, 1))
            #gqe.mouseLabel.setPos( gqe.x[0], gqe.y[0])
            gqe.plotItem.addItem( gqe.mouseLabel, ignoreBounds = True)
            gqe.mouseLabel.hide()
    elif type(gqe) == _gqe.Image:
        gqe.mouseLabel = _pg.TextItem( ".", color='b', anchor = (0.5, 0.5))
        gqe.mouseLabel.setPos( 0., 0.,)
        gqe.plotItem.addItem( gqe.mouseLabel, ignoreBounds = True)
        gqe.mouseLabel.hide()
    #
    # gqe.mousePrepared: needed because we can have several display() 
    # calls without cls()
    #
    gqe.mousePrepared = True
    return 

def _textIsOnDisplay( textStr):
    '''
    searches the list of Items to see whether textStr exists already
    '''
    for item in _graphicsWindow.items():
        if type( item) is _pg.graphicsItems.LabelItem.LabelItem: 
            if textStr == item.text:
                return True

    return False

def configGraphics(): 
    '''
    called from the GuiClass to adjust the distance between the plots
    '''
    if _QApp is None or _graphicsWindow is None: 
        _initGraphic()

    _graphicsWindow.ci.layout.setContentsMargins( _definitions.marginLeft, _definitions.marginTop, 
                                       _definitions.marginRight, _definitions.marginBottom)
    _graphicsWindow.ci.layout.setHorizontalSpacing( _definitions.spacingHorizontal)
    _graphicsWindow.ci.layout.setVerticalSpacing( _definitions.spacingVertical)
    return

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
    for item in _graphicsWindow.items():
        if isinstance( item, _pg.graphicsItems.GraphicsLayout.GraphicsLayout):
            if item.getItem( row, col) is not None:
                for elm in item.items:
                    if type( elm) == _pg.graphicsItems.LabelItem.LabelItem:
                        print "pqt_graphics.isCellTaken (%d, %d) %s" % (row, col, elm.text)
                        pass
                    else: 
                        print "pqt_graphics.isCellTaken (%d, %d) %s " % (row, col, repr( elm))
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
    title = _gqe.getTitle()
    if title is not None:
        if not _textIsOnDisplay( title):
            _graphicsWindow.addLabel( title, row = 0, col = 0, colspan = 10)

    comment = _gqe.getComment()
    if comment is not None:
        if not _textIsOnDisplay( comment):
            _graphicsWindow.addLabel( comment, row = 1, col = 0, colspan = 10)

def _calcTextPosition( scan, xIn, yIn): 
    '''
    return the text position, taking into accout:
      - autoscale
      - log scale
    '''
    
    if not scan.xLog:
        x = (_utils.xMax( scan) - _utils.xMin( scan))*xIn + _utils.xMin( scan)
    else:
        if scan.xMax <= 0. or scan.xMin <= 0.:
            raise ValueError( "pqt_graphics.calcTextPosition: xLog && (xMin <= 0: %g or xMax <= 0: %g" % 
                              (scan.xMin, scan.xMax))
        x = (_math.log10( scan.xMax) - _math.log10( scan.xMin))*xIn + _math.log10( scan.xMin)

    if scan.autoscaleY:  
        yMax = scan.getYMax()
        yMin = scan.getYMin()
        if not scan.yLog:
            y = ( yMax - yMin)*yIn + yMin
        else:
            if yMax <= 0. or yMin <= 0.:
                raise ValueError( "pqt_graphics.calcTextPosition: yLog && (yMin <= 0: %g or yMax <= 0: %g" % 
                                  (yMin, yMax))
            y = ( _math.log10( yMax) - _math.log10( yMin))*yIn + _math.log10( yMin)
    else: 
        if scan.yMax is None: 
            scan.yMax = scan.getYMax()
        if scan.yMin is None: 
            scan.yMin = scan.getYMin()
        if not scan.yLog:
            #y = ( scan.yMax - scan.yMin)*yIn + scan.yMin
            y = (_utils.yMax( scan) - _utils.yMin( scan))*yIn + _utils.yMin( scan)
        else:
            if scan.yMax <= 0. or scan.yMin <= 0.:
                raise ValueError( "pqt_graphics.calcTextPosition: yLog && (yMin <= 0: %g or yMax <= 0: %g" % 
                                  (scan.yMin, scan.yMax))
            y = ( _math.log10( scan.yMax) - _math.log10( scan.yMin))*yIn + _math.log10( scan.yMin)
    #
    #print "pqt_graphics.calcTextPosition: yMin %g, yMax %g, y %g" % ( _utils.yMin( scan), 
    #                                                                  _utils.yMax( scan), y)
    #if hasattr( scan, "plotDataItem"): 
    #    print scan.plotDataItem.dataBounds(1)
    return( x, y)

def _addTexts( scan, nameList): 

    if type( scan) != _gqe.Scan:
        return 

    fontSize = _gqe.getFontSize( nameList)
    
    for elm in scan.textList:

        if elm.fontSize is None:
            elm.fontSizeTemp = fontSize
        else:
            elm.fontSizeTemp = elm.fontSize

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
        if elm.color.lower() in _definitions.colorCode:
            textItem = _pg.TextItem( color=_definitions.colorCode[ elm.color.lower()], anchor = ( anchorX, anchorY))
            textItem.setHtml( '<div style="font-size:%dpx;">%s</div>' % ( elm.fontSizeTemp, elm.text))
        else:
            textItem = _pg.TextItem( color='k', anchor = ( anchorX, anchorY))
            textItem.setHtml( '<div style="font-size:%dpx;">%s</div>' % ( elm.fontSizeTemp, elm.text))

        if scan.textOnly:
            x = elm.x
            y = elm.y
        else:
            (x, y) = _calcTextPosition( scan, elm.x, elm.y)
            
        elm.textItem = textItem
        #
        # if 'ignoreBounds=True' is removed, the x-scaling goes
        # crazy and the logTickStrings() error, AxisItem.py l.766
        # appears
        #
        scan.plotItem.addItem( textItem, ignoreBounds = True)
        textItem.setPos( x, y)
        textItem.show()
    return

def _updateTextPosition( scan): 
    '''
    need this for autoscaled scans
    '''
    for elm in scan.textList:

        if scan.textOnly:
            x = elm.x
            y = elm.y
        else:
            (x, y) = _calcTextPosition( scan, elm.x, elm.y)
        elm.textItem.setPos( x, y)
        elm.textItem.setHtml( '<div style="font-size:%dpx;">%s</div>' % ( elm.fontSizeTemp, elm.text))
    return 

def _setTitle( scan, nameList): 

    fontSize = _gqe.getFontSize( nameList)

    #
    # the length of the title has to be limited. Otherwise pg 
    # screws up. The plots will no longer fit into the workstation viewport
    # and the following display command, even with less scans, will 
    # also not fit into the graphics window
    #
    if len( scan.name) > _definitions.LEN_MAX_TITLE:
        tempName = "X_" + scan.name[-_definitions.LEN_MAX_TITLE:]
    else: 
        tempName = scan.name 

    #
    # the title is above the plot. This is the save way to plot the 
    # title. If we do it with TextItem, see below and if we use
    # autoscale, the x-axis is screwed-up
    #
    # see also 
    #   /home/kracht/Misc/pySpectra/examples/create22.py
    #   /home/kracht/Misc/pySpectra/examples/pyqtgraph/create22.py
    #
    if True or _gqe.getNumberOfGqesToBeDisplayed( nameList) < _definitions.MANY_GQES: 
        scan.plotItem.setLabel( 'top', text=tempName, size = '%dpx' % fontSize)
    #
    # too many plots, so put the title into the plot
    #
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
        if scan.autoscaleY: 
            y = ( scan.getYMax() - scan.getYMin())*0.85 + scan.getYMin()
        else: 
            if scan.yMax is None: 
                scan.yMax = scan.getYMax()
            if scan.yMin is None: 
                scan.yMin = scan.getYMin()
            if not scan.yLog:
                y = ( scan.yMax - scan.yMin)*0.85 + scan.yMin
            else:
                if scan.yMax <= 0. or scan.yMin <= 0.:
                    raise ValueError( "pqt_graphics.setTitle: yLog && (yMin <= 0: %g or yMax <= 0: %g" % (scan.yMin, scan.yMax))
                y = ( _math.log10( scan.yMax) - _math.log10( scan.yMin))*0.85 + \
                    _math.log10( scan.yMin)
        txt.setPos( x, y)
        #
        # if 'ignoreBounds=True', the x-range is corrent and the log tick 
        # mark error does not appear
        #
        vb.addItem( txt, ignoreBounds = True)
    return 

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

def _setAutoscaleForOverlaid( scan, target):

    if scan.autoscaleY is False:
        if scan.yMin is None or scan.yMax is None: 
            if target.yMin is not None and target.yMax is not None: 
                scan.viewBox.setYRange( target.yMin, target.yMax)
                aY = False
            else:
                aY = True
                #raise ValueError( "pqt_graphics.display: not autoscaleY and (yMin is None or yMax is None)")
        else:
            scan.viewBox.setYRange( scan.yMin, scan.yMax)
            aY = False
    else:
        aY = True

    if scan.autoscaleX is False:
        if scan.xMin is None or scan.xMax is None: 
            if target.xMin is not None and target.xMax is not None: 
                scan.viewBox.setXRange( target.xMin, target.xMax)
                aX = False
            else:
                aX = True
                #raise ValueError( "pqt_graphics.display: not autoscaleX and (xMin is None or xMax is None)")
        else:
            scan.viewBox.setXRange( scan.xMin, scan.xMax)
            aX = False
    else:
        aX = True
    #scan.viewBox.enableAutoscale( x = aX, y = aY)
    return 

def _isOverlayTarget( scan, nameList): 
    '''
    returns True, if the scan is the target for the overlay 
    of another scan
    '''
    gqeList = _gqe.getGqeList()
    for elm in gqeList: 
        if elm.overlay is None: 
            continue
        if scan.name.lower() == elm.overlay.lower():
            #
            # is the overlaid scan really displayed?
            #
            if elm.name.lower() in nameList:
                return True
    return False


class SmartFormat( _pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(SmartFormat, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        if self.logMode:
            return [ "%g" % x for x in 10 ** _np.array(values).astype(float)]
        return super( SmartFormat, self).tickStrings( values, scale, spacing)

def _createPlotItem( gqe, nameList):            
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
    #print "graphics.createPlotItem", gqe.name, repr( gqe.at)
    #print "graphics.createPlotItem, nrow", gqe.nrow, "ncol", gqe.ncol, \
    #    "nplot", gqe.nplot
    row = int( _math.floor(float( gqe.nplot - 1)/float(gqe.ncol)))
    col = int( gqe.nplot - 1 - row*gqe.ncol) 
    #
    # take title and comment into account
    #
    row += 2
    
    if _isCellTaken( row, col):
        raise ValueError( "pqt_graphics.createPlotItem: %s cell (%d, %d) is already taken" % ( gqe.name, row, col))
    #
    # the textContainer
    #
    if type( gqe) == _gqe.Scan and gqe.textOnly:
        #
        # pyqtgraph.graphicsItems.ViewBox.ViewBox.ViewBox
        #
        gqe.plotItem = _graphicsWindow.addViewBox( row, col)
        gqe.plotItem.setRange( xRange = ( 0, 1), yRange = ( 0., 1.))
        _addTexts( gqe, nameList)
        return 

    try:
        if type( gqe) == _gqe.Scan and gqe.doty: 
            plotItem = _graphicsWindow.addPlot( axisItems = { 'bottom': _CAxisTime( orientation='bottom'),
                                                              'left': SmartFormat(orientation='left'),
                                                              'right': SmartFormat(orientation='right')}, # if overlay
                                                row = row, col = col, colspan = gqe.colSpan) 
        else:
            #
            # <class 'pyqtgraph.graphicsItems.PlotItem.PlotItem.PlotItem'>
            #
            if type( gqe) == _gqe.Image:
                l = _CAxisImageY( orientation='left')
                b = _CAxisImageX( orientation='bottom')
                l.gqe = gqe
                b.gqe = gqe
                if gqe.flagAxes:
                    plotItem = _graphicsWindow.addPlot( row = row, col = col, colspan = gqe.colSpan,
                                             axisItems = { 'left': l, 
                                                           'right': SmartFormat(orientation='right'),  # if overlay
                                                           'bottom': b})
                else: 
                    plotItem = _graphicsWindow.addPlot( row = row, col = col, colspan = gqe.colSpan)
            else:
                plotItem = _graphicsWindow.addPlot( row = row, col = col, colspan = gqe.colSpan,
                                         axisItems = { 'left': SmartFormat(orientation='left'), 
                                                       'right': SmartFormat(orientation='right'),  # if overlay
                                                       'bottom': SmartFormat(orientation='bottom')})

            
    except Exception, e:
        print "graphics.createPlotItem: caught exception, row", row, "col", col, "colspan", gqe.colSpan
        print repr( e)
        raise ValueError( "graphics.createPlotItem, throwing exception")

    gqe.plotItem = plotItem 
    #
    # Set the default clip-to-view mode for all PlotDataItems managed by this plot. 
    # If clip is True, then PlotDataItems will attempt to draw only points within 
    # the visible range of the ViewBox.
    #
    gqe.plotItem.setClipToView( False)
    #
    # we want a closed axis box and we want tick marks 
    # at the top and right axis, but no tick mark texts
    #
    gqe.plotItem.showAxis('top')
    gqe.plotItem.getAxis('top').style[ 'showValues'] = False #  not working on Debian-8, 0.9.8-3 
    #
    # plot the right axis here, if the gqe is not the target
    # of another gqe which is overlaid.
    #
    if not _isOverlayTarget( gqe, nameList):
        gqe.plotItem.showAxis('right')
        gqe.plotItem.getAxis('right').style[ 'showValues'] = False #  not working on Debian-8, 0.9.8-3 
    #
    # 0.9.8-3 
    #
    if _pg.__version__ is None: 
        gqe.plotItem.getAxis('top').setTicks( [])
        if not _isOverlayTarget( gqe, nameList):
            gqe.plotItem.getAxis('right').setTicks( [])

    if type( gqe) == _gqe.Scan: 
        gqe.plotItem.showGrid( x = gqe.showGridX, y = gqe.showGridY)

    if _gqe.getNumberOfGqesToBeDisplayed( nameList) <= _definitions.MANY_GQES:
        if hasattr( gqe, 'xLabel') and gqe.xLabel is not None:
            gqe.plotItem.setLabel( 'bottom', text=gqe.xLabel)
        if hasattr( gqe, 'yLabel')  and gqe.yLabel is not None:
            gqe.plotItem.setLabel( 'left', text=gqe.yLabel)
    #
    # autoscale
    #
    if type( gqe) == _gqe.Scan:
        arX = gqe.autoscaleX
        arY = gqe.autoscaleY
        #
        # this is a very bad fix for a bug that popped up in viewStatETH0.py. 
        # There we have chosen a log scale with autorange == True
        #
        # see also the raise() at line 768 in 
        #   /usr/lib/python2.7/dist-packages/pyqtgraph/graphicsItems/AxisItem.py
        #
        if arY and gqe.yLog and len( _gqe.getGqeList()) > 15:
            arY = False
            #print "pqt_graphics.createPlotItem: changing autoRangeY to False"
            gqe.setLimits()

        if gqe.yMin is None or gqe.yMax is None:
            arY = True
        #
        # problem: autoscale needs padding != 0
        #
        gqe.plotItem.enableAutoRange( x = arX, y = arY)
        #
        # log scale
        # this statement has to precede the setYRange()
        #
        gqe.plotItem.setLogMode( x = gqe.xLog, y = gqe.yLog)

        if not arY: 
            if gqe.yLog:
                #
                # if yLog, the limits have to be supplied as logs
                #
                if gqe.yMax <= 0. or gqe.yMin <= 0.:
                    raise ValueError( "pqt_graphics.createPlotItem: yLog && (yMin <= 0: %g or yMax <= 0: %g" % \
                                      (gqe.yMin, gqe.yMax))
                gqe.plotItem.setYRange( _math.log10( gqe.yMin), _math.log10(gqe.yMax))
            else:
                gqe.plotItem.setYRange( gqe.yMin, gqe.yMax)

        if not arX: 
            if gqe.xLog:
                if gqe.xMax <= 0. or gqe.xMin <= 0.:
                    raise ValueError( "pqt_graphics.createPlotItem: xLog && (xMin <= 0: %g or xMax <= 0: %g" % \
                                      (gqe.xMin, gqe.xMax))
                gqe.plotItem.setXRange( _math.log10( gqe.xMin), _math.log10(gqe.xMax))
            else:
                gqe.plotItem.setXRange( gqe.xMin, gqe.xMax) #, padding = 0)

    gqe.plotItem.setMouseEnabled( x = True, y = True)

    _setTitle( gqe, nameList)
    _addTexts( gqe, nameList)

    return

def _cmap_xmap(function, cmap):
    """ Applies function, on the indices of colormap cmap. Beware, function
    should map the [0, 1] segment to itself, or you are in for surprises.

    See also cmap_xmap.
    """
    cdict = cmap._segmentdata
    function_to_map = lambda x : (function(x[0]), x[1], x[2])
    for key in ('red','green','blue'):
        cdict[key] = map(function_to_map, cdict[key])
        cdict[key].sort()
        assert (cdict[key][0]<0 or cdict[key][-1]>1), "Resulting indices extend out of the [0, 1] segment."

    return _mpl.colors.LinearSegmentedColormap('colormap',cdict,1024)

def _displayImages( flagDisplaySingle, nameList = None):

    gqeList = _gqe.getGqeList()

    for imageGqe in gqeList:
        if type( imageGqe) != _gqe.Image: 
            continue
        if len( nameList) > 0: 
            if imageGqe.name not in nameList:
                continue
        if imageGqe.plotItem is None: 
            _createPlotItem( imageGqe, nameList)

        #imageGqe.plotItem = _graphicsWindow.addPlot( row = imageGqe.row, col = imageGqe.col)
        if imageGqe.img is None:
            imageGqe.img = _pg.ImageItem()
            imageGqe.plotItem.addItem( imageGqe.img)
            if imageGqe.log:
                try:
                    imageGqe.img.setImage( _np.log( imageGqe.data))
                except Exception, e: 
                    imageGqe.log = False
                    print "pqt_graphics: log failed"
                    print repr( e)
                    return 
            else:
                if imageGqe.modulo != -1:
                    imageGqe.img.setImage( imageGqe.data % imageGqe.modulo)
                else: 
                    imageGqe.img.setImage( imageGqe.data)
        else: 
            if imageGqe.log:
                try:
                    imageGqe.img.setImage( _np.log( imageGqe.data))
                except Exception, e: 
                    imageGqe.log = False
                    print "pqt_graphics: log failed"
                    print repr( e)
                    return 
            else:
                if imageGqe.modulo != -1:
                    imageGqe.img.setImage( imageGqe.data % imageGqe.modulo)
                else: 
                    imageGqe.img.setImage( imageGqe.data)
        try: 
            #
            # matplotlib.colors.LinearSegmentedColormap
            #
            if imageGqe.colorMap == 'blackwhite':
                import matplotlib.colors as clr
                colormap = clr.LinearSegmentedColormap.from_list('blackwhite',     ['#000000','#ffffff'], N=256)
                colormap._init()
                lut = (colormap._lut * 255).view( _np.ndarray)  # Convert matplotlib colormap from 0-1 to 0-255 for Qt
                length = lut.shape[0] - 3
                lutTemp = _np.copy( lut)
                for i in range( length):
                    if (i%2) == 0:
                        lutTemp[i] = [0., 0., 0., 255.] 
                    else:
                        lutTemp[i] = [255., 255., 255., 255.] 
                lut = _np.copy( lutTemp)
            else:
                colormap = cm.get_cmap( imageGqe.colorMap)
                colormap._init()
                lut = (colormap._lut * 255).view( _np.ndarray)  # Convert matplotlib colormap from 0-1 to 0-255 for Qt
                length = lut.shape[0] - 3
                lutTemp = _np.copy( lut)

            for i in range( length):
                j = i - (imageGqe.indexRotate % length)
                if j < 0: 
                    j = j + length
                lutTemp[j] = lut[i]

            lut = _np.copy( lutTemp)

            imageGqe.img.setLookupTable( lut)
        except Exception, e: 
            print "pqt_graphics: problem accessing color map, using default"
            print repr( e)
            lut = _np.zeros((256,3), dtype=_np.ubyte)
            lut[:128,0] = _np.arange(0,255,2)
            lut[128:,0] = 255
            lut[:,1] = _np.arange(256)
            imageGqe.img.setLookupTable(lut)

        if flagDisplaySingle:
            _prepareMouse( imageGqe)

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
    #import HasyUtils
    #HasyUtils.printCallStack()
    #print "pqt_graphics.display, nameList:", repr( nameList)
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
    # see if the members of nameList are in the gqeList
    #
    for nm in nameList:
        if _gqe.getGqe( nm) is None:
            raise ValueError( "graphics.display: %s is not in the gqeList" % nm)

    gqeList = _gqe.getGqeList()
    #
    # find out whether only one gqe will be displayed 
    # in this case the mouse-cursor will be activated
    #
    flagDisplaySingle = False
    if len( nameList) == 1 or len( gqeList) == 1:
        flagDisplaySingle = True

    #
    # adjust the graphics window to the number of displayed scans
    #
    nDisplay = _gqe.getNumberOfGqesToBeDisplayed( nameList)
    _setSizeGraphicsWindow( nDisplay)
    _adjustFigure( nDisplay)

    #
    # set scan.nrow, scan.ncol, scan.nplot
    #
    _utils.setGqeVPs( nameList, flagDisplaySingle, cls)

    #
    # _displayTitleComment() uses (0,0) and (1, 0)
    # this has to follow setGqeVPs because this function
    # might execute a cls()
    #
    _displayTitleComment()
    #
    # images
    #
    _displayImages( flagDisplaySingle, nameList)
    
    #_allocateViewBox()
    #
    # --- first pass: run through the scans in gqeList and display 
    #     non-overlaid scans
    #
    for scan in gqeList:

        if type( scan) != _gqe.Scan: 
            continue
        #print "graphics.display.firstPass,", scan.name

        #
        # if currentIndex == 0 it is a problem to draw the axes, escpecially 
        # to put text strings on the screen
        #
        if not scan.textOnly and scan.currentIndex == 0:
            continue
        #
        # overlay? - don't create a plot for this scan. Plot it
        # in the second pass. But it is displayed, if it is the only 
        # scan or if it is the only scan mentioned in nameList
        #
        if scan.overlay is not None and not flagDisplaySingle:
            #
            # maybe the scan.overlay has beed deleted
            #
            if _gqe.getGqe( scan.overlay) is None:
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
                                                           symbolPen = _definitions.colorCode[ scan.symbolColor.lower()], 
                                                           symbolBrush = _definitions.colorCode[ scan.symbolColor.lower()], 
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
        #
        # the mouse interferes a little bit with scanning type displays.
        # the problem is that the cursor, or ' ' is placed somewhere on
        # the screen and this may have an influence of the whole graphics
        #
        # even after finishing a scan the currentIndex is != len()
        #
        #if scan.currentIndex == (len( scan.x) - 1) and flagDisplaySingle: 
        if flagDisplaySingle: 
            _prepareMouse( scan)
            _addInfiniteLines( scan, nameList)
        _updateTextPosition( scan)

    #
    # --- 
    # --- second pass: display overlaid scans
    # --- 
    #
    for scan in gqeList:
        #print "graphics.display.secondPass,", scan.name

        if type( scan) != _gqe.Scan: 
            continue

        #
        # if only one scan is displayed, there is no overlay
        #
        if len( nameList) == 1:
            break
        #
        # textContainers are not overlaid
        #
        if scan.textOnly:
            continue
        #
        if scan.overlay is None:
            continue
        #
        # check, if there is something to display
        #
        if scan.lastIndex == scan.currentIndex:
            continue
        
        if len( nameList) > 0 and scan.name not in nameList:
            continue

        target = _gqe.getGqe( scan.overlay)
        if target is None or target.plotItem is None:
            raise ValueError( "pqt_graphics.display: %s tries to overlay to %s" %
                              (scan.name, scan.overlay))

        scan.plotItem = target.plotItem

        if scan.viewBox is None:
            scan.viewBox = _pg.ViewBox()
            target.scene = target.plotItem.scene()
            target.scene.addItem( scan.viewBox)
            #
            # _graphicsWindow.clear() doesn't really work. Therefore we have to 
            # prepare a function to be called by cls()
            #
            _clsFunctions.append( _makeClsSceneFunc( target.scene, scan.viewBox))
            #
            # link the views x-axis to another view
            #
            scan.viewBox.setXLink( target.plotItem)

        _setAutoscaleForOverlaid( scan, target)
        #
        # for the overlaid scan show the right axis ...
        #
        target.plotItem.showAxis('right') 
        #
        # ... but if there are too many to be displayed, remove the tick mark labels
        #
        if nDisplay > 10: 
            target.plotItem.getAxis('right').style[ 'showValues'] = False #  not working on Debian-8, 0.9.8-3 

        target.plotItem.getAxis('right').linkToView( scan.viewBox)
        #
        # _graphicsWindow.clear() doesn't really work. Therefore we have to 
        # prepare a function to be called by cls()
        #
        #_clsFunctions.append( _makeClsSceneFunc( target.scene, scan.viewBox))
        _updateViews( target, scan)
        #
        # link the views x-axis to another view
        #
        #scan.viewBox.setXLink( target.plotItem)

        target.plotItem.vb.sigResized.connect( _make_updateViews( target, scan))

        if scan.plotDataItem is None:
            if scan.symbolColor.upper()  == 'NONE':
                #curveItem = _pg.PlotCurveItem( x = scan.x, y = scan.y, pen = _getPen( scan))
                scan.plotDataItem = _pg.PlotDataItem( x = scan.x, y = scan.y, pen = _getPen( scan))
            else:
                #scan.plotDataItem = _pg.PlotDataItem( x = scan.x, y = scan.y, pen = _getPen( scan))
                scan.plotDataItem = _pg.ScatterPlotItem( x = scan.x, y = scan.y,
                                                         symbol = scan.symbol, 
                                                         pen = _definitions.colorCode[ scan.symbolColor.lower()], 
                                                         brush = _definitions.colorCode[ scan.symbolColor.lower()], 
                                                         size = scan.symbolSize)
            scan.viewBox.addItem( scan.plotDataItem )
                
        if scan.yLog:
            #
            # if yLog, the limits have to be supplied as logs
            #
            if scan.yMax <= 0. or scan.yMin <= 0.:
                raise ValueError( "pqt_graphics.createPlotItem: yLog && (yMin (%g) <= 0 or yMax (%g) <= 0" % \
                                  (scan.yMin, scan.yMax))
            scan.plotDataItem.setLogMode( False, True)
            scan.viewBox.setYRange( _math.log10( scan.yMin), _math.log10(scan.yMax))
        else:
            if scan.useTargetWindow:
                if target.autoscaleY:
                    mi = target.getYMin()
                    ma = target.getYMax()
                    scan.viewBox.setYRange( mi, ma)
                    target.plotItem.setYRange( mi, ma)
                    scan.xMin = mi
                    scan.xMax = ma
                else: 
                    scan.viewBox.setYRange( target.yMin, target.yMax)

            #scan.plotItem.setYRange( scan.yMin, scan.yMax)
            pass
        #
        # we have to suppress the tick marks of the right axis, if
        # the overlaid plot and the target don not have the same logMode
        #
        # example files: 
        #   pySpectra/examples/Overlay2.py
        #   pySpectra/examples/Overlay2BothLog.py
        #   pySpectra/examples/Overlay2FirstLog.py
        #   pySpectra/examples/Overlay2SecondLog.py
        #
        if scan.yLog and not target.yLog or \
           not scan.yLog and target.yLog:
            target.plotItem.getAxis('right').style[ 'showValues'] = False

        #scan.viewBox.addItem( dataItem )
        
        scan.lastIndex = scan.currentIndex
        _updateTextPosition( scan)

    processEvents()

    return
