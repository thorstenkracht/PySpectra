#!/usr/bin/env python
'''
An interface to PySpectra, used by ipython, see 00-start.py, 
and by pyspViewer.py

  #!/usr/bin/env python
  import __builtin__
  #__builtin__.__dict__[ 'graphicsLib'] = 'matplotlib'
  __builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'
  import PySpectra as pysp
  import PySpectra.ipython.startup
 
  PySpectra.ipython.startup contains the macro definitions

  Afterwards: 
    In [1]: create s1
    In [1]: display

  Commands: 
    antiderivative src [target] 
      calculates the anti-derivative
    cls 
      clears the graphics screen
    create 
      creates a scan 
    createPDF
    derivative src [target] 
      calculates the derivative
    display
    delete
    info
    overlay s1 s2
      s1 is plotted in the viewport of s2
    read fileName
    setComment
    setArrowMotorCurrent
    setArrowMotorSetPoint
      used by the mouse-click callback
    setArrowMotorMisc  
      this arrow is ignored by the refresh() of pyspMonitor, 
      used by e.g. mvsa
    setPixelImage
    setPixelWorld
    setText
    setTitle
    setWsViewport
    setX
    setXY
    setY
    show
    write
    y2my
      y to minus y
'''
import itertools
import PySpectra
import PySpectra.mtpltlb.graphics as _mpl_graphics # to create postscript
import PySpectra.dMgt.calc as _calc
import PySpectra.dMgt.GQE as _gqe

def command( line):
    '''
    receives a line like: 'cls', 'create t1', etc.
    the line is split into pieces and the pysp functions
    are called depending on the first token, the verb.

    Examples
      PySpectra.command( "create s1")
      PySpectra.command( "display")
    '''
    line = line.strip()
    if len( line) == 0:
        return
    lst = line.split( ' ')

    if len( lst) > 1:
        lineRest = " ".join( lst[1:])
    else:
        lineRest = None
    #
    # antiderivative src [target] 
    #
    if lst[0] == 'antiderivative':
        return antiderivative( lineRest)
    #
    # cls
    #
    elif lst[0] == 'cls':
        return cls( lineRest)
    #
    #  create name scanname xMin 0. xMax 1. nPts 101
    #  create scanname 0. 1. 101
    #  create scanname
    #
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
    elif lst[0] == 'info':
        return info( lineRest)
    elif lst[0] == 'overlay':
        return overlay( lineRest)
    elif lst[0] == 'read':
        return read( lineRest)
    elif lst[0] == 'setArrowMotorCurrent':
        return setArrowMotorCurrent( lineRest)
    elif lst[0] == 'setArrowMotorSetPoint':
        return setArrowMotorSetPoint( lineRest)
    elif lst[0] == 'setArrowMotorMisc':
        return setArrowMotorMisc( lineRest)
    elif lst[0] == 'setComment':
        return setComment( lineRest)
    elif lst[0] == 'setPixelImage':
        return setPixelImage( lineRest)
    elif lst[0] == 'setPixelWorld':
        return setPixelWorld( lineRest)
    elif lst[0] == 'setText':
        return setText( lineRest)
    elif lst[0] == 'setTitle':
        return setTitle( lineRest)
    elif lst[0] == 'setWsViewport':
        return setWsViewport( lineRest)
    elif lst[0] == 'setX':
        return setX( lineRest)
    elif lst[0] == 'setXY':
        return setXY( lineRest)
    elif lst[0] == 'setY':
        return setY( lineRest)
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
        _calc.antiderivative( lst[0])
    elif len( lst) == 2: 
        _calc.antiderivative( lst[0], lst[1])
    else:
        raise ValueError( "ifc.antiderivative: wrong syntax %s" % line)

def cls( line):
    '''
    clears the graphics screen
    '''
    PySpectra.cls()

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
        hsh = dict(itertools.zip_longest(*[iter(l)] * 2, fillvalue=""))
    else:
        raise ValueError( "ifs.createScan: wrong syntax %s" % line)
        
    _gqe.Scan( **hsh)

def createPDF( line):
    '''
    create a PDF 
    '''
    fName = None
    if line is not None:
        l = line.split( ' ')
        if l is not None and len(l) > 0:
            fName = l[0]
    _mpl_graphics.createPDF( fileName = fName)

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
        _calc.derivative( lst[0])
    elif len( lst) == 2: 
        _calc.derivative( lst[0], lst[1])
    else:
        raise ValueError( "ifc.derivative: wrong syntax %s" % line)

def display( line):
    '''
    display 
    display nameGqe ...
    '''
    lst = None
    if line is not None:
        if len( line) > 0:
            lst = line.split( ' ')
        
    PySpectra.display( lst)

def delete( line):
    lst = None
    if line: 
        lst = line.split(' ')
    _gqe.delete( lst)

def info( line):
    '''
    displays some information
    '''
    PySpectra.info()

def overlay( line):
    '''
    overlay s1 s2
      s1 is plotted in the viewport of s2
    '''
    lst = line.split( ' ')
    if len( lst) != 2:
        raise ValueError( "ifc.overlay: expecting two scan names")
    _gqe.overlay( lst[0], lst[1])

def read( line):
    '''
    read fileName 
    read fileName -mca
    '''
    lst = None
    if line: 
        lst = line.split(' ')
    if len( lst) == 0:
        raise ValueError( "ifc.read: expecting a file name and optionally '-mca'")
        return 
    _gqe.read( lst)

def setComment( line):
    '''
    set the comment string for the whole plot
    '''
    _gqe.setComment( line)

def _pairs( lst): 
    a = iter(lst)
    return list( zip(a, a))

def _mySplit( s): 
    import re
    lst = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', s)
    return lst
    

def setText( line):
    '''
    setText gqeName textName string stringValue ...
            x xValue y yValue 
            hAlign hAlignValue vAlign vAlignValue 
            color colorValue 
            fontSize fontSizeValue
            NDC NDCValue

      setText       keyword
      gqeName       the GQE (Scan, Image) which will receive the text
      textName      the name of the textGqe
      string        keyword
      stringValue   the string to be displayed
      x             keyword
      xValue        the x-position
      y             keyword
      yValue        the y-position
      hAlign        keyword
      hAlignValue   left, right, center
      vAlign        keyword
      vAlignValue   top, bottom, center
      color         keyword
      colorValue    red, green, blue, yellow, cyan, magenta, black
      fontSize      keyword
      fontSizeValue 12

    example: 
      setText s1 comment string \"this is a comment\" x 0.1 hAlign left y 0.9 hAlign top color red

    '''
    lst = _mySplit( line)
    try:
        o = _gqe.getGqe( lst[0])
    except Exception as e: 
        raise ValueError( "ifc.setText: failed to gqeGqe %s" % lst[0])
        return
    flag = False
    #
    # first run: see, if textName is in textList
    #
    for t in o.textList: 
        if t.name == lst[1]: 
            flag = True
            break
    #
    # otherwise create it
    #
    if not flag: 
        o.addText( name = lst[1], text = lst[2])
    #
    # set the attributes of the text
    #
    # hAlign: 'left', 'right', 'center'
    # vAlign: 'top', 'bottom', 'center'
    # color: 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'black'
    # fontSize: e.g. 12 or None
    #  if None, the fontsize is chosen automatically depending on the number of plots
    # NDC: True, normalized device coordinates
    #
    for t in o.textList: 
        if t.name == lst[1]: 
            for k, v in _pairs( lst[2:]):
                if k == 'string': 
                    if v[0] == '"' and v[-1] == '"':
                        v = v[1:-1]
                    t.text = v
                elif k == 'color':
                    t.color =  v
                elif k == 'fontSize':
                    t.fontSize = int( v)
                elif k == 'NDC':
                    t.NDC = bool( v)
                elif k == 'hAlign':
                    t.hAlign =  v
                elif k == 'vAlign':
                    t.vAlign =  v
                elif k == 'x':
                    t.x = float( v)
                elif k == 'y':
                    t.y = float( v)
                else:
                    raise ValueError(" ifc.setText: failed to identify %s" % k)
            flag = True
            break

def setTitle( line):
    '''
    set the title of the whole plot
    '''
    _gqe.setTitle( line)

def setPixelImage( line): 
    '''
    setPixelImage nameGqe ix iy value
      ix, iy: indices, image coordinate frame
        ix > 0 and ix < width
        iy > 0 and iy < height
    '''
    lst = line.split( ' ')
    o = _gqe.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setPixelImage: failed to find %s" % lst[0])
    ix = int( lst[1])
    iy = int( lst[2])
    val = float( lst[3])
    o.setPixelImage( ix, iy, val)
    return 

def setArrowMotorCurrent( line): 
    '''
    handle the arrowMotorCurrent
      setArrowMotorCurrent nameGqe position <targetPos>
      setArrowMotorCurrent nameGqe hide
      setArrowMotorCurrent nameGqe show

      position: the motor current position, maybe from mvsa
    '''
    lst = line.split( ' ')
    o = _gqe.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setArrowMotorSCurrent: failed to find %s" % lst[0])
    o.setArrowMotorCurrent( lst[1:])
    return 

def setArrowMotorSetPoint( line): 
    '''
    handle the arrowMotorSetPoint
      setArrowMotorSetPoint nameGqe position <targetPos>
      setArrowMotorSetPoint nameGqe hide
      setArrowMotorSetPoint nameGqe show

      position: the motor target position, mayby from mouse-click
    '''
    lst = line.split( ' ')
    o = _gqe.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setArrowMotorSetPoint: failed to find %s" % lst[0])
    o.setArrowMotorSetPoint( lst[1:])
    return 

def setArrowMotorMisc( line): 
    '''
    handle the arrowMotorMisc
      setArrowMotorMisc nameGqe position <targetPos>
      setArrowMotorMisc nameGqe hide
      setArrowMotorMisc nameGqe show

      position: the motor target position, maybe from mvsa
    '''
    lst = line.split( ' ')
    o = _gqe.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setArrowMotorMisc: failed to find %s" % lst[0])
    o.setArrowMotorMisc( lst[1:])
    return 

def setPixelWorld( line): 
    '''
    setPixelWorld nameGqe x y value
      x, y: in world coordinates
        x >= xMin and x <= xMax
        y >= yMin and y <= yMax
    '''
    lst = line.split( ' ')
    o = _gqe.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setPixelWorld: failed to find %s" % lst[0])
    x = float( lst[1])
    y = float( lst[2])
    val = float( lst[3])
    o.setPixelWorld( x, y, val)
    return 

def setX( line): 
    '''
    setX nameGqe index x
    '''
    lst = line.split( ' ')
    o = _gqe.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setX: failed to find %s" % lst[0])
    index = int( lst[1])
    if index >= o.nPts: 
        raise ValueError(" ifc.setX: %s, index %d > nPts %d" % (lst[0], index, o.nPts))
        
    o.x[index] = float( lst[2]) 
    o.currentIndex = index
    return 

def setY( line): 
    '''
    setY nameGqe index y
    '''
    lst = line.split( ' ')
    o = _gqe.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setY: failed to find %s" % lst[0])
    index = int( lst[1])
    if index >= o.nPts: 
        raise ValueError(" ifc.setY: %s, index %d > nPts %d" % (lst[0], index, o.nPts))
        
    o.y[index] = float( lst[2]) 
    o.currentIndex = index
    return 

def setXY( line): 
    '''
    setXY nameGqe index x y
    '''
    lst = line.split( ' ')
    o = _gqe.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setXY: failed to find %s" % lst[0])
    index = int( lst[1])
    if index >= o.nPts: 
        raise ValueError(" ifc.setXY: %s, index %d > nPts %d" % (lst[0], index, o.nPts))
        
    o.x[index] = float( lst[2]) 
    o.y[index] = float( lst[3]) 
    o.currentIndex = index
    return 
    
def setWsViewport( line):
    '''
    setWsViewPort dina4
      dina4, dina4p, dina4s, dina5, dina5p, dina5s, dina6, dina6p, dina6s, 
    '''
    lst = None
    if line:
        lst = line.split( ' ')
    if len( lst) > 1:
        raise ValueError( "ifc.setWsViewport: expecting zero or one arguments")
        return 

    if len( lst) == 0:
        PySpectra.setWsViewport( None)
    else:
        PySpectra.setWsViewport( lst[0])

def show( line):
    '''
    show the list of scans
    '''
    _gqe.show()

def write( line):
    ''' 
    write the specified scans or all scans to a .fio file. 
    the prefix is pysp

    write
      write all scans

    write s1 s2
      write selected scans
    '''
    lst = line.split( ' ')
    _gqe.write( lst)

def y2my( line):
    lst = line.split( ' ')
    if len( lst) != 1 and len( lst) != 2:
        raise ValueError( "ifc.y2my: expecting one or two scan names")
    hsh = {}
    hsh[ 'name'] = lst[0]
    if len( lst) == 2:
        hsh[ 'nameNew'] = lst[1]
    _calc.yToMinusY( **hsh)
    
