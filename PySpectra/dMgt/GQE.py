#!/bin/env python
'''
GQE - contains the Scan() class and functions to handle scans: 
      delete(), getScan(), getScanList(), show(), overlay(), show()
'''
# 1.8.2

import numpy as _np
import PySpectra as _PySpectra
import HasyUtils as _HasyUtils
from taurus.external.qt import QtGui as _QtGui
from taurus.external.qt import QtCore as _QtCore
import PyTango as _PyTango

_scanList = []
_scanIndex = None  # used by next/back
_title = None
_comment = None
#
# if the wsViewport is set, e.g. to dina4, it is fixed, i.e. independent 
# of how many scans are displayed 
#
_wsViewportFixed = False

ScanAttrs = [ 'at', 'autorangeX', 'autorangeY', 'colSpan', 'color', 'currentIndex', 
              'dType', 'doty', 'fileName', 'lastIndex', 
              'nPts', 'name', 'ncol', 'nplot', 'nrow', 'overlay', 'showGridX', 
              'showGridY', 'style', 'textList', 'width', 'xLabel', 'xMax', 'xMin',
              'xLabel', 'yLabel', 'yMin', 'yMax'] 

class Text(): 
    '''
    Texts live on the viewport of a scan. Therefore: x [0., 1.], y [0., 1.]
    hAlign: 'left', 'right', 'center'
    vAlign: 'top', 'bottom', 'center'
    '''
    def __init__( self, text = 'Empty', x = 0.5, y = 0.5, 
                  hAlign = 'left', vAlign = 'top', color = 'black'): 

        self.text = text
        self.x = x
        self.y = y
        self.hAlign = hAlign
        self.vAlign = vAlign
        self.color = color
'''
A value of (0,0) sets the upper-left corner
                     of the text box to be at the position specified by setPos(), while a value of (1,1)
                     sets the lower-right corner.        
'''
class Scan():
    '''
    create a scan
      - a scan contains 2 arrays, x and y, and graphics attributes

    PySpectra.Scan( name = 'name', filename = 'test.fio', x = 1, y = 2)
    PySpectra.Scan( name = 'name', x = xArr, y = yArr)
    PySpectra.Scan( name = 'name', xMin = 0., xMax = 10., nPts = 101)
    PySpectra.Scan( name = 'name')
      the same as PySpectra.Scan( name = 'name', xMin = 0., xMax = 10., nPts = 101)
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
        # noData means no texts
        #
        if 'textOnly' in kwargs:
            self.textOnly = True
            del kwargs[ 'textOnly']
            pass
        #    
        # 'fileName': data are read from a file
        #    
        elif 'fileName' in kwargs: 
            if 'x' not in kwargs or 'y' not in kwargs:
                raise ValueError( "GQE.Scan.__init__: 'fileName' but no 'x' and 'y', %s" % kwargs[ 'fileName'])
            fioCol = read( kwargs[ 'fileName'], kwargs[ 'x'], kwargs[ 'y'])
            kwargs[ 'x']= fioCol.x
            kwargs[ 'y']= fioCol.y
            self._createScanFromData( kwargs)
        #
        # if 'x' and 'y' are supplied the scan is created using data
        #
        elif 'x' in kwargs:
            self._createScanFromData( kwargs)
        #
        # otherwise we use limits and the limits have defaults
        #
        else:
            self._createScanFromLimits( kwargs)

        #
        # if we store the scan also in the module name space, we 
        # can access it via e.g.: pysp.t1
        #
        _PySpectra.__dict__[ name] = self
        
        self.setAttr( kwargs)

        if kwargs:
            raise ValueError( "GQE.Scan: dct not empty %s" % str( kwargs))
        
        self.textList = []

        _scanList.append( self)

    @staticmethod
    def move( target): 
        #print "GQE.Scan.move: to", target, "using", Scan.monitorGui.scanInfo
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
        r = (motorArr[motorIndex]['targetPos'] - motorArr[motorIndex]['start']) / (motorArr[motorIndex]['stop'] - motorArr[motorIndex]['start']) 

        if length == 1:
            p0 = _PyTango.DeviceProxy( motorArr[0]['name'])
            msg = "Move %s from %s to %s" % (motorArr[0]['name'], 
                                             repr(p0.read_attribute( 'Position').value), 
                                             repr(motorArr[0]['targetPos']))
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
        self.xMin = _np.min( self.x)
        self.xMax = _np.max( self.x)
        self.yMin = _np.min( self.y)
        self.yMax = _np.max( self.y)

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
          if yMin is None, autorange will be enabled for y
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
        #
        # the currentIndex points to the last valid point.
        # it starts at 0.
        #
        self.lastIndex = 0
        self.currentIndex = self.nPts - 1
            
        return

    def setAttr( self, kwargs):
        '''
        set the graphics attributes of a scan

        Parameters
        ----------
        name:    string
                 The name of the scan
        autorangeX, autorangeY
                 if you know the x-range beforehand, set autorangeY to False
        color:   'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'black'
        colSpan: def.: 1
        doty:    def. False
        fileName 
        overlay: string 
                 the name of the scan occupying the target viewport 
        showGridX, 
        showGridY: True/False
        style:   'SOLID', 'DASHED', 'DOTTED', 'DASHDOTTED', 'DASHDOTDOTTED'
        symbol:  o, s, t, d, +,
        width:   float: 1.0, 1.2, 1.4, 1.6, 1.8, 2.0
                 line width, def.: 1
        xLabel:  string
                 the description of the x-axis, def. 'position'
        yLabel:  string
                 the description of the y-axis, def. 'signal'

        Returns
        -------
        None
        '''

        self.at = None
        self.autorangeX = False
        self.autorangeY = True
        self.color = 'red'
        self.colSpan = 1
        self.doty = False            # x-axis is date-of-the year
        self.fileName = None
        self.plotItem = None
        self.showGridX = False
        self.showGridY = False
        self.width = 1.
        self.style = 'SOLID'
        self.xLabel = 'position'
        self.yLabel = 'signal'
        self.overlay = None
        #
        # the attributes plot and mouseLabel are created by graphics.display(). 
        # However, it is initialized here to help cls()
        #
        self.plotItem = None
        self.mouseLabel = None
        self.mouseProxy = None

        for attr in [ 'autorangeX', 'autorangeY', 'color', 'colSpan', 'doty', 'fileName',  
                      'ncol', 'nrow', 'nplot', 'overlay', 'showGridX', 'showGridY', 
                      'style', 'symbol', 'xLabel', 'yLabel', 'yMin', 'yMax']:
            if attr in kwargs:
                setattr( self, attr, kwargs[ attr])
                del kwargs[ attr]

        attr = 'width'
        if attr in kwargs:
            if str(kwargs[ attr]) in pysp.widthArr:
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

    def addText( self, text = 'Empty', x = 0.5, y = 0.5, hAlign = 'left', vAlign = 'top', color = 'black'):
        '''
        Creates a text 

        The object is appended to the textList of the scan.

        Parameters: 
        -----------
        x, y: float
          the coordinates w.r.t the viewbox [0., 1.0]
        hAlign: 'left', 'center', 'right'
        vAlign: 'top', 'center', 'bottom'
        color:  'red', 'green', ...
        '''
        txt = Text( text, x, y, hAlign, vAlign, color)
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
                              ( self.name, index, self.y.size))
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
                              ( self.name, index, self.x.size))
        self.x[ index] = xValue
        self.currentIndex = index
        return

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

def getScanList():
    '''
    returns the list of scans
    '''
    return _scanList

def getDisplayList(): 
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
        if name == scan.name:
            return scan
    return None

def setTitle( text = None): 
    '''
    the title appears across all columns

    the title is cleared, if no argument is supplied
    delete() also clears the title
    '''
    global _title 
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

    PySpectra.delete()
      delete all scans
    '''
    global _scanIndex
    #print "GQE.delete, nameList:", repr( nameLst)
    
    if not nameLst:    
        while len( _scanList) > 0:
            tmp = _scanList.pop()
            if tmp.plotItem is not None:
                tmp.plotItem.clear()
            del _PySpectra.__dict__[ tmp.name]
            _scanIndex = None
        setTitle( None)
        setComment( None)
        return 

    for name in nameLst:
        for i in range( len( _scanList)):
            if name == _scanList[i].name:
                #
                # we had many MCA spectra displayed on top of each other
                #
                if _scanList[i].plotItem is not None:
                    _scanList[i].plotItem.clear()
                del _PySpectra.__dict__[ _scanList[i].name]
                del _scanList[i]
                break
        else:
            print "GQE.delete: not found", name

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
    
def show( scanName = None):
    '''
    if no scan is supplied, prints the contents of scanList
    '''

    if scanName is not None:
        scan = getScan( scanName)
        _showScan( scan)
        return 

    if not _scanList:
        print "GQE.show: scanList is empty"
        return 

    print "The List of Scans:"
    for scan in _scanList:
        _showScan( scan)

    _PySpectra.listGraphicsItems()

    print " %s scans" % count

    if _title: 
        print "Title:  ", _title
    if _comment: 
        print "Comment:", _comment

def _showScan( scan): 
    '''
    '''
    print "--- \n", scan.name
    for attr in ScanAttrs:
        try:
            print "%s -> %s" % ( attr, repr( getattr( scan, attr)))
        except Exception, e:
            print "GQE._showScan: trouble with", scan.name
            print repr( e)

def nextScan():
    '''
    nextScan/prevScan return the next/previous scan objec
    '''
    global _scanIndex

    if len( _scanList) == 0:
        raise ValueError( "GQE.nextScan: scan list empty")

    if _scanIndex is None:
        _scanIndex = 0
    else:
        _scanIndex += 1
        
    if _scanIndex >= len( _scanList) :
        _scanIndex = 0

    return _scanList[ _scanIndex]

def prevScan():
    '''
    nextScan/prevScan return the next/previous scan objec
    '''
    global _scanIndex

    if len( _scanList) == 0:
        raise ValueError( "GQE.prevScan: scan list empty")

    if _scanIndex is None:
        _scanIndex = 0
    else:
        _scanIndex -= 1

    if _scanIndex < 0:
        _scanIndex = len( _scanList) - 1

    if _scanIndex >= len( _scanList):
        _scanIndex = 0

    return _scanList[ _scanIndex]

def getIndex( name): 
    index = 0
    for scan in _scanList:
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

    Supported extensions: .fio, .dat

    if flagMCA, the input file contains MCA data, no x-axis
    '''

    fioObj = _HasyUtils.fioReader( fileName, flagMCA)

    if y is not None:
        if y > len( fioObj.columns): 
            raise ValueError( "GQE.read: %s, y %d > len( columns) %d" % ( fileName, y, len( fioObj.columns)))
        return fioObj.columns[ y - 1]

    for elm in fioObj.columns:
        scn =  Scan( name = elm.name, x = elm.x, y = elm.y, fileName = fileName)

    return None
    
def write( lst = None): 
    '''
    write the specified scans of all scans
    '''
    if len(_scanList) == 0: 
        raise ValueError( "GQE.write: scan list is empty")

    #
    # check if all scans have the same length
    #
    lngth = len( _scanList[0].x)
    obj = _HasyUtils.fioObj( namePrefix = "pysp")
    for scan in _scanList:
        if lst is not None:
            if scan.name not in lst:
                continue
        if lngth != len( scan.x): 
            raise ValueError( "GQE.display: wrong length %s" % scan.name)
    
        col = _HasyUtils.fioColumn( scan.name)
        col.x = scan.x
        col.y = scan.y
        obj.columns.append( col)
    fileName = obj.write()
    print "created", fileName
    
def getNumberOfScansToBeDisplayed( nameList): 
    '''
    return the number of scans to be displayed.
    Scans that are overlaid do not require extra space
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

def getNoOverlaid( nameList = None):
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
