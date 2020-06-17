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

        #print( "+++graPyspIfc.Scan: %s" % repr( kwargs))
        if name is None:
            raise ValueError( "graPyspIfc.Scan: 'name' is missing")
        
        self.name = name

        DctOut = {}

        if 'start' in kwargs: 
            DctOut[ 'xMin'] = kwargs[ 'start']
            del kwargs[ 'start']
        elif 'xMin' in kwargs: 
            DctOut[ 'xMin'] = kwargs[ 'xMin']
            del kwargs[ 'xMin']
        elif 'x' in kwargs: 
            DctOut[ 'xMin'] = kwargs[ 'x'][0]
        elif 'y' in kwargs: 
            DctOut[ 'xMin'] = 0.
        else: 
            DctOut[ 'xMin'] = 0.

        if 'stop' in kwargs: 
            DctOut[ 'xMax'] = kwargs[ 'stop']
            del kwargs[ 'stop']
        elif 'xMax' in kwargs: 
            DctOut[ 'xMax'] = kwargs[ 'xMax']
            del kwargs[ 'xMax']
        elif 'x' in kwargs: 
            DctOut[ 'xMax'] = kwargs[ 'x'][-1]
        elif 'y' in kwargs: 
            DctOut[ 'xMax'] = float( len( kwargs[ 'y']) - 1)
        else: 
            DctOut[ 'xMax'] = 10.
        
        if 'np' in kwargs:
            DctOut[ 'nPts'] = kwargs[ 'np']
            del kwargs[ 'np']
        elif 'nPts' in kwargs:  
            DctOut[ 'nPts'] = kwargs[ 'nPts']
            del kwargs[ 'nPts']
        elif 'x' in kwargs: 
            DctOut[ 'nPts'] = len( kwargs[ 'x'])
        elif 'y' in kwargs: 
            DctOut[ 'nPts'] = len( kwargs[ 'y'])
        else: 
            DctOut[ 'nPts'] = 101

        if 'yMin' in kwargs: 
            DctOut[ 'yMin'] = kwargs[ 'yMin']
            del kwargs[ 'yMin']

        if 'yMax' in kwargs: 
            DctOut[ 'yMax'] = kwargs[ 'yMax']
            del kwargs[ 'yMax']

        if 'xlabel' in kwargs:
            DctOut[ 'xLabel'] = kwargs[ 'xlabel']
            del kwargs[ 'xlabel']
        if 'xLabel' in kwargs:
            DctOut[ 'xLabel'] = kwargs[ 'xLabel']
            del kwargs[ 'xLabel']

        if 'ylabel' in kwargs:
            DctOut[ 'yLabel'] = kwargs[ 'ylabel']
            del kwargs[ 'ylabel']
        if 'yLabel' in kwargs:
            DctOut[ 'yLabel'] = kwargs[ 'yLabel']
            del kwargs[ 'yLabel']

        if 'colour' in kwargs:
            DctOut[ 'lineColor'] = kwargs[ 'colour']
            del kwargs[ 'colour']
        if 'color' in kwargs:
            DctOut[ 'lineColor'] = kwargs[ 'color']
            del kwargs[ 'color']
        if 'lineColor' in kwargs:
            DctOut[ 'lineColor'] = kwargs[ 'lineColor']
            del kwargs[ 'lineColor']

        if 'at' in kwargs: 
            DctOut[ 'at'] = kwargs[ 'at']
            del kwargs[ 'at']
        else: 
            DctOut[ 'at'] = '(1,1,1)'

        #
        # do not use 'x' here because this causes recursion in the Scan()
        # call caused by __getattr__()
        #
        if 'x' in kwargs: 
            DctOut[ 'xLocal'] = kwargs[ 'x'][:]
            del kwargs[ 'x']
        if 'y' in kwargs: 
            DctOut[ 'yLocal'] = kwargs[ 'y'][:]
            del kwargs[ 'y']
        #
        # Spectra
        #
        if spectraInstalled and useSpectra:
            if 'NoDelete' in kwargs: 
                DctOut[ 'reUse'] = kwargs[ 'NoDelete']
                del kwargs[ 'nodelete']

            if kwargs:
                raise ValueError( "graPyspIfs.Scan (Spectra): dct not empty %s" % str( kwargs))

            DctOut[ 'lineColor'] = utils.colorPyspToSpectra( DctOut[ 'lineColor'])

            #print( "+++graPyspIfc: %s" % repr( DctOut))
            self.scan = Spectra.SCAN( name = name, 
                                      start = DctOut[ 'xMin'], 
                                      stop = DctOut[ 'xMax'],
                                      np = DctOut[ 'nPts'],
                                      #xlabel = DctOut[ 'xLabel'],
                                      #ylabel = DctOut[ 'yLabel'],
                                      #NoDelete = DctOut[ 'reUse'],
                                      colour = DctOut[ 'lineColor'],
                                      at = DctOut[ 'at'])

            #
            # set x and y to values provided by the user or to 
            # some default, x: linspace(), y: zeros()
            #
            if 'xLocal' in DctOut: 
                for i in range( len( DctOut[ 'xLocal'])): 
                    self.scan.setX( i, DctOut[ 'xLocal'][i])
            else: 
                x = np.linspace( DctOut[ 'xMin'], DctOut[ 'xMax'], DctOut[ 'nPts'])
                for i in range( len( x)): 
                    self.scan.setX( i, x[i])
                
            if 'yLocal' in DctOut:
                for i in range( len( DctOut[ 'yLocal'])): 
                    self.scan.setY( i, DctOut[ 'yLocal'][i])
            else: 
                y = np.zeros( DctOut[ 'nPts'], np.float64)
                for i in range( len( y)): 
                    self.scan.setY( i, y[i])

            self.nPts = self.scan.np
            self.xMin = self.scan.x_min
            self.xMax = self.scan.x_max
            self.lineColor = utils.colorSpectraToPysp( self.scan.colour)
        else:
            #
            # PySpectra
            #
            if type( DctOut[ 'lineColor']) == int:
                DctOut[ 'lineColor'] = utils.colorSpectraToPysp( DctOut[ 'lineColor'])

            if 'NoDelete' in kwargs: 
                DctOut[ 'reUse'] = kwargs[ 'NoDelete']
                del kwargs[ 'NoDelete']
            if 'reUse' in kwargs: 
                DctOut[ 'reUse'] = kwargs[ 'reUse']
                del kwargs[ 'reUse']
            if 'comment' in kwargs: 
                PySpectra.setComment( kwargs[ 'comment'])
                del kwargs[ 'comment']

            motorNameList = None
            if 'motorNameList' in kwargs:
                DctOut[ 'motorNameList'] = kwargs[ 'motorNameList'][:]
                del kwargs[ 'motorNameList']

            logWidget = None
            if 'logWidget' in kwargs:
                DctOut[ 'logWidget'] = kwargs[ 'logWidget']
                del kwargs[ 'logWidget']
        
            if kwargs:
                raise ValueError( "graPyspIfs.Scan (PySPectra): dct not empty %s" % str( kwargs))

            self.scan = PySpectra.Scan( name = name, **DctOut)

            self.nPts = self.scan.nPts
            self.xMin = self.scan.xMin
            self.xMax = self.scan.xMax
            self.lineColor = self.scan.lineColor

        return 

    def getCurrent( self): 
        return self.scan.getCurrent()

    def setCurrent( self, index): 
        self.scan.setCurrent( index)
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
    


