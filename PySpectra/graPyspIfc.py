#!/usr/bin/env python
'''
this module actracts Spectra, PySpectra
'''
import PySpectra 
import PySpectra.utils as utils
import PySpectra.GQE as GQE
import numpy as np

try: 
    import Spectra
    spectraInstalled = True
except: 
    spectraInstalled = False

useSpectra = False

def setSpectra( flag):
    global useSpectra
    
    if flag:
        if not spectraInstalled: 
            print( "*** graPyspIfc.setSpectra: spectra is not installed")
            sys.exit( 255)
        useSpectra = True
    else:
        useSpectra = False
    return True

def getSpectra(): 
    return useSpectra
 
def cls():
    if spectraInstalled and useSpectra:
        Spectra.gra_command( "cls/graphic")
    else:
        PySpectra.cls()
    return 

def close(): 

    if spectraInstalled and useSpectra:
        argout = True
    else:
        argout = PySpectra.close()
    return 

def createHardCopy( printer = None, flagPrint = False, format = 'DINA4'):
    '''
    create postscript/pdf file and send it to the printer
    '''
    fName = None
    if spectraInstalled and useSpectra:
        Spectra.gra_command(" set 0.1/border=1")
        Spectra.gra_command(" postscript/%s/redisplay/nolog/nocon/print/lp=%s" % (format, prnt))
        Spectra.gra_command(" set 0.1/border=0")
        Spectra.gra_command(" postscript/redisplay/nolog/nocon/print/lp=%s" % printer)
    else:
        fName = PySpectra.createPDF( flagPrint = flagPrint, format = format)
        #
        # necessary to bring pqt and mpl again in-sync, mind lastIndex
        #
        PySpectra.cls()
        PySpectra.display()

    return fName

def deleteScan( scan): 
    '''
    delete a single scan
    '''
    if spectraInstalled and useSpectra:
        del scan
        argout = True
    else: 
        argout = PySpectra.delete( [scan.name])
        PySpectra.cls()

    return argout

def delete():
    '''
    delete all internal data
    '''
    if spectraInstalled and useSpectra:
        argout = Spectra.gra_command("delete *.*")
    else: 
        PySpectra.cls()
        argout = PySpectra.delete()

    return argout

def display(): 
    if spectraInstalled and useSpectra:
        argout = Spectra.gra_command("display/vp")
    else: 
        argout = PySpectra.display()
    return argout

def getGqe( name): 
    '''
    used by moveMotor() to see whether the signal scan is still existing
    '''
    if spectraInstalled and useSpectra:
        return None
    else: 
        return PySpectra.getGqe( name)
    
class Scan( object): 
    """
    interfaces to GQE.Scan oder spectra
    """
    def __init__( self, name = None, **kwargs):

        # print( "+++graPyspIfc.Scan: %s" % repr( kwargs))
        if name is None:
            raise ValueError( "graPyspIfc.Scan: 'name' is missing")
        
        self.name = name

        if 'start' in kwargs: 
            xMin = kwargs[ 'start']
            del kwargs[ 'start']
        elif 'xMin' in kwargs: 
            xMin = kwargs[ 'xMin']
            del kwargs[ 'xMin']
        elif 'x' in kwargs: 
            xMin = kwargs[ 'x'][0]
        elif 'y' in kwargs: 
            xMin = 0.
        else: 
            xMin = 0.

        if 'stop' in kwargs: 
            xMax = kwargs[ 'stop']
            del kwargs[ 'stop']
        elif 'xMax' in kwargs: 
            xMax = kwargs[ 'xMax']
            del kwargs[ 'xMax']
        elif 'x' in kwargs: 
            xMax = kwargs[ 'x'][-1]
        elif 'y' in kwargs: 
            xMax = float( len( kwargs[ 'y']) - 1)
        else: 
            xMax = 10.
        
        nPts = 101
        if 'np' in kwargs:
            nPts = kwargs[ 'np']
            del kwargs[ 'np']
        elif 'nPts' in kwargs:  
            nPts = kwargs[ 'nPts']
            del kwargs[ 'nPts']
        elif 'x' in kwargs: 
            nPts = len( kwargs[ 'x'])
        elif 'y' in kwargs: 
            nPts = len( kwargs[ 'y'])
        else: 
            nPts = 101

        if 'yMin' in kwargs: 
            yMin = kwargs[ 'yMin']
            del kwargs[ 'yMin']

        if 'yMax' in kwargs: 
            yMax = kwargs[ 'yMax']
            del kwargs[ 'yMax']

        xLabel = 'x-axis'
        if 'xlabel' in kwargs:
            xLabel = kwargs[ 'xlabel']
            del kwargs[ 'xlabel']
        if 'xLabel' in kwargs:
            xLabel = kwargs[ 'xLabel']
            del kwargs[ 'xLabel']

        yLabel = 'y-axis'
        if 'ylabel' in kwargs:
            yLabel = kwargs[ 'ylabel']
            del kwargs[ 'ylabel']
        if 'yLabel' in kwargs:
            yLabel = kwargs[ 'yLabel']
            del kwargs[ 'yLabel']

        lineColor = 2
        if 'colour' in kwargs:
            lineColor = kwargs[ 'colour']
            del kwargs[ 'colour']
        if 'color' in kwargs:
            lineColor = kwargs[ 'color']
            del kwargs[ 'color']
        if 'lineColor' in kwargs:
            lineColor = kwargs[ 'lineColor']
            del kwargs[ 'lineColor']

        at = None
        if 'at' in kwargs: 
            at = kwargs[ 'at']
            del kwargs[ 'at']

        #
        # do not use 'x' here because this causes recursion in the Scan()
        # call caused by __getattr__()
        #
        xLocal = None
        if 'x' in kwargs: 
            xLocal = kwargs[ 'x'][:]
            del kwargs[ 'x']
        yLocal = None
        if 'y' in kwargs: 
            yLocal = kwargs[ 'y'][:]
            del kwargs[ 'y']
        #
        # Spectra
        #
        if spectraInstalled and useSpectra:
            reUse = False
            if 'NoDelete' in kwargs: 
                reUse = kwargs[ 'NoDelete']
                del kwargs[ 'nodelete']

            if kwargs:
                raise ValueError( "graPyspIfs.Scan (Spectra): dct not empty %s" % str( kwargs))

            colorGra = utils.colorPyspToSpectra( lineColor)
            self.scan = Spectra.SCAN( name = name,
                                      start = xMin, 
                                      stop = xMax,
                                      np = nPts,
                                      xlabel = xLabel,
                                      ylabel = yLabel,
                                      NoDelete = reUse,
                                      lineColour = colorGra,
                                      at = at)
            #
            # set x and y to values provided by the user or to 
            # some default, x: linspace(), y: zeros()
            #
            if xLocal is not None: 
                for i in range( len( xLocal)): 
                    self.scan.setX( i, xLocal[i])
            else: 
                x = np.linspace( xMin, xMax, nPts)
                for i in range( len( x)): 
                    self.scan.setX( i, x[i])
                
            if yLocal is not None: 
                for i in range( len( yLocal)): 
                    self.scan.setY( i, yLocal[i])
            else: 
                y = np.zeros( nPts, np.float64)
                for i in range( len( y)): 
                    self.scan.setY( i, y[i])

        else:
            #
            # PySpectra
            #
            if type(lineColor) == int:
                lineColor = utils.colorSpectraToPysp( lineColor)

            reUse = False
            if 'reUse' in kwargs: 
                reUse = kwargs[ 'reUse']
                del kwargs[ 'reUse']

            motorNameList = None
            if 'motorNameList' in kwargs:
                motorNameList = kwargs[ 'motorNameList'][:]
                del kwargs[ 'motorNameList']

            logWidget = None
            if 'logWidget' in kwargs:
                logWidget = kwargs[ 'logWidget']
                del kwargs[ 'logWidget']
        
            if kwargs:
                raise ValueError( "graPyspIfs.Scan (PySPectra): dct not empty %s" % str( kwargs))

            self.scan = PySpectra.Scan( name = name, 
                                        xMin = xMin, 
                                        xMax = xMax,
                                        nPts = nPts,
                                        xLabel = xLabel, 
                                        yLabel = yLabel,
                                        lineColor = lineColor,
                                        autoscaleX = True, 
                                        autoscaleY = True,
                                        motorNameList = motorNameList,
                                        logWidget = logWidget,
                                        reUse = reUse, 
                                        x = xLocal, 
                                        y = yLocal, 
                                        at = at)

        return 

    def display( self): 
        self.scan.display()
        return 

    #
    # recursion can be avoided by calling the super class of scan.
    # hence, Scan needs to be an object
    #
    def __setattr__( self, name, value): 
        #print( "graPyspIfc.Scan.__setattr__: name %s, value %s" % (name, repr(value)))
        if name in [ 'x']:
            if value is None: 
                return 
            if spectraInstalled and useSpectra:
                for i in range( len( value)): 
                    self.scan.setX( i, value[i])
            else: 
                self.scan.x = value[:]
        if name in [ 'y']:
            if value is None: 
                return 
            if spectraInstalled and useSpectra:
                for i in range( len( value)): 
                    self.scan.setY( i, value[i])
            else: 
                self.scan.y = value[:]
        elif name in GQE.ScanAttrsPublic or \
             name in GQE.ScanAttrsPrivate or \
             name in [ 'scan']: 
            super( Scan, self).__setattr__(name, value)
        else: 
            raise ValueError( "graPyspIfc.Scan.__setattr__: %s unknown attribute %s" % ( self.name, name))
        return 

    def __getattr__( self, name):
        #print( "graPyspIfc.Scan.__getattr__() %s" % name)
        argout = None
        if name == 'x': 
            if spectraInstalled and useSpectra:
                argout = np.zeros( self.scan.np, np.float64)
                for i in range( self.scan.np): 
                    argout[i] = self.scan.getX( i)
            else: 
                argout = self.scan.x[:]
        elif name == 'y': 
            if spectraInstalled and useSpectra:
                argout = np.zeros( self.scan.np, np.float64)
                for i in range( self.scan.np): 
                    argout[i] = self.scan.getY( i)
            else: 
                argout = self.scan.y[:]
        return argout

def setComment( line): 
    if spectraInstalled and useSpectra:
        argout = None
    else: 
        argout = PySpectra.setComment( line) 
    return argout

def getComment( line): 
    if spectraInstalled and useSpectra:
        argout = "NoComment"
    else: 
        argout = PySpectra.getComment() 
    return argout 

def setTitle( line): 
    if spectraInstalled and useSpectra:
        argout = None
    else: 
        argout = PySpectra.setTitle( line) 
    return argout

def getTitle( line): 
    if spectraInstalled and useSpectra:
        argout = None
    else: 
        argout = PySpectra.getTitle()
    return argout

def write( names = None):
    """
    write a .fio file

    names is None:        PySpectra only
    type( names) is list: PySpectra only
    type( names) is str:  PySpectra, Spectra
    """
    if spectraInstalled and useSpectra:
        if names is None: 
            raise ValueError( "graPyspIfc.write: expecting a name")
        Spectra.gra_command( "write/fio %s" % names)
    else:
        if names is None: 
            PySpectra.write()
        elif type( names) is list: 
            PySpectra.write( names)
        else:
            PySpectra.write( [names])

    return 
    


