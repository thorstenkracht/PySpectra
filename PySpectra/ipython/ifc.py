#!/usr/bin/env python
'''
A command-line-like interface to PySpectra, used by 
  - pyspMonitor.py to execute the commands received via ZMQ 
  - pyspDoor.py, via a queue
  - ipython command line, magic commands

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
    move s1 51 [flagConfirm]
    moveStart s1 51 [flagConfirm]
      display s1 and move the first motor of s1.motorNameList
    noop
    overlay s1 s2
      s1 is plotted in the viewport of s2
    read fileName
    setComment
    setArrowCurrent
    setArrowSetPoint
      used by the mouse-click callback
    setArrowMisc  
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
#
#
# The applictions that call ifc.command():
#
#  - pyspMonitor.py to execute the commands received via ZMQ 
#    pyspMonitorClass.py
#      zmqIfc.execHsh( hsh)
#        zmqIfc.execCommand( hsh): 
#          ifc.command( cmd)
#
#  - pyspDoor.py
#      sendHshQueue() 
#        pyspMonitorClass.py
#          execHshLocal( hsh)
#            zmqIfc.execHsh( hsh)
#              zmqIfc.execCommand( hsh): 
#                ifc.command( cmd)
#
#  - ipython, details can be found here: 
#      /home/kracht/Misc/pySpectra/PySpectra/__init__.py
#
import itertools
import PySpectra
import PySpectra.mtpltlb.graphics as _mpl_graphics # to create postscript
import PySpectra.calc as calc
import PySpectra.tangoIfc as tangoIfc

def command( line):
    '''
    receives a line like: 'cls', 'create t1', etc.
    the line is split into pieces and the pysp functions
    are called depending on the first token, the verb.

    Examples
      PySpectra.command( "create s1")
      PySpectra.command( "display")

    called from 
      - /home/kracht/Misc/pySpectra/PySpectra/ipython/startup.py
        to execute magic commands
      - /home/kracht/Misc/pySpectra/PySpectra/misc/zmqIfc.py
        execHsh() -> _execCommand() -> ifc.command()
    '''
    argout = None
    line = line.strip()
    if len( line) == 0:
        return argout
    lst = line.split( ' ')

    if len( lst) > 1:
        lineRest = " ".join( lst[1:])
    else:
        lineRest = None
    try: 
        #
        # antiderivative src [target] 
        #
        if lst[0] == 'antiderivative':
            return antiderivative( lineRest)
        #
        # cls
        #
        elif lst[0] == 'cls':
            argout = cls( lineRest)
            #
            #  create name scanname xMin 0. xMax 1. nPts 101
            #  create scanname 0. 1. 101
            #  create scanname
            #
        elif lst[0] == 'create':
            argout = create( lineRest)    
        elif lst[0] == 'createPDF':
            argout = createPDF( lineRest)
        elif lst[0] == 'delete':
            argout = delete( lineRest)
        elif lst[0] == 'derivative':
            argout = derivative( lineRest)
        elif lst[0] == 'display':
            argout = display( lineRest)
        elif lst[0] == 'info':
            argout = info( lineRest)
        elif lst[0] == 'move':
            argout = move( lineRest)
        elif lst[0] == 'moveStart':
            argout = moveStart( lineRest)
        elif lst[0] == 'noop':
            argout = noop( lineRest)
        elif lst[0] == 'overlay':
            argout = overlay( lineRest)
        elif lst[0] == 'read':
            argout = read( lineRest)
        elif lst[0] == 'setArrowCurrent':
            argout = setArrowCurrentCmd( lineRest)
        elif lst[0] == 'setArrowSetPoint':
            argout = setArrowSetPointCmd( lineRest)
        elif lst[0] == 'setArrowMisc':
            argout = setArrowMiscCmd( lineRest)
        elif lst[0] == 'setComment':
            argout = setComment( lineRest)
        elif lst[0] == 'setPixelImage':
            argout = setPixelImage( lineRest)
        elif lst[0] == 'setPixelWorld':
            argout = setPixelWorld( lineRest)
        elif lst[0] == 'setText':
            argout = setText( lineRest)
        elif lst[0] == 'setTitle':
            argout = setTitle( lineRest)
        elif lst[0] == 'setWsViewport':
            argout = setWsViewport( lineRest)
        elif lst[0] == 'setX':
            argout = setX( lineRest)
        elif lst[0] == 'setXY':
            argout = setXY( lineRest)
        elif lst[0] == 'setY':
            argout = setY( lineRest)
        elif lst[0] == 'show':
            argout = show( lineRest)
        elif lst[0] == 'write':
            argout = write( lineRest)
        elif lst[0] == 'y2my':
            argout = y2my( lineRest)
        else:
            raise ValueError( "ifc.command: failed to identify %s" % line)
    except Exception, e: 
        print( "ifc.command: error for '%s'" % line)
        print( "ifc.command: %s" % repr( e))
        argout = repr( e)
    
    return argout

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
        calc.antiderivative( lst[0])
    elif len( lst) == 2: 
        calc.antiderivative( lst[0], lst[1])
    else:
        raise ValueError( "ifc.antiderivative: wrong syntax %s" % line)

def cls( line):
    '''
    clears the graphics screen
    '''
    PySpectra.cls()

    return "done"

def create( line):
    '''
    creates a scan 
   
    Examples:     
      create name <scanname> xMin 0. xMax 1. nPts 101
      create <scanname> 0. 1. 101
      create <scanname>
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
        
    PySpectra.Scan( **hsh)
    return "done"

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
    return "done"

def derivative( line):
    '''
    derivative <src> [<target>] 
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
        calc.derivative( lst[0])
    elif len( lst) == 2: 
        calc.derivative( lst[0], lst[1])
    else:
        raise ValueError( "ifc.derivative: wrong syntax %s" % line)
    return "done"

def display( line):
    '''
    display 
    display <nameGqe> ...
    '''
    lst = None
    if line is not None:
        if len( line) > 0:
            lst = line.split( ' ')
        
    PySpectra.display( lst)
    return "done"

def delete( line):
    '''
    delete s1 s2
      deletes scans s1 and s2

    delete
      deletes all scans

    '''
    lst = None
    if line: 
        lst = line.split(' ')
    PySpectra.delete( lst)
    return "done"

def info( line):
    '''
    displays some information
    '''
    PySpectra.info()
    return "done"

def move( line):
    '''
    move s1 50 <flagConfirm> 

    <flagConfirm> - specify whether the user is prompted for 
                    confirmation before the move is executed, 
                    def.: True, safety first
    '''
    lst = line.split( ' ')
    if len( lst) < 2:
        raise ValueError( "ifc.move: expecting at least a scan name and the destination")
    gqe = PySpectra.getGqe( lst[0])
    flagConfirm = True
    if len( lst) == 3:
        if lst[2].upper() == "FALSE": 
            flagConfirm = False
    tangoIfc.move( gqe, float( lst[1]), flagConfirm = flagConfirm)
    return "done"

def moveStart( line):
    '''
    moveStart s1 50 <flagConfirm>

    <flagConfirm> - specify whether the user is prompted for 
                    confirmation before the move is executed, 
                    def.: True, safety first
    '''
    lst = line.split( ' ')
    if len( lst) < 2:
        raise ValueError( "ifc.moveStart: expecting at least a scan name and the destination")
    gqe = PySpectra.getGqe( lst[0])
    flagConfirm = True
    if len( lst) == 3:
        if lst[2].upper() == "FALSE": 
            flagConfirm = False
    tangoIfc.moveStart( gqe, float( lst[1]), flagConfirm = flagConfirm)
    return "done"

def noop( line):
    '''
    noop

      no operation
    '''
    return "done"

def overlay( line):
    '''
    overlay <s1> <s2>
      s1 is plotted in the viewport of s2
    '''
    lst = line.split( ' ')
    if len( lst) != 2:
        raise ValueError( "ifc.overlay: expecting two scan names")
    PySpectra.overlay( lst[0], lst[1])
    return "done"

def read( line):
    '''
    read <fileName> 
    read <fileName> -mca
    '''
    lst = None
    if line: 
        lst = line.split(' ')
    if len( lst) == 0:
        raise ValueError( "ifc.read: expecting a file name and optionally '-mca'")
    PySpectra.read( lst)
    return "done"

def setComment( line):
    '''
    setComment "some comment"
      set the comment string for the whole plot
    '''
    argout = "done"
    if not PySpectra.setComment( line): 
        argout = "trouble from PySpectra.setComment()"
    return argout

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
        o = PySpectra.getGqe( lst[0])
    except Exception as e: 
        raise ValueError( "ifc.setText: failed to gqeGqe %s" % lst[0])

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
    return "done"

def setTitle( line):
    '''
    set the title of the whole plot
    '''
    argout = "done"
    if not PySpectra.setTitle( line): 
        argout = "trouble from PySpectra.setTitle()"
    return argout

def setPixelImage( line): 
    '''
    setPixelImage <nameGqe> <ix> iy value
      ix, iy: indices, image coordinate frame
        ix > 0 and ix < width
        iy > 0 and iy < height
    '''
    lst = line.split( ' ')
    o = PySpectra.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setPixelImage: failed to find %s" % lst[0])
    ix = int( lst[1])
    iy = int( lst[2])
    val = float( lst[3])
    o.setPixelImage( ix, iy, val)
    return "done"

def setArrowCurrentCmd( line): 
    '''
    handle the arrowCurrent
      setArrowCurrent <nameGqe> position <targetPos>
      setArrowCurrent <nameGqe> hide
      setArrowCurrent <nameGqe> show

      position: the motor current position, maybe from mvsa
    '''
    lst = line.split( ' ')
    o = PySpectra.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setArrowSCurrent: failed to find %s" % lst[0])
    o.setArrowCurrentCmd( lst[1:])
    return "done"

def setArrowSetPointCmd( line): 
    '''
    handle the arrowSetPoint
      setArrowSetPoint <nameGqe> position <targetPos>
      setArrowSetPoint <nameGqe> hide
      setArrowSetPoint <nameGqe> show

      position: the motor target position, mayby from mouse-click
    '''
    lst = line.split( ' ')
    o = PySpectra.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setArrowSetPoint: failed to find %s" % lst[0])
    o.setArrowSetPointCmd( lst[1:])
    return "done"

def setArrowMiscCmd( line): 
    '''
    handle the arrowMisc
      setArrowMisc <nameGqe> position <targetPos>
      setArrowMisc <nameGqe> hide
      setArrowMisc <nameGqe> show

      position: the motor target position, maybe from mvsa
    '''
    lst = line.split( ' ')
    o = PySpectra.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setArrowMisc: failed to find %s" % lst[0])
    o.setArrowMiscCmd( lst[1:])
    return "done"

def setPixelWorld( line): 
    '''
    setPixelWorld <nameGqe> x y value
      x, y: in world coordinates
        x >= xMin and x <= xMax
        y >= yMin and y <= yMax
    '''
    lst = line.split( ' ')
    o = PySpectra.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setPixelWorld: failed to find %s" % lst[0])
    x = float( lst[1])
    y = float( lst[2])
    val = float( lst[3])
    o.setPixelWorld( x, y, val)
    return "done"

def setX( line): 
    '''
    setX <nameGqe> index x
    '''
    lst = line.split( ' ')
    o = PySpectra.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setX: failed to find %s" % lst[0])
    index = int( lst[1])
    if index >= o.nPts: 
        raise ValueError(" ifc.setX: %s, index %d > nPts %d" % (lst[0], index, o.nPts))
        
    o.x[index] = float( lst[2]) 
    o.currentIndex = index
    return "done"

def setY( line): 
    '''
    setY <nameGqe> index y
    '''
    lst = line.split( ' ')
    o = PySpectra.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setY: failed to find %s" % lst[0])
    index = int( lst[1])
    if index >= o.nPts: 
        raise ValueError(" ifc.setY: %s, index %d > nPts %d" % (lst[0], index, o.nPts))
        
    o.y[index] = float( lst[2]) 
    o.currentIndex = index
    return "done"

def setXY( line): 
    '''
    setXY <nameGqe> index x y
    '''
    lst = line.split( ' ')
    o = PySpectra.getGqe( lst[0])
    if o is None: 
        raise ValueError(" ifc.setXY: failed to find %s" % lst[0])
    index = int( lst[1])
    if index >= o.nPts: 
        raise ValueError(" ifc.setXY: %s, index %d > nPts %d" % (lst[0], index, o.nPts))
        
    o.x[index] = float( lst[2]) 
    o.y[index] = float( lst[3]) 
    o.currentIndex = index
    return "done"
    
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

    if len( lst) == 0:
        PySpectra.setWsViewport( None)
    else:
        PySpectra.setWsViewport( lst[0])

    return "done"

def show( line):
    '''
    show the list of scans
    '''
    PySpectra.show()
    return "done"

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
    PySpectra.write( lst)
    return "done"

def y2my( line):
    lst = line.split( ' ')
    if len( lst) != 1 and len( lst) != 2:
        raise ValueError( "ifc.y2my: expecting one or two scan names")
    hsh = {}
    hsh[ 'name'] = lst[0]
    if len( lst) == 2:
        hsh[ 'nameNew'] = lst[1]
    calc.yToMinusY( **hsh)
    return "done"
    
