#!/bin/env python
'''
GQE - contains the Scan() class and functions to handle scans: 
      delete(), getGqe(), getGqeList(), info(), overlay(), show()
'''
# 1.8.2

import numpy as _numpy
from PyQt4 import QtGui as _QtGui
import PyTango as _PyTango
import PySpectra 
import PySpectra.definitions as definitions 
import PySpectra.utils as utils
import PySpectra.calc as calc
import pyqtgraph as _pyqtgraph
import HasyUtils as _HasyUtils

_gqeList = []
_gqeIndex = None  # used by next/back
_title = None
_comment = None
_scanInfo = None
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
                     'logWidget', 'motorNameList', 
                     'symbol', 'symbolColor', 'symbolSize', 
                     'textList', 'textOnly', 'viewBox', 
                     'x', 'xLog', 'xMax', 'xMin', 
                     'xLabel', 'y', 'yLabel', 'yLog', 'yMin', 'yMax',
                     'yTicksVisible'] 

_ScanAttrsPrivate = [ 'attributeWidget', 'infLineLeft', 'infLineRight', 'infLineMouseX', 'infLineMouseY', 
                      'arrowCurrent', 'labelArrowCurrent', 'arrowSetPoint', 'arrowMisc',    
                      'arrowInvisibleLeft', 'arrowInvisibleRight', 
                      'mousePrepared', 'mouseLabel', 'cb_mouseLabel', 
                      'plotItem', 'plotDataItem', 'scene', 'xDateMpl']

_ImageAttrsPublic = [ 'at', 'colorMap', 'colSpan', 'data', 'estimatedMax', 'flagAxes', 'indexRotate', 
                      'log', 'logWidget', 'maxIter', 'modulo', 
                      'name', 'ncol', 'nplot', 'nrow', 'overlay', 'textOnly', 'xMin', 'xMax',
                      'yMin', 'yMax', 'width', 'height', 'viewBox', 'xLabel', 'yLabel', 'zoomFactor']
#
# img is used in pqt_graphics
#
_ImageAttrsPrivate = [ 'attributeWidget', 'cbZoomMbProgress', 'flagZoomMbSlow', 'flagZoomingMb', 'img', 'plotItem', 'mousePrepared', 'mouseLabel', 'cb_mouseLabel']


class InfoBlock( object): 
    monitorGui = None
    doorProxy = None

    def __init__( self):
        pass
    #
    # the monitorGui is set from pyspMonitorClass.__init__()
    # it is used by misc/tangoIfc.py 
    #
    @staticmethod
    def setMonitorGui( monitorGui): 
        InfoBlock.monitorGui = monitorGui
        if hasattr( monitorGui, 'door'):
            InfoBlock.doorProxy = monitorGui.door
        return 
    #
    # the monitorGui is set from pyspMonitorClass.__init__()
    # it is used by misc/tangoIfc.py 
    #
    @staticmethod
    def getDoorProxy():

        if InfoBlock.doorProxy is not None:
            return InfoBlock.doorProxy

        doorNames = _HasyUtils.getDoorNames()
        if doorNames is None or len( doorNames) == 0: 
            raise ValueError( "GQE.InfoBlocl.setDoorProxy: no doorNames")

        try: 
            InfoBlock.doorProxy = _PyTango.DeviceProxy( doorNames[0])
        except exception as e: 
            print( "GQE.InfoBlock.getDoorProxy: exception %s" % repr( e))
            return None 

        return InfoBlock.doorProxy

class Text(): 
    '''
    Texts are an instance of GQE.Text(). 

    They belong to a Scan, they are created by Scan.addText(), they are stored in Scan.textList.

    Scan.addText() passes the arguments to Text(). Here are the arguments with their defaults: 
      name: 'NoName'
      text: 'Empty'
      x: 0.5
      y: 0.5
      hAlign: 'left' (default), 'right', 'center'
      vAlign: 'top' (default), 'bottom', 'center'
      color: 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'black' (default)
      fontSize: e.g. 12 or None
        if None, the fontsize is chosen automatically depending on the number of plots
      NDC: True, normalized device coordinates, i.e. x, y are from [0, 1]
      tag = 'n.n.', e.g. 'ssa_result'
      ---
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
#
# to understand, why object is needed, goto 'def __setattr__( ...)'
#
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
    PySpectra.Scan( name = "textContainer", textOnly = True)
      no data, just Texts, fill with gqe.addText()

    The attributes of the constructor: 
        autoscaleX, 
        autoscaleY
                    default: True
        comment:    string
                    the global comment
        colSpan:    def.: 1
        doty:       bool
                    if True, the x-axis tick mark labels are dates, def. False
        fileName:   string
        flagMCA     data from MCA, don't use for movements
        motorNameList: 
                    used, if called from moveMotor() or pyspDoor
        showGridX, 
        showGridY:  True/False
        lineColor:  'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'black', 'NONE'
        lineStyle:  'None', 'SOLID', 'DASHED', 'DOTTED', 'DASHDOTTED'
                    if None, the line is not plotted
        lineWidth:  float: 1.0, 1.2, 1.4, 1.6, 1.8, 2.0
                    line width, def.: 1
        overlay:    string 
                    the name of the scan occupying the target viewport 
        symbol:     string
                    o - circle, s - square, t - triangle, d - diamond, + - plus
        symbolColor: 
                    def.: NONE
        symbolSize: float
                    def.: 5
        textOnly:   True/False (def.)
                    if True, Scan has no data, just Texts, fill with addText()
        xLabel,
        yLabel:     string
                    the description of the x- or y-axis
        xLog, 
        yLog:       bool
                    def. False

    To add texts
      Scan.addText()

    '''
    #
    # this class variable stores the Gui, needed to configure the motorsWidget, 
    # which happens for each new scan
    #
    def __init__( self, name = None, **kwargs):
        global _gqeList

        #print( "GQE.Scan: %s" % repr( kwargs))
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
                    _gqeList[i].lastIndex = -1
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

        return 

    def __del__( self): 
        #print( "SCAN.destructor %s" % (self.name)
        return 
    #
    # recursion can be avoided by calling the super class of scan.
    # hence, Scan needs to be an object
    #
    def __setattr__( self, name, value): 
        #print( "GQE.Scan.__setattr__: name %s, value %s" % (name, value))
        if name in _ScanAttrsPublic or \
           name in _ScanAttrsPrivate: 
            super( Scan, self).__setattr__(name, value)
        else: 
            raise ValueError( "GQE.Scan.__setattr__: %s unknown attribute %s" % ( self.name, name))

    def __getattr__( self, name): 
        raise ValueError( "GQE.Scan.__getattr__: %s unknown attribute %s" % ( self.name, name))
        #if name in _ScanAttrsPublic or \
        #   name in _ScanAttrsPrivate: 
        #    return super(Scan, self).__getattr__(name)
        #else: 
        #    raise ValueError( "GQE.Scan.__getattr__: Scan %s unknown attribute name %s" % ( self.name, name))
        
    def checkTargetWithinLimits( self, name, target, proxy, flagConfirm = True): 
        '''
        return False, if the target position is outside the limits
        '''
        #
        # tango servers have UnitLimitMin/Max
        #
        if hasattr( proxy, "UnitLimitMin"): 
            try: 
                if target < proxy.UnitLimitMin: 
                    if flagConfirm: 
                        _QtGui.QMessageBox.about( None, 'Info Box', "%s, target %g < unitLimitMin %g" % 
                                                 ( name, target, proxy.UnitLimitMin))
                    else: 
                        print( "GQE.checkTargetWithinLimits: %s, target %g < unitLimitMin %g" % 
                                                 ( name, target, proxy.UnitLimitMin))
                    return False
                if target > proxy.UnitLimitMax: 
                    if flagConfirm: 
                        _QtGui.QMessageBox.about( None, 'Info Box', "%s, target %g > unitLimitMax %g" % 
                                                 ( name, target, proxy.UnitLimitMax))
                    else: 
                        print( "GQE.checkTargetWithinLimits: %s, target %g > unitLimitMax %g" % 
                                                 ( name, target, proxy.UnitLimitMax))
                    return False
            except Exception as e: 
                if flagConfirm: 
                    _QtGui.QMessageBox.about( None, 'Info Box', "CheckTargetWithinLimits: %s %s" % 
                                             ( name, repr( e)))
                else: 
                    print( "GQE.checkTargetWithinLimits: error %s, %s" % ( name, repr( e)))
                return False
        #
        # pool motors: need to check the attribute configuration
        #
        else: 
            attrConfig = proxy.get_attribute_config_ex( "Position")
            if target < float( attrConfig[0].min_value): 
                if flagConfirm: 
                    _QtGui.QMessageBox.about( None, 'Info Box', "%s, target %g < attrConf.min_value %g" % 
                                             ( name, target, float( attrConfig[0].min_value)))
                else: 
                    print( "GQE.checkTargetWithinLimits: %s, target %g < attrConf.min_value %g" % 
                           ( name, target, float( attrConfig[0].min_value)))
                return False
            if target > float( attrConfig[0].max_value): 
                if flagConfirm: 
                    _QtGui.QMessageBox.about( None, 'Info Box', "%s, target %g > attrConf.max_value %g" % 
                                             ( name, target, float( attrConfig[0].max_value)))
                else: 
                    print( "GQE.checkTargetWithinLimits: %s, target %g > attrConf.max_value %g" % 
                           ( name, target, float( attrConfig[0].max_value)))
                return False
        return True
            

    def _createScanFromData( self, kwargs):
        '''
        creates a scan using x, y
        '''

        if 'y' not in kwargs:
            raise ValueError( "GQE.Scan._createScanFromData: 'y' not supplied")

        self.x = _numpy.copy( kwargs[ 'x'])
        del kwargs[ 'x']
        self.y = _numpy.copy( kwargs[ 'y'])
        del kwargs[ 'y']
        if len( self.x) != len( self.y):
            raise ValueError( "GQE.Scan._createScanFromData: 'x' and 'y' differ in length %d (x) %d (y)" % (len( self.x), len( self.y)))

        if len( self.x) == 0:
            raise ValueError( "GQE.Scan._createScanFromData: %s len(x) == 0" % (self.name))

        self.setLimits()

        self.dType = type( self.x[0])

        self.nPts = len( self.x)
        self.lastIndex = -1
        #
        # currentIndex points to the last valid x- or y-value with nPts == currentIndex + 1
        #
        self.currentIndex = self.nPts - 1

        return

    def _createScanFromLimits( self, kwargs):
        '''
        creates a scan using 
        xMin, def.: 0.
        xMax, def.: 10.
        nPts, def.: 101
        dType, def.: _numpy.float64

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
            self.dType = _numpy.float64
        else:
            self.dType = kwargs[ 'dType']
            del kwargs[ 'dType']
        #
        # the 1.8 version of linspace does not allow to specify the dType
        # 
        self.x = _numpy.linspace( self.xMin, self.xMax, self.nPts)
        if self.x.dtype != self.dType:
            self.x = _numpy.astype( self.dType)
        self.y = _numpy.linspace( self.xMin, self.xMax, self.nPts)
        if self.y.dtype != self.dType:
            self.y = _numpy.astype( self.dType)

        if self.yMin is None:
            self.yMin = self.xMin
        if self.yMax is None:
            self.yMax = self.xMax
        #
        # the currentIndex points to the last valid point.
        # it starts at 0.
        #
        self.lastIndex = -1
        self.currentIndex = self.nPts - 1
            
        return

    def setAttr( self, kwargs):
        '''
        set the graphics attributes of a scan, see docu in Scan()

        Returns None
        '''

        self.arrowCurrent = None
        self.arrowSetPoint = None
        self.arrowMisc = None # for e.g. mvsa
        self.labelArrowCurrent = None
        self.arrowInvisibleLeft = None
        self.arrowInvisibleRight = None
        self.at = None
        self.attributeWidget = None
        self.autoscaleX = True
        self.autoscaleY = True
        self.colSpan = 1
        self.doty = False            # x-axis is date-of-the year
        self.fileName = None
        self.flagDisplayVLines = False
        self.flagMCA = False
        self.nrow = None
        self.ncol = None
        self.nplot = None
        self.overlay = None
        self.useTargetWindow = False
        self.infLineLeft = None
        self.infLineRight = None
        self.infLineMouseX = None
        self.infLineMouseY = None
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
        #
        # motorNameList from moveMotor.py or graPyspIfc.py
        #
        self.motorNameList = None
        self.mousePrepared = False
        self.cb_mouseLabel = None
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
                      'xLog', 'yLog', 'logWidget', 'motorNameList', 
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
            if str(kwargs[ attr]) in definitions.lineWidthArr:
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
            if type( atStr) is tuple or type( atStr) is list:
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
        self.xMin = _numpy.min( self.x)
        self.xMax = _numpy.max( self.x)
        self.yMin = _numpy.min( self.y)
        self.yMax = _numpy.max( self.y)
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
        currentIndex refers to the last valid x-, y-value; nPts == currentIndex + 1

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
        currentIndex refers to the last valid x-, y-value; nPts == currentIndex + 1

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
        currentIndex refers to the last valid x-, y-value; nPts == currentIndex + 1

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

    def getIndex( self, x): 
        '''
        return the index which is closest to x
        '''

        #
        # getIndex() makes sense only, if the x-values are ordered
        # 1. test: normal direction: left-right?
        flagLeftToRight = True
        #
        # range( currentIndex) and not range( currentIndex + 1) 
        # because inside the loop we refer to x[i + 1]
        #
        for i in range( self.currentIndex):   
            if self.x[i] > self.x[i + 1]:
                flagLeftToRight = False
                break
        # 2. test: reverse direction: right-left? can be created by motor moves
        if not flagLeftToRight: 
            for i in range( self.currentIndex): 
                if self.x[i] < self.x[i + 1]:
                    raise ValueError( "GQE.getIndex: %s, x-values are not ordered in either direction, return" % ( self.name))

        if flagLeftToRight: 
            if x < self.x[0]: 
                raise ValueError( "GQE.getIndex(L2R): x %g < x[0] %g" % ( x, self.x[0]))
            if x > self.x[ self.currentIndex]: 
                raise ValueError( "GQE.getIndex(L2R): x %g > x[currentIndex] %g" % 
                                  ( x, self.x[ self.currentIndex]))

            argout = None
            for i in range( self.currentIndex): 
                if x >= self.x[i] and x < self.x[i + 1]:
                    if (x - self.x[i]) < (self.x[i+1] - x): 
                        argout = i
                    else: 
                        argout = i + 1
                        break
        else: 
            if x < self.x[ self.currentIndex]: 
                raise ValueError( "GQE.getIndex(R2L): x %g < x[currentIndex] %g" % ( x, self.x[ self.currentIndex]))
            if x > self.x[0]: 
                raise ValueError( "GQE.getIndex(R2L): x %g > x[0] %g" % 
                                  ( x, self.x[ 0]))

            argout = None
            for i in range( self.currentIndex): 
                if x < self.x[i] and x >= self.x[i + 1]:
                    if (self.x[i] - x) < (x - self.x[i+1]): 
                        argout = i
                    else: 
                        argout = i + 1
                        break

        if argout is None: 
            raise ValueError( "GQE.getIndex: something is wrong: x %g [%g, %g]" % 
                              (x, self.x[0], self.x[self.currentIndex]))
        return argout
 
    def getYMin( self): 
        '''
        returns the minimum of the y-values
        '''
        # currentIndex refers to the last valid x-, y-value; nPts == currentIndex + 1
        return _numpy.min( self.y[:self.currentIndex + 1])

    def getYMax( self): 
        '''
        returns the maximum of the y-values
        '''
        # currentIndex refers to the last valid x-, y-value; nPts == currentIndex + 1
        return _numpy.max( self.y[:self.currentIndex + 1])

    def setArrowCurrent( self, x): 
        '''
        set the position of the arrow pointing to the current motor position

        to be taken into account: 
          - try to plot the arrow at a constant height
          - the arrow should always by visible, esp. when used from moveMotor(). 
            In this case the motor always is heading towards outside of the
            plot. To ensure that it stays visible, the arrow is plotted to 
            the ViewBox and there are 2 invisible arrows left and right of its 
            position which should be taken into account by the autoscale 
            procedure.
        '''

        if self.arrowInvisibleLeft is not None: 
            delta = 1.
            if self.currentIndex > 0: 
                delta = (self.x[ self.currentIndex] - self.x[self.currentIndex - 1])*2.
            xScene = 300
            yScene = PySpectra.getGraphicsWindowHeight() - definitions.ARROW_Y_OFFSET*2
            posVb = self.plotItem.vb.mapSceneToView( _pyqtgraph.Point( xScene, yScene))
            self.arrowInvisibleLeft.setPos( x - delta, posVb.y())
            self.arrowInvisibleRight.setPos( x + delta, posVb.y())
            self.arrowInvisibleLeft.show()
            self.arrowInvisibleRight.show()

        if self.motorNameList is None or len( self.motorNameList) == 0:
            raise ValueError( "GQE.setArrowCurrent: motorNameList empty or None")

        yScene = PySpectra.getGraphicsWindowHeight() - definitions.ARROW_Y_OFFSET
        if self.xLabel is not None: 
            yScene = yScene - definitions.ARROW_Y_OFFSET_EXTRA
        posScene = self.plotItem.vb.mapViewToScene( _pyqtgraph.Point( x, self.getYMin()))
        self.arrowCurrent.setPos( posScene.x(), yScene)
        self.labelArrowCurrent.setPos(  posScene.x(), yScene)
        self.labelArrowCurrent.setHtml( '<div>%s: %g</div>' % ( self.motorNameList[0], x))

        self.arrowCurrent.show()
        self.labelArrowCurrent.show()

        PySpectra.processEvents()

        return

    def setArrowSetPoint( self, x): 
        '''
        set the position of the arrow pointing to the set-point
        '''
        xScene = 300
        yScene = PySpectra.getGraphicsWindowHeight() - definitions.ARROW_Y_OFFSET
        if self.xLabel is not None: 
            yScene = yScene - definitions.ARROW_Y_OFFSET_EXTRA
        posScene = self.plotItem.vb.mapViewToScene( _pyqtgraph.Point( x, self.getYMin()))
        self.arrowSetPoint.setPos( posScene.x(), yScene)
        #posVb = self.plotItem.vb.mapSceneToView( _pyqtgraph.Point( xScene, yScene)).toPoint()
        #self.arrowSetPoint.setPos( x, posVb.y())
        self.arrowSetPoint.show()

        PySpectra.processEvents()

        return

    def setArrowMisc( self, x): 
        '''
        set the position of the arrow pointing to Misc
        '''
        xScene = 300
        yScene = PySpectra.getGraphicsWindowHeight() - definitions.ARROW_Y_OFFSET
        if self.xLabel is not None: 
            yScene = yScene - definitions.ARROW_Y_OFFSET_EXTRA
        posScene = self.plotItem.vb.mapViewToScene( _pyqtgraph.Point( x, self.getYMin()))
        self.arrowMisc.setPos( posScene.x(), yScene)

        #posVb = self.plotItem.vb.mapSceneToView( _pyqtgraph.Point( xScene, yScene)).toPoint()
        #self.arrowMisc.setPos( x, posVb.y())
        self.arrowMisc.show()

        PySpectra.processEvents()

        return

    def updateArrowCurrent( self):
        '''
        updates the arrow pointing to the current position of the motor. 
        called from: 
          - pySpectraGuiClass.py, time-out callback
          - tngGui/lib/moveMotor.py
        '''
        #
        # arrowCurrent can be None, if
        #   - display() hasn't been called yet
        #   - more than one Scan is on the display
        #
        if self.arrowCurrent is None:
            return

        #
        # called from the moveMotor menu
        #
        if self.motorNameList is None or len( self.motorNameList) == 0:
            raise ValueError( "GQE.updateArrowCurrent: motorNameList is None or empty")

        proxy = _PyTango.DeviceProxy( self.motorNameList[0])
        motName = self.motorNameList[0]

        self.setArrowCurrent( proxy.position)

        #
        # we check the existence of arrowSetPoint although arrowCurrent
        # was checked before (and both are created at the same time)
        # because the 2 'display' paths pyspDoor and  
        # PySpectraGuiClass.cb_refreshPySpectraGui() may interfere destructively
        #
        if self.arrowSetPoint is not None: 
            if proxy.state() == _PyTango.DevState.ON: 
                self.arrowSetPoint.hide()
                
        return

    def setArrowCurrentCmd( self, lst): 
        '''
        handle the arrow pointing to the current position
          'setArrowCurrent sig_gen position 50.6'
          'setArrowCurrent sig_gen hide'
          'setArrowCurrent sig_gen show'

          lst: 
            - 'position', '<motName>', '<pos>'
            - 'hide'
            - 'show'
        used from mvsa, via toPyspMonitor(). 
        '''
        
        if self.arrowSetPoint is None:
            self.display()

        if len( lst) == 1 and lst[0].upper() == 'HIDE': 
            self.arrowCurrent.hide()
        elif len( lst) == 1 and lst[0].upper() == 'SHOW': 
            self.arrowCurrent.show()
        elif len( lst) == 2 and lst[0].upper() == 'POSITION': 
            x = float( lst[1])
            self.setArrowCurrent( x)
        else: 
            raise ValueError( "GQE.setArrowCurrent: strange list %s" % str( lst))
                                    
        return 

    def setArrowSetPointCmd( self, lst): 
        '''
        handle the arrow pointing to the target position
          'setArrowSetPoint sig_gen position 50.6'
          'setArrowSetPoint sig_gen hide'
          'setArrowSetPoint sig_gen show'
          lst: 
            - 'position', '<pos>'
            - 'hide'
            - 'show'
        used from 
          - pqtgraphic, mouse click
        '''
        
        if self.arrowSetPoint is None:
            self.display()

        if len( lst) == 1 and lst[0].upper() == 'HIDE': 
            self.arrowSetPoint.hide()
        elif len( lst) == 1 and lst[0].upper() == 'SHOW': 
            self.arrowSetPoint.show()
        elif len( lst) == 2 and lst[0].upper() == 'POSITION': 
            x = float( lst[1])
            self.setArrowSetPoint( x)
        else: 
            raise ValueError( "GQE.setArrowSetPoint: strange list %s" % str( lst))
                                    
        return 

    def setArrowMiscCmd( self, lst): 
        '''
        handle the arrow pointing to a target position defined by e.g. mvsa
          'setArrowMisc sig_gen position 50.6'
          'setArrowMisc sig_gen hide'
          'setArrowMisc sig_gen show'
          lst: 
            - 'position', '<pos>'
            - 'hide'
            - 'show'
        used from 
          - mvsa
        '''

        if self.arrowSetPoint is None:
            self.display()

        if len( lst) == 1 and lst[0].upper() == 'HIDE': 
            self.arrowMisc.hide()
        elif len( lst) == 1 and lst[0].upper() == 'SHOW': 
            self.arrowMisc.show()
        elif len( lst) == 2 and lst[0].upper() == 'POSITION':
            x = float( lst[1])
            self.setArrowMisc( x)
        else: 
            raise ValueError( "GQE.setArrowMisc: strange list %s" % str( lst))
                                    
        return 
        
    def sort( self): 
        '''
        put this functions in because it is in Spectra, I don't know
        whether we really need it in pysp. reserve scans do not make 
        any problems in _pyqtgraph. however, in matplotlib it plots
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
        PySpectra.display( [self.name])
        return 

    def yGreaterThanZero( self): 
        '''
        prepare for log display: remove points with y <= 0. 
        '''
        x = _numpy.copy( self.x)
        y = _numpy.copy( self.y)
        count = 0
        for i in range( len( self.y)):
            if self.y[i] <= 0.:
                continue
            x[count] = self.x[i]
            y[count] = self.y[i]
            count += 1
        self.x = _numpy.copy( x[:count])
        self.y = _numpy.copy( y[:count])
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
            lstX = self.x[:self.currentIndex + 1]
            lstY = self.y[:self.currentIndex + 1]
            if logWidget is not None:
                logWidget.append( "ssa: %s total x-range" % (self.name))
        #
        # reversed x-values?
        #
        if lstX[0] > lstX[-1]:
            lstX = list( reversed( lstX))
            lstY = list( reversed( lstY))
                
        hsh = calc.ssa( _numpy.array( lstX), _numpy.array( lstY))

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
                if t.tag.lower() == 'fsa_result':
                    continue
                if t.tag.lower() == 'ssa_result':
                    continue
                lst.append( t)
            self.textList = lst[:]
        
        self.addText( text = "SSA results", x = 0.02, y = 1.00, hAlign = 'left', vAlign = 'top', tag = 'ssa_result')
        self.addText( text = "midpoint: %g" % hsh[ 'midpoint'], x = 0.02, y = 0.95, hAlign = 'left', vAlign = 'top', tag = 'ssa_result')
        self.addText( text = "peak-x:   %g" % hsh[ 'peak_x'], x = 0.02, y = 0.90, hAlign = 'left', vAlign = 'top', tag = 'ssa_result')
        self.addText( text = "cms:      %g" % hsh[ 'cms'], x = 0.02, y = 0.85, hAlign = 'left', vAlign = 'top', tag = 'ssa_result')
        self.addText( text = "fwhm:     %g" % hsh[ 'fwhm'], x = 0.02, y = 0.80, hAlign = 'left', vAlign = 'top', tag = 'ssa_result')

        ssaName = '%s_ssa' % self.name
        count = 1
        while getGqe( ssaName): 
            ssaName = '%s_ssa_%-d' % (self.name, count)
            count += 1
            
        res = Scan( name = ssaName, x = self.x[:self.currentIndex + 1], y = self.y[:self.currentIndex + 1],
                    lineColor = 'None', 
                    symbolColor = 'blue', symbolSize = 5, symbol = '+')

        a = hsh[ 'integral']
        mu = hsh[ 'midpoint'] 
        sigma = hsh[ 'fwhm']/2.3548
        
        res.y = a/(sigma*_numpy.sqrt(2.*_numpy.pi))*_numpy.exp( -(res.x-mu)**2/(2*sigma**2))
        res.overlay = self.name
        res.useTargetWindow = True
        return 

    def fsa( self, logWidget = None):
        '''
        calls HasyUtils.fastscananalysis(), author Michael Sprung
        returns: (message, xpos, xpeak, xcms, xcen)
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
            lstX = self.x[:self.currentIndex + 1]
            lstY = self.y[:self.currentIndex + 1]
            if logWidget is not None:
                logWidget.append( "fsa: %s total x-range" % (self.name))
        #
        # reversed x-values?
        #
        if lstX[0] > lstX[-1]:
            lstX = list( reversed( lstX))
            lstY = list( reversed( lstY))
                
        try: 
            message, xpos, xpeak, xcms, xcen = calc.fastscananalysis( lstX, lstY, mode)
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


        #
        # clear the text list. Otherwise several SSA results will appear on the screen.
        #
        if len( self.textList) > 0:
            lst = []
            for t in self.textList:
                if t.tag.lower() == 'fsa_result':
                    continue
                if t.tag.lower() == 'ssa_result':
                    continue
                lst.append( t)
            self.textList = lst[:]

        self.addText( text = "FSA results", x = 0.02, y = 1.00, hAlign = 'left', vAlign = 'top', tag = 'fsa_result')
        self.addText( text = "xpos: %g" % xpos, x = 0.02, y = 0.95, hAlign = 'left', vAlign = 'top', tag = 'fsa_result')
        self.addText( text = "xpeak:   %g" % xpeak, x = 0.02, y = 0.90, hAlign = 'left', vAlign = 'top', tag = 'fsa_result')
        self.addText( text = "xcms:      %g" % xcms, x = 0.02, y = 0.85, hAlign = 'left', vAlign = 'top', tag = 'fsa_result')
        self.addText( text = "xcen:     %g" % xcen, x = 0.02, y = 0.80, hAlign = 'left', vAlign = 'top', tag = 'fsa_result')



        return (message, xpos, xpeak, xcms, xcen)


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
    if text is None or len( text) == 0:
        _title = None
        return True
    text = text.replace( "'", "")
    text = text.replace( '"', '')
    _title = text
    return True

def getTitle():
    return _title

def setComment( text = None): 
    '''
    the comment line appears across all columns below the title

    the comment is cleared, if no argument is supplied or if 
    the text has zero length

    delete() also clears the comment
    '''
    global _comment 
    if text is None or len( text) == 0:
        _comment = None
        return True
    text = text.replace( "'", "")
    text = text.replace( '"', '')

    _comment = text
    return True

def getComment():
    return _comment

def delete( nameLst = None):
    '''
    if nameLst is supplied, delete the specified scans from the gqeList
    otherwise delete all scans

    PySpectra.GQE.delete( ["t1"])
      delete the scan t1

    PySpectra.GQE.delete( ["t1", "t2"])
      delete t1 and t2

    PySpectra.GQE.delete( "t1")
      delete the scan t1, also OK

    PySpectra.GQE.delete()
      delete all scans
    '''
    global _gqeIndex

    #print( "GQE.delete, nameList: %s" % repr( nameLst))
    #print( "GQE.delete: %s" % repr( _HasyUtils.getTraceBackList()))

    #
    # delete everything
    #
    if not nameLst:
        while len( _gqeList) > 0:
            tmp = _gqeList.pop()
            PySpectra.clear( tmp)
            if tmp.attributeWidget is not None: 
                tmp.attributeWidget.close()
            del tmp
            _gqeIndex = None
        setTitle( None)
        setComment( None)
        return 
    #
    # delete a single GQE
    #
    if type( nameLst) is not list:
        name = nameLst
        for i in range( len( _gqeList)):
            if name.upper() != _gqeList[i].name.upper():
                continue
            PySpectra.clear( _gqeList[i])
            if _gqeList[i].attributeWidget is not None: 
                _gqeList[i].attributeWidget.close()
            del _gqeList[i]
            break
        else:
            print( "GQE.delete (single): %s" % repr( _HasyUtils.getTraceBackList()))
            raise ValueError( "GQE.delete: not found %s" % name)
        return 
    #
    # delete a list of GQEs
    #
    for name in nameLst:
        for i in range( len( _gqeList)):
            if name.upper() != _gqeList[i].name.upper():
                continue
            PySpectra.clear( _gqeList[i])
            if _gqeList[i].attributeWidget is not None: 
                _gqeList[i].attributeWidget.close()
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

    Module: PySpectra.GQE.py
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
            raise ValueError( "GQE.prevScan: failed to find the previous Scan")

    return _gqeList[ _gqeIndex]

def nextImage( name = None):
    '''
    nextImage/prevImage return the next/previous scan object
    '''
    global _gqeIndex

    if len( _gqeList) == 0:
        raise ValueError( "GQE.nextImage: gqe list empty")

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
        raise ValueError( "GQE.prevImage: scan list empty")

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
            raise ValueError( "GQE.prevImage: failed to find the previous Image")

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

def _insertFioObj2Image( fioObj):
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

    data = _numpy.array( fioObj.columns[0].x).reshape(  fioObj.parameters[ 'width'],  fioObj.parameters[ 'height'])
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

    fioObj = _HasyUtils.fioReader( fileName, flagMCA)

    if fioObj.isImage:
        return _insertFioObj2Image( fioObj); 

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
        if type( gqe) is Scan: 
            if length is None:
                length = len( gqe.x)
            if length != len( gqe.x):
                raise ValueError( "GQE.write: output GQEs differ in length")
        if type( gqe) is Image: 
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
            if type( gqe) is Scan: 
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
    if type(x) is list or type(x) is _numpy.ndarray:
        return True
    else:
        return False

def getFontSize( nameList): 
    '''
    depending on how many gqes are displayed the font size is adjusted
    '''
    if utils.getNumberOfGqesToBeDisplayed( nameList) < definitions.MANY_GQES:
        fontSize = definitions.FONT_SIZE_NORMAL
    elif utils.getNumberOfGqesToBeDisplayed( nameList) <= definitions.VERY_MANY_GQES:
        fontSize = definitions.FONT_SIZE_SMALL
    else: 
        fontSize = definitions.FONT_SIZE_VERY_SMALL

    return fontSize

def getData():
    '''
    pack the interesting part of the PySpectra storage which has been
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

    if _scanInfo is not None: 
        hsh[ 'symbols'] = {}
        temp = _scanInfo[ 'filename']
        if type( temp) is list:
            hsh[ 'symbols'][ 'file_name_'] = temp[0]
        else:
            hsh[ 'symbols'][ 'file_name_'] = temp
    return hsh

#
# to understand, why object is needed, goto 'def __setattr__( ...)'
#
class Image( object):
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
        self.cbZoomMbProgress = None
        self.attributeWidget = None
        self.flagZoomMbSlow = None
        self.flagZoomingMb = False

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

    #
    # recursion can be avoided by calling the super class of scan.
    # hence, Scan needs to be an object
    #
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
        self.cb_mouseLabel = None
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
        self.zoomFactor = 4. 
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
        # if data come as a list, convert them to numpy arrays
        #
        if type( self.data) is list: 
            for kw in [ 'width', 'height']: 
                if not hasattr( self, kw): 
                    raise ValueError( "GQE.Image.createImageFromData: %s no %s" % ( self.name, kw))
            np_array = _numpy.asarray( self.data, _numpy.float64)
            #self.data = np_array.reshape( self.width, self.height).T 
            self.data = np_array.reshape( self.width, self.height)

        elif type( self.data) is _numpy.ndarray: 
            if self.width is not None and self.width != self.data.shape[0]: 
                raise ValueError( "GQE.Image.createImageFromLimits: width %d != shape[0] %d" % 
                                  (self.width, self.data.shape[0]))
            if self.height is not None and self.height != self.data.shape[1]: 
                raise ValueError( "GQE.Image.createImageFromLimits: height %d != shape[1] %d" % 
                                  (self.height, self.data.shape[1]))
            self.width = self.data.shape[0]
            self.height = self.data.shape[1]

        else: 
            raise ValueError( "GQE.Image.createImageFromData: wrong data type %s" % type( self.data))


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

        self.data  = _numpy.zeros( ( self.width, self.height))
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

        return True

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
    # 
    #
    def shift( self, targetIX, targetIY): 
        '''
        this function is invoked by a middel-button mouse click from pqtgrph/graphics.py
        '''

        if str(self.name).upper().find( "MANDELBROT") != -1:
            return self.zoomMb( targetIX, targetIY, True)

        return 

    '''
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

        r1 = _numpy.linspace( self.xMin, self.xMax, self.width)
        r2 = _numpy.linspace( self.yMin, self.yMax, self.height)
        for i in range( self.width):
            for j in range( self.height):
                res = self.mandelbrot(r1[i] + 1j*r2[j], self.maxIter)
                self.setPixelWorld( x = r1[i], y = r2[j], value = res)

            if (i % 10) == 0:
                PySpectra.display()

        PySpectra.cls()
        PySpectra.display()

        print( "GQE.zoom, DONE")
        #if targetIX is not None:
        #    print( "GQE.Image.zoom x %d, y %d, DONE" % (targetIX, targetIY))
        
        return 
    '''

    def mandelbrot_numpy( self, flagDisplay = True):
        
        #print( "GQE.mandelbrot_numpy: xMin %g, xMax %g, width %d" % (self.xMin, self.xMax, self.width))
        #print( "GQE.mandelbrot_numpy: yMin %g, yMax %g, height %d" % (self.yMin, self.yMax, self.height))
        r1 = _numpy.linspace( self.xMin, self.xMax, self.width, dtype=_numpy.float64)
        r2 = _numpy.linspace( self.yMin, self.yMax, self.height, dtype=_numpy.float64)
        c = r1 + r2[:,None]*1j

        output = _numpy.zeros(c.shape)
        z = _numpy.zeros(c.shape, _numpy.complex128)
        for it in range( self.maxIter):
            notdone = _numpy.less(z.real*z.real + z.imag*z.imag, 4.0)
            output[notdone] = it
            z[notdone] = z[notdone]**2 + c[notdone]
            if (it % 20) == 0: 
                self.data = output.transpose()
                if flagDisplay: 
                    PySpectra.display()
                if self.cbZoomMbProgress is not None:
                    self.cbZoomMbProgress( "%d/%d" % ( it, self.maxIter))
        output[output == self.maxIter-1] = 0
        self.data = output.transpose()
        #print( "GQE.mandelbrot_numpy: data %s" % ( str(self.data.shape)))
        
        if self.cbZoomMbProgress is not None:
            self.cbZoomMbProgress( "DONE")

        if flagDisplay: 
            PySpectra.cls()
            PySpectra.display()

        return 

    def zoomMb( self, targetIX = None, targetIY = None, flagShift = False, flagDisplay = True): 
        """
        'Mb' because of Mandelbrot
        """
        self.flagZoomingMb = True

        #if self.flagZoomMbSlow:
        #    self.zoomSlow( targetIX, targetIY)
        #    self.flagZoomingMb = False
        #    return 

        if targetIX is not None and targetIY is not None: 
            targetX = float( targetIX)/float( self.width)*( self.xMax - self.xMin) + self.xMin
            targetY = float( targetIY)/float( self.height)*( self.yMax - self.yMin) + self.yMin

            deltaX = self.xMax - self.xMin
            deltaY = self.yMax - self.yMin

            if not flagShift: 
                deltaX = deltaX/2./self.zoomFactor
                deltaY = deltaY/2./self.zoomFactor

                self.xMin = targetX - deltaX
                self.xMax = targetX + deltaX

                self.yMin = targetY - deltaY
                self.yMax = targetY + deltaY
            else: 
                self.xMin = targetX - deltaX/2.
                self.xMax = targetX + deltaX/2.

                self.yMin = targetY - deltaY/2.
                self.yMax = targetY + deltaX/2.

        self.mandelbrot_numpy( flagDisplay = flagDisplay)
        self.flagZoomingMb = False
        return 


