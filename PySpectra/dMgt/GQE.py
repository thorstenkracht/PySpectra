#!/bin/env python
'''
GQE - contains the Scan() class and functions to handle scans: 
      delete(), getScan(), getScanList(), info(), overlay(), show()
'''
# 1.8.2

import numpy as _np
import PySpectra as _pysp
from PyQt4 import QtCore as _QtCore
from PyQt4 import QtGui as _QtGui


_scanList = []
_scanIndex = None  # used by next/back
_title = None
_comment = None
#
# if the wsViewport is set, e.g. to dina4, it is fixed, i.e. independent 
# of how many scans are displayed 
#
_wsViewportFixed = False

_ScanAttrsPublic = [ 'at', 'autoscaleX', 'autoscaleY', 'colSpan', 'currentIndex', 
                     'dType', 'doty', 'fileName', 'flagDisplayVLines', 'lastIndex', 
                     'nPts', 'name', 'ncol', 'nplot', 'nrow', 'overlay', 'overlayUseTargetWindow', 
                     'showGridX', 'showGridY', 
                     'lineColor', 'lineStyle', 'lineWidth', 
                     'logWidget', 'motorList', 
                     'symbol', 'symbolColor', 'symbolSize', 
                     'textList', 'textOnly', 'viewBox', 
                     'x', 'xLog', 'xMax', 'xMin', 'xMaxDisplay', 'xMinDisplay', 
                     'xLabel', 'y', 'yLabel', 'yLog', 'yMin', 'yMax','yMinDisplay', 'yMaxDisplay',
                     'yTicksVisible'] 

_ScanAttrsPrivate = [ 'infLineLeft', 'infLineRight', 'mouseClick', 'mouseLabel', 'mouseProxy', 
                      'plotItem', 'plotDataItem', 'scene', 'xDateMpl']

class Text(): 
    '''
    Texts belong to a Scan, created by Scan.addText(), they are stored in Scan.textList.
    text: 'someString'
    x: 0.5
    y: 0.5
    hAlign: 'left', 'right', 'center'
    vAlign: 'top', 'bottom', 'center'
    color: 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'black'
    fontSize: e.g. 12 or None
      if None, the fontsize is chosen automatically depending on the number of plots
    NDC: True, normalized device coordinates
    '''
    def __init__( self, text = 'Empty', x = 0.5, y = 0.5, 
                  hAlign = 'left', vAlign = 'top', color = 'black', fontSize = None,
                  NDC = True): 

        self.text = text
        self.x = x
        self.y = y
        self.hAlign = hAlign
        self.vAlign = vAlign
        self.color = color
        self.fontSize = fontSize
        self.NDC = NDC
'''
A value of (0,0) sets the upper-left corner
                     of the text box to be at the position specified by setPos(), while a value of (1,1)
                     sets the lower-right corner.        
'''
class Scan( object):
    '''
    A Scan contains 2 arrays, x and y, and graphics attributes

    PySpectra.Scan( name = 'name', filename = 'test.fio', x = 1, y = 2)
      read the data from a file
    PySpectra.Scan( name = 'name', x = xArr, y = yArr)
      pass the data as arrays
    PySpectra.Scan( name = 'name', xMin = 0., xMax = 10., nPts = 101)
    PySpectra.Scan( name = 'name')
      the same as PySpectra.Scan( name = 'name', xMin = 0., xMax = 10., nPts = 101)
    PySpectra.Scan( name = 'name', reUse = True, xArr, y = yArr)
      re-use the existing data struckture, useful for MCA scans

    The attributes: 
        autoscaleX, autoscaleY
                    default: True
        colSpan:    def.: 1
        doty:       bool
                    if True, the x-axis tick mark labels are dates, def. False
        fileName:   string
        xLog, 
        yLog:       bool
                    def. False
        overlay:    string 
                    the name of the scan occupying the target viewport 
        showGridX, 
        showGridY:  True/False
        lineColor:  'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'black', 'NONE'
        lineStyle:  'None', 'SOLID', 'DASHED', 'DOTTED', 'DASHDOTTED'
                    if None, the line is not plotted
        lineWidth:  float: 1.0, 1.2, 1.4, 1.6, 1.8, 2.0
                    line width, def.: 1
        symbol:     string
                    o - circle, s - square, t - triangle, d - diamond, + - plus
        symbolColor: 
                    def.: NONE
        symbolSize: float
                    def.: 5
        xLabel:     string
                    the description of the x-axis
        yLabel:     string
                    the description of the y-axis
    '''
    #
    # this class variable stores the Gui, needed to configure the motorsWidget, 
    # which happens for each new scan
    #
    monitorGui = None

    def __init__( self, name = None, **kwargs):
        global _scanList

        #print "GQE.Scan: ", repr( kwargs)

        if name is None:
            raise ValueError( "GQE.Scan: 'name' is missing")
        #
        #
        #
        self.textOnly = False
        #
        # We 'reUse' e.g. MCA scans
        #
        for i in range( len( _scanList)): 
            if name == _scanList[i].name:
                if 'reUse' in kwargs: 
                    if len( _scanList[i].x) != len( kwargs['x']):
                        raise ValueError( "GQE.Scan: len( scan.x) %d != len( kwargs[ 'x'])" % \
                                          ( len( _scanList[i].x), len( kwargs['x'])))
                    if len( _scanList[i].y) != len( kwargs['y']):
                        raise ValueError( "GQE.Scan: len( scan.y) %d != len( kwargs[ 'y'])" % \
                                          ( len( _scanList[i].y), len( kwargs['y'])))
                    _scanList[i].x = kwargs['x']
                    _scanList[i].y = kwargs['y']
                    _scanList[i].lastIndex = 0
                    return
                else:
                    raise ValueError( "GQE.Scan: %s exists already" % name)
        if 'reUse' in kwargs:
            del kwargs[ 'reUse'] 
            
        self.name = name
        if 'x' in kwargs and 'y' not in kwargs or \
           'x' not in kwargs and 'y' in kwargs:
            raise ValueError( "GQE.Scan.__init__: if 'x' or 'y' then both have to be supplied")
        #
        # textOnly scans have no data, consist of Texts( in textList) only
        #
        if 'textOnly' in kwargs:
            self.textOnly = True
            del kwargs[ 'textOnly']
            pass
        #
        # if 'x' and 'y' are supplied the scan is created using data
        # Note: a file name may be supplied, e.g. if the scan comes from a file.
        #
        elif 'x' in kwargs and _isArrayLike( kwargs[ 'x']) and \
             'y' in kwargs and _isArrayLike( kwargs[ 'y']):
            self._createScanFromData( kwargs)
        #    
        # 'fileName': data are read from a file
        #    
        elif 'fileName' in kwargs: 
            if 'x' not in kwargs or 'y' not in kwargs:
                raise ValueError( "GQE.Scan.__init__: 'fileName' but no 'x' and no 'y', %s" % kwargs[ 'fileName'])

            fioCol = read( kwargs[ 'fileName'], kwargs[ 'x'], kwargs[ 'y'])
            kwargs[ 'x']= fioCol.x
            kwargs[ 'y']= fioCol.y
            self._createScanFromData( kwargs)
        #
        # otherwise we use limits and the limits have defaults
        #
        else:
            self._createScanFromLimits( kwargs)

        self.setAttr( kwargs)

        if kwargs:
            raise ValueError( "GQE.Scan: dct not empty %s" % str( kwargs))
        
        self.textList = []

        _scanList.append( self)

    def __setattr__( self, name, value): 
        #print "GQE.Scan.__setattr__: name %s, value %s" % (name, value)
        if name in _ScanAttrsPublic or \
           name in _ScanAttrsPrivate: 
            super(Scan, self).__setattr__(name, value)
        else: 
            raise ValueError( "GQE.Scan.__setattr__: Scan %s wrong attribute name %s" % ( self.name, name))

    def __getattr__( self, name): 
        raise ValueError( "GQE.Scan.__getattr__: %s wrong attribute %s" % ( self.name, name))
        #if name in _ScanAttrsPublic or \
        #   name in _ScanAttrsPrivate: 
        #    return super(Scan, self).__getattr__(name)
        #else: 
        #    raise ValueError( "GQE.Scan.__getattr__: Scan %s wrong attribute name %s" % ( self.name, name))
        
    def __del__( self): 
        pass

    #@staticmethod
    #
    # why do we need a class function for move()
    #
    def move( self, target): 
        import PyTango as _PyTango
        import time as _time

        #print "GQE.Scan.move: to", target, "using", Scan.monitorGui.scanInfo
        #
        # from moveMotor widget
        #
        if self.motorList is not None:
            if len( self.motorList) != 1:
                print "GQE.Scan.move: len != 1"
                return 

            proxy = self.motorList[0]
            #
            # stop the motor, if it is moving
            #
            if proxy.state() == _PyTango.DevState.MOVING:
                if self.logWidget is not None:
                    self.logWidget.append( "Move: stopping %s" % proxy.name()) 
                proxy.stopMove()
            while proxy.state() == _PyTango.DevState.MOVING:
                _time.sleep(0.01)

            msg = "Move %s from %g to %g" % ( proxy.name(), 
                                             float( proxy.read_attribute( 'Position').value), 
                                             float( target))
            reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No)        
            if not reply == _QtGui.QMessageBox.Yes:
                if self.logWidget is not None:
                    self.logWidget.append( "Move: move not confirmed") 
                else:
                    print "Move: move not confirmed"
                return
            if self.logWidget is not None:
                self.logWidget.append( "Moving %s from %g to %g" % ( proxy.name(), 
                                                                    float( proxy.read_attribute( 'Position').value), 
                                                                    target))
            self.motorList[0].Position = target
            return 

        #
        # move() has to be called from the pyspMonitor application
        #
        if Scan.monitorGui is None or Scan.monitorGui.scanInfo is None: 
            return

        motorArr = Scan.monitorGui.scanInfo['motors']        
        length = len( motorArr)
        if  length == 0 or length > 3:
            _QtGui.QMessageBox.about( None, 'Info Box', "no. of motors == 0 or > 3") 
            return

        motorIndex = Scan.monitorGui.scanInfo['motorIndex']

        if motorIndex >= length:
            _QtGui.QMessageBox.about( None, 'Info Box', "motorIndex %d >= no. of motors %d" % (motorIndex, length))
            return
            
        motorArr[motorIndex]['targetPos'] = target
        r = (motorArr[motorIndex]['targetPos'] - motorArr[motorIndex]['start']) / \
            (motorArr[motorIndex]['stop'] - motorArr[motorIndex]['start']) 

        if length == 1:
            p0 = _PyTango.DeviceProxy( motorArr[0]['name'])
            msg = "Move %s from %g to %g" % (motorArr[0]['name'], 
                                             float(p0.read_attribute( 'Position').value), 
                                             float( motorArr[0]['targetPos']))
            reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No)        

        #
        # for hklscan: a h-move may move the same motors as a k-move, etc. 
        #
        elif length == 2:
            motorArr[0]['targetPos'] = (motorArr[0]['stop'] - motorArr[0]['start'])*r + motorArr[0]['start']
            motorArr[1]['targetPos'] = (motorArr[1]['stop'] - motorArr[1]['start'])*r + motorArr[1]['start']
            p0 = _PyTango.DeviceProxy( motorArr[0]['name'])
            p1 = _PyTango.DeviceProxy( motorArr[1]['name'])
            msg = "Move\n  %s from %g to %g\n  %s from %g to %g " % \
                  (motorArr[0]['name'], p0.read_attribute( 'Position').value, motorArr[0]['targetPos'],
                   motorArr[1]['name'], p1.read_attribute( 'Position').value, motorArr[1]['targetPos'])
            reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No)

        #
        # for hklscan: a h-move may move the same motors as a k-move, etc. 
        #   - therefore we may have to repeat the Move2Cursor
        #   - and we have to check whether a motor is already in-target
        #
        elif length == 3:
            motorArr[0]['targetPos'] = (motorArr[0]['stop'] - motorArr[0]['start'])*r + motorArr[0]['start']
            motorArr[1]['targetPos'] = (motorArr[1]['stop'] - motorArr[1]['start'])*r + motorArr[1]['start']
            motorArr[2]['targetPos'] = (motorArr[2]['stop'] - motorArr[2]['start'])*r + motorArr[2]['start']
            p0 = _PyTango.DeviceProxy( motorArr[0]['name'])
            p1 = _PyTango.DeviceProxy( motorArr[1]['name'])
            p2 = _PyTango.DeviceProxy( motorArr[2]['name'])
            msg = "Move\n  %s from %g to %g\n  %s from %g to %g\n  %s from %g to %g " % \
                  (motorArr[0]['name'], p0.read_attribute( 'Position').value, motorArr[0]['targetPos'],
                   motorArr[1]['name'], p1.read_attribute( 'Position').value, motorArr[1]['targetPos'],
                   motorArr[2]['name'], p2.read_attribute( 'Position').value, motorArr[2]['targetPos'])
            reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No)

        if not reply == _QtGui.QMessageBox.Yes:
            Scan.monitorGui.logWidget.append( "Move: move not confirmed")
            return

        if Scan.monitorGui.scanInfo['title'].find( "hklscan") == 0:
            Scan.monitorGui.logWidget.append( "br %g %g %g" % (motorArr[0]['targetPos'],motorArr[1]['targetPos'],motorArr[2]['targetPos']))
            Scan.monitorGui.door.RunMacro( ["br",  
                                 "%g" %  motorArr[0]['targetPos'], 
                                 "%g" %  motorArr[1]['targetPos'], 
                                 "%g" %  motorArr[2]['targetPos']])
        else:
            lst = [ "umv"]
            for hsh in motorArr:
                lst.append( "%s" % (hsh['name']))
                lst.append( "%g" % (hsh['targetPos']))
                Scan.monitorGui.logWidget.append( "%s to %g" % (hsh['name'], hsh['targetPos']))
            Scan.monitorGui.door.RunMacro( lst)
        return 

    #
    # called from pyspMonitorClass, if scanInfo is received
    #
    @staticmethod
    def setMonitorGui( monitorGui): 
        Scan.monitorGui = monitorGui
    
    def _createScanFromData( self, kwargs):
        '''
        creates a scan using x, y
        '''

        if 'y' not in kwargs:
            raise ValueError( "GQE.Scan._createScanFromData: 'y' not supplied")

        self.x = _np.copy( kwargs[ 'x'])
        del kwargs[ 'x']
        self.y = _np.copy( kwargs[ 'y'])
        del kwargs[ 'y']
        if len( self.x) != len( self.y):
            raise ValueError( "GQE.Scan._createScanFromData: 'x' and 'y' differ in length %d (x) %d (y)" % (len( self.x), len( self.y)))

        if len( self.x) == 0:
            raise ValueError( "GQE.Scan._createScanFromData: %s len(x) == 0" % (self.name))

        self.setLimits()

        self.dType = type( self.x[0])

        self.nPts = len( self.x)
        self.lastIndex = 0
        self.currentIndex = self.nPts - 1

        return

    def _createScanFromLimits( self, kwargs):
        '''
        creates a scan using 
        xMin, def.: 0.
        xMax, def.: 10.
        nPts, def.: 101
        dType, def.: np.float64

        yMin, def.: None
        yMax, def.: None
          if yMin is None, autoscale will be enabled for y
        '''
        #
        # 
        #
        self.xMin = 0.
        self.xMax = 10.
        self.yMin = None
        self.yMax = None
        self.nPts = 101
 
        for attr in ['xMin', 'xMax', 'yMin', 'yMax']:
            if attr in kwargs:
                setattr( self, attr, float(kwargs[ attr]))
                del kwargs[ attr]

        for attr in ['nPts']:
            if attr in kwargs:
                setattr( self, attr, int( kwargs[ attr]))
                del kwargs[ attr]

        if 'dType' not in kwargs:
            self.dType = _np.float64
        else:
            self.dType = kwargs[ 'dType']
            del kwargs[ 'dType']
        #
        # the 1.8 version of linspace does not allow to specify the dType
        # 
        self.x = _np.linspace( self.xMin, self.xMax, self.nPts)
        if self.x.dtype != self.dType:
            self.x = _np.astype( self.dType)
        self.y = _np.linspace( self.xMin, self.xMax, self.nPts)
        if self.y.dtype != self.dType:
            self.y = _np.astype( self.dType)

        if self.yMin is None:
            self.yMin = self.xMin
        if self.yMax is None:
            self.yMax = self.xMax
        #
        # the currentIndex points to the last valid point.
        # it starts at 0.
        #
        self.lastIndex = 0
        self.currentIndex = self.nPts - 1
            
        return

    def setAttr( self, kwargs):
        '''
        set the graphics attributes of a scan, see docu in Scan()

        Returns None
        '''

        self.at = None
        self.autoscaleX = True
        self.autoscaleY = True
        self.colSpan = 1
        self.doty = False            # x-axis is date-of-the year
        self.fileName = None
        self.flagDisplayVLines = False
        self.nrow = None
        self.ncol = None
        self.nplot = None
        self.overlay = None
        self.overlayUseTargetWindow = False
        self.plotItem = None
        self.plotDataItem = None
        self.scene = None
        self.viewBox = None
        self.showGridX = False
        self.showGridY = False
        self.lineColor = 'red'
        self.lineStyle = 'SOLID'
        self.lineWidth = 1.
        self.logWidget = None
        self.motorList = None
        self.mouseProxy = None
        self.mouseClick = None
        self.symbol = 'o'
        self.symbolColor = 'NONE'
        self.symbolSize = 10
        self.viewBox = None
        self.xLabel = None
        self.yLabel = None
        self.xLog = False
        self.yLog = False
        self.yTicksVisible = True
        #
        # the attributes plot and mouseLabel are created by graphics.display(). 
        # However, it is initialized here to help cls()
        #
        self.plotItem = None
        self.mouseLabel = None
        self.mouseProxy = None

        for attr in [ 'autoscaleX', 'autoscaleY', 'colSpan', 'doty', 'fileName',  
                      'xLog', 'yLog', 'logWidget', 'motorList', 
                      'ncol', 'nrow', 'nplot', 'overlay', 'showGridX', 'showGridY', 
                      'lineColor', 'lineStyle', 
                      'symbol', 'symbolColor', 'symbolSize', 
                      'xLabel', 'yLabel', 'yMin', 'yMax']:
            if attr in kwargs:
                setattr( self, attr, kwargs[ attr])
                del kwargs[ attr]
        #
        # be friendly: 'color' translates to 'lineColor'
        #
        if 'color' in kwargs: 
            self.lineColor = kwargs[ 'color']
            del kwargs[ 'color']

        attr = 'lineWidth'
        if attr in kwargs:
            if str(kwargs[ attr]) in _pysp.definitions.lineWidthArr:
                setattr( self, attr, float( kwargs[ attr]))
            else: 
                setattr( self, attr, 1.0)
            del kwargs[ attr]

        #
        # if at is None, graphics.display() makes a guess
        #
        if 'at' in kwargs: 
            atStr = kwargs[ 'at']
            del kwargs[ 'at']
            #
            # the string '(2, 3, 4)' -> list of ints [1, 2, 3]
            #
            if type( atStr) is tuple:
                self.at = list( atStr)
            elif type( atStr) is list:
                self.at = list( atStr)
            else:
                lstStr = atStr.strip()[1:-1].split( ',')
                if len( lstStr) != 3:
                    self.at = [1, 1, 1]
                else:
                    self.at = [int( i) for i in lstStr]
            for scan in _scanList: 
                if scan is self:
                    continue
                if self.at is None or scan.at is None: 
                    continue
                if self.at[0] == scan.at[0] and \
                   self.at[1] == scan.at[1] and \
                   self.at[2] == scan.at[2]:
                    raise ValueError( "GQE.Scan.setAttr: %s is already at %s %s" % 
                                      (scan.name, str( self.at), self.name))
        return 

    def setLimits( self): 
        '''
        use x and y to calculate xMin, xMax, yMin and yMax
        '''
        if len( self.x) == 0:
            raise ValueError( "GQE.Scan.setLimits: %s len(x) == 0" % (self.name))
        if len( self.y) == 0:
            raise ValueError( "GQE.Scan.setLimits: %s len(y) == 0" % (self.name))
        self.xMin = _np.min( self.x)
        self.xMax = _np.max( self.x)
        self.yMin = _np.min( self.y)
        self.yMax = _np.max( self.y)
        self.yMax += (self.yMax - self.yMin)*0.05
        return 

    def addText( self, text = 'Empty', x = 0.5, y = 0.5, 
                 hAlign = 'left', vAlign = 'top', 
                 color = 'black', fontSize = None, NDC = True):
        '''
        Docu can found in Text()
        '''
        txt = Text( text, x, y, hAlign, vAlign, color, fontSize, NDC)
        self.textList.append( txt)

    def setY( self, index, yValue):
        '''
        Sets a y-value of the scan

        The currentIndex, which is used for display, is set to index. 

        Parameters:
        -----------
        index: int
          The index of the first point is 0
        yValue: float
          the y-value
        '''
        if index >= self.y.size:
            raise ValueError( "GQE.Scan.setY: %s, index %d out of range [0, %d]" % 
                              ( self.name, index, self.y.size - 1))
        self.y[ index] = yValue
        self.currentIndex = index
        return

    def setX( self, index, xValue):
        '''
        Sets a x-value of the scan

        The currentIndex, which is used for display, is set to index. 

        Parameters:
        -----------
        index: int
          The index of the first point is 0
        xValue: float
          the x-value
        '''
        if index >= self.y.size:
            raise ValueError( "GQE.Scan.setX: %s, index %d out of range [0, %d]" % 
                              ( self.name, index, self.x.size - 1))
        self.x[ index] = xValue
        self.currentIndex = index
        return

    def getX( self, index):
        '''
        Gets a x-value of the scan

        Parameters:
        -----------
        index: int
          The index of the first point is 0
        '''
        if index >= self.y.size:
            raise ValueError( "GQE.Scan.getX: %s, index %d out of range [0, %d]" % 
                              ( self.name, index, self.x.size))
        return self.x[ index] 

    def getY( self, index):
        '''
        Gets a y-value of the scan

        Parameters:
        -----------
        index: int
          The index of the first point is 0
        '''
        if index >= self.y.size:
            raise ValueError( "GQE.Scan.getY: %s, index %d out of range [0, %d]" % 
                              ( self.name, index, self.y.size))
        return self.y[ index] 

    def setXY( self, index, xValue, yValue):
        '''
        Sets the x- and y-value at index

        The currentIndex, which is used for display, is set to index. 

        Parameters:
        -----------
        index: int
          The index of the first point is 0
        xValue: float
          the x-value
        yValue: float
          the y-value
        '''
        if index >= self.y.size:
            raise ValueError( "GQE.Scan.setX: %s, index %d out of range [0, %d]" % 
                              ( self.name, index, self.x.size))
        self.x[ index] = xValue
        self.y[ index] = yValue
        self.currentIndex = index
        return

    def sort( self): 
        '''
        put this functions in because it is in Spectra, I don't know
        whether we really need it in pysp. reserve scans do not make 
        any problems in pyqtgraph. however, in matplotlib it plots
        from the wrong direction.
        '''
        pass

    def setCurrent( self, i): 
        '''
        be compatible with spectra
        '''
        self.currentIndex = i
        return 

    def autoscale( self): 
        '''
        be compatible with spectra
        '''
        pass

    def display( self): 
        _pysp.display()
        return 

    def yGreaterThanZero( self): 
        '''
        prepare for log display: remove points with y <= 0. 
        '''
        x = _np.copy( self.x)
        y = _np.copy( self.y)
        count = 0
        for i in range( len( self.y)):
            if self.y[i] <= 0.:
                continue
            x[count] = self.x[i]
            y[count] = self.y[i]
            count += 1
        self.x = _np.copy( x[:count])
        self.y = _np.copy( y[:count])
        return 

    def ssa( self, logWidget = None):
        '''
        simple scan analysis interface, called from e.g. PySpectraGuiClass.
        the x-range may be determined by the VLines. Otherwise the whole
        x-range is taken.
        '''
        lstX = []
        lstY = []

        if self.flagDisplayVLines: 
            xi = self.infLineLeft.getPos()[0]
            xa = self.infLineRight.getPos()[0]
            if xa < xi: 
                temp = xa
                xa = xi
                xi = temp
            for i in range( self.currentIndex + 1):
                #
                # sorted normally
                #
                if self.x[i] >= xi and self.x[i] <= xa: 
                    lstX.append( self.x[i])
                    lstY.append( self.y[i])
            logWidget.append( "ssa: %s limits: %g, %g" % (self.name, xi, xa))
        else: 
            lstX = self.x[:self.currentIndex]
            lstY = self.y[:self.currentIndex]
            logWidget.append( "ssa: %s total x-range" % (self.name))
        #
        # reversed x-values?
        #
        if lstX[0] > lstX[-1]:
            lstX = list( reversed( lstX))
            lstY = list( reversed( lstY))
                
        hsh = _pysp.ssa( _np.array( lstX), _np.array( lstY))

        if hsh[ 'status'] != 1:
            if logWidget is not None:
                logWidget.append( "cb_ssa: ssa failed, reason: %s" % hsh[ 'reasonString'])
            return

        if logWidget is not None: 
            logWidget.append( " midpoint: %g" % hsh[ 'midpoint'])
            logWidget.append( " peak-x:   %g" % hsh[ 'peak_x'])
            logWidget.append( " cms:      %g" % hsh[ 'cms'])
            logWidget.append( " fwhm:     %g" % hsh[ 'fwhm'])
            logWidget.append( " integral: %g" % hsh[ 'integral'])

        self.addText( text = "midpoint: %g" % hsh[ 'midpoint'], x = 0.05, y = 0.95, hAlign = 'left', vAlign = 'top')
        self.addText( text = "peak-x:   %g" % hsh[ 'peak_x'], x = 0.05, y = 0.88, hAlign = 'left', vAlign = 'top')
        self.addText( text = "cms:      %g" % hsh[ 'cms'], x = 0.05, y = 0.81, hAlign = 'left', vAlign = 'top')
        self.addText( text = "fwhm:     %g" % hsh[ 'fwhm'], x = 0.05, y = 0.74, hAlign = 'left', vAlign = 'top')

        ssaName = '%s_ssa' % self.name
        count = 1
        while getScan( ssaName): 
            ssaName = '%s_ssa_%-d' % (self.name, count)
            count += 1
            
        res = Scan( name = ssaName, x = self.x[:self.currentIndex], y = self.y[:self.currentIndex],
                    lineColor = 'None', 
                    symbolColor = 'blue', symbolSize = 5, symbol = '+')

        a = hsh[ 'integral']
        mu = hsh[ 'midpoint'] 
        sigma = hsh[ 'fwhm']/2.3548
        
        res.y = a/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(res.x-mu)**2/(2*sigma**2))
        res.overlay = self.name
        res.overlayUseTargetWindow = True
        return 

def getScanList():
    '''
    returns the list of scans
    '''
    return _scanList

def _getDisplayList(): 
    '''
    returns a list of scans which are currently displayed
    '''

    argout = []
    for scan in _scanList: 
        if scan.plotItem is not None:
            argout.append( scan)

    return argout

def getScan( name):
    '''
    return the scan object with obj.name == name, 
    otherwise return None
    '''
    for scan in _scanList:
        if str( name).upper() == scan.name.upper():
            return scan
    return None

def setTitle( text = None): 
    '''
    the title appears across all columns

    the title is cleared, if no argument is supplied
    delete() also clears the title
    '''
    global _title 
    if text is None:
        _title = None
        return 
    text = text.replace( "'", "")
    text = text.replace( '"', '')
    _title = text
    return 

def getTitle():
    return _title

def setComment( text = None): 
    '''
    the comment line appears across all columns below the title

    the comment is cleared, if no argument is supplied
    delete() also clears the comment
    '''
    global _comment 
    if text is None:
        _comment = None
        return 
    text = text.replace( "'", "")
    text = text.replace( '"', '')

    _comment = text
    return 

def getComment():
    return _comment

def delete( nameLst = None):
    '''
    if nameLst is supplied, delete the specified scans from the scanList
    otherwise delete all scans

    PySpectra.delete( ["t1"])
      delete the scan t1

    PySpectra.delete( ["t1", "t2"])
      delete t1 and t2

    PySpectra.delete( "t1")
      delete the scan t1, also OK

    PySpectra.delete()
      delete all scans
    '''
    global _scanIndex

    #print "GQE.delete, nameList:", repr( nameLst)
    
    if not nameLst:    
        while len( _scanList) > 0:
            tmp = _scanList.pop()
            if tmp.plotItem is not None:
                #
                # clear.__doc__: 'Remove all items from the ViewBox'
                #
                _pysp.clear( tmp)
                #tmp.plotItem.clear()
            _scanIndex = None
        setTitle( None)
        setComment( None)
        return 

    if type( nameLst) is not list:
        name = nameLst
        for i in range( len( _scanList)):
            if name.upper() == _scanList[i].name.upper():
                #
                # we had many MCA spectra displayed on top of each other
                #
                if _scanList[i].plotItem is not None:
                    _pysp.clear( _scanList[i])
                    #_scanList[i].plotItem.clear()
                del _scanList[i]
                break
        else:
            raise ValueError( "GQE.delete: not found %s" % name)
        return 

    for name in nameLst:
        for i in range( len( _scanList)):
            if name.upper() == _scanList[i].name.upper():
                #
                # we had many MCA spectra displayed on top of each other
                #
                if _scanList[i].plotItem is not None:
                    #
                    # clear.__doc__: 'Remove all items from the ViewBox'
                    #
                    _pysp.clear( _scanList[i])
                    #_scanList[i].plotItem.clear()
                del _scanList[i]
                break
        else:
            print "GQE.delete: not found", name
    return 

def overlay( src, trgt):
    '''
    the scan src is displayed in the viewport of trgt
    the window limits are defined by trgt

    Parameters
    ----------
    src:  string
          the name of the scan to be displayed in the viewport of trgt
    trgt: string
          
    Return
    ------
    None

    Module: PySpectra.dMgt.GQE.py
    '''
    scanSrc = getScan( src)
    scanTrgt = getScan( trgt)
    scanSrc.overlay = scanTrgt.name
    return 
    
def info( scanList = None):
    '''
    prints some information about scans in scanList.
    if scanList is not supplied, info is displayed for all scans
    '''

    if scanList is not None:
        if type(scanList) is not list:
            scan = getScan( scanList)
            _infoScan( scan)
            return 

        for scn in scanList:
            scan = getScan( scn)
            _infoScan( scan)
        return 

    if _scanList:
        print "The List of Scans:"
        for scan in _scanList:
            _infoScan( scan)
        print "\n--- %s scans" % len( _scanList)
    else: 
        print "scan list is empty"

    if _title: 
        print "Title:  ", _title
    if _comment: 
        print "Comment:", _comment

def _displayTextList( scan): 
    for text in scan.textList:
        print "  text:", text.text
        print "    x: %g, y: %g" % (text.x, text.y)
        print "    hAlign: %s, vAlign: %s" % ( str(text.hAlign), str(text.vAlign))
        print "    color: %s" % str( text.color)
    return 

def _infoScan( scan): 
    '''
    
    '''
    if scan.textOnly: 
        print "--- GQE._infoScan \n", scan.name, "(textOnly)"
        _displayTextList( scan)
        return 
    #
    # create a local copy of ScanAttrs to delete elements which
    # are already shown
    #
    scanAttrsPrinted = []
    print "--- \n", scan.name
    scanAttrsPrinted.append( 'name')
    print "  currentIndex: %d, lastIndex: %d, Pts: %d" % (scan.currentIndex, scan.lastIndex, scan.nPts)
    scanAttrsPrinted.append( 'currentIndex')
    scanAttrsPrinted.append( 'lastIndex')
    scanAttrsPrinted.append( 'nPts')
    print "  nrow: %s, ncol: %s, nplot: %s" % ( str(scan.nrow), str(scan.ncol), str(scan.nplot))
    scanAttrsPrinted.append( 'nrow')
    scanAttrsPrinted.append( 'ncol')
    scanAttrsPrinted.append( 'nplot')
    print "  showGridX: %s, showGridY: %s" % ( str(scan.showGridX), str(scan.showGridY))
    scanAttrsPrinted.append( 'showGridX')
    scanAttrsPrinted.append( 'showGridY')
    print "  xMin: %s, xMax: %s" % ( str(scan.xMin), str(scan.xMax))
    scanAttrsPrinted.append( 'xMin')
    scanAttrsPrinted.append( 'xMax')
    print "  yMin: %s, yMax: %s" % ( str(scan.yMin), str(scan.yMax))
    scanAttrsPrinted.append( 'yMin')
    scanAttrsPrinted.append( 'yMax')
    print "  xLabel: %s, yLabel: %s" % ( str(scan.xLabel), str(scan.yLabel))
    scanAttrsPrinted.append( 'xLabel')
    scanAttrsPrinted.append( 'yLabel')
    print "  autoscaleX: %s, autoscaleY: %s" % ( str(scan.autoscaleX), str(scan.autoscaleY))
    scanAttrsPrinted.append( 'autoscaleX')
    scanAttrsPrinted.append( 'autoscaleY')
    print "  at: %s, colSpan: %s" % ( str(scan.at), str(scan.colSpan))
    scanAttrsPrinted.append( 'at')
    scanAttrsPrinted.append( 'colSpan')
    print "  lineColor: %s, lineWidth: %s, lineStyle: %s" % ( str(scan.lineColor), str(scan.lineWidth), str( scan.lineStyle))
    scanAttrsPrinted.append( 'lineColor')
    scanAttrsPrinted.append( 'lineWidth')
    scanAttrsPrinted.append( 'lineStyle')
    print "  symbolColor: %s, symbolWidth: %s, symbol: %s" % ( str(scan.symbolColor), str(scan.symbolSize), str( scan.symbol))
    scanAttrsPrinted.append( 'symbolColor')
    scanAttrsPrinted.append( 'symbolSize')
    scanAttrsPrinted.append( 'symbol')

    for attr in _ScanAttrsPublic:
        if attr in scanAttrsPrinted: 
            continue
        if attr == 'x' or attr == 'y':
            if len( getattr( scan, attr)) <= 10: 
                print "  %s: %s" % ( attr, repr( getattr( scan, attr)))
            else:
                print "  %s[:10]: %s" % ( attr, repr( getattr( scan, attr)[:10]))
            continue
        try:
            print "  %s: %s" % ( attr, repr( getattr( scan, attr)))
        except Exception, e:
            print "GQE._showScan: trouble with", scan.name
            print repr( e)

    if len( scan.textList) > 0:
        _displayTextList( scan)

    return 

def show(): 
    '''
    lists all scans, one line per scan
    '''
    if _scanList is None: 
        print "scan list is empty"

    print "The List of Scans:"
    for scan in _scanList:
        print "%s, nPts %d, xMin %g, xMax %g" % (scan.name, scan.nPts, scan.xMin, scan.xMax)

def _nextScan( name = None):
    '''
    nextScan/prevScan return the next/previous scan object
    '''
    global _scanIndex

    if len( _scanList) == 0:
        raise ValueError( "GQE._nextScan: scan list empty")

    if name is not None:
        for i in range( len(_scanList)): 
            if _scanList[i].name == name:
                _scanIndex = i + 1
                break
    else:
        if _scanIndex is None:
            _scanIndex = 0
        else:
            _scanIndex += 1
        
    if _scanIndex >= len( _scanList) :
        _scanIndex = 0

    return _scanList[ _scanIndex]

def _prevScan( name = None):
    '''
    nextScan/prevScan return the next/previous scan object
    '''
    global _scanIndex

    if len( _scanList) == 0:
        raise ValueError( "GQE._prevScan: scan list empty")

    if name is not None:
        for i in range( len(_scanList)): 
            if _scanList[i].name == name:
                _scanIndex = i + 1
                break
    else:
        if _scanIndex is None:
            _scanIndex = 0
        else:
            _scanIndex -= 1

    if _scanIndex < 0:
        _scanIndex = len( _scanList) - 1

    if _scanIndex >= len( _scanList):
        _scanIndex = 0

    return _scanList[ _scanIndex]

def _getIndex( name): 
    '''
    returns the position of a scan in the scanList, 
    the first index is 0.
    '''
    index = 0
    for scan in _scanList:
        if scan.name == name:
            return index
        index += 1
    raise ValueError( "GQE._getIndex: not found %s" % name)
    
def read( fileName, x = 1, y = None, flagMCA = False):
    '''    
    if y is None: 
      read all columns from a file
      creating many scans
      return None
    otherwise: 
      return a fioColumn object
    
     'x' and 'y' correspond to the column numbers in the .fio files
     assume that a file contains 25 columns, the first column contains
     the x-values and len( fioObj.columns) == 24. A scan containing data 
     from the last column is then specified by Scan( ..., x = 1, y = 25)

    Supported extensions: .fio, .dat, iint

    if flagMCA, the input file contains MCA data, no x-axis
    '''
    #print "+++GQE.read: %s, x %s, y %s, flagMCA %s" % ( fileName, repr( x), repr( y), repr( flagMCA))
    #
    # fioReader may throw an exception, e.g. if the file does not exist.
    # Do not catch it here, leave it to the application
    #
    import HasyUtils as _HasyUtils
    fioObj = _HasyUtils.fioReader( fileName, flagMCA)

    if y is not None:
        if y > (len( fioObj.columns) + 1): 
            raise ValueError( "GQE.read: %s, y: %d > (len( columns) + 1): %d" % ( fileName, y, len( fioObj.columns)))
        return fioObj.columns[ y - 2]

    for elm in fioObj.columns:
        scn =  Scan( name = elm.name, x = elm.x, y = elm.y, fileName = fileName)

    return None
    
def write( lst = None): 
    '''
    write the specified scans or all scans to a .fio file. 
    the prefix is pysp

    PySpectra.write()
      write all scans

    PySpectra.write( [ 's1', 's2'])
      write selected scans
    '''
    import HasyUtils as _HasyUtils
    if len(_scanList) == 0: 
        raise ValueError( "GQE.write: scan list is empty")

    #
    # check if all scans have the same length
    #
    length = None
    for scan in _scanList:
        if scan.textOnly: 
            continue
        if lst is not None:
            if scan.name not in lst:
                continue
        if length is None:
            length = len( scan.x)
            continue
        if length != len( scan.x):
            raise ValueError( "GQE.write: wrong length %s" % scan.name)
    
    obj = _HasyUtils.fioObj( namePrefix = "pysp")
    for scan in _scanList:
        if scan.textOnly: 
            continue
        if lst is not None:
            if scan.name not in lst:
                continue
        col = _HasyUtils.fioColumn( scan.name)
        col.x = scan.x
        col.y = scan.y
        obj.columns.append( col)
    fileName = obj.write()
    print "created", fileName
    return fileName
    
def getNumberOfScansToBeDisplayed( nameList): 
    '''
    return the number of scans to be displayed.
    Scans that are overlaid do not require extra space
    and are therefore not counted.
    '''
    if len( nameList) == 0:
        nOverlay = 0
        for scan in _scanList:
            if scan.overlay is not None:
                nOverlay += 1
        nScan = len( _scanList) - nOverlay
        if nScan < 1:
            nScan = 1
    else:
        nOverlay = 0
        for name in nameList:
            if getScan( name).overlay is not None:
                nOverlay += 1
        nScan = len( nameList) - nOverlay
        if nScan < 1:
            nScan = 1
    #print "graphics.getNoOfScansToBeDisplayed: nScan %d" %(nScan)
    return nScan

def _getNumberOfOverlaid( nameList = None):
    '''
    returns the number of scans which are overlaid to another, 
    used by e.g. graphics.display()
    '''
    count = 0
    for scan in _scanList:
        if nameList is not None: 
            if scan.name not in nameList:
                continue
        if scan.overlay is not None:
            count += 1

    return count
    
def setWsViewportFixed( flag):
    '''
    flag: True or False
    
    if True, the wsViewport is not changed automatically 
             to take many scans into account
    '''
    global _wsViewportFixed 
    _wsViewportFixed = flag
    return 
    
def getWsViewportFixed():
    return _wsViewportFixed 

def _isArrayLike( x): 
    '''    
    returns True, if y is a list or a numpy array
    '''
    if type(x) is list or type(x) is _np.ndarray:
        return True
    else:
        return False

def getFontSize( nameList): 
    '''
    depending on how many scans are displayed the font size is adjusted
    '''
    if getNumberOfScansToBeDisplayed( nameList) < _pysp.definitions.MANY_SCANS:
        fontSize = _pysp.definitions.FONT_SIZE_NORMAL
    elif getNumberOfScansToBeDisplayed( nameList) <= _pysp.definitions.VERY_MANY_SCANS:
        fontSize = _pysp.definitions.FONT_SIZE_SMALL
    else: 
        fontSize = _pysp.definitions.FONT_SIZE_VERY_SMALL

    return fontSize

def getTickFontSize( nameList): 
    '''
    depending on how many scans are displayed the font size is adjusted
    '''
    if getNumberOfScansToBeDisplayed( nameList) < _pysp.definitions.MANY_SCANS:
        fontSize = _pysp.definitions.TICK_FONT_SIZE_NORMAL
    elif getNumberOfScansToBeDisplayed( nameList) <= _pysp.definitions.VERY_MANY_SCANS:
        fontSize = _pysp.definitions.TICK_FONT_SIZE_SMALL
    else: 
        fontSize = _pysp.definitions.TICK_FONT_SIZE_VERY_SMALL

    print "GQE.getTickFontSize", fontSize
    return fontSize

