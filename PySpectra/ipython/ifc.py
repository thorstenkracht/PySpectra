#!/usr/bin/env python
'''
An interface to PySpectra, used by ipython, see 00-start.py, 
and by pyspFio.py
'''

import PySpectra.dMgt.GQE as _GQE
import PySpectra.dMgt.calc as _calc
import PySpectra.pqtgrph.graphics as _graphics
import itertools

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
    elif lst[0] == 'set':
        return set( lineRest)
    elif lst[0] == 'show':
        return show( lineRest)
    elif lst[0] == 'y2my':
        return y2my( lineRest)
    else:
        raise ValueError( "ifc.command: failed to identify %s" % line)

    return 

def antiderivative( line):
    '''
    antiderivative t1
    antiderivative t1 t1_d
    '''
    lst = None
    if line is not None:
        if len( line) > 0:
            lst = line.split( ' ')
        
    _calc.antiderivative( lst)

def cls( line):
    _graphics.cls()

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
        
    _GQE.Scan( **hsh)

def derivative( line):
    '''
    derivative t1
    derivative t1 t1_d
    '''
    lst = None
    if line is not None:
        if len( line) > 0:
            lst = line.split( ' ')
        
    _calc.derivative( lst)

def display( line):

    lst = None
    if line is not None:
        if len( line) > 0:
            lst = line.split( ' ')
        
    _graphics.display( lst)

def delete( line):
    lst = None
    if line: 
        lst = line.split(' ')
    _GQE.delete( lst)

def overlay( line):
    lst = line.split( ' ')
    if len( lst) != 2:
        raise ValueError( "ifc.overlay: expecting two scan names")
    _GQE.overlay( lst[0], lst[1])

def procEventsLoop( line):
    _graphics.procEventsLoop()

def read( line):
    lst = None
    if line: 
        lst = line.split(' ')
    if len( lst) == 0:
        raise ValueError( "ifc.read: expecting a file name and optionally '-mca'")
        return 
    _GQE.read( lst)

def set( line):
    lst = None
    if line:
        lst = line.split( ' ')
    if len( lst) == 0 or len( lst) > 2:
        raise ValueError( "ifc.set: expecting one or two arguments")
        return 

    if lst[0] == 'comment':
        if len( lst) == 2:
            _GQE.setComment(  lst[1])
        else:
            _GQE.setComment( None)
    if lst[0] == 'title':
        if len( lst) == 2:
            _GQE.setTitel(  lst[1])
        else:
            _GQE.setTitel( None)

def show( line):
    _GQE.show()

def y2my( line):
    lst = line.split( ' ')
    if len( lst) != 1 and len( lst) != 2:
        raise ValueError( "ifc.y2my: expecting one or two scan names")
    hsh = {}
    hsh[ 'name'] = lst[0]
    if len( lst) == 2:
        hsh[ 'nameNew'] = lst[1]
    _calc.yToMinusY( **hsh)
    

        
        
