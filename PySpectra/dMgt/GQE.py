#!/bin/env python
'''
GQE - contains the Scan() class and functions to handle scans: 
      delete(), getGqe(), getGqeList(), info(), overlay(), show()
'''
# 1.8.2

import numpy as _np
import PySpectra as _pysp
from PyQt4 import QtCore as _QtCore
from PyQt4 import QtGui as _QtGui
import math as _math
import HasyUtils

_gqeList = []
_gqeIndex = None  # used by next/back
_title = None
_comment = None
#
# if the wsViewport is set, e.g. to dina4, it is fixed, i.e. independent 
# of how many scans are displayed 
#
_wsViewportFixed = False

_ScanAttrsPublic = [ 'at', 'autoscaleX', 'autoscaleY', 'colSpan', 'currentIndex', 
                     'dType', 'doty', 'fileName', 
                     'flagDisplayVLines', 'flagMCA', 
                     'lastIndex', 
                     'nPts', 'name', 'ncol', 'nplot', 'nrow', 'overlay', 'useTargetWindow', 
                     'showGridX', 'showGridY', 
                     'lineColor', 'lineStyle', 'lineWidth', 
                     'logWidget', 'motorList', 
                     'symbol', 'symbolColor', 'symbolSize', 
                     'textList', 'textOnly', 'viewBox', 
                     'x', 'xLog', 'xMax', 'xMin', 
                     'xLabel', 'y', 'yLabel', 'yLog', 'yMin', 'yMax',
                     'yTicksVisible'] 

_ScanAttrsPrivate = [ 'infLineLeft', 'infLineRight', 'mouseClick', 'mouseLabel', 'mouseProxy', 
                      'plotItem', 'plotDataItem', 'scene', 'xDateMpl']

_MeshAttrsPublic = [ 'at', 'colSpan', 'data', 'log', 'logWidget', 
                     'name', 'ncol', 'nplot', 'nrow', 'overlay', 'xMin', 'xMax',
                     'yMin', 'yMax', 'width', 'height', 'viewBox', 'xLabel', 'yLabel']

_MeshAttrsPrivate = [ 'img', 'plotItem', 'mouseClick', 'mouseLabel', 'mouseProxy']

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
    tag = 'n.n.', e.g. 'ssa_result'
    '''
    def __init__( self, text = 'Empty', x = 0.5, y = 0.5, 
                  hAlign = 'left', vAlign = 'top', color = 'black', fontSize = None,
                  NDC = True, tag = 'n.n.'): 

        self.text = text
        self.x = x
        self.y = y
        self.hAlign = hAlign
        self.vAlign = vAlign
        self.color = color
        self.fontSize = fontSize
        self.NDC = NDC
        self.tag = tag
'''
A value of (0,0) sets the upper-left corner
                     of the text box to be at the position specified by setPos(), while a value of (1,1)
                     sets the lower-right corner.        
'''

class GQE( object): 
    monitorGui = None

    def __init__( self):
        pass
    #
    # called from pyspMonitorClass, if scanInfo is received
    #
    @staticmethod
    def setMonitorGui( monitorGui): 
        GQE.monitorGui = monitorGui
        return 


class Scan( GQE):
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
        flagIsMCA   data from MCA, don't use for movements
    '''
    #
    # this class variable stores the Gui, needed to configure the motorsWidget, 
    # which happens for each new scan
    #
    def __init__( self, name = None, **kwargs):
        global _gqeList

        #print "GQE.Scan: ", repr( kwargs)
        super( Scan, self).__init__()
        if name is None:
            raise ValueError( "GQE.Scan: 'name' is missing")
        #
        #
        #
        self.textOnly = False
        #
        # We 'reUse' e.g. MCA scans
        #
        for i in range( len( _gqeList)): 
            if name == _gqeList[i].name:
                if 'reUse' in kwargs: 
                    if len( _gqeList[i].x) != len( kwargs['x']):
                        raise ValueError( "GQE.Scan: len( scan.x) %d != len( kwargs[ 'x']) %d" % \
                                          ( len( _gqeList[i].x), len( kwargs['x'])))
                    if len( _gqeList[i].y) != len( kwargs['y']):
                        raise ValueError( "GQE.Scan: len( scan.y) %d != len( kwargs[ 'y']) %d" % \
                                          ( len( _gqeList[i].y), len( kwargs['y'])))
                    _gqeList[i].x = kwargs['x']
                    _gqeList[i].y = kwargs['y']
                    _gqeList[i].lastIndex = 0
                    return
                else:
                    raise ValueError( "GQE.Scan.__init__(): %s exists already" % name)
        if 'reUse' in kwargs:
            del kwargs[ 'reUse'] 
            
        self.name = name
        if 'x' in kwargs and 'y' not in kwargs or \
           'x' not in kwargs and 'y' in kwargs:
            raise ValueError( "GQE.Scan.__init__(): if 'x' or 'y' then both have to be supplied")
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
        #  scan = PySpectra.Scan( name = 't1', fileName = "fName.fio", x = 1, y = 2)
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
            raise ValueError( "GQE.Scan.__init__(): dct not empty %s" % str( kwargs))
        
        self.textList = []

        _gqeList.append( self)

    def __setattr__( self, name, value): 
        #print "GQE.Scan.__setattr__: name %s, value %s" % (name, value)
        if name in _ScanAttrsPublic or \
           name in _ScanAttrsPrivate: 
            super(Scan, self).__setattr__(name, value)
        else: 
            raise ValueError( "GQE.Scan.__setattr__: %s unknown attribute %s" % ( self.name, name))

    def __getattr__( self, name): 
        raise ValueError( "GQE.Scan.__getattr__: %s unknown attribute %s" % ( self.name, name))
        #if name in _ScanAttrsPublic or \
        #   name in _ScanAttrsPrivate: 
        #    return super(Scan, self).__getattr__(name)
        #else: 
        #    raise ValueError( "GQE.Scan.__getattr__: Scan %s unknown attribute name %s" % ( self.name, name))
        
    def __del__( self): 
        pass

    #@staticmethod
    #
    # why do we need a class function for move()
    #
    def move( self, target): 
        '''
        this function is invoked by a mouse click from pqtgrph/graphics.py
        '''
        import PyTango as _PyTango
        import time as _time


        if GQE.monitorGui is None:
            if self.logWidget is not None:
                self.logWidget.append( "GQE.Scan.move: not called from pyspMonitor") 
            else:
                print "GQE.Scan.move: not called from pyspMonitor"
            return 

        #
        # don't use MCA data to move motors
        #
        if self.flagMCA:
            GQE.monitorGui.logWidget.append( "GQE.Scan.move: don't use MCAs to move motors") 
            return 

        #print "GQE.Scan.move: to", target, "using", GQE.monitorGui.scanInfo

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
        if GQE.monitorGui is None or GQE.monitorGui.scanInfo is None: 
            return

        motorArr = GQE.monitorGui.scanInfo['motors']        
        length = len( motorArr)
        if  length == 0 or length > 3:
            _QtGui.QMessageBox.about( None, 'Info Box', "no. of motors == 0 or > 3") 
            return

        motorIndex = GQE.monitorGui.scanInfo['motorIndex']

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
            GQE.monitorGui.logWidget.append( "Move: move not confirmed")
            return

        if GQE.monitorGui.scanInfo['title'].find( "hklscan") == 0:
            GQE.monitorGui.logWidget.append( "br %g %g %g" % (motorArr[0]['targetPos'],motorArr[1]['targetPos'],motorArr[2]['targetPos']))
            GQE.monitorGui.door.RunMacro( ["br",  
                                 "%g" %  motorArr[0]['targetPos'], 
                                 "%g" %  motorArr[1]['targetPos'], 
                                 "%g" %  motorArr[2]['targetPos']])
        else:
            lst = [ "umv"]
            for hsh in motorArr:
                lst.append( "%s" % (hsh['name']))
                lst.append( "%g" % (hsh['targetPos']))
                GQE.monitorGui.logWidget.append( "%s to %g" % (hsh['name'], hsh['targetPos']))
            GQE.monitorGui.door.RunMacro( lst)
        return 

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
        self.useTargetWindow = False
        self.flagMCA = False
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
                      'flagMCA', 
                      'xLog', 'yLog', 'logWidget', 'motorList', 
                      'ncol', 'nrow', 'nplot', 'overlay', 'showGridX', 'showGridY', 
                      'lineColor', 'lineStyle', 
                      'symbol', 'symbolColor', 'symbolSize', 
                      'xLabel', 'xMin', 'xMax', 'yLabel', 'yMin', 'yMax']:
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
            if int(self.at[0]) * int(self.at[1]) < int( self.at[2]):
                raise ValueError( "GQE.Scan.setAttr: %s, 'at(%s,%s,%s)' is wrong, nplot > nrow*ncol" % 
                                  (self.name, self.at[0], self.at[1], self.at[2]))
                
            for scan in _gqeList: 
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
                 color = 'black', fontSize = None, NDC = True, tag = 'n.n.'):
        '''
        Docu can found in Text()
        '''
        txt = Text( text, x, y, hAlign, vAlign, color, fontSize, NDC, tag)
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
            raise ValueError( "GQE.Scan.setXY: %s, index %d out of range [0, %d]" % 
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
            if logWidget is not None:
                logWidget.append( "ssa: %s limits: %g, %g" % (self.name, xi, xa))
        else: 
            lstX = self.x[:self.currentIndex]
            lstY = self.y[:self.currentIndex]
            if logWidget is not None:
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

        #
        # clear the text list. Otherwise several SSA results will appear on the screen.
        #
        if len( self.textList) > 0:
            lst = []
            for t in self.textList:
                if t.tag.lower() == 'ssa_result':
                    continue
                lst.append( t)
            self.textList = lst[:]
        
        self.addText( text = "midpoint: %g" % hsh[ 'midpoint'], x = 0.02, y = 0.95, hAlign = 'left', vAlign = 'top', tag = 'ssa_result')
        self.addText( text = "peak-x:   %g" % hsh[ 'peak_x'], x = 0.02, y = 0.90, hAlign = 'left', vAlign = 'top', tag = 'ssa_result')
        self.addText( text = "cms:      %g" % hsh[ 'cms'], x = 0.02, y = 0.85, hAlign = 'left', vAlign = 'top', tag = 'ssa_result')
        self.addText( text = "fwhm:     %g" % hsh[ 'fwhm'], x = 0.02, y = 0.80, hAlign = 'left', vAlign = 'top', tag = 'ssa_result')

        ssaName = '%s_ssa' % self.name
        count = 1
        while getGqe( ssaName): 
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
        res.useTargetWindow = True
        return 

    def fsa( self, logWidget = None):
        '''

        '''
        #
        # 'peak','cms','cen',  'dip','dipm','dipc',  'slit', 'slitm', 'slitc',   'step','stepm' and 'stepc'
        #
        mode = 'peak'


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
            if logWidget is not None:
                logWidget.append( "fsa: %s limits: %g, %g" % (self.name, xi, xa))
        else: 
            lstX = self.x[:self.currentIndex]
            lstY = self.y[:self.currentIndex]
            if logWidget is not None:
                logWidget.append( "fsa: %s total x-range" % (self.name))
        #
        # reversed x-values?
        #
        if lstX[0] > lstX[-1]:
            lstX = list( reversed( lstX))
            lstY = list( reversed( lstY))
                
        try: 
            message, xpos, xpeak, xcms, xcen = _pysp.fastscananalysis( lstX, lstY, mode)
        except Exception, e:
            print "GQE.fsa: trouble with", self.name
            print repr( e)
            

        if logWidget is not None: 
            logWidget.append( " message:  %s" % message)
            logWidget.append( " xpos:     %g" % xpos)
            logWidget.append( " xpeak:    %g" % xpeak)
            logWidget.append( " xcms:     %g" % xcms)
            logWidget.append( " xcen:     %g" % xcen)
        else:
            print "GQE.fsa: message", message, "xpos", xpos, "xpeak", xpeak, "xcms", xcms, "xcen", xcen

        return 

def getGqeList():
    '''
    returns the list of scans
    '''
    return _gqeList

def getDisplayList(): 
    '''
    returns a list of scans which are currently displayed
    '''

    argout = []
    for scan in _gqeList: 
        if scan.plotItem is not None:
            argout.append( scan)

    return argout

def getGqe( name):
    '''
    return the scan object with obj.name == name, 
    otherwise return None
    '''
    for scan in _gqeList:
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
    if nameLst is supplied, delete the specified scans from the gqeList
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
    global _gqeIndex

    #print "GQE.delete, nameList:", repr( nameLst)
    #print "GQE.delete: %s" % repr( HasyUtils.getTraceBackList())

    if not nameLst:    
        while len( _gqeList) > 0:
            tmp = _gqeList.pop()
            if tmp.plotItem is not None:
                #
                # clear.__doc__: 'Remove all items from the ViewBox'
                #
                _pysp.clear( tmp)
                #tmp.plotItem.clear()
            _gqeIndex = None
        setTitle( None)
        setComment( None)
        return 

    if type( nameLst) is not list:
        name = nameLst
        for i in range( len( _gqeList)):
            if name.upper() == _gqeList[i].name.upper():
                #
                # we had many MCA spectra displayed on top of each other
                #
                if _gqeList[i].plotItem is not None:
                    _pysp.clear( _gqeList[i])
                    #_gqeList[i].plotItem.clear()
                del _gqeList[i]
                break
        else:
            raise ValueError( "GQE.delete: not found %s" % name)
        return 

    for name in nameLst:
        for i in range( len( _gqeList)):
            if name.upper() == _gqeList[i].name.upper():
                #
                # we had many MCA spectra displayed on top of each other
                #
                if _gqeList[i].plotItem is not None:
                    #
                    # clear.__doc__: 'Remove all items from the ViewBox'
                    #
                    _pysp.clear( _gqeList[i])
                    #_gqeList[i].plotItem.clear()
                del _gqeList[i]
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
    scanSrc = getGqe( src)
    scanTrgt = getGqe( trgt)
    scanSrc.overlay = scanTrgt.name
    return 
    
def info( gqeList = None):
    '''
    prints some information about scans in gqeList.
    if gqeList is not supplied, info is displayed for all scans
    '''

    if gqeList is not None:
        if type(gqeList) is not list:
            scan = getGqe( gqeList)
            _infoScan( scan)
            return 1

        for scn in gqeList:
            scan = getGqe( scn)
            _infoScan( scan)
        return len( gqeList)

    argout = 0

    if _gqeList:
        print "The List of Scans:"
        for scan in _gqeList:
            _infoScan( scan)
        print "\n--- %s scans" % len( _gqeList)
        argout += len( _gqeList)
    else: 
        print "scan list is empty"

    if _title: 
        print "Title:  ", _title
    if _comment: 
        print "Comment:", _comment

    return argout

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
    if _gqeList is None: 
        print "scan list is empty"

    print "The List of Scans:"
    for scan in _gqeList:
        print "%s, nPts %d, xMin %g, xMax %g" % (scan.name, scan.nPts, scan.xMin, scan.xMax)

def nextScan( name = None):
    '''
    nextScan/prevScan return the next/previous scan object
    '''
    global _gqeIndex

    if len( _gqeList) == 0:
        raise ValueError( "GQE.nextScan: scan list empty")

    if name is not None:
        for i in range( len(_gqeList)): 
            if _gqeList[i].name == name:
                _gqeIndex = i + 1
                break
    else:
        if _gqeIndex is None:
            _gqeIndex = 0
        else:
            _gqeIndex += 1
        
    if _gqeIndex >= len( _gqeList) :
        _gqeIndex = 0

    while type( _gqeList[ _gqeIndex]) != Scan:
        _gqeIndex += 1
        if _gqeIndex >= len( _gqeList): 
            raise ValueError( "GQE.nextScan: failed to find the next Scan")

    return _gqeList[ _gqeIndex]

def prevScan( name = None):
    '''
    nextScan/prevScan return the next/previous scan object
    '''
    global _gqeIndex

    if len( _gqeList) == 0:
        raise ValueError( "GQE.prevScan: scan list empty")

    if name is not None:
        for i in range( len(_gqeList)): 
            if _gqeList[i].name == name:
                _gqeIndex = i + 1
                break
    else:
        if _gqeIndex is None:
            _gqeIndex = 0
        else:
            _gqeIndex -= 1

    if _gqeIndex < 0:
        _gqeIndex = len( _gqeList) - 1

    if _gqeIndex >= len( _gqeList):
        _gqeIndex = 0


    while type( _gqeList[ _gqeIndex]) != Scan:
        _gqeIndex += 1
        if _gqeIndex >= len( _gqeList): 
            raise ValueError( "GQE.nextMesh: failed to find the previous Scan")

    return _gqeList[ _gqeIndex]

def nextMesh( name = None):
    '''
    nextMesh/prevMesh return the next/previous scan object
    '''
    global _gqeIndex

    if len( _gqeList) == 0:
        raise ValueError( "GQE.nextScan: gqe list empty")

    if name is not None:
        for i in range( len(_gqeList)): 
            if _gqeList[i].name == name:
                _gqeIndex = i + 1
                break
    else:
        if _gqeIndex is None:
            _gqeIndex = 0
        else:
            _gqeIndex += 1
            
    if _gqeIndex >= len( _gqeList) :
        _gqeIndex = 0

    while type( _gqeList[ _gqeIndex]) != Mesh:
        _gqeIndex += 1
        if _gqeIndex >= len( _gqeList): 
            raise ValueError( "GQE.nextMesh: failed to find the next Mesh")

    return _gqeList[ _gqeIndex]

def prevMesh( name = None):
    '''
    nextScan/prevScan return the next/previous scan object
    '''
    global _gqeIndex

    if len( _gqeList) == 0:
        raise ValueError( "GQE.prevScan: scan list empty")

    if name is not None:
        for i in range( len(_gqeList)): 
            if _gqeList[i].name == name:
                _gqeIndex = i + 1
                break
    else:
        if _gqeIndex is None:
            _gqeIndex = 0
        else:
            _gqeIndex -= 1

    if _gqeIndex < 0:
        _gqeIndex = len( _gqeList) - 1

    if _gqeIndex >= len( _gqeList):
        _gqeIndex = 0

    while type( _gqeList[ _gqeIndex]) != Mesh:
        _gqeIndex -= 1
        if _gqeIndex < 0:
            raise ValueError( "GQE.nextMesh: failed to find the previous Mesh")

    return _gqeList[ _gqeIndex]

def getIndex( name): 
    '''
    returns the position of a scan in the gqeList, 
    the first index is 0.
    '''
    index = 0
    for scan in _gqeList:
        if scan.name == name:
            return index
        index += 1
    raise ValueError( "GQE.getIndex: not found %s" % name)
    
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
        scn =  Scan( name = elm.name, x = elm.x, y = elm.y, fileName = fileName, xLabel = fioObj.motorName)

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
    if len(_gqeList) == 0: 
        raise ValueError( "GQE.write: scan list is empty")

    #
    # check if all scans have the same length
    #
    length = None
    for scan in _gqeList:
        if scan.textOnly: 
            continue
        if lst is not None:
            if scan.name not in lst:
                continue
        if length is None:
            length = len( scan.x)
            continue
        if length != len( scan.x):
            raise ValueError( "GQE.write: output GQEs differ in length")
    
    obj = _HasyUtils.fioObj( namePrefix = "pysp")
    for scan in _gqeList:
        if scan.textOnly: 
            continue
        if lst is not None:
            if scan.name not in lst:
                continue
        col = _HasyUtils.fioColumn( scan.name)
        #
        # Mind currentIndex starts at 0. So, if currentIndex == 100, 
        # we have 101 list elements
        #
        col.x = scan.x[:scan.currentIndex + 1]
        col.y = scan.y[:scan.currentIndex + 1]
        obj.columns.append( col)
    fileName = obj.write()
    #print "created", fileName
    return fileName
    
def getNumberOfGqesToBeDisplayed( nameList): 
    '''
    return the number of scans to be displayed.
    Scans that are overlaid do not require extra space
    and are therefore not counted.
    '''
    if len( nameList) == 0:
        nOverlay = 0
        for gqe in _gqeList:
            if gqe.overlay is not None:
                nOverlay += 1
        nGqe = len( _gqeList) - nOverlay
        if nGqe < 1:
            nGqe = 1
    else:
        nOverlay = 0
        for name in nameList:
            if getGqe( name).overlay is not None:
                nOverlay += 1
        nGqe = len( nameList) - nOverlay
        if nGqe < 1:
            nGqe = 1
    #print "graphics.getNoOfGqesToBeDisplayed: nGqe %d" %(nGqe)
    return nGqe

def _getNumberOfOverlaid( nameList = None):
    '''
    returns the number of gqes which are overlaid to another, 
    used by e.g. graphics.display()
    '''
    count = 0
    for gqe in _gqeList:
        if nameList is not None: 
            if gqe.name not in nameList:
                continue
        if gqe.overlay is not None:
            count += 1

    return count
    
def setWsViewportFixed( flag):
    '''
    flag: True or False
    
    if True, the wsViewport is not changed automatically 
             to take many gqes into account
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
    depending on how many gqes are displayed the font size is adjusted
    '''
    if getNumberOfGqesToBeDisplayed( nameList) < _pysp.definitions.MANY_GQES:
        fontSize = _pysp.definitions.FONT_SIZE_NORMAL
    elif getNumberOfGqesToBeDisplayed( nameList) <= _pysp.definitions.VERY_MANY_GQES:
        fontSize = _pysp.definitions.FONT_SIZE_SMALL
    else: 
        fontSize = _pysp.definitions.FONT_SIZE_VERY_SMALL

    return fontSize

def getData():
    '''
    pack the interesting part of the spectra storage which has been
    created by the pyspMonitor into a dictionary. 
    '''
    hsh = {}
    for gqe in _gqeList:
        if type( gqe) != Scan: 
            continue
        name = gqe.name.upper() # needed by MVSA
        hsh[ name] = {}
        #
        # numpy array cannot be json-encoded
        #
        if gqe.currentIndex >= 0:
            hsh[ name]['x'] = list( gqe.x[:(gqe.currentIndex + 1)])
            hsh[ name]['y'] = list( gqe.y[:(gqe.currentIndex + 1)])
        else:
            hsh[ name]['x'] = []
            hsh[ name]['y'] = []
    # just to make mvsa happy

    if GQE.monitorGui is not None and GQE.monitorGui.scanInfo is not None: 
        hsh[ 'symbols'] = {}
        temp = GQE.monitorGui.scanInfo[ 'filename']
        if type( temp) is list:
            hsh[ 'symbols'][ 'file_name_'] = temp[0]
        else:
            hsh[ 'symbols'][ 'file_name_'] = temp
    return hsh

def fillDataMesh( hsh): 
    '''
    hsh = { 'putData': 
    { 'name': 'meshName', 
      'type': 'mesh', 
      'xMin': xmin, 'xMax': xmax, 'width': width,
      'yMin': ymin, 'yMax': ymax, 'height': height,}}

    hsh = { 'putData': 
    { 'name': 'meshName', 
      'setPixel': (x, y, value)}}
    '''

    if hsh.has_key( 'xMin'): 
        m = _pysp.Mesh( name = hsh[ 'name'],  
                        xMin = hsh[ 'xMin'], xMax = hsh[ 'xMax'], width = hsh[ 'width'],
                        yMin = hsh[ 'yMin'], yMax = hsh[ 'yMax'], height = hsh[ 'height'])
        o = getGqe( hsh[ 'name'])
    elif hsh.has_key( 'setPixel'): 
        o = getGqe( hsh[ 'name'])
        o.setPixel( x = hsh[ 'setPixel'][0],
                    y = hsh[ 'setPixel'][1],
                    value = hsh[ 'setPixel'][2])
        if not hsh.has_key( 'noDisplay') or not hsh[ 'noDisplay']: 
            _pysp.cls()
            _pysp.display()

    else: 
        raise ValueError( "GQE.fillDataMesh: dictionary unexpected")

    return "done"
    
def fillDataByColumns( hsh):
    if len( hsh[ 'columns']) < 2: 
        raise Exception( "GQE.fillDataByColumns", "less than 2 columns")

    columns = []
    xcol = hsh[ 'columns'][0]
    for elm in hsh[ 'columns'][1:]:
        if not elm.has_key( 'name'):
            raise Exception( "GQE.fillDataByGqes", "missing 'name'")
        if not elm.has_key( 'data'):
            raise Exception( "GQE.fillDataByGqes", "missing 'data'")
        data = elm[ 'data']
        if len( data) != len( xcol[ 'data']):
            raise Exception( "GQE.fillDataByGqes", 
                             "column length differ %s: %d, %s: %d" % ( xcol[ 'name'], len( xcol[ 'data']),
                                                                       elm[ 'name'], len(elm[ 'data'])))
        scan = Scan( name = elm[ 'name'], 
                    xMin = data[0], xMax = data[-1], nPts = len(data),
                    xLabel = xcol[ 'name'], yLabel = elm[ 'name'],
                    lineColor = 'red',
                )
        for i in range(len(data)):
            scan.setX( i, xcol[ 'data'][i])
            scan.setY( i, data[i])
    _pysp.display()

    return 

def colorSpectraToPysp( color): 
    '''
    to be backwards compatible: allow the user to specify colors a la Spectra
    '''
    if color == 1:
        color = 'black'
    elif color == 2:
        color = 'red'
    elif color == 3:
        color = 'green'
    elif color == 4:
        color = 'blue'
    elif color == 5:
        color = 'cyan'
    elif color == 5:
        color = 'cyan'
    elif color == 6:
        color = 'yellow'
    elif color == 7:
        color = 'magenta'

    return color

def fillDataByGqes( hsh):

    flagAtFound = False
    flagOverlayFound = False
    
    gqes = []
    for elm in hsh[ 'gqes']:
        if not elm.has_key( 'name'):
            raise Exception( "GQE.fillDataByGqes", "missing 'name'")
        if not elm.has_key( 'x'):
            raise Exception( "GQE.fillDataByGqes", "missing 'x' for %s" % elm[ 'name'])
        if not elm.has_key( 'y'):
            raise Exception( "GQE.fillDataByGqes", "missing 'y' for %s" % elm[ 'name'])
        if len( elm[ 'x']) != len( elm[ 'y']):
            raise Exception( "GQE.fillDataByGqes", "%s, x and y have different length %d != %d" % \
                             (elm[ 'name'], len( elm[ 'x']), len( elm[ 'y'])))
        at = '(1,1,1)'
        if elm.has_key( 'at'):
            flagAtFound = True
            at = elm[ 'at']
        xLabel = 'x-axis'
        if elm.has_key( 'xlabel'):
            xLabel = elm[ 'xlabel']
        if elm.has_key( 'xLabel'):
            xLabel = elm[ 'xLabel']
        yLabel = 'y-axis'
        if elm.has_key( 'ylabel'):
            yLabel = elm[ 'ylabel']
        if elm.has_key( 'yLabel'):
            yLabel = elm[ 'yLabel']
        color = 'red'
        if elm.has_key( 'color'):
            color = elm[ 'color']
            color = colorSpectraToPysp( color)
        
        x = elm[ 'x']
        y = elm[ 'y']
        gqe = SCAN( name = elm[ 'name'],
                    at = at, 
                    xMin = x[0], xMax = x[-1], nPts = len(x),
                    xLabel = xLabel, yLabel = yLabel,
                    lineColor = color,
                )
        for i in range(len(x)):
            gqe.setX( i, x[i])
            gqe.setY( i, y[i])


    _pysp.display()

    return 

def toPysp( hsh): 
    '''
    this function is used by the ZMQ receiver and it can also be 
    called directly to simulate the toPyspMonitor() interface
    '''
    argout = {}
    if hsh.has_key( 'command'):
        argout[ 'result'] = _pysp.commandIfc( hsh)
    elif hsh.has_key( 'putData'):
        argout[ 'result'] = putData( hsh[ 'putData'])
    elif hsh.has_key( 'getData'):
        try:
            argout[ 'getData'] = getData()
            argout[ 'result'] = 'done'
        except Exception, e:
            argout[ 'getData'] = {}
            argout[ 'result'] = repr( e)
    elif hsh.has_key( 'command'):
        argout[ 'result'] = _pysp.command( hsh[ 'command'])
    elif hsh.has_key( 'isAlive'):
        argout[ 'result'] = 'done'
    else:
        argout[ 'result'] = "pyspMonitorClass.cb_timerZMG: something is wrong"

    return argout

def putData( hsh):
    '''
    a plot is created based on a dictionary 
    the use case: some data are sent pyspMonitor
    '''

    argout = 'n.n.'
    if not hsh.has_key( 'title'):
        setTitle( "NoTitle")
    else:
        setTitle( hsh[ 'title'])

    if hsh.has_key( 'columns'):
        delete()
        _pysp.cls()
        argout = fillDataByColumns( hsh)
    elif hsh.has_key( 'gqes'):
        delete()
        _pysp.cls()
        argout = fillDataByGqes( hsh)
    elif hsh.has_key( 'type') and hsh[ 'type'] == 'mesh':
        argout = fillDataMesh( hsh)
    elif hsh.has_key( 'setPixel'):
        argout = fillDataMesh( hsh)
    else:
        raise Exception( "GQE.putData", "expecting 'columns' or 'gqes'")

    return argout

def commandIfc( hsh): 
    '''
    passes commands to pysp.ipython.ifc.command()

    called from /home/kracht/Misc/pySpectra/PySpectra/pyspMonitorClass.py
    
    List of commands: 
      hsh = { 'command': ['cls', 'display']}
    Single commands
    hsh = { 'command': 'display'}
    '''
    argout = "n.n."
    if type( hsh[ 'command']) == list:
        for cmd in hsh[ 'command']: 
            ret = _pysp.ipython.ifc.command( cmd)
            argout += "%s -> %s;" % (cmd, repr( ret))

        return "done"

    ret = _pysp.ipython.ifc.command( hsh[ 'command'])
    argout = "%s -> %s" % (hsh[ 'command'], repr( ret))
    return argout

class Mesh( GQE):
    '''
    a Mesh a 2D data array

    PySpectra.Mesh( name = 'name', data = data)

    The attributes: 
        autoscale   default: True
        log:        bool, def. false
    '''
    def __init__( self, name = None, **kwargs):
        global _gqeList

        super( Mesh, self).__init__()

        #print "GQE.Mesh: ", repr( kwargs)

        if name is None:
            raise ValueError( "GQE.Mesh: 'name' is missing")

        for i in range( len( _gqeList)):
            if name == _gqeList[i].name:
                raise ValueError( "GQE.Mesh.__init__(): %s exists already" % name)
   
        self.name = name

        self.setAttr( kwargs)

        if 'data' in kwargs: 
            self._createMeshFromData( kwargs)
        elif 'xMin' in kwargs: 
            self._createMeshFromLimits( kwargs)


        if kwargs:
            raise ValueError( "GQE.Mesh: dct not empty %s" % str( kwargs))

        _gqeList.append( self)

    def __setattr__( self, name, value): 
        #print "GQE.Mesh.__setattr__: name %s, value %s" % (name, value)
        if name in _MeshAttrsPublic or \
           name in _MeshAttrsPrivate: 
            super(Mesh, self).__setattr__(name, value)
        else: 
            raise ValueError( "GQE.Mesh.__setattr__: %s unknown attribute %s" % ( self.name, name))

    def __getattr__( self, name): 
        raise ValueError( "GQE.Mesh.__getattr__: %s unknown attribute %s" % ( self.name, name))
        
    def __del__( self): 
        pass

    def setAttr( self, kwargs):
        '''
        set the graphics attributes of a Mesh, see docu in Mesh()

        Returns None
        '''

        self.at = None
        self.colSpan = 1
        self.log = False
        self.ncol = None
        self.nrow = None
        self.nplot = None
        self.overlay = None
        self.img = None
        self.logWidget = None
        self.mouseProxy = None
        self.mouseClick = None
        self.mouseLabel = None
        self.viewBox = None
        self.xLabel = None
        self.yLabel = None
        #
        # the attributes plot and mouseLabel are created by graphics.display(). 
        # However, it is initialized here to help cls()
        #
        self.plotItem = None

        for attr in [ 'at', 'log']:
            if attr in kwargs:
                setattr( self, attr, kwargs[ attr])
                del kwargs[ attr]

        
    def _createMeshFromData( self, kwargs): 

        if not kwargs.has_key( 'data'): 
            raise ValueError( "GQE.Mesh.createMeshFromData: %s no 'data'" % ( self.name))

        self.data = kwargs[ 'data'][:]
        del kwargs[ 'data']

        self.width = self.data.shape[0]
        self.height = self.data.shape[1]

        self.xMin = 0
        self.xMax = self.width
        self.yMin = 0
        self.yMax = self.height

        self.xLabel = "xLabel"
        self.yLabel = "yLabel"


        for kw in [ 'xMin', 'xMax', 'yMin', 'yMax', 'width', 'height', 'xLabel', 'yLabel']: 
            if not kwargs.has_key( kw): 
                continue
            setattr( self, kw, kwargs[ kw])
            del kwargs[ kw]

        return 

    def _createMeshFromLimits( self, kwargs): 

        for kw in [ 'xMin', 'xMax', 'yMin', 'yMax', 'width', 'height']: 
            if not kwargs.has_key( kw): 
                raise ValueError( "GQE.Mesh.createMeshFromLimits: %s no %s" % ( self.name, kw))

        for kw in [ 'xMin', 'xMax', 'yMin', 'yMax', 'width', 'height', 'xLabel', 'yLabel']: 
            if not kwargs.has_key( kw): 
                continue
            setattr( self, kw, kwargs[ kw])
            del kwargs[ kw]

        #
        # consider this: x [-2, 1], width 100
        #  if x == 1 -> ix == 100, so we need '+ 1'
        #
        self.data  = _np.zeros( ( self.width + 1, self.height + 1))
            
        return 

    def setPixel( self, x = None, y = None, value = None):
        '''
        x and y are in physical coordinates
        '''

        if x < self.xMin or x > self.xMax:
            raise( ValueError( "GQE.Mesh.setXY: out of x-bounds %g [%g, %g]" % ( x, self.xMin, self.xMax)))
        if y < self.yMin or y > self.yMax:
            raise( ValueError( "GQE.Mesh.setXY: out of y-bounds %g [%g, %g]" % ( y, self.yMin, self.yMax)))

        ix = int( _math.floor((x - self.xMin)/(self.xMax - self.xMin)*(self.width)))
        iy = int( _math.floor((y - self.yMin)/(self.yMax - self.yMin)*(self.height)))

        if ix < 0 or ix > self.width:
            raise ValueError( "GQE.Mesh.setPixel: ix %d not in [%d, %d], %g [%g, %g]" % \
                              (ix, 0, self.width, 
                               x, self.xMin, self.xMax))
        if iy < 0 or iy > self.height:
            raise ValueError( "GQE.Mesh.setPixel: iy %d not in [%d, %d], %g [%g, %g]" % \
                              (iy, 0, self.height,
                               y, self.yMin, self.yMax))

        self.data[ix][iy] = value

        return 

    #
    # why do we need a class function for move()
    #
    def move( self, targetIX, targetIY): 
        '''
        this function is invoked by a mouse click from pqtgrph/graphics.py
        '''
        import PyTango as _PyTango
        import time as _time

        if not hasattr( self, 'xMin'):
            print "Gqe.Mesh.move: %s no attribute xMin" % self.name
            return 

        if type( self) != Mesh:
            print "Gqe.Mesh.move: %s is not a Mesh" % self.name
            return 
            
        targetX = float( targetIX)/float( self.width)*( self.xMax - self.xMin) + self.xMin
        targetY = float( targetIY)/float( self.height)*( self.yMax - self.yMin) + self.yMin
        print "GQE.Mesh.move x %g, y %g" % (targetX, targetY)

        if GQE.monitorGui is None:
            if self.logWidget is not None:
                self.logWidget.append( "GQE.Mesh.move: not called from pyspMonitor") 
            else:
                print "GQE.Mesh.move: not called from pyspMonitor"
            return 

        try: 
            proxyX = _PyTango.DeviceProxy( self.xLabel)
        except Exception, e:
            print "Mesh.move: no proxy to %s" % self.xLabel
            print repr( e)
            return 

        try: 
            proxyY = _PyTango.DeviceProxy( self.yLabel)
        except Exception, e:
            print "Mesh.move: no proxy to %s" % self.yLabel
            print repr( e)
            return 

        #
        # stop the motors, if they is moving
        #
        if proxyX.state() == _PyTango.DevState.MOVING:
            if self.logWidget is not None:
                self.logWidget.append( "Mesh.Move: stopping %s" % proxyX.name()) 
            proxyX.stopMove()
        while proxyX.state() == _PyTango.DevState.MOVING:
            _time.sleep(0.01)
        if proxyY.state() == _PyTango.DevState.MOVING:
            if self.logWidget is not None:
                self.logWidget.append( "Mesh.Move: stopping %s" % proxyY.name()) 
            proxyY.stopMove()
        while proxyY.state() == _PyTango.DevState.MOVING:
            _time.sleep(0.01)

        msg = "Move\n  %s from %g to %g\n  %s from %g to %g " % \
              (proxyX.name(), proxyX.read_attribute( 'Position').value, targetX,
               proxyY.name(), proxyY.read_attribute( 'Position').value, targetY)
        reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No)
        
        if not reply == _QtGui.QMessageBox.Yes:
            if self.logWidget is not None:
                GQE.monitorGui.logWidget.append( "Mesh.Move: move not confirmed")
            return

        lst = [ "umv %s %g %s %g" % (proxyX.name(), targetX, proxyY.name(), targetY)]
        
        if self.logWidget is not None:
                GQE.monitorGui.logWidget.append( "%s" % (lst[0]))

        GQE.monitorGui.door.RunMacro( lst)
        return 

