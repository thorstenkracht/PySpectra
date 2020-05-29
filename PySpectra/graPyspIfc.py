#!/usr/bin/env python
'''
this module actracts Spectra, PySpectra
'''
import PySpectra 
import PySpectra.utils as utils

try: 
    import Spectra
    spectraInstalled = True
except: 
    spectraInstalled = False

lineColorArr = [ 
    'RED', 
    'GREEN',
    'BLUE',
    'YELLOW',
    'CYAN',
    'MAGENTA',
    'BLACK',
    'WHITE', 
    'NONE', 
]

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
        argout = Spectra.gra_command("display")
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
    
def Scan( **hsh):
    '''
    create a scan and return it
    '''
    if not 'name' in hsh:
        raise ValueError( "graPyspIfc.Scan: 'name' is missing")

    name = hsh[ 'name']
    del hsh[ 'name']

    if 'start' in hsh: 
        xMin = hsh[ 'start']
        del hsh[ 'start']
    elif 'xMin' in hsh: 
        xMin = hsh[ 'xMin']
        del hsh[ 'xMin']
    elif 'x' in hsh: 
        xMin = hsh[ 'x'][0]
    elif 'y' in hsh: 
        xMin = 0.
    else: 
        xMin = 0.

    if 'stop' in hsh: 
        xMax = hsh[ 'stop']
        del hsh[ 'stop']
    elif 'xMax' in hsh: 
        xMax = hsh[ 'xMax']
        del hsh[ 'xMax']
    elif 'x' in hsh: 
        xMax = hsh[ 'x'][-1]
    elif 'y' in hsh: 
        xMax = float( len( hsh[ 'y']) - 1)
    else: 
        xMax = 10.

    nPts = 101
    if 'np' in hsh:
        nPts = hsh[ 'np']
        del hsh[ 'np']
    elif 'nPts' in hsh:  
        nPts = hsh[ 'nPts']
        del hsh[ 'nPts']
    elif 'x' in hsh: 
        nPts = len( hsh[ 'x'])
    elif 'y' in hsh: 
        nPts = len( hsh[ 'y'])
    else: 
        nPts = 101

    xLabel = 'x-axis'
    if 'xlabel' in hsh:
        xLabel = hsh[ 'xlabel']
        del hsh[ 'xlabel']
    yLabel = 'y-axis'
    if 'ylabel' in hsh:
        yLabel = hsh[ 'ylabel']
        del hsh[ 'ylabel']


    color = 2
    if 'colour' in hsh:
        color = hsh[ 'colour']
        del hsh[ 'colour']
    if 'color' in hsh:
        color = hsh[ 'color']
        del hsh[ 'color']

    at = "(1,1,1)"
    if 'at' in hsh: 
        at = hsh[ 'at']
        del hsh[ 'at']

    comment = "A comment"
    if 'comment' in hsh: 
        comment = hsh[ 'comment']
        del hsh[ 'comment']

    x = None
    if 'x' in hsh: 
        x = hsh[ 'x'][:]
        del hsh[ 'x']
    y = None
    if 'y' in hsh: 
        y = hsh[ 'y'][:]
        del hsh[ 'y']

    if spectraInstalled and useSpectra:
        nodelete = False
        if 'NoDelete' in hsh: 
            nodelete = hsh[ 'NoDelete']
            del hsh[ 'nodelete']

        if hsh:
            raise ValueError( "graPyspIfs.Scan (Spectra): dct not empty %s" % str( hsh))
        scan = Spectra.SCAN( name = name,
                             start = xMin, 
                             stop = xMax,
                             np = nPts,
                             xlabel = xLabel,
                             ylabel = yLabel,
                             comment = comment,
                             NoDelete = nodelete,
                             colour = color,
                             at = at)
        if x is not None: 
            for i in range( len( x)): 
                scan.setX( i, x[i])
        if y is not None: 
            for i in range( len(y)): 
                scan.setY( i, y[i])
    else:

        if type(color) == int:
            utils.colorSpectraToPysp( color)

        reUse = False
        if 'reUser' in hsh: 
            reUse = hsh[ 'reUse']
            del hsh[ 'reUse']

        motorNameList = None
        if 'motorNameList' in hsh:
            motorNameList = hsh[ 'motorNameList'][:]
            del hsh[ 'motorNameList']
        logWidget = None
        if 'logWidget' in hsh:
            logWidget = hsh[ 'logWidget']
            del hsh[ 'logWidget']
        

        if hsh:
            raise ValueError( "graPyspIfs.Scan (PySPectra): dct not empty %s" % str( hsh))

        scan = PySpectra.Scan( name = name, 
                               xMin = xMin, 
                               xMax = xMax,
                               nPts = nPts,
                               xLabel = xLabel, 
                               yLabel = yLabel,
                               color = color,
                               autoscaleX = True, 
                               autoscaleY = True,
                               motorNameList = motorNameList,
                               logWidget = logWidget,
                               reUser = reUse, 
                               x = x, 
                               y = y, 
                               at = at)

        scan.addText( text = comment, 
                      x = 0.95, y = 0.95, 
                      hAlign = 'right', vAlign = 'top', 
                      color = 'black', fontSize = None)
            
    return scan

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
    


