#!/usr/bin/env python
'''
An interface to PySpectra, used by ipython, see 00-start.py, 
and by pyspViewer.py
'''
import PySpectra as pysp
import itertools
import PySpectra.mtpltlb.graphics as _mpl_graphics # to create postscript

def command( line):
    '''
    receives a line like: 'cls', 'create t1', etc.
    the line is split into pieces and the pysp functions
    are called
    '''
    line = line.strip()
    if len( line) == 0:
        return

    lst = line.split( ' ')

    if len( lst) > 1:
        lineRest = " ".join( lst[1:])
    else:
        lineRest = None
                    
    if lst[0] == 'antiderivative':
        return antiderivative( lineRest)
    elif lst[0] == 'cls':
        return cls( lineRest)
    elif lst[0] == 'create':
        return create( lineRest)
    elif lst[0] == 'createPDF':
        return createPDF( lineRest)
    elif lst[0] == 'delete':
        return delete( lineRest)
    elif lst[0] == 'derivative':
        return derivative( lineRest)
    elif lst[0] == 'display':
        return display( lineRest)
    elif lst[0] == 'overlay':
        return overlay( lineRest)
    elif lst[0] == 'read':
        return read( lineRest)
    elif lst[0] == 'setComment':
        return setComment( lineRest)
    elif lst[0] == 'setTitle':
        return setTitle( lineRest)
    elif lst[0] == 'setWsViewport':
        return setWsViewport( lineRest)
    elif lst[0] == 'show':
        return show( lineRest)
    elif lst[0] == 'write':
        return write( lineRest)
    elif lst[0] == 'y2my':
        return y2my( lineRest)
    else:
        raise ValueError( "ifc.command: failed to identify %s" % line)

    return 

def antiderivative( line):
    '''
    antiderivative src [target] 
      the default target name is <src>_antiderivative
      
    calculates the Stammfunktion 

      Examples: 
        antiderivative t1
        antiderivative t1 t1_d

    '''
    lst = None
    if line is not None:
        if len( line) > 0:
            lst = line.split( ' ')

        
    if len( lst) == 1: 
        pysp.antiderivative( lst[0])
    elif len( lst) == 2: 
        pysp.antiderivative( lst[0], lst[1])
    else:
        raise ValueError( "ifc.antiderivative: wrong syntax %s" % line)

def cls( line):
    '''
    clears the graphics screen
    '''
    pysp.cls()

def create( line):
    '''
    creates a scan 
   
    Examples:     
      create name scanname xMin 0. xMax 1. nPts 101
      create scanname 0. 1. 101
      create scanname
    '''
    l = line.split( ' ')

    #
    # create t1
    #
    if len( l) == 1:
        hsh = {}
        hsh[ 'name'] = l[0]
    #
    # create t1 0 10 101
    #
    elif len( l) == 4:
        hsh = {}
        hsh[ 'name'] = l[0]
        hsh[ 'xMin'] = float( l[1])
        hsh[ 'xMax'] = float( l[2])
        hsh[ 'nPts'] = int( l[3])
    #
    # create t1 xMin 0 xMax 10 nPts  101
    #
    elif line.find( 'xMin') > 0:
        hsh = dict(itertools.izip_longest(*[iter(l)] * 2, fillvalue=""))
    else:
        raise ValueError( "ifs.createScan: wrong syntax %s" % line)
        
    pysp.Scan( **hsh)

def createPDF( line):
    '''
    create a PDF 
    '''
    fileName = None
    if line is not None:
        l = line.split( ' ')
        if l is not None and len(l) > 0:
            fileName = l[0]

    _mpl_graphics.createPDF( fileName)

def derivative( line):
    '''
    derivative src [target] 
      the default target name is <src>_derivative
      
      Examples: 
        derivative t1
        derivative t1 t1_d
    '''
    lst = None
    if line is not None:
        if len( line) > 0:
            lst = line.split( ' ')
        
    if len( lst) == 1: 
        pysp.derivative( lst[0])
    elif len( lst) == 2: 
        pysp.derivative( lst[0], lst[1])
    else:
        raise ValueError( "ifc.derivative: wrong syntax %s" % line)

def display( line):

    lst = None
    if line is not None:
        if len( line) > 0:
            lst = line.split( ' ')
        
    pysp.display( lst)

def delete( line):
    lst = None
    if line: 
        lst = line.split(' ')
    pysp.delete( lst)

def overlay( line):
    lst = line.split( ' ')
    if len( lst) != 2:
        raise ValueError( "ifc.overlay: expecting two scan names")
    pysp.overlay( lst[0], lst[1])

def procEventsLoop( line):
    pysp.procEventsLoop()

def read( line):
    lst = None
    if line: 
        lst = line.split(' ')
    if len( lst) == 0:
        raise ValueError( "ifc.read: expecting a file name and optionally '-mca'")
        return 
    pysp.read( lst)

def setComment( line):
    pysp.setComment( line)

def setTitle( line):
    pysp.setTitle( line)

def setWsViewport( line):
    lst = None
    if line:
        lst = line.split( ' ')
    if len( lst) > 1:
        raise ValueError( "ifc.setWsViewport: expecting zero or one arguments")
        return 

    if len( lst) == 0:
        pysp.setWsViewport( None)
    else:
        pysp.setWsViewport( lst[0])

def show( line):
    pysp.show()

def write( line):
    pysp.write()

def y2my( line):
    lst = line.split( ' ')
    if len( lst) != 1 and len( lst) != 2:
        raise ValueError( "ifc.y2my: expecting one or two scan names")
    hsh = {}
    hsh[ 'name'] = lst[0]
    if len( lst) == 2:
        hsh[ 'nameNew'] = lst[1]
    pysp.yToMinusY( **hsh)
    

        
        
