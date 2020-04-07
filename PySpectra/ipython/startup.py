#!/usr/bin/env python
'''
This file defines those magic commands that operate PySpectra from ipython. 
It is imported by 00-start.py

  #!/usr/bin/env python
  import PySpectra.ipython.startup

see 'pyspectra_help' 
'''
from IPython.core.magic import (register_line_magic)
from IPython.core.getipython import get_ipython
import PySpectra.ipython.ifc as ifc
import PySpectra 
import PySpectra.dMgt.GQE as GQE
import numpy as np

ip = get_ipython()

@register_line_magic
def antiderivative(line):
    '''
    antiderivative <scan> [<scanNew>] 

    creates the antiderivative of a scan (Stammfunktion) a la Spectra

    Example
    -------
    antiderivative s1
      creates s1_antiderivative
    '''
    ifc.command( "antiderivative " + line)

@register_line_magic
def cls(line):
    '''
    cls - clear the screen
    '''
    ifc.command( "cls")

@register_line_magic
def create(line):
    '''
    Create a scan

    Examples:
      create s1
        uses these defaults:  xMin = 0., xMax = 10., nPts = 101

      create s1 0 1 11

      create name s1 xMin 0. xMax 10. nPts 101
    '''
    ifc.command( "create " + line)

@register_line_magic
def createPDF(line):
    '''
    Create a pdf file
    '''
    ifc.command( "createPDF " + line)

@register_line_magic
def delete(line):
    '''
    Delete one or all scans

    Parameters
    ----------
    None: 
          delete all scans
    Name: string
          a list of scans to be deleted

    Example
    -------
    delete s1 s2
      deletes scans s1 and s2
    delete
      deletes all scans
    '''
    ifc.command( "delete " + line)

@register_line_magic
def derivative(line):
    '''
    derivative <scan> [<scanNew>] 
    calculates the derivative of a scan a la Spectra

    Example
    -------
    derivative s1
      creates s1_derivative
    '''
    ifc.command( "derivative " + line)

@register_line_magic
def display(line):
    '''
    display one or more or all scans

    Parameters
    ----------
    None: 
          display all scans
    Name: string
          a list of scans to be displayed

    Example
    -------
    display s1 s2
      display scans s1 and s2
    display
      display all scans
    '''
    ifc.command( "display " + line)

@register_line_magic
def info(line):
    '''
    prints information about scans
    '''
    ifc.command( "info " + line)

@register_line_magic
def overlay(line):
    '''
    overlay scan1 scan2
      display scan1 in the viewport of scan2. The 
      window limits are defined by scan2
    '''
    ifc.command( "overlay " + line)

@register_line_magic
def procEventsLoop(line):
    PySpectra.ipython.procEventsLoop( line)

@register_line_magic
def pyspectra_help( line):
    print( "")
    print( " The ipython - PySpectra interface")
    print( " ---------------------------------")
    print( " These are the available commands")
    print( "   antiderivative, cls, create, delete, derivative,")
    print( "   display, info, overlay, procEventsLoop, read, setTitle, ")
    print( "   setComment, show, write, y2my")
    print( "")
    print( "  for more help use, e.g.: create?")
    print( "")

@register_line_magic
def read(line):
    '''
    print the list of scans
    '''
    ifc.command( "read " + line)

@register_line_magic
def write(line):
    '''
    write a .fio file
    '''
    ifc.command( "write " + line)

@register_line_magic
def setComment(line):
    '''
    setComment aComment
    '''
    ifc.command( "setComment " + line)

@register_line_magic
def setText(line):
    '''
    setText nameGqe nameText string SomeText x 0.1 y 0.9 hAlign left vAlign top color red 
    '''
    ifc.command( "setText " + line)

@register_line_magic
def setTitle(line):
    '''
    setTitle einTitel
    '''
    ifc.command( "setTitle " + line)

@register_line_magic
def setWsViewport(line):
    '''
    setWsViewport DINA4
    '''
    ifc.command( "setWsViewport " + line)

@register_line_magic
def setPixelImage(line):
    '''
    setPixelImage nameGqe ix iy val
      ix, iy in image coordinated
        ix >= 0 and ix < width
        iy >= 0 and iy < height
    '''
    ifc.command( "setPixelImage " + line)

@register_line_magic
def setPixelWorld(line):
    '''
    setPixelWorld nameGqe x y val
      x, y in physical coordinated
        x >= xMin and x <= xMax
        y >= yMin and y <= yMax
    '''
    ifc.command( "setPixelWorld " + line)

@register_line_magic
def setX(line):
    '''
    setX nameGqe index x-value

    index starts at 0
    this function sets the currentIndex
    '''
    ifc.command( "setX " + line)

@register_line_magic
def setXY(line):
    '''
    setXY nameGqe index x-value y-value

    index starts at 0
    this function sets the currentIndex
    '''
    ifc.command( "setXY " + line)

@register_line_magic
def setY(line):
    '''
    setY nameGqe index y-value

      index starts at 0
      this function sets the currentIndex
    '''
    ifc.command( "setY " + line)

@register_line_magic
def show(line):
    '''
    print the list of scans
    '''
    ifc.command( "show " + line)

@register_line_magic
def y2my(line):
    '''
    inverts y (y -> -y) 

    Examples
    --------
    y2my s1
      creates s1_y2my

    y2my s1 s2

    '''
    ifc.command( "y2my " + line)

#
# ====================================
# prepare some scan lists
#

@register_line_magic
def sl1(line):
    '''
    create 1 scan
    '''
    PySpectra.cls()
    GQE.delete()
    t1 = GQE.Scan( name = "t1", color = 'blue', yLabel = 'sin')
    t1.y = np.sin( t1.x)

@register_line_magic
def sl2(line):
    '''
    scan list 1, creates some scans, fill them with data
    '''
    PySpectra.cls()
    GQE.delete()
    t1 = GQE.Scan( name = "t1", color = 'blue', yLabel = 'sin')
    t1.y = np.sin( t1.x)
    t2 = GQE.Scan( "t2", yLabel = 'cos')
    t2.y = np.cos( t2.x)
    t3 = GQE.Scan( name = "t3", color = 'green', yLabel = 'tan')
    t3.y = np.tan( t3.x)
    t4 = GQE.Scan( name = "t4", color = 'cyan', yLabel = 'random')
    t4.y = np.random.random_sample( (len( t4.y), ))
    t5 = GQE.Scan( name = "t5", color = 'magenta', yLabel = 'x**2')
    t5.y = t5.x * t5.x
    GQE.overlay( 't5', 't3')

@register_line_magic
def sl3(line):
    '''
    many scans
    '''
    PySpectra.cls()
    GQE.delete()
    for i in range( 20):
        t = GQE.Scan( name = "t%d" % i, color = 'blue')
        t.y = np.random.random_sample( (len( t.y), ))

@register_line_magic
def sl4(line):
    '''
    gauss
    '''
    PySpectra.cls()
    GQE.delete()
    g = GQE.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma * np.sqrt(2 * np.pi)) * \
          np.exp( - (g.y - mu)**2 / (2 * sigma**2))

pyspectra_help("")        

# We delete these to avoid name conflicts for automagic to work
del antiderivative
del cls
del create
del createPDF
del delete
del derivative
del display
del info
del overlay
del procEventsLoop
del pyspectra_help
del read
del show
del setComment
del setText
del setTitle
del setPixelImage
del setPixelWorld
del setX
del setXY
del setY
del setWsViewport
del write
del y2my

del sl1
del sl2
del sl3
del sl4

