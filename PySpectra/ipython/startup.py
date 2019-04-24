#!/usr/bin/env python
'''
this file is imported by 00-start.py

  #!/usr/bin/env python
  import sys
  sys.path.append( "/home/kracht/Misc/pySpectra")
  import PySpectra.ipython.startup

it defines those magic commands that operate PySpectra from ipython

see 'pysp_help' 
'''
from IPython.core.magic import (register_line_magic)
from IPython.core.getipython import get_ipython
import PySpectra.ipython.ifc as ifc
import PySpectra as pysp
import numpy as np

ip = get_ipython()

@register_line_magic
def antiderivative(line):
    '''
    creates the antiderivative of a scan (Stammfunktion)

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
    calc the derivative of a scan

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
def overlay(line):
    '''
    overlay scan1 scan2
      display scan1 in the viewport of scan2. The 
      window limits are defined by scan2
    '''
    ifc.command( "overlay " + line)

@register_line_magic
def procEventsLoop(line):
    pysp.ipython.procEventsLoop( line)

@register_line_magic
def pysp_help( line):
    print ""
    print " The ipython - PySpectra interface"
    print " ---------------------------------"
    print " These are the available commands"
    print "   antiderivative, cls, create, delete, derivative,"
    print "   display, overlay, procEventsLoop, read, setTitle, "
    print "   setComment, show, write, y2my"
    print ""
    print "  for more help use, e.g.: create?"
    print ""

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
    pysp.cls()
    pysp.delete()
    t1 = pysp.Scan( name = "t1", color = 'blue', yLabel = 'sin')
    t1.y = np.sin( t1.x)

@register_line_magic
def sl2(line):
    '''
    scan list 1, creates some scans, fill them with data
    '''
    pysp.cls()
    pysp.delete()
    t1 = pysp.Scan( name = "t1", color = 'blue', yLabel = 'sin')
    t1.y = np.sin( t1.x)
    t2 = pysp.Scan( "t2", yLabel = 'cos')
    t2.y = np.cos( t2.x)
    t3 = pysp.Scan( name = "t3", color = 'green', yLabel = 'tan')
    t3.y = np.tan( t3.x)
    t4 = pysp.Scan( name = "t4", color = 'cyan', yLabel = 'random')
    t4.y = np.random.random_sample( (len( t4.y), ))
    t5 = pysp.Scan( name = "t5", color = 'magenta', yLabel = 'x**2')
    t5.y = t5.x * t5.x
    pysp.overlay( 't5', 't3')

@register_line_magic
def sl3(line):
    '''
    many scans
    '''
    pysp.cls()
    pysp.delete()
    for i in range( 20):
        t = pysp.Scan( name = "t%d" % i, color = 'blue')
        t.y = np.random.random_sample( (len( t.y), ))

@register_line_magic
def sl4(line):
    '''
    gauss
    '''
    pysp.cls()
    pysp.delete()
    g = pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma * np.sqrt(2 * np.pi)) * \
          np.exp( - (g.y - mu)**2 / (2 * sigma**2))

pysp_help("")        

# We delete these to avoid name conflicts for automagic to work
del antiderivative
del cls
del create
del createPDF
del delete
del derivative
del display
del overlay
del procEventsLoop
del pysp_help
del read
del show
del setComment
del setTitle
del setWsViewport
del write
del y2my

del sl1
del sl2
del sl3
del sl4

