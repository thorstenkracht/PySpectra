#!/usr/bin/env python
'''
this module actracts Spectra, PySpectra
'''
import PySpectra 
import PySpectra.utils as utils
import PySpectra.GQE as GQE
import numpy as np
import sys
 
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
        if flagPrint: 
            if printer is None: 
                raise ValueError( "graPyspIfc.createHardCopy: flagPrint == True but no printer")

            Spectra.gra_command(" postscript/%s/redisplay/nolog/nocon/print/lp=%s" % (format, printer))
        else: 
            Spectra.gra_command(" postscript/%s/redisplay/nolog/nocon/print" % (format))
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
        Spectra.gra_command( "delete %s.*" % scan.name)
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
    """
    in PySpectra there is mostly autoscale when displaying things
    therefore we do it when calling spectra as well
    """
    if spectraInstalled and useSpectra:
        argout = Spectra.gra_command("display/autoscale/vp")
    else: 
        argout = PySpectra.display()
    return argout

def getGqe( name): 
    '''
    Spectra: 1, if the scan exist, 0 otherwise

    used by moveMotor() to see whether the signal scan is still existing
    '''
    if spectraInstalled and useSpectra:
        (sts, ret) = Spectra.gra_decode_int( "search_scan( %s)" % name)
        if sts == 0: 
            raise ValueError( "graPyspIfc.getGqe: failed to search for %s" % name)
        return ret
    else: 
        return PySpectra.getGqe( name)
    
class Scan( object): 
    """
    interfaces to GQE.Scan oder spectra
    """
    def __init__( self, name = None, **kwargs):

        #print( "graPyspIfc.Scan: %s" % repr( kwargs))
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
        # do not use 'x' here because this causes recursion in the
        # Scan() call caused by __getattr__()
        #
        if 'x' in kwargs: 
            DctOut[ 'x'] = kwargs[ 'x'][:]
            del kwargs[ 'x']
        else: 
            DctOut[ 'x'] = None

        if 'y' in kwargs: 
            DctOut[ 'y'] = kwargs[ 'y'][:]
            del kwargs[ 'y']
        else: 
            DctOut[ 'y'] = None
        #
        # Spectra
        #
        if spectraInstalled and useSpectra:
            if kwargs:
                raise ValueError( "graPyspIfs.Scan (Spectra): dct not empty %s" % str( kwargs))

            DctOut[ 'lineColor'] = utils.colorPyspToSpectra( DctOut[ 'lineColor'])

            #
            # Spectra has to 'x' or 'y' parameter in the constructor
            #
            self.scan = Spectra.SCAN( name = name, 
                                      start = DctOut[ 'xMin'], 
                                      stop = DctOut[ 'xMax'],
                                      np = DctOut[ 'nPts'],
                                      #xlabel = DctOut[ 'xLabel'],
                                      #ylabel = DctOut[ 'yLabel'],
                                      colour = DctOut[ 'lineColor'],
                                      at = DctOut[ 'at'])

            #
            # set x and y to values provided by the user or to 
            # some default, x: linspace(), y: zeros()
            #
            if 'x' in DctOut and DctOut[ 'x'] is not None: 
                for i in range( len( DctOut[ 'x'])): 
                    self.scan.setX( i, DctOut[ 'x'][i])
            else: 
                x = np.linspace( DctOut[ 'xMin'], DctOut[ 'xMax'], DctOut[ 'nPts'])
                for i in range( len( x)): 
                    self.scan.setX( i, x[i])
                
            if 'y' in DctOut and DctOut[ 'y'] is not None:
                for i in range( len( DctOut[ 'y'])): 
                    self.scan.setY( i, DctOut[ 'y'][i])
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
            if 'lineColor' in DctOut:
                if type( DctOut[ 'lineColor']) == int:
                    DctOut[ 'lineColor'] = utils.colorSpectraToPysp( DctOut[ 'lineColor'])
            else: 
                DctOut[ 'lineColor'] = 'blue'

            if 'comment' in kwargs: 
                PySpectra.setComment( kwargs[ 'comment'])
                del kwargs[ 'comment']

            if 'motorNameList' in kwargs:
                DctOut[ 'motorNameList'] = kwargs[ 'motorNameList'][:]
                del kwargs[ 'motorNameList']
            else: 
                DctOut[ 'motorNameList'] = None

            if 'logWidget' in kwargs:
                DctOut[ 'logWidget'] = kwargs[ 'logWidget']
                del kwargs[ 'logWidget']
            else: 
                DctOut[ 'logWidget'] = None
        
            if kwargs:
                raise ValueError( "graPyspIfs.Scan (PySPectra): dct not empty %s" % str( kwargs))

            self.scan = PySpectra.Scan( name = name, 
                                        x = DctOut[ 'x'], 
                                        y = DctOut[ 'y'], 
                                        xMin = DctOut[ 'xMin'], 
                                        xMax = DctOut[ 'xMax'], 
                                        lineColor = DctOut[ 'lineColor'], 
                                        motorNameList = DctOut[ 'motorNameList'], 
                                        logWidget = DctOut[ 'logWidget'],
                                        nPts = DctOut[ 'nPts'])

            self.nPts = self.scan.nPts
            self.xMin = self.scan.xMin
            self.xMax = self.scan.xMax
            self.lineColor = self.scan.lineColor

        return 

    def updateArrowCurrent( self): 
        if spectraInstalled and useSpectra:
            pass
        else: 
            self.scan.updateArrowCurrent()
        return 
        
    def autoscale( self):
        self.scan.autoscale()
        return

    def getCurrent( self): 
        return self.scan.getCurrent()

    def setCurrent( self, index): 
        self.scan.setCurrent( index)
        return 

    def getX( self, index):
        return self.scan.getX( index)

    def getY( self, index):
        return self.scan.getY( index)

    def setX( self, index, x): 
        self.scan.setX( index, x)
        return 
    def setY( self, index, x): 
        self.scan.setY( index, x)
        return 

    def sort( self): 
        return self.scan.sort()

    def display( self): 
        self.scan.display()
        if spectraInstalled and useSpectra:
            pass
        else: 
            self.plotDataItem = self.scan.plotDataItem
        return 

    def smartUpdateDataAndDisplay( self, x = None, y = None): 
        """
        for PySpectra: smartUpdataDataAndDisplay() updates the
        plotDataItem (created by the first display) and
        processes the events to update the display also
        """
        if spectraInstalled and useSpectra:
            if x is not None: 
                for i in range( len( x)): 
                    self.scan.setX( i, x[i])
            if y is not None: 
                for i in range( len( y)): 
                    self.scan.setY( i, y[i])
            Spectra.gra_command( "cls/graphic")            
            Spectra.gra_command( "autoscale")            
            self.scan.display()
        else: 
            self.scan.smartUpdateDataAndDisplay( x, y)
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

def getComment(): 
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

def getTitle(): 
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
            raise ValueError( "graPyspIfc.write: expecting a string containing the name")
        elif type( names) is list:
            raise ValueError( "graPyspIfc.write: input must no be a list")
        else: 
            Spectra.gra_command( "write/fio %s" % names)
    else:
        if names is None: 
            PySpectra.write()
        elif type( names) is list: 
            PySpectra.write( names)
        else:
            PySpectra.write( [names])

    return 
    


