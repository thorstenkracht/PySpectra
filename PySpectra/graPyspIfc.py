#!/usr/bin/env python
'''
this module actracts Spectra, PySpectra
'''
import PySpectra 
import PySpectra.GQE as GQE

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
    return 

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
        pass
    else:
        PySpectra.close()
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
    else: 
        GQE.delete( [scan.name])
        PySpectra.cls()

    return 

def delete():
    '''
    delete all internal data
    '''
    if spectraInstalled and useSpectra:
        Spectra.gra_command("delete *.*")
    else: 
        PySpectra.cls()
        GQE.delete()

    return 

def getGqe( name): 
    '''
    used by moveMotor() to see whether the signal scan is still existing
    '''
    if spectraInstalled and useSpectra:
        return None
    else: 
        return GQE.getGqe( name)
    
def Scan( **hsh):
    '''
    create a scan and return it
    '''
    if spectraInstalled and useSpectra:
        scan = Spectra.SCAN( name = hsh[ 'name'],
                             start = hsh[ 'start'], 
                             stop = hsh[ 'stop'],
                             np = hsh[ 'np'],
                             xlabel = hsh[ 'xlabel'],
                             ylabel = hsh[ 'ylabel'],
                             comment = hsh[ 'comment'],
                             NoDelete = hsh[ 'NoDelete'],
                             colour = hsh[ 'colour'],
                             at = hsh[ 'at'])
    else:
        if not 'name' in hsh:
            raise ValueError( "graPyspIfc.Scan: 'name' is missing")

        name = hsh[ 'name']
        xMin = 0
        if 'start' in hsh:
            xMin = hsh[ 'start']
        xMax = 10.
        if 'stop' in hsh:
            xMax = hsh[ 'stop']
        nPts = 101
        if 'np' in hsh:
            nPts = hsh[ 'np']
        xLabel = 'x-axis'
        if 'xlabel' in hsh:
            xLabel = hsh[ 'xlabel']
        yLabel = 'y-axis'
        if 'ylabel' in hsh:
            yLabel = hsh[ 'ylabel']
        color = 2
        if 'colour' in hsh:
            color = hsh[ 'colour']
        if 'color' in hsh:
            color = hsh[ 'color']
        if type(color) == int:
            GQE.colorSpectraToPysp( color)

        motorNameList = None
        if 'motorNameList' in hsh:
            motorNameList = hsh[ 'motorNameList']
        logWidget = None
        if 'logWidget' in hsh:
            logWidget = hsh[ 'logWidget']
        at = "(1,1,1)"
        if 'at' in hsh: 
            at = hsh[ 'at']
        
        scan = GQE.Scan( name = name, 
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
                         at = at)

        scan.addText( text = hsh[ 'comment'], 
                      x = 0.95, y = 0.95, 
                      hAlign = 'right', vAlign = 'top', 
                      color = 'black', fontSize = None)
            
    return scan

def setComment( line): 
    return GQE.setComment( line) 

def getComment( line): 
    return GQE.getComment()

def setTitle( line): 
    return GQE.setTitle( line) 

def getTitle( line): 
    return GQE.getTitle()

def writeFile( nameGQE):

    if spectraInstalled and useSpectra:
        Spectra.gra_command( "write/fio %s" % nameGQE)
    else:
        PySpectra.write( [nameGQE])

    return 
    


