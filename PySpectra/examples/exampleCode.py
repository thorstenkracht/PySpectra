#!/usr/bin/env python
'''
the functions in this module are automatically inserted into the 'Examples' menu of 
  /home/kracht/Misc/pySpectra/PySpectra/pySpectraGuiClass.py 
and they are unittest-executed by
  /home/kracht/Misc/pySpectra/test/examples/testExamples.py

From the command line: 
  python -c 'import PySpectra; PySpectra.example22Scans()'

'''

import numpy as _np
import math as _math
import os as _os
import time as _time
import pyqtgraph as _pg
import PySpectra 
import PySpectra.misc.zmqIfc as _zmqIfc
import PySpectra.dMgt.GQE as _gqe


def exampleDataVia_execHsh(): 
    '''
    replace execHsh() with toPyspMonitor() to connect to pyspMonitor.py
    '''
    import random
    MAX = 25
    #
    # create some data
    #
    pos = [float(n)/MAX for n in range( MAX)]
    d1 = [random.random() for n in range( MAX)]
    d2 = [random.random() for n in range( MAX)]
    #
    # colors: 'RED', 'GREEN', 'BLUE','YELLOW', 'CYAN', 'MAGENTA', 'BLACK', 'WHITE', 'NONE', 
    # lineStyles: 'SOLID', 'DASHED', 'DOTTED', 'DASHDOTTED'
    # symbols: 'o', 's', 'd', '+'
    #
    #
    # send the data 
    #
    hsh = { 'putData': 
            {'title': "Important Data", 
             'comment': "a comment", 
             'columns': 
             [ { 'name': "eh_mot01", 'data' : pos},
               { 'name': "eh_c01", 'data' : d1},
               { 'name': "eh_c02", 'data' : d2, 
                 'symbolColor': 'blue', 'symbol': '+', 'symbolSize': 5, 
                 'xLog': False, 'yLog': False, 
                 'showGridX': False, 'showGridY': False},
             ]}}

    hsh = _zmqIfc.execHsh( hsh)
    print( "exampleDataVia_execHsh: putData returns %s" % repr( hsh) )

    #
    # retrieve the data 
    #
    hsh = _zmqIfc.execHsh( { 'getData': True})
    #
    # ... and compare.
    #
    for i in range( MAX):
        if pos[i] != hsh[ 'getData']['EH_C01']['x'][i]:
            print( "error: pos[i] != x[i]")
        if d1[i] != hsh[ 'getData'][ 'EH_C01'][ 'y'][i]:
            print( "error: d1[i] != y[i]")
        
    print( "exampleDataVia_execHsh: getData returns x(EH_C01) %s " % hsh[ 'getData']['EH_C01']['x'])
    print( "exampleDataVia_execHsh: getData returns y(EH_C01) %s" % hsh[ 'getData']['EH_C01']['y'])
    return 

def mandelbrot( c, maxiter):
    '''
    needed for the testing procedures
    '''
    z = c
    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return 0

def exampleImageMBVia_execHsh(): 
    '''
    this examples simulates the toPyspMonitor() interface

    replace execHsh() by toPyspMonitor() to connect to pyspMonitor.py 
    '''
    PySpectra.setWsViewport( 'DINA5S')

    PySpectra.cls()
    _gqe.delete()

    (xmin, xmax) = (-2.,-0.5)
    (ymin, ymax) = (0, 1.5)
    (width, height) = (10, 10)
    maxiter = 25

    #
    # do the clean-up before we start
    #
    hsh =  _zmqIfc.execHsh( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
    if hsh[ 'result'] != "done":
        print( "error from ['delete', 'setWsViewport DINA5S', 'cls']")
        return 
    #
    # create the image
    #
    hsh = { 'Image': 
            { 'name': "Mandelbrot",
              'xMin': xmin, 'xMax': xmax, 'width': width, 
              'yMin': ymin, 'yMax': ymax, 'height': height}}

    hsh = _zmqIfc.execHsh( hsh)
    if hsh[ 'result'] != "done":
        print( "error from putData")
        return 
    #
    # fill the image, pixel by pixel
    #
    r1 = _np.linspace(xmin, xmax, width)
    r2 = _np.linspace(ymin, ymax, height)
    for i in range(width):
        for j in range(height):
            res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
            hsh = { 'command': [ 'setPixelImage Mandelbrot %d %d %g' % ( i, j, res)]}
            hsh = _zmqIfc.execHsh( hsh)
            if hsh[ 'result'] != "done":
                print( "error from setPixel")
                return
        PySpectra.cls()
        PySpectra.display()

    return 

def exampleImageMBVia_execHsh_OneChunk(): 
    '''
    this examples simulates the toPyspMonitor() interface

    replace execHsh() by toPyspMonitor() to connect to pyspMonitor.py 
    '''
    print( "execHsh_OneChunk") 
    PySpectra.setWsViewport( 'DINA5S')

    PySpectra.cls()
    _gqe.delete()

    (xmin, xmax) = (-2., 1.0)
    (ymin, ymax) = ( -1.5, 1.5)
    (width, height) = (500, 500)
    maxiter = 128

    #
    # do the clean-up before we start
    #
    hsh =  _zmqIfc.execHsh( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
    if hsh[ 'result'] != "done":
        print( "error from ['delete', 'setWsViewport DINA5S', 'cls']")
        return 
    #
    # fill the image, pixel by pixel
    #
    r1 = _np.linspace(xmin, xmax, width)
    r2 = _np.linspace(ymin, ymax, height)
    #data = _np.ndarray( (width, height), _np.int32)
    data = _np.ndarray( (width, height), _np.float64)
    for i in range(width):
        for j in range(height):
            res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
            data[i][j] = int( res)

    print( "execHsh_OneChunk-1") 
    _zmqIfc.execHsh( { 'putData': 
                    { 'images': [{'name': "Mandelbrot", 'data': data,
                                  'xMin': xmin, 'xMax': xmax, 
                                  'yMin': ymin, 'yMax': ymax}]}})
    print( "execHsh_OneChunk-2") 
    PySpectra.cls()
    print( "execHsh_OneChunk-3") 
    PySpectra.display()
    print( "execHsh_OneChunk DONE") 

    return 


def example_LogPlotWithText():
    '''
    create 1 scan, y-log scale, one text
    '''
    PySpectra.cls()
    _gqe.delete()
    PySpectra.setWsViewport( "DINA5")
    t1 = _gqe.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, 
                     lineColor = 'blue', xLabel='Position', 
                     yLabel = 'signal', yLog = True)
    t1.addText( text = "a left/center aligned text, should be in the center", 
                x = 0.05, y = 0.5, hAlign = 'left', vAlign = 'center')
    PySpectra.display()

def example_LogXScale():
    PySpectra.cls()
    _gqe.delete()
    PySpectra.setWsViewport( "DINA5")
    _gqe.setTitle( "log x-scale")
    t1 = _gqe.Scan( name = "t1", xMin = 0.01, xMax = 100., nPts = 101, 
                    lineColor = 'blue', xLabel='Position', yLabel = 'signal', 
                     yLog = False, xLog = True)
    PySpectra.display()


def example_PlotWithSeveralTexts():
    '''
    create 1 scan with several texts
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "Here could be the title")
    _gqe.setComment( "comment: Sinus(), shifted up by 1.1")
    PySpectra.setWsViewport( "DINA5")
    t1 = _gqe.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, 
                     lineColor = 'blue', xLabel = 'Position', yLabel = 'sin')
    t1.addText( text = "a left/center aligned text", x = 0.05, y = 0.8, 
                hAlign = 'left', vAlign = 'center')
    t1.addText( text = "a right/centeraligned text", x = 0.95, y = 0.8, 
                hAlign = 'right', vAlign = 'center')
    t1.addText( text = "a center/top aligned text, red, fontSize: 10", 
                x = 0.5, y = 0.5, hAlign = 'center', 
                vAlign = 'top', fontSize=10, color = 'red')
    t1.addText( text = "a center/center aligned text", x = 0.5, y = 0.5, 
                hAlign = 'center', vAlign = 'center')
    t1.addText( text = "a center/bottom aligned text", x = 0.5, y = 0.5, 
                hAlign = 'center', vAlign = 'bottom')
    t1.y = _np.sin( t1.x) + 1.001
    PySpectra.display()

def example_Overlay2():
    '''
    create 2 overlaid scans
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "Overlay 2 Scans")
    _gqe.setComment( "no comment")
    PySpectra.setWsViewport( "DINA5")
    g = _gqe.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                    lineColor = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2.*sigma**2))
    t1 = _gqe.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    _gqe.overlay( "sinus", "gauss")
    PySpectra.display()

def example_OverlayDoty():
    '''
    create 2 overlaid scans
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "2 Overlay scans, x-axis tick labels show date")
    PySpectra.setWsViewport( "DINA5")
    t1 = _gqe.Scan( name = "t1", xMin = 0, xMax = 10, nPts = 101, 
                     lineColor = 'blue', 
                     xLabel = 'Position', yLabel = 'sin', doty = True)
    t1.y = _np.sin( t1.x)
    t2 = _gqe.Scan( "t2", xLabel = 'Position', yLabel = 'cos', 
                     xMin = 0, xMax = 10, nPts = 101, 
                     lineColor = 'green', doty = True)
    t2.y = _np.cos( t2.x)
    t2.overlay = "t1"
    PySpectra.display()

def example_PlotsWithTextContainer():
    '''
    create 3 scans and a text container
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "here could be a title")
    _gqe.setComment( "this is a comment")
    PySpectra.setWsViewport( "DINA5")
    textScan = _gqe.Scan( name = "textContainer", textOnly = True)
    textScan.addText( text = "some information", 
                      x = 0., y = 0.95, color = 'blue')
    textScan.addText( text = "and more infos", 
                      x = 0., y = 0.85, color = 'blue')
    t1 = _gqe.Scan( "t1", lineColor = 'blue', xLabel = 'Position', 
                     yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    t2 = _gqe.Scan( "t2", xLabel = 'Position', yLabel = 'cos', 
                     symbol = 'o', symbolColor = 'red', symbolSize = 5)
    t2.y = _np.cos( t2.x)
    t3 = _gqe.Scan( "t3", xLabel = 'Position', yLabel = 'tan', 
                     symbol = '+', lineColor = 'cyan', 
                     symbolColor = 'green', symbolSize = 5)
    t3.y = _np.tan( t3.x)
    PySpectra.display()

def example_Create5Plots():
    '''
    create 5 scans, different colors, demonstrate overlay feature
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "5 Scans, t5 is overlaid to t3")
    PySpectra.setWsViewport( "DINA5")
    t1 = _gqe.Scan( name = "t1", lineColor = 'blue', yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    t2 = _gqe.Scan( "t2", xLabel = 'Position', yLabel = 'cos', symbol = '+')
    t2.y = _np.cos( t2.x)
    t3 = _gqe.Scan( name = "t3", lineColor = 'green', 
                     xLabel = 'Position', yLabel = 'tan')
    t3.y = _np.tan( t3.x)
    t4 = _gqe.Scan( name = "t4", lineColor = 'NONE', 
                     xLabel = 'Position', yLabel = 'random', 
                     symbol = '+', symbolColor = 'CYAN')
    t4.y = _np.random.random_sample( (len( t4.y), ))
    t5 = _gqe.Scan( name = "t5", lineColor = 'magenta', 
                     xLabel = 'Position', yLabel = 'x**2')
    t5.y = t5.x * t5.x
    _gqe.overlay( 't5', 't3')
    PySpectra.display()

def example_Create22Plots():
    '''
    create 22 plots
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "22 Scans")
    _gqe.setComment( "and a comment")
    PySpectra.setWsViewport( "DINA4")
    for i in range( 22): 
        t = _gqe.Scan( name = "t%d" % i, lineColor = 'blue',
                        xLabel = 'Position', yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
    PySpectra.display()

def example_Create56x3Plots():
    '''
    create 56x3 plots
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "56 x 3 Scans")
    _gqe.setComment( "Display many Scans")
    PySpectra.setWsViewport( "DINA4")
    for i in range( 56): 
        t = _gqe.Scan( name = "t%d_a" % i, lineColor = 'blue', nPts = 200, 
                        yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
        t = _gqe.Scan( name = "t%d_b" % i, lineColor = 'red', nPts = 200, 
                        yLabel = 'rand', overlay = "t%d_a" % i)
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
        t = _gqe.Scan( name = "t%d_c" % i, lineColor = 'green', nPts = 200, 
                        yLabel = 'rand', overlay = "t%d_a" % i)
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
    PySpectra.display()
    return 

def example_CreatePDF():
    '''
    create a pdf file
    '''
    printer = _os.getenv( "PRINTER")
    if printer is None: 
        print( "examplecreatePDF: environment variable PRINTER not defined, returning")
        return 

    PySpectra.cls()
    _gqe.delete()

    _gqe.setTitle( "Create PDF file and send it to the printer")
    PySpectra.setWsViewport( "DINA5")
    scan = _gqe.Scan( name = 'PDF Output', nPts = 100, xMin = -1., xMax = 1.,
                           xLabel = 'Position', yLabel = "Counts")
    
    scan.y = _np.sin( scan.x)

    PySpectra.setWsViewport( "DINA4")
    PySpectra.display()

    PySpectra.createPDF( flagPrint = True)
    return 

def example_GaussAndSinusOverlay():
    '''
    overlay 2 scans
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "2 Overlay Scans")
    PySpectra.setWsViewport( "DINA5")
    g = _gqe.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                    lineColor = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2.*sigma**2))
    t1 = _gqe.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    _gqe.overlay( "sinus", "gauss")
    PySpectra.display()

def example_Gauss():
    '''
    gauss plot
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "A simple Gauss curve")
    _gqe.setComment( "Can be used with SSA, calculating derivative and so")
    PySpectra.setWsViewport( "DINA5")
    g = _gqe.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2*sigma**2))
    PySpectra.display()
    return 

def example_GaussManyOverlay():
    '''
    gauss plot
    '''
    PySpectra.cls()
    _gqe.delete()
    PySpectra.setWsViewport( "DINA5")
    g = _gqe.Scan( name = "gauss", xMin = -10., xMax = 10., nPts = 101)
    #mu = 0.
    #sigma = 1.
    #g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2*sigma**2))
    mu1 = 0.
    sigma1 = 1.
    mu2 = 6.5
    sigma2 = 1.2
    g.y = 1./(sigma1*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu1)**2/(2*sigma1**2)) + \
          2./(sigma2*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu2)**2/(2*sigma2**2))
    g.autoscaleX = False
    g.autoscaleY = False
    g.xMax = 11
    g.xMin = -4
    g.yMin = 0
    g.yMax = 2
    for i in range( 1,50):  # don't want i == 0
        gqe = _gqe.Scan( name = "gauss%d" % i, xMin = -5., xMax = 5., 
                          nPts = 101)
        gqe.x = g.x + 0.02 * i
        gqe.y = g.y + 0.02 * i
        _gqe.overlay( "gauss%d" % i, "gauss")
        gqe.useTargetWindow = True
        
    PySpectra.display()
    return 

def example_GaussNoisy():
    '''
    gauss plot
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "a noisy Gauss")
    _gqe.setComment( "See how SSA behaves with noisy data")
    PySpectra.setWsViewport( "DINA5")
    g = _gqe.Scan( name = "gauss_noisy", xMin = -5., xMax = 5., nPts = 101)
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2*sigma**2)) + \
          _np.random.random_sample( (len( g.x), ))*0.05
    PySpectra.display()
    return 

def example_Gauss2():
    ''' 
    2 gauss plot
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "Two Gauss curves")
    _gqe.setComment( "To demonstrate how SSA limits can be defined with VLines")
    PySpectra.setWsViewport( "DINA5")
    g = _gqe.Scan( name = "gauss", xMin = -10., xMax = 10., nPts = 101)
    mu1 = 0.
    sigma1 = 1.
    mu2 = 6.5
    sigma2 = 1.2
    g.y = 1./(sigma1*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu1)**2/(2*sigma1**2)) + \
          2./(sigma2*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu2)**2/(2*sigma2**2))
    PySpectra.display()
    return 

def example_Scanning():
    '''    
    '''
    PySpectra.cls()
    _gqe.delete()

    _gqe.setTitle( "scanning, x-axis is fixed")
    PySpectra.setWsViewport( "DINA5")
    sinus = _gqe.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, 
                        autoscaleX = False, lineColor = 'red')


    for i in range( sinus.nPts): 
        sinus.setX( i, i/10. + 0.01)
        sinus.setY( i, _math.sin( i/10.))
        PySpectra.display( ['sinus'])
        _time.sleep( 0.01)
    return 

def example_ScanningMesh():
    '''    
    '''
    PySpectra.cls()
    _gqe.delete()

    (xmin, xmax) = (-2., 1)
    (ymin, ymax) = (-1.5, 1.5)
    (width, height) = (20, 20)
    maxiter = 20
    
    r1 = _np.linspace(xmin, xmax, width)
    r2 = _np.linspace(ymin, ymax, height)
    n3 = _np.zeros((width,height))
            
    m = _gqe.Image( name = "MandelbrotSet", colorMap = 'Greys', 
                     estimatedMax = 20, 
                     xMin = xmin, xMax = xmax, width = width, 
                     yMin = ymin, yMax = ymax, height = height)
    
    _gqe.setTitle( "Simulate a mesh scan")
    PySpectra.setWsViewport( "DINA5")
    sinus = _gqe.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = width*height, 
                        autoscaleX = False, lineColor = 'red')
    cosinus = _gqe.Scan( name = 'cosinus', xMin = 0., xMax = 6.0, nPts = width*height, 
                        autoscaleX = False, lineColor = 'red')

    PySpectra.display()

    (iI, jI) = (0, 0)
    for i in range( sinus.nPts): 
        x = float(i)*6.28/float(sinus.nPts)
        sinus.setX( i, x)
        cosinus.setX( i, x)
        sinus.setY( i, _math.sin( x))
        cosinus.setY( i, _math.cos( x))
        res = mandelbrot(r1[iI] + 1j*r2[jI],maxiter)
        m.data[iI][jI] = res 
        iI += 1
        if iI == width: 
            iI = 0
            jI += 1
        PySpectra.display()
    PySpectra.cls()
    PySpectra.display()
    return 

def example_ScanningAutoscaleX():
    '''    
    '''
    PySpectra.cls()
    _gqe.delete()
    
    _gqe.setTitle( "scanning, x-axis is re-scaled")
    PySpectra.setWsViewport( "DINA5")
    sinus = _gqe.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, 
                        autoscaleX = True, lineColor = 'red')
    for i in range( sinus.nPts): 
        sinus.setX( i, i/10. + 0.01)
        sinus.setY( i, _math.sin( i/10.))
        PySpectra.display( ['sinus'])
        _time.sleep( 0.01)
    return 

def example_ScanningReverse():
    '''    
    '''
    PySpectra.cls()
    _gqe.delete()
    
    _gqe.setTitle( "scanning in reverse direction, x-axis is fixed")
    PySpectra.setWsViewport( "DINA5")
    sinus = _gqe.Scan( name = 'sinus', 
                        xMin = 0., xMax = 6.0, nPts = 101, 
                        autoscaleX = False, 
                        lineColor = 'red')
    sinus.xMax = 10.
    for i in range( sinus.nPts): 
        x = 10. - i/10.
        sinus.setX( i, x)
        sinus.setY( i, _math.sin( i/10.))
        PySpectra.display( ['sinus'])
        _time.sleep( 0.05)
    return 

def example_ScanningReverseAutoscaleX():
    '''    
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "scanning in reverse direction, the x-axis is re-scaled")
    PySpectra.setWsViewport( "DINA5")
    sinus = _gqe.Scan( name = 'sinus', 
                            xMin = 0., xMax = 6.0, nPts = 101, 
                            autoscaleX = True, 
                            lineColor = 'red')
    for i in range( sinus.nPts): 
        x = 10. - i/10.
        sinus.x[i] = x
        sinus.y[i] = _math.sin( i/10.)
        sinus.currentIndex = i
        PySpectra.display( ['sinus'])
        _time.sleep( 0.02)

def example_Lissajous(): 
    '''
    plots and updates a Lissajous figure
    '''
    PySpectra.setWsViewport( "DINA5S")
    
    PySpectra.cls()
    _gqe.delete()
    scan = _gqe.Scan( name = 'Lissajous', nPts = 1000, xMin = -1., xMax = 1.)
    
    x  = _np.linspace( 0., 6.5, 1000)
    y  = _np.linspace( 0., 6.5, 1000)
    
    scan.x = _np.cos( x)
    scan.y = _np.sin( y)
    
    PySpectra.display()
    
    for i in range( 500):
        x = x + 0.005
        scan.plotDataItem.setData(_np.cos( x), _np.sin( y))
        PySpectra.processEvents()

def example_Overlay2BothLog(): 
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "2 Overlay Scans, both with log scale")
    _gqe.setComment( "both axes have different ranges")
    PySpectra.setWsViewport( "DINA5")
    g1 = _gqe.Scan( name = "gauss", xMin = -5., xMax = 5., 
                     yLog = True, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = _gqe.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0.001, 
                     yLog = True, yMax = 1., nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))*100.

    _gqe.overlay( "gauss2", "gauss")

    PySpectra.display()

def example_Overlay2FirstLog(): 
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "2 Overlay Scans, first (red) has log scale")
    _gqe.setComment( "Sadly, there are no major tick mark strings at the right axis")
    PySpectra.setWsViewport( "DINA5")
    g1 = _gqe.Scan( name = "gauss", xMin = -5., xMax = 5., 
                     yLog = True, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = _gqe.Scan( name = "gauss2", xMin = -5., xMax = 5., yLog = False, 
                    yMax = 1., nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))

    _gqe.overlay( "gauss2", "gauss")

    PySpectra.display()

def example_Overlay2SecondLog(): 
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "2 Overlay Scans, 2nd (green) has log scale")
    _gqe.setComment( "Sadly, there are no major tick mark strings at the right axis")
    PySpectra.setWsViewport( "DINA5")
    g1 = _gqe.Scan( name = "gauss", xMin = -5., xMax = 5., 
                     yLog = False, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = _gqe.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0.001, 
                     yLog = True, yMax = 1., nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))

    _gqe.overlay( "gauss2", "gauss")

    PySpectra.display()

def example_ImageMB(): 

    PySpectra.setWsViewport( 'DINA5S')

    PySpectra.cls()
    _gqe.delete()

    (xmin, xmax) = (-2., 0.5)
    (ymin, ymax) = (-1.25, 1.25)
    (width, height) = (750, 750)
    maxiter = 512
    
    m = _gqe.Image( name = "MandelbrotSet",
                     flagAxes = True, 
                     maxIter = maxiter, 
                     xMin = xmin, xMax = xmax, width = width, 
                     yMin = ymin, yMax = ymax, height = height)
    m.flagZoomSlow = False
    m.zoom()
    PySpectra.cls()
    PySpectra.display()
    return 
"""
def example_ImageMBSlow(): 

    PySpectra.setWsViewport( 'DINA5S')

    PySpectra.cls()
    _gqe.delete()

    (xmin, xmax) = (-2., 0.5)
    (ymin, ymax) = (-1.25, 1.25)
    (width, height) = (500, 500)
    maxiter = 256
    
    m = _gqe.Image( name = "MandelbrotSet",
                    xMin = xmin, xMax = xmax, width = width, 
                    yMin = ymin, yMax = ymax, height = height)

    m.flagZoomSlow = True
    m.zoom()
    PySpectra.cls()
    PySpectra.display()
    return 
"""
def example_ImageRandom(): 

    import random
    
    PySpectra.setWsViewport( 'DINA5S')

    PySpectra.cls()
    _gqe.delete()

    (xmin, xmax) = (-2., 1)
    (ymin, ymax) = (-1.5, 1.5)
    (width, height) = (500, 500)
    
    r1 = _np.linspace(xmin, xmax, width)
    r2 = _np.linspace(ymin, ymax, height)
    n3 = _np.empty((width,height))
    for i in range(width):
        for j in range(height):
            n3[i,j] = i + random.random()*j + 100.
            
    m = _gqe.Image( name = "ImageRandom", data = n3, 
                    xMin = xmin, xMax = xmax, width = width, 
                    yMin = ymin, yMax = ymax, height = height, 
                    xLabel = "x-Axis", yLabel = "y-Axis")

    PySpectra.cls()
    PySpectra.display()
    return 


def example_mvsa():
    '''
    move by scan analysis
    '''
    PySpectra.cls()
    _gqe.delete()
    _gqe.setTitle( "Move by Scan Analysis")
    PySpectra.setWsViewport( "DINA5")
    g = _gqe.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                    lineColor = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2.*sigma**2))
    PySpectra.display()

'''
#!/usr/bin/env python

# 
# this piece of code can only be executed, if the pyspMonitor.py is running
# some date are sent to the pyspMonitor where they are displayed
# then data are retrieved from pyspMonitor and compared with the originals
#
import PySpectra as pysp
import random

def main():
    MAX = 5
    #
    # create some data
    #
    pos = [float(n)/MAX for n in range( MAX)]
    d1 = [random.random() for n in range( MAX)]
    d2 = [random.random() for n in range( MAX)]
    
    print( "pos %s" % repr( pos))
    print( "d1: %s" % repr( d1))
    #
    # colors: 'RED', 'GREEN', 'BLUE','YELLOW', 'CYAN', 'MAGENTA', 'BLACK', 'WHITE', 'NONE', 
    # lineStyles: 'SOLID', 'DASHED', 'DOTTED', 'DASHDOTTED'
    # symbols: 'o', 's', 'd', '+'
    #
    #
    # send the data to pyspMonitor
    #
    hsh = { 'putData': 
            {'title': "Important Data", 
             'columns': 
             [ { 'name': "eh_mot01", 'data' : pos},
               { 'name': "eh_c01", 'data' : d1},
               { 'name': "eh_c02", 'data' : d2, 
                 'symbolColor': 'blue', 'symbol': '+', 'symbolSize': 5, 
                 'xLog': False, 'yLog': False, 
                 'showGridX': False, 'showGridY': False},
             ]}}

    hsh = pysp.toPyspMonitor( hsh)
    print( "return values of putData: %s" % repr( hsh) )

    #
    # retrieve the data from pyspMonitor
    #
    hsh = pysp.toPyspMonitor( { 'getData': True})
    #
    # ... and compare.
    #
    for i in range( MAX):
        if pos[i] != hsh[ 'getData']['EH_C01']['x'][i]:
            print( "error: pos[i] != x[i]")
        if d1[i] != hsh[ 'getData'][ 'EH_C01'][ 'y'][i]:
            print( "error: d1[i] != y[i]")
        
    print( "getData, pos: %s" % hsh[ 'getData']['EH_C01']['x'])
    print( "getData, pos: %s" % hsh[ 'getData']['EH_C01']['y'])
    return 

if __name__ == "__main__":
    main()

----- cut here

#!/usr/bin/env python
# 
# this piece of code can only be executed,   
# if the pyspMonitor.py is running
#
import PySpectra as pysp
import random
import numpy as np
import time

def mandelbrot( c, maxiter):
    z = c
    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return 0

def main():
  
    (xmin, xmax) = (-2.,-0.5)
    (ymin, ymax) = (0, 1.5)
    (width, height) = (20, 20)
    maxiter = 15
    #
    # do the clean-up before we start
    #
    hsh = pysp.toPyspMonitor( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
    if hsh[ 'result'] != "done":
        print( "error from ['delete', 'setWsViewport DINA5S', 'cls']")
        return 
    
    hsh = { 'putData': 
             { 'name': "Mandelbrot",
               'type': 'image', 
               'xMin': xmin, 'xMax': xmax, 'width': width, 
               'yMin': ymin, 'yMax': ymax, 'height': height}}
    hsh = pysp.toPyspMonitor( hsh)
    if hsh[ 'result'] != "done":
        print( "error from putData")
        return 

    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    for i in range(width):
        for j in range(height):
            res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
            hsh = { 'putData': 
                     { 'name': "Mandelbrot",
                       'setPixelWorld': ( r1[i], r2[j], res)}}
            hsh = pysp.toPyspMonitor( hsh)
            if hsh[ 'result'] != "done":
                print( "error from setPixel")
                return 
    return 

if __name__ == "__main__":
    main()

'''
