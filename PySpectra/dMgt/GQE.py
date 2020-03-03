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

_ScanAttrsPrivate = [ 'infLineLeft', 'infLineRight', 'mousePrepared', 'mouseLabel',  
                      'plotItem', 'plotDataItem', 'scene', 'xDateMpl']

_ImageAttrsPublic = [ 'at', 'colorMap', 'colSpan', 'data', 'estimatedMax', 'flagAxes', 'indexRotate', 
                      'log', 'logWidget', 'maxIter', 'modulo', 
                      'name', 'ncol', 'nplot', 'nrow', 'overlay', 'textOnly', 'xMin', 'xMax',
                     'yMin', 'yMax', 'width', 'height', 'viewBox', 'xLabel', 'yLabel']
#
# img is used in pqt_graphics
#
_ImageAttrsPrivate = [ 'cbZoomProgress', 'flagZoomSlow', 'img', 'plotItem', 'mousePrepared', 'mouseLabel']

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
    def __init__( self, name = "NoName", text = 'Empty', x = 0.5, y = 0.5, 
                  hAlign = 'left', vAlign = 'top', color = 'black', fontSize = None,
                  NDC = True, tag = 'n.n.'): 

        self.name = name
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

        #print( "GQE.Scan: %s" % repr( kwargs))
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
        #print( "GQE.Scan.__setattr__: name %s, value %s" % (name, value))
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

    def _checkTargetWithinLimits( self, name, target, proxy): 
        '''
        return False, if the target position is outside the limits
        '''
        #
        # tango servers have UnitLimitMin/Max
        #
        if hasattr( proxy, "UnitLimitMin"): 
            try: 
                if target < proxy.UnitLimitMin: 
                    _QtGui.QMessageBox.about( None, 'Info Box', "%s, target %g < unitLimitMin %g" % 
                                              ( name, target, proxy.UnitLimitMin))
                    return False
                if target > proxy.UnitLimitMax: 
                    _QtGui.QMessageBox.about( None, 'Info Box', "%s, target %g > unitLimitMax %g" % 
                                              ( name, target, proxy.UnitLimitMax))
                    return False
            except Exception as e: 
                _QtGui.QMessageBox.about( None, 'Info Box', "CheckTargetWithinLimits: %s %s" % 
                                          ( name, repr( e)))
                return False
        #
        # pool motors: need to check the attribute configuration
        #
        else: 
            attrConfig = proxy.get_attribute_config_ex( "Position")
            if target < float( attrConfig[0].min_value): 
                _QtGui.QMessageBox.about( None, 'Info Box', "%s, target %g < attrConf.min_value %g" % 
                                          ( name, target, float( attrConfig[0].min_value)))
                return False
            if target > float( attrConfig[0].max_value): 
                _QtGui.QMessageBox.about( None, 'Info Box', "%s, target %g > attrConf.max_value %g" % 
                                          ( name, target, float( attrConfig[0].max_value)))
                return False
        return True
                
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
                print( "GQE.Scan.move: not called from pyspMonitor")
            return 
        #
        # make sure the target is inside the x-range of the plot
        #
        if target < self.xMin or target > self.xMax:
            _QtGui.QMessageBox.about( None, "Info Box", 
                                      "GQE.Move: target %g outside %s x-axis %g %g" % (target, self.name, self.xMin, self.xMax))
            return
            
        #
        # don't use MCA data to move motors
        #
        if self.flagMCA:
            if self.logWidget is not None:
                self.logWidget.append( "GQE.Scan.move: error, don't use MCAs to move motors") 
            return 

        #print( "GQE.Scan.move: to", target, "using %s" % GQE.monitorGui.scanInfo)

        #
        # ---
        # from moveMotor widget
        # ---
        #
        if self.motorList is not None:
            if len( self.motorList) != 1:
                if self.logWidget is not None:
                    self.logWidget.append( "GQE.Scan.move: error, len( motorList) != 1") 
                else: 
                    print( "GQE.Scan.move: error, len( motorList) != 1") 
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
                    print( "Move: move not confirmed")
                return
            if self.logWidget is not None:
                self.logWidget.append( "Moving %s from %g to %g" % ( proxy.name(), 
                                                                    float( proxy.read_attribute( 'Position').value), 
                                                                    target))
            self.motorList[0].Position = target
            return 
        
        #
        # ---
        # from the pyspMonitor application
        # ---
        #
        if GQE.monitorGui is None or GQE.monitorGui.scanInfo is None: 
            _QtGui.QMessageBox.about( None, "Info Box", 
                                      "GQE.Move: GQE.monitorGui is None or GQE.monitorGui.scanInfo is None")
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
            if not self._checkTargetWithinLimits( motorArr[0]['name'], float( motorArr[0]['targetPos']), p0): 
                return 
                
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
            if not self._checkTargetWithinLimits( motorArr[0]['name'], float( motorArr[0]['targetPos']), p0): 
                return 
            if not self._checkTargetWithinLimits( motorArr[1]['name'], float( motorArr[1]['targetPos']), p1): 
                return 
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
            if not self._checkTargetWithinLimits( motorArr[0]['name'], float( motorArr[0]['targetPos']), p0): 
                return 
            if not self._checkTargetWithinLimits( motorArr[1]['name'], float( motorArr[1]['targetPos']), p1): 
                return 
            if not self._checkTargetWithinLimits( motorArr[2]['name'], float( motorArr[2]['targetPos']), p2): 
                return 
            msg = "Move\n  %s from %g to %g\n  %s from %g to %g\n  %s from %g to %g " % \
                  (motorArr[0]['name'], p0.read_attribute( 'Position').value, motorArr[0]['targetPos'],
                   motorArr[1]['name'], p1.read_attribute( 'Position').value, motorArr[1]['targetPos'],
                   motorArr[2]['name'], p2.read_attribute( 'Position').value, motorArr[2]['targetPos'])
            reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No)

        if not reply == _QtGui.QMessageBox.Yes:
            GQE.monitorGui.logWidget.append( "Move: move not confirmed")
            return

        if GQE.monitorGui.scanInfo['title'].find( "hklscan") == 0:
            GQE.monitorGui.logWidget.append( "br %g %g %g" % 
                                             (motorArr[0]['targetPos'],motorArr[1]['targetPos'],motorArr[2]['targetPos']))
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
        self.mousePrepared = False
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

    def addText( self, name = 'NoName', text = 'Empty', x = 0.5, y = 0.5, 
                 hAlign = 'left', vAlign = 'top', 
                 color = 'black', fontSize = None, NDC = True, tag = 'n.n.'):
        '''
        Docu can found in Text()
        '''
        txt = Text( name, text, x, y, hAlign, vAlign, color, fontSize, NDC, tag)
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
        except Exception as e:
            print( "GQE.fsa: trouble with %s" % self.name)
            print( repr( e))
            

        if logWidget is not None: 
            logWidget.append( " message:  %s" % message)
            logWidget.append( " xpos:     %g" % xpos)
            logWidget.append( " xpeak:    %g" % xpeak)
            logWidget.append( " xcms:     %g" % xcms)
            logWidget.append( " xcen:     %g" % xcen)
        else:
            print( "GQE.fsa: message %s xpos %g xpeak %g xmcs %g xcen %g" % (message, xpos, xpeak, xcms, xcen))

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

    #print( "GQE.delete, nameList: %s" % repr( nameLst))
    #print( "GQE.delete: %s" % repr( HasyUtils.getTraceBackList()))

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
            print( "GQE.delete: not found %s" % name)
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
        print( "The List of Scans:")
        for scan in _gqeList:
            _infoScan( scan)
        print( "\n--- %s scans" % len( _gqeList))
        argout += len( _gqeList)
    else: 
        print( "scan list is empty")

    if _title: 
        print( "Title:  %s" % _title)
    if _comment: 
        print( "Comment: %s" % _comment)

    return argout

def _displayTextList( scan): 
    for text in scan.textList:
        print( "  text: %s" % text.text)
        print( "    x: %g, y: %g" % (text.x, text.y))
        print( "    hAlign: %s, vAlign: %s" % ( str(text.hAlign), str(text.vAlign)))
        print( "    color: %s" % str( text.color))
    return 

def _infoScan( scan): 
    '''
    
    '''
    if scan.textOnly: 
        print( "--- GQE._infoScan %s (textonly) \n" % scan.name)
        _displayTextList( scan)
        return 
    #
    # create a local copy of ScanAttrs to delete elements which
    # are already shown
    #
    scanAttrsPrinted = []
    print( "--- \n %s" % scan.name)
    scanAttrsPrinted.append( 'name')
    print( "  currentIndex: %d, lastIndex: %d, Pts: %d" % (scan.currentIndex, scan.lastIndex, scan.nPts))
    scanAttrsPrinted.append( 'currentIndex')
    scanAttrsPrinted.append( 'lastIndex')
    scanAttrsPrinted.append( 'nPts')
    print( "  nrow: %s, ncol: %s, nplot: %s" % ( str(scan.nrow), str(scan.ncol), str(scan.nplot)))
    scanAttrsPrinted.append( 'nrow')
    scanAttrsPrinted.append( 'ncol')
    scanAttrsPrinted.append( 'nplot')
    print( "  showGridX: %s, showGridY: %s" % ( str(scan.showGridX), str(scan.showGridY)))
    scanAttrsPrinted.append( 'showGridX')
    scanAttrsPrinted.append( 'showGridY')
    print( "  xMin: %s, xMax: %s" % ( str(scan.xMin), str(scan.xMax)))
    scanAttrsPrinted.append( 'xMin')
    scanAttrsPrinted.append( 'xMax')
    print( "  yMin: %s, yMax: %s" % ( str(scan.yMin), str(scan.yMax)))
    scanAttrsPrinted.append( 'yMin')
    scanAttrsPrinted.append( 'yMax')
    print( "  xLabel: %s, yLabel: %s" % ( str(scan.xLabel), str(scan.yLabel)))
    scanAttrsPrinted.append( 'xLabel')
    scanAttrsPrinted.append( 'yLabel')
    print( "  autoscaleX: %s, autoscaleY: %s" % ( str(scan.autoscaleX), str(scan.autoscaleY)))
    scanAttrsPrinted.append( 'autoscaleX')
    scanAttrsPrinted.append( 'autoscaleY')
    print( "  at: %s, colSpan: %s" % ( str(scan.at), str(scan.colSpan)))
    scanAttrsPrinted.append( 'at')
    scanAttrsPrinted.append( 'colSpan')
    print( "  lineColor: %s, lineWidth: %s, lineStyle: %s" % ( str(scan.lineColor), str(scan.lineWidth), str( scan.lineStyle)))
    scanAttrsPrinted.append( 'lineColor')
    scanAttrsPrinted.append( 'lineWidth')
    scanAttrsPrinted.append( 'lineStyle')
    print( "  symbolColor: %s, symbolWidth: %s, symbol: %s" % ( str(scan.symbolColor), str(scan.symbolSize), str( scan.symbol)))
    scanAttrsPrinted.append( 'symbolColor')
    scanAttrsPrinted.append( 'symbolSize')
    scanAttrsPrinted.append( 'symbol')

    for attr in _ScanAttrsPublic:
        if attr in scanAttrsPrinted: 
            continue
        if attr == 'x' or attr == 'y':
            if len( getattr( scan, attr)) <= 10: 
                print( "  %s: %s" % ( attr, repr( getattr( scan, attr))))
            else:
                print( "  %s[:10]: %s" % ( attr, repr( getattr( scan, attr)[:10])))
            continue
        try:
            print( "  %s: %s" % ( attr, repr( getattr( scan, attr))))
        except Exception as e:
            print( "GQE._showScan: trouble with %s" % scan.name)
            print( repr( e))

    if len( scan.textList) > 0:
        _displayTextList( scan)

    return 

def show(): 
    '''
    lists all scans, one line per scan
    '''
    if _gqeList is None: 
        print( "scan list is empty")

    print( "The List of Scans:")
    for scan in _gqeList:
        print( "%s, nPts %d, xMin %g, xMax %g" % (scan.name, scan.nPts, scan.xMin, scan.xMax))

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
            raise ValueError( "GQE.nextImage: failed to find the previous Scan")

    return _gqeList[ _gqeIndex]

def nextImage( name = None):
    '''
    nextImage/prevImage return the next/previous scan object
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

    while type( _gqeList[ _gqeIndex]) != Image:
        _gqeIndex += 1
        if _gqeIndex >= len( _gqeList): 
            raise ValueError( "GQE.nextImage: failed to find the next Image")

    return _gqeList[ _gqeIndex]

def prevImage( name = None):
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

    while type( _gqeList[ _gqeIndex]) != Image:
        _gqeIndex -= 1
        if _gqeIndex < 0:
            raise ValueError( "GQE.nextImage: failed to find the previous Image")

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

def _insertImage( fioObj):
    '''
    fioObj contains an image
    '''
    if 'xMin' not in fioObj.parameters:
        fioObj.parameters[ 'xMin'] = 0
    if 'xMax' not in fioObj.parameters:
        fioObj.parameters[ 'xMax'] = 1
    if 'yMin' not in fioObj.parameters:
        fioObj.parameters[ 'yMin'] = 0
    if 'yMax' not in fioObj.parameters:
        fioObj.parameters[ 'yMax'] = 1
    #
    # the parameters as the come from the file are strings
    #
    for elm in [ 'width', 'height']: 
        fioObj.parameters[ elm] = int( fioObj.parameters[ elm])
    for elm in [ 'xMin', 'xMax', 'yMin', 'yMax']: 
        fioObj.parameters[ elm] = float( fioObj.parameters[ elm])

    data = _np.array( fioObj.columns[0].x).reshape(  fioObj.parameters[ 'width'],  fioObj.parameters[ 'height'])
    Image( name = fioObj.motorName, data = data, 
           width = fioObj.parameters[ 'width'], height = fioObj.parameters[ 'height'], 
           xMin = fioObj.parameters[ 'xMin'], xMax = fioObj.parameters[ 'xMax'], 
           yMin = fioObj.parameters[ 'yMin'], yMax = fioObj.parameters[ 'yMax'])

    return True

def read( fileName, x = 1, y = None, flagMCA = False):
    '''    
    this function reads files and creates Scans or Images

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

    if fioObj.isImage:
        return _insertImage( fioObj); 

    if len( fioObj.columns) == 0:
        raise ValueError( "GQE.read: %s, len( columns) == 0" % ( fileName))

    if y is not None:
        if y > (len( fioObj.columns) + 1): 
            raise ValueError( "GQE.read: %s, y: %d > (len( columns) + 1): %d" % ( fileName, y, (len( fioObj.columns) + 1)))
        return fioObj.columns[ y - 2]
    #
    # be sure not to call Scan() with fileName. Otherwise
    # you create a loop.
    #
    for elm in fioObj.columns:
        scn =  Scan( name = elm.name, x = elm.x, y = elm.y, xLabel = fioObj.motorName)

    return True
    
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
    #
    # store those GQEs that are to be written
    #
    outLst = []
    flagImage = False
    for gqe in _gqeList:
        if gqe.textOnly: 
            continue
        if lst is not None:
            if gqe.name not in lst:
                continue
        if type( gqe) is _pysp.dMgt.GQE.Scan: 
            if length is None:
                length = len( gqe.x)
            if length != len( gqe.x):
                raise ValueError( "GQE.write: output GQEs differ in length")
        if type( gqe) is _pysp.dMgt.GQE.Image: 
            flagImage = True
        outLst.append( gqe)
    #
    # if we write an image, allow just one
    #
    if flagImage is True and len( outLst) > 1: 
        raise ValueError( "GQE.write: len( lst) > 0 and flagImage")

    #
    # complain, if len( outLst ) == 0
    #
    if len( outLst) == 0:
        raise ValueError( "GQE.write: len( outLst) == 0")
    #
    # create an empty object
    #
    obj = _HasyUtils.fioObj( namePrefix = "pysp")
    if flagImage: 
        ima = outLst[0]
        obj.motorName = ima.name
        obj.parameters[ 'name'] = ima.name
        obj.parameters[ 'width'] = ima.width
        obj.parameters[ 'height'] = ima.height
        obj.parameters[ 'xMin'] = ima.xMin
        obj.parameters[ 'xMax'] = ima.xMax
        obj.parameters[ 'yMin'] = ima.yMin
        obj.parameters[ 'yMax'] = ima.yMax
        col = _HasyUtils.fioColumn( gqe.name)
        col.x = gqe.data.flatten()
        col.y = None
        obj.columns.append( col)
    else: 
        for gqe in outLst:
            col = _HasyUtils.fioColumn( gqe.name)
            if type( gqe) is _pysp.dMgt.GQE.Scan: 
                #
                # Mind currentIndex starts at 0. So, if currentIndex == 100, 
                # we have 101 list elements
                #
                col.x = gqe.x[:gqe.currentIndex + 1]
                col.y = gqe.y[:gqe.currentIndex + 1]
                obj.columns.append( col)

    fileName = obj.write()
    print( "GQE.write: created %s" % fileName)
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
    #print( "graphics.getNoOfGqesToBeDisplayed: nGqe %d" %(nGqe))
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
    '''
    flag: True or False
    
    if True, the wsViewport is not changed automatically 
             to take many gqes into account
    '''
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

def fillDataImage( hsh): 
    '''
    hsh = { 'putData': 
            { 'name': 'imageName', 
              'noDisplay': True, 
              'setPixelWorld': (x, y, value)}}
    '''

    if 'setPixelWorld' in hsh: 
        o = getGqe( hsh[ 'name'])
        o.setPixelWorld( x = hsh[ 'setPixelWorld'][0],
                         y = hsh[ 'setPixelWorld'][1],
                         value = hsh[ 'setPixelWorld'][2])
        if 'noDisplay' not in hsh or not hsh[ 'noDisplay']: 
            _pysp.cls()
            _pysp.display()
    elif 'setPixelImage' in hsh: 
        o = getGqe( hsh[ 'name'])
        o.setPixelImage( x = hsh[ 'setPixelImage'][0],
                         y = hsh[ 'setPixelImage'][1],
                         value = hsh[ 'setPixelImage'][2])
        if 'noDisplay' not in hsh or not hsh[ 'noDisplay']: 
            _pysp.cls()
            _pysp.display()

    else: 
        raise ValueError( "GQE.fillDataImage: dictionary unexpected")

    return "done"

def fillDataXY( hsh): 
    '''
    this function is mainly used during mesh scans

    hsh = { 'putData': 
    { 'name': 'MeshScan', 
      'xMin': xmin, 'xMax': xmax, 
      'yMin': ymin, 'yMax': ymax,
      'nPts': nPts}}

    hsh = { 'putData': 
    { 'name': 'MeshScan', 
      'setXY': (index, x, y)}}
    '''

    if 'xMin' in hsh: 
        m = _pysp.Scan( name = hsh[ 'name'],  
                        xMin = hsh[ 'xMin'], xMax = hsh[ 'xMax'], 
                        yMin = hsh[ 'yMin'], yMax = hsh[ 'yMax'],
                        nPts = hsh[ 'nPts'] )
        o = getGqe( hsh[ 'name'])
    elif 'setXY' in hsh: 
        o = getGqe( hsh[ 'name'])
        o.setXY( int( hsh[ 'setXY'][0]), 
                 hsh[ 'setXY'][1],
                 hsh[ 'setXY'][2])
        if 'noDisplay' not in hsh or not hsh[ 'noDisplay']: 
            _pysp.cls()
            _pysp.display()

    else: 
        raise ValueError( "GQE.fillDataImage: dictionary unexpected")

    return "done"
    
def fillDataByColumns( hsh):
    if len( hsh[ 'columns']) < 2: 
        raise Exception( "GQE.fillDataByColumns", "less than 2 columns")

    if 'title' in hsh: 
        setTitle( hsh[ 'title'])

    if 'comment' in hsh: 
        setComment( hsh[ 'comment'])

    columns = []
    xcol = hsh[ 'columns'][0]
    for elm in hsh[ 'columns'][1:]:
        if 'name' not in elm:
            raise Exception( "GQE.fillDataByGqes", "missing 'name'")
        if 'data' not in elm:
            raise Exception( "GQE.fillDataByGqes", "missing 'data'")
        data = elm[ 'data']
        del elm[ 'data']
        if len( data) != len( xcol[ 'data']):
            raise Exception( "GQE.fillDataByGqes", 
                             "column length differ %s: %d, %s: %d" % ( xcol[ 'name'], len( xcol[ 'data']),
                                                                       elm[ 'name'], len(elm[ 'data'])))

        lineColor = 'red'
        if 'lineColor' in elm:
            lineColor = elm[ 'lineColor']
            del elm[ 'lineColor'] 
            symbolColor = 'NONE'
        elif 'symbolColor' not in elm:
            lineColor = 'red'
            symbolColor = 'NONE'
        else: 
            symbolColor= 'red'
            lineColor = 'NONE'
            if 'symbolColor' in elm:
                symbolColor = elm[ 'symbolColor']
                del elm[ 'symbolColor'] 

        lineWidth = 1
        if 'lineWidth' in elm:
            lineWidth = elm[ 'lineWidth']
            del elm[ 'lineWidth'] 
        lineStyle = 'SOLID'
        if 'lineStyle' in elm:
            lineStyle = elm[ 'lineStyle']
            del elm[ 'lineStyle'] 
        showGridX = False
        if 'showGridX' in elm:
            showGridX = elm[ 'showGridX']
            del elm[ 'showGridX'] 
        showGridY = False
        if 'showGridY' in elm:
            showGridY = elm[ 'showGridY']
            del elm[ 'showGridY'] 
        xLog = False
        if 'xLog' in elm:
            xLog = elm[ 'xLog']
            del elm[ 'xLog'] 
        yLog = False
        if 'yLog' in elm:
            yLog = elm[ 'yLog']
            del elm[ 'yLog'] 
        symbol = '+'
        if 'symbol' in elm:
            symbol = elm[ 'symbol']
            del elm[ 'symbol'] 
        symbolSize= 10
        if 'symbolSize' in elm:
            symbolSize = elm[ 'symbolSize']
            del elm[ 'symbolSize'] 

        name = elm['name']
        del elm[ 'name']

        if len( list( elm.keys())) > 0: 
            raise ValueError( "GQE.fillDataByColumns: dct not empty %s" % repr( elm))

        scan = Scan( name = name, 
                     xMin = data[0], xMax = data[-1], nPts = len(data),
                     xLabel = xcol[ 'name'], yLabel = name,
                     lineColor = lineColor, lineWidth = lineWidth, lineStyle = lineStyle,
                     showGridX = showGridX, showGridY = showGridY, 
                     xLog = xLog, yLog = yLog, 
                     symbol = symbol, symbolColor = symbolColor, symbolSize = symbolSize, 
                )
        for i in range(len(data)):
            scan.setX( i, xcol[ 'data'][i])
            scan.setY( i, data[i])
    _pysp.display()

    return "done"

def colorSpectraToPysp( color): 
    '''
    to be backwards compatible: allow the user to specify colors by numbers (1 - 7), a la Spectra
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
    else: 
        color = 'black'

    return color

def fillDataByGqes( hsh):

    flagAtFound = False
    flagOverlayFound = False
    
    gqes = []
    for elm in hsh[ 'gqes']:
        if 'name' not in elm:
            raise Exception( "GQE.fillDataByGqes", "missing 'name'")
        if 'x' not in elm:
            raise Exception( "GQE.fillDataByGqes", "missing 'x' for %s" % elm[ 'name'])
        if 'y' not in elm:
            raise Exception( "GQE.fillDataByGqes", "missing 'y' for %s" % elm[ 'name'])
        if len( elm[ 'x']) != len( elm[ 'y']):
            raise Exception( "GQE.fillDataByGqes", "%s, x and y have different length %d != %d" % \
                             (elm[ 'name'], len( elm[ 'x']), len( elm[ 'y'])))
        at = '(1,1,1)'
        if 'at' in elm:
            flagAtFound = True
            at = elm[ 'at']
        xLabel = 'x-axis'
        if 'xlabel' in elm:
            xLabel = elm[ 'xlabel']
        yLabel = 'y-axis'
        if 'ylabel' in elm:
            yLabel = elm[ 'ylabel']
        color = 'red'
        if 'color' in elm:
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

    return "done"

def toPysp( hsh): 
    '''
    this function executes dictionaries which are received from 
      - ZMQ, from another client calling toPyspMonitor()
      - Queue, from pyspDoor
      - from an application directly (to simulate the to toPyspMonitor() interface

     hsh: 
       Misc
         {'command': ['delete']}
           delete all internal data
         {'command': ['cls']}
           clear the screen
         {'command': ['delete', 'cls']}
           deletes all internal data and clears the screen
         {'command': ['display']}
           a display command

       Title and comment for the whole widget
         {'command': [u'setTitle ascan exp_dmy01 0.0 1.0 3 0.2']}
           set the title 
         {'command': [u'setComment "tst_01366.fio, Wed Dec 18 10:02:09 2019"']}
           set the comment

       Scan
         {'Scan': {'name': 'eh_c01', 'xMax': 1.0, 'autoscaleX': False, 'lineColor': 'red', 'xMin': 0.0, 'nPts': 6}}
           create an empty scan. Notice, the inner dictionary is passed to the Scan constructor
         {'Scan': {'yMax': 2.0, 'symbol': '+', 'autoscaleY': False, 'autoscaleX': False, 
                   'xMax': 1.0, 'nPts': 24, 'symbolColor': 'red', 'name': 'MeshScan', 
                   'symbolSize': 5, 'lineColor': 'None', 'xMin': 0.0, 'yMin': 1.0}}
           create an empty scan setting more attributes.
         {'Scan': {'name': 'eh_mca01', 'flagMCA': True, 'lineColor': 'blue', 
                   'y': array([  0., ..., 35.,  30.]), 
                   'x': array([  0.0, ..., 2.047e+03]), 'reUse': True}}
           create an MCA scan, which is re-used
         {'command': ['setY eh_c01 0 71.41']}
           set a y-value of eh_c01, index 0
         {'command': ['setX eh_c01 0 0.0']}
           set a x-value of eh_c01, index 0
         {'command': ['setXY MeshScan 0 0.0 1.0']}
           set the x- and y-value by a single call, index is 0
         {'putData': {'columns': [{'data': [0.0, ..., 0.96], 'name': 'eh_mot01'}, 
                                  {'data': [0.39623, ... 0.01250], 'name': 'eh_c01'}, 
                                  {'showGridY': False, 'symbolColor': 'blue', 'showGridX': False, 
                                   'name': 'eh_c02', 'yLog': False, 'symbol': '+', 
                                   'data': [0.1853, ... 0.611], 
                                   'xLog': False, 'symbolSize': 5}], 
                      'title': 'a title', 
                      'comment': 'a comment'}}
           create the scans eh_c01 and eh_c02. The common x-axis is given by eh_mot01

       Image 
         {'Image': {'name': 'MandelBrot', 
                    'height': 5, 'width': 5, 
                    'xMax': -0.5, 'xMin': -2.0, 
                    'yMin': 0, 'yMax': 1.5}}
           create an empty image
         {'putData': {'images': [{'data': array([[0, 0, 0, ..., 0, 0, 0],
                                                 [0, 0, 0, ..., 1, 1, 1]], dtype=int32), 
                                  'name': 'MandelBrot'}]}
           create an image from a 2D array
         {'Image': {'data': data, 'name': "Mandelbrot"}}
           create an image by sending the data, e.g. data = np.ndarray( (width, height), _np.int32)
         {'command': ['setPixelImage Mandelbrot 1 3 200']}
           set a pixel value. the position is specified by indices
         {'command': ['setPixelWorld Mandelbrot 0.5 1.5 200']}
           set a pixel value. the position is specified by world coordinate
         Text
         {'command': ['setText MeshScan comment string "Sweep: 1/4" x 0.05 y 0.95']}
           create a text GQE for the scan MeshScan, the name of the text is comment

       Retrieve data
         {'getData': True}
           {'getData': {'EH_C02': {'y': [0.3183, ... 0.6510], 'x': [0.0, ... 0.959]}, 
                        'EH_C01': {'y': [0.0234, ... 0.4918], 'x': [0.0, ... 0.959]}}, 
            'result': 'done'}

    '''
    #print( "GQE.toPysp: %s" % repr( hsh))
    argout = {}
    if 'command' in hsh:
        argout[ 'result'] = _pysp.commandIfc( hsh)
    elif 'putData' in hsh:
        argout[ 'result'] = _putData( hsh[ 'putData'])
    elif 'getData' in hsh:
        try:
            argout[ 'getData'] = getData()
            argout[ 'result'] = 'done'
        except Exception as e:
            argout[ 'getData'] = {}
            argout[ 'result'] = "GQE.toPysp: error, %s" % repr( e)
    #
    # the 'isAlive' question comes from a toPyspMonitor() client, not from the door
    #
    elif 'isAlive' in hsh:
        argout[ 'result'] = 'done'
    elif 'Image' in hsh:
        try: 
            Image( **hsh[ 'Image']) 
            argout[ 'result'] = 'done'
        except Exception as e:
            argout[ 'result'] = "GQE.toPysp: error, %s" % repr( e)
    elif 'Scan' in hsh:
        try: 
            Scan( **hsh[ 'Scan']) 
            argout[ 'result'] = 'done'
        except Exception as e:
            argout[ 'result'] = "GQE.toPysp: error, %s" % repr( e)
    else:
        argout[ 'result'] = "GQE.toPysp: error, failed to identify %s" % repr( hsh)

    #print( "GQE.toPysp: return %s" % repr( argout))
    return argout

def _putData( hsh):
    '''
    a plot is created based on a dictionary 
    the use case: some data are sent pyspMonitor
    '''

    argout = 'n.n.'
    if 'title' not in hsh:
        setTitle( "NoTitle")
    else:
        setTitle( hsh[ 'title'])

    if 'columns' in hsh:
        delete()
        _pysp.cls()
        argout = fillDataByColumns( hsh)
    elif 'gqes' in hsh:
        delete()
        _pysp.cls()
        argout = fillDataByGqes( hsh)
    #
    # hsh = { 'putData': 
    #         { 'name': "MandelBrot",
    #           'type': 'image', 
    #           'xMin': xmin, 'xMax': xmax, 'width': width, 
    #           'yMin': ymin, 'yMax': ymax, 'height': height}}
    #
    elif 'type' in hsh and hsh[ 'type'] == 'image':
        del hsh[ 'type']
        Image( **hsh)
        argout = "done"
    #
    #_pysp.toPysp( { 'putData': 
    #                { 'images': [{'name': "Mandelbrot", 'data': data,
    #                              'xMin': xmin, 'xMax': xmax, 
    #                              'yMin': ymin, 'yMax': ymax}]}})
    #
    elif 'images' in hsh:
        for h in hsh[ 'images']: 
            Image( **h)
        argout = "done"
    elif 'setPixelImage' in hsh or 'setPixelWorld' in hsh:
        argout = fillDataImage( hsh)
    elif 'setXY' in hsh:
        argout = fillDataXY( hsh)
    else:
        raise Exception( "GQE.putData", "expecting 'columns', 'gqes', 'setPixelImage', 'setPixelWorld'")

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

class Image( GQE):
    '''
    a Image a 2D data array

    Constructors: 
      PySpectra.Image( name = 'name', data = data)
      PySpectra.Image( name = 'name', 
                       xMin = xmin, xMax = xmax, 
                       yMin = ymin, yMax = ymax, 
                       width = width, height = height)

    The attributes: 
        autoscale     default: True
        colorMap:     default: nipy_spectral
        estimatedMax: make a guess about the values to be expectd, def.: 100
        height
        log:          bool, def. false
        modulo:       def.: -1  (modulo disables)
        width: 
        xLabel
        yLabel
        xMin: 
        xMax: 
        yMin: 
        yMax: 
    '''
    def __init__( self, name = None, **kwargs):
        global _gqeList

        super( Image, self).__init__()

        #print( "GQE.Image: %s" % repr( kwargs))

        if name is None:
            raise ValueError( "GQE.Image: 'name' is missing")

        for i in range( len( _gqeList)):
            if name == _gqeList[i].name:
                raise ValueError( "GQE.Image.__init__(): %s exists already" % name)
   
        self.name = name
        self.textOnly = False
        #
        # ccallback function to update the zoom progress in the menu
        #
        self.cbZoomProgress = None
        self.flagZoomSlow = None

        self.setAttr( kwargs)

        if 'data' in kwargs: 
            self._createImageFromData( kwargs)
        elif hasattr( self, 'xMin'):
            self._createImageFromLimits( kwargs)
        else:
            raise ValueError( "GQE.Image: neither data nor xMin found")

        if kwargs:
            raise ValueError( "GQE.Image: dct not empty %s" % str( kwargs))

        _gqeList.append( self)

    def __setattr__( self, name, value): 
        #print( "GQE.Image.__setattr__: name %s, value %s" % (name, value))
        if name in _ImageAttrsPublic or \
           name in _ImageAttrsPrivate: 
            super(Image, self).__setattr__(name, value)
        else: 
            raise ValueError( "GQE.Image.__setattr__: %s unknown attribute %s" % ( self.name, name))

    def __getattr__( self, name): 
        raise ValueError( "GQE.Image.__getattr__: %s unknown attribute %s" % ( self.name, name))
        
    def __del__( self): 
        pass

    def setAttr( self, kwargs):
        '''
        set the graphics attributes of a Image, see docu in Image()

        Returns None
        '''

        self.at = None
        self.colorMap = "nipy_spectral"
        self.colSpan = 1
        self.estimatedMax = 100
        self.flagAxes = True  # 
        self.height = None
        self.indexRotate = 0
        self.log = False
        self.modulo = -1   # -1: disable modulo
        self.ncol = None
        self.nrow = None
        self.nplot = None
        self.overlay = None
        self.img = None
        self.logWidget = None
        self.maxIter = 512
        self.mouseLabel = None
        self.mousePrepared = False
        self.viewBox = None
        self.width = None
        self.xLabel = None
        self.xMin = None
        self.xMax = None
        self.yMin = None
        self.yMax = None
        self.yLabel = None
        #
        # the attributes plot and mouseLabel are created by graphics.display(). 
        # However, it is initialized here to help cls()
        #
        self.plotItem = None

        for attr in [ 'at', 'colorMap', 'xLabel', 'yLabel']:
            if attr in kwargs:
                setattr( self, attr, kwargs[ attr])
                del kwargs[ attr]

        for attr in [ 'flagAxes', 'log']:
            if attr in kwargs:
                setattr( self, attr, bool(kwargs[ attr]))
                del kwargs[ attr]

        for attr in [ 'height', 'maxIter', 'modulo', 'width']:
            if attr in kwargs:
                setattr( self, attr, int(kwargs[ attr]))
                del kwargs[ attr]

        for attr in [ 'estimatedMax', 'xMin', 'xMax', 'yMin', 'yMax']:
            if attr in kwargs:
                setattr( self, attr, float(kwargs[ attr]))
                del kwargs[ attr]

        return 

    def _createImageFromData( self, kwargs): 
        '''
        image data is passed through the keyword data. they are
        copied to self.data as they are
        '''
        if 'data' not in kwargs: 
            raise ValueError( "GQE.Image.createImageFromData: %s no 'data'" % ( self.name))

        self.data = kwargs[ 'data'][:]
        del kwargs[ 'data']

        #
        # to understand '+ 1'consider : x [-2, 1], width 100
        #  if x == 1 -> ix == 100, so we need '+ 1'
        #
        if self.width is not None and self.width != self.data.shape[0]: 
            raise ValueError( "GQE.Image.createImageFromLimits: width %d != shape[0] %d" % 
                              (self.width, self.data.shape[0]))
        if self.height is not None and self.height != self.data.shape[1]: 
            raise ValueError( "GQE.Image.createImageFromLimits: height %d != shape[1] %d" % 
                              (self.height, self.data.shape[1]))

        self.width = self.data.shape[0]
        self.height = self.data.shape[1]

        if self.xMin is None: 
            self.xMin = 0
        if self.xMax is None: 
            self.xMax = float(self.width)
        if self.yMin is None: 
            self.yMin = 0
        if self.yMax is None: 
            self.yMax = float(self.height)

        return 

    def _createImageFromLimits( self, kwargs): 

        for kw in [ 'xMin', 'xMax', 'yMin', 'yMax', 'width', 'height']: 
            if not hasattr( self, kw): 
                raise ValueError( "GQE.Image.createImageFromLimits: %s no %s" % ( self.name, kw))

        self.data  = _np.zeros( ( self.width, self.height))
        #
        # fill the righ column with a linear gradient, max: estimatedMax, to 
        # create some dynamical range for the incoming data
        #
        for i in range( self.height): 
            self.data[ self.width - 1][i] = float(self.estimatedMax)*float(i)/float( self.height)
            
        return 

    def setPixelImage( self, ix = None, iy = None, value = None):
        '''
        ix and iy are in image coordinates
        '''

        if ix < 0 or ix >= self.width:
            raise ValueError( "GQE.Image.setPixelImage: ix %d not in [%d, %d]" % \
                              (ix, 0, self.width))
        if iy < 0 or iy >= self.height:
            raise ValueError( "GQE.Image.setPixelImage: iy %d not in [%d, %d]" % \
                              (iy, 0, self.height))

        self.data[ix][iy] = value

        return 

    def setPixelWorld( self, x = None, y = None, value = None):
        '''
        x and y are in physical coordinates

        Consider this command: 
          mesh exp_dmy01 0 1 5 exp_dmy02 1 2 4 0.1
        it creates a 6x5 image  

        x: [0, 0.2, 0.4, 0.6, 0.8, 1.0] -> ix [0, 1, 2, 3, 4, 5]
      '''
        debug = False

        if x < self.xMin or x > self.xMax:
            raise ValueError( "GQE.Image.setXY: out of x-bounds %g [%g, %g]" % ( x, self.xMin, self.xMax))
        if y < self.yMin or y > self.yMax:
            raise ValueError( "GQE.Image.setXY: out of y-bounds %g [%g, %g]" % ( y, self.yMin, self.yMax))

        ix = int( round( (x - self.xMin)/(self.xMax - self.xMin)*(self.width - 1)))
        iy = int( round( (y - self.yMin)/(self.yMax - self.yMin)*(self.height - 1)))

        if debug: 
            print( "GQE.Image.setPixelWorld: x %g, [%g, %g], ix %d [0, %d]" % (x, self.xMin, self.xMax, ix, self.width - 1))
            print( "                         y %g, [%g, %g], iy %d [0, %d]" % (y, self.yMin, self.yMax, iy, self.height - 1))

        #print( "GQE.Image.setPixelWorld: ix: %d  [%d, %d[, x: %g [%g, %g]" % \
        #                      (ix, 0, self.width, 
        #                       x, self.xMin, self.xMax))

        if ix < 0 or ix >= self.width:
            raise ValueError( "GQE.Image.setPixelWorld: ix %d not in [%d, %d], x: %g [%g, %g]" % \
                              (ix, 0, self.width - 1, 
                               x, self.xMin, self.xMax))
        if iy < 0 or iy >= self.height:
            raise ValueError( "GQE.Image.setPixelWorld: iy %d not in [%d, %d], y: %g [%g, %g]" % \
                              (iy, 0, self.height - 1,
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

        if str(self.name).upper().find( "MANDELBROT") != -1:
            return self.zoom( targetIX, targetIY)

        if not hasattr( self, 'xMin'):
            print( "Gqe.Image.move: %s no attribute xMin" % self.name)
            return 

        if type( self) != Image:
            print( "Gqe.Image.move: %s is not a Image" % self.name)
            return 
            
        targetX = float( targetIX)/float( self.width)*( self.xMax - self.xMin) + self.xMin
        targetY = float( targetIY)/float( self.height)*( self.yMax - self.yMin) + self.yMin
        print( "GQE.Image.move x %g, y %g" % (targetX, targetY))

        if GQE.monitorGui is None:
            if self.logWidget is not None:
                self.logWidget.append( "GQE.Image.move: not called from pyspMonitor") 
            else:
                print( "GQE.Image.move: not called from pyspMonitor")
            return 

        try: 
            proxyX = _PyTango.DeviceProxy( self.xLabel)
        except Exception as e:
            print( "Image.move: no proxy to %s" % self.xLabel)
            print( repr( e))
            return 

        try: 
            proxyY = _PyTango.DeviceProxy( self.yLabel)
        except Exception as e:
            print( "Image.move: no proxy to %s" % self.yLabel)
            print( repr( e))
            return 

        #
        # stop the motors, if they is moving
        #
        if proxyX.state() == _PyTango.DevState.MOVING:
            if self.logWidget is not None:
                self.logWidget.append( "Image.Move: stopping %s" % proxyX.name()) 
            proxyX.stopMove()
        while proxyX.state() == _PyTango.DevState.MOVING:
            _time.sleep(0.01)
        if proxyY.state() == _PyTango.DevState.MOVING:
            if self.logWidget is not None:
                self.logWidget.append( "Image.Move: stopping %s" % proxyY.name()) 
            proxyY.stopMove()
        while proxyY.state() == _PyTango.DevState.MOVING:
            _time.sleep(0.01)

        msg = "Move\n  %s from %g to %g\n  %s from %g to %g " % \
              (proxyX.name(), proxyX.read_attribute( 'Position').value, targetX,
               proxyY.name(), proxyY.read_attribute( 'Position').value, targetY)
        reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No)
        
        if not reply == _QtGui.QMessageBox.Yes:
            if self.logWidget is not None:
                GQE.monitorGui.logWidget.append( "Image.Move: move not confirmed")
            return

        lst = [ "umv %s %g %s %g" % (proxyX.name(), targetX, proxyY.name(), targetY)]
        
        if self.logWidget is not None:
                GQE.monitorGui.logWidget.append( "%s" % (lst[0]))

        GQE.monitorGui.door.RunMacro( lst)
        return 

    def mandelbrot( self, c, maxiter):
        z = c
        for n in range(maxiter):
            if abs(z) > 2:
                return n
            z = z*z + c
        return 0

    def zoomSlow( self, targetIX = None, targetIY = None): 
        print( "GQE.zoom, starting")
        if targetIX is not None and targetIY is not None: 
            targetX = float( targetIX)/float( self.width)*( self.xMax - self.xMin) + self.xMin
            targetY = float( targetIY)/float( self.height)*( self.yMax - self.yMin) + self.yMin
            #print( "GQE.Image.zoom x %g, y %g" % (targetX, targetY))

            deltaX = self.xMax - self.xMin
            deltaY = self.yMax - self.yMin

            self.xMin = targetX - deltaX/8.
            self.xMax = targetX + deltaX/8.

            self.yMin = targetY - deltaY/8.
            self.yMax = targetY + deltaX/8.

        r1 = _np.linspace( self.xMin, self.xMax, self.width)
        r2 = _np.linspace( self.yMin, self.yMax, self.height)
        for i in range( self.width):
            for j in range( self.height):
                res = self.mandelbrot(r1[i] + 1j*r2[j], self.maxIter)
                self.setPixelWorld( x = r1[i], y = r2[j], value = res)

            if (i % 10) == 0:
                _pysp.display()

        _pysp.cls()
        _pysp.display()

        print( "GQE.zoom, DONE")
        #if targetIX is not None:
        #    print( "GQE.Image.zoom x %d, y %d, DONE" % (targetIX, targetIY))
        
        return 

    def mandelbrot_numpy( self):
        
        #print( "GQE.mandelbrot_numpy: xMin %g, xMax %g, width %d" % (self.xMin, self.xMax, self.width))
        #print( "GQE.mandelbrot_numpy: yMin %g, yMax %g, height %d" % (self.yMin, self.yMax, self.height))
        r1 = _np.linspace( self.xMin, self.xMax, self.width, dtype=_np.float64)
        r2 = _np.linspace( self.yMin, self.yMax, self.height, dtype=_np.float64)
        c = r1 + r2[:,None]*1j

        output = _np.zeros(c.shape)
        z = _np.zeros(c.shape, _np.complex128)
        for it in range( self.maxIter):
            notdone = _np.less(z.real*z.real + z.imag*z.imag, 4.0)
            output[notdone] = it
            z[notdone] = z[notdone]**2 + c[notdone]
            if (it % 50) == 0: 
                self.data = output.transpose()
                _pysp.display()
                if self.cbZoomProgress is not None:
                    self.cbZoomProgress( "%d/%d" % ( it, self.maxIter))
        output[output == self.maxIter-1] = 0
        self.data = output.transpose()
        #print( "GQE.mandelbrot_numpy: data %s" % ( str(self.data.shape)))
        
        if self.cbZoomProgress is not None:
            self.cbZoomProgress( "DONE")
        _pysp.cls()
        _pysp.display()
        return 

    def zoom( self, targetIX = None, targetIY = None): 

        if self.flagZoomSlow:
            self.zoomSlow( targetIX, targetIY)
            return 

        if targetIX is not None and targetIY is not None: 
            targetX = float( targetIX)/float( self.width)*( self.xMax - self.xMin) + self.xMin
            targetY = float( targetIY)/float( self.height)*( self.yMax - self.yMin) + self.yMin

            deltaX = self.xMax - self.xMin
            deltaY = self.yMax - self.yMin

            self.xMin = targetX - deltaX/6.
            self.xMax = targetX + deltaX/6.

            self.yMin = targetY - deltaY/6.
            self.yMax = targetY + deltaX/6.

        self.mandelbrot_numpy()
        return 

