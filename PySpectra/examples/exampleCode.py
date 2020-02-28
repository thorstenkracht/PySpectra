#!/usr/bin/env python
'''
the functions in this module are automatically inserted into the 'Examples' menu of 
  /home/kracht/Misc/pySpectra/PySpectra/pySpectraGuiClass.py 
and they are unittest-executed by
  /home/kracht/Misc/pySpectra/test/examples/testExamples.py

From the command line: 
  python -c 'import PySpectra; PySpectra.example22Scans()'

'''

import PySpectra as _pysp
import numpy as _np
import math as _math
import os as _os
import time as _time
import pyqtgraph as _pg


def exampleDataVia_toPysp(): 
    '''
    replace toPysp() with toPyspMonitor() to connect to pyspMonitor.py
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

    hsh = _pysp.toPysp( hsh)
    print( "exampleDataVia_toPysp: putData returns %s" % repr( hsh) )

    #
    # retrieve the data 
    #
    hsh = _pysp.toPysp( { 'getData': True})
    #
    # ... and compare.
    #
    for i in range( MAX):
        if pos[i] != hsh[ 'getData']['EH_C01']['x'][i]:
            print( "error: pos[i] != x[i]")
        if d1[i] != hsh[ 'getData'][ 'EH_C01'][ 'y'][i]:
            print( "error: d1[i] != y[i]")
        
    print( "exampleDataVia_toPysp: getData returns x(EH_C01) %s " % hsh[ 'getData']['EH_C01']['x'])
    print( "exampleDataVia_toPysp: getData returns y(EH_C01) %s" % hsh[ 'getData']['EH_C01']['y'])
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

def exampleImageMBVia_toPysp(): 
    '''
    this examples simulates the toPyspMonitor() interface

    replace toPysp() by toPyspMonitor() to connect to pyspMonitor.py 
    '''
    _pysp.setWsViewport( 'DINA5S')

    _pysp.cls()
    _pysp.delete()

    (xmin, xmax) = (-2.,-0.5)
    (ymin, ymax) = (0, 1.5)
    (width, height) = (10, 10)
    maxiter = 25

    #
    # do the clean-up before we start
    #
    hsh =  _pysp.toPysp( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
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

    hsh = _pysp.toPysp( hsh)
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
            #hsh = { 'putData': 
            #         { 'name': "Mandelbrot",
            #           'noDisplay': True, 
            #           'setPixelWorld': ( r1[i], r2[j], res)}}
            #hsh = { 'command': [ 'setPixelWorld Mandelbrot %g %g %g' % ( r1[i], r2[j], res)]}
            hsh = { 'command': [ 'setPixelImage Mandelbrot %d %d %g' % ( i, j, res)]}
            hsh = _pysp.toPysp( hsh)
            if hsh[ 'result'] != "done":
                print( "error from setPixel")
                return
        _pysp.cls()
        _pysp.display()

    return 

def exampleImageMBVia_toPysp_OneChunk(): 
    '''
    this examples simulates the toPyspMonitor() interface

    replace toPysp() by toPyspMonitor() to connect to pyspMonitor.py 
    '''
    _pysp.setWsViewport( 'DINA5S')

    _pysp.cls()
    _pysp.delete()

    (xmin, xmax) = (-2., 1.0)
    (ymin, ymax) = ( -1.5, 1.5)
    (width, height) = (500, 500)
    maxiter = 128

    #
    # do the clean-up before we start
    #
    hsh =  _pysp.toPysp( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
    if hsh[ 'result'] != "done":
        print( "error from ['delete', 'setWsViewport DINA5S', 'cls']")
        return 
    #
    # fill the image, pixel by pixel
    #
    r1 = _np.linspace(xmin, xmax, width)
    r2 = _np.linspace(ymin, ymax, height)
    data = _np.ndarray( (width, height), _np.int32)
    for i in range(width):
        for j in range(height):
            res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
            data[i][j] = int( res)

    _pysp.toPysp( { 'putData': 
                    { 'images': [{'name': "Mandelbrot", 'data': data,
                                  'xMin': xmin, 'xMax': xmax, 
                                  'yMin': ymin, 'yMax': ymax}]}})
    _pysp.cls()
    _pysp.display()

    return 


def example_LogPlotWithText():
    '''
    create 1 scan, y-log scale, one text
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setWsViewport( "DINA5")
    t1 = _pysp.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, 
                     lineColor = 'blue', xLabel='Position', 
                     yLabel = 'signal', yLog = True)
    t1.addText( text = "a left/center aligned text, should be in the center", 
                x = 0.05, y = 0.5, hAlign = 'left', vAlign = 'center')
    _pysp.display()

def example_LogXScale():
    _pysp.cls()
    _pysp.delete()
    _pysp.setWsViewport( "DINA5")
    _pysp.setTitle( "log x-scale")
    t1 = _pysp.Scan( name = "t1", xMin = 0.01, xMax = 100., nPts = 101, 
                    lineColor = 'blue', xLabel='Position', yLabel = 'signal', 
                     yLog = False, xLog = True)
    _pysp.display()


def example_PlotWithSeveralTexts():
    '''
    create 1 scan with several texts
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "Here could be the title")
    _pysp.setComment( "comment: Sinus(), shifted up by 1.1")
    _pysp.setWsViewport( "DINA5")
    t1 = _pysp.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, 
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
    _pysp.display()

def example_Overlay2():
    '''
    create 2 overlaid scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "Overlay 2 Scans")
    _pysp.setComment( "no comment")
    _pysp.setWsViewport( "DINA5")
    g = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                    lineColor = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2.*sigma**2))
    t1 = _pysp.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    _pysp.overlay( "sinus", "gauss")
    _pysp.display()

def example_OverlayDoty():
    '''
    create 2 overlaid scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay scans, x-axis tick labels show date")
    _pysp.setWsViewport( "DINA5")
    t1 = _pysp.Scan( name = "t1", xMin = 0, xMax = 10, nPts = 101, 
                     lineColor = 'blue', 
                     xLabel = 'Position', yLabel = 'sin', doty = True)
    t1.y = _np.sin( t1.x)
    t2 = _pysp.Scan( "t2", xLabel = 'Position', yLabel = 'cos', 
                     xMin = 0, xMax = 10, nPts = 101, 
                     lineColor = 'green', doty = True)
    t2.y = _np.cos( t2.x)
    t2.overlay = "t1"
    _pysp.display()

def example_PlotsWithTextContainer():
    '''
    create 3 scans and a text container
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "here could be a title")
    _pysp.setComment( "this is a comment")
    _pysp.setWsViewport( "DINA5")
    textScan = _pysp.Scan( name = "textContainer", textOnly = True)
    textScan.addText( text = "some information", 
                      x = 0., y = 0.95, color = 'blue')
    textScan.addText( text = "and more infos", 
                      x = 0., y = 0.85, color = 'blue')
    t1 = _pysp.Scan( "t1", lineColor = 'blue', xLabel = 'Position', 
                     yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    t2 = _pysp.Scan( "t2", xLabel = 'Position', yLabel = 'cos', 
                     symbol = 'o', symbolColor = 'red', symbolSize = 5)
    t2.y = _np.cos( t2.x)
    t3 = _pysp.Scan( "t3", xLabel = 'Position', yLabel = 'tan', 
                     symbol = '+', lineColor = 'cyan', 
                     symbolColor = 'green', symbolSize = 5)
    t3.y = _np.tan( t3.x)
    _pysp.display()

def example_Create5Plots():
    '''
    create 5 scans, different colors, demonstrate overlay feature
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "5 Scans, t5 is overlaid to t3")
    _pysp.setWsViewport( "DINA5")
    t1 = _pysp.Scan( name = "t1", lineColor = 'blue', yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    t2 = _pysp.Scan( "t2", xLabel = 'Position', yLabel = 'cos', symbol = '+')
    t2.y = _np.cos( t2.x)
    t3 = _pysp.Scan( name = "t3", lineColor = 'green', 
                     xLabel = 'Position', yLabel = 'tan')
    t3.y = _np.tan( t3.x)
    t4 = _pysp.Scan( name = "t4", lineColor = 'NONE', 
                     xLabel = 'Position', yLabel = 'random', 
                     symbol = '+', symbolColor = 'CYAN')
    t4.y = _np.random.random_sample( (len( t4.y), ))
    t5 = _pysp.Scan( name = "t5", lineColor = 'magenta', 
                     xLabel = 'Position', yLabel = 'x**2')
    t5.y = t5.x * t5.x
    _pysp.overlay( 't5', 't3')
    _pysp.display()

def example_Create22Plots():
    '''
    create 22 plots
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "22 Scans")
    _pysp.setComment( "and a comment")
    _pysp.setWsViewport( "DINA4")
    for i in range( 22): 
        t = _pysp.Scan( name = "t%d" % i, lineColor = 'blue',
                        xLabel = 'Position', yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
    _pysp.display()

def example_Create56x3Plots():
    '''
    create 56x3 plots
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "56 x 3 Scans")
    _pysp.setComment( "Display many Scans")
    _pysp.setWsViewport( "DINA4")
    for i in range( 56): 
        t = _pysp.Scan( name = "t%d_a" % i, lineColor = 'blue', nPts = 200, 
                        yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
        t = _pysp.Scan( name = "t%d_b" % i, lineColor = 'red', nPts = 200, 
                        yLabel = 'rand', overlay = "t%d_a" % i)
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
        t = _pysp.Scan( name = "t%d_c" % i, lineColor = 'green', nPts = 200, 
                        yLabel = 'rand', overlay = "t%d_a" % i)
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
    _pysp.display()
    return 

def example_CreatePDF():
    '''
    create a pdf file
    '''
    printer = _os.getenv( "PRINTER")
    if printer is None: 
        print( "examplecreatePDF: environment variable PRINTER not defined, returning")
        return 

    _pysp.cls()
    _pysp.delete()

    _pysp.setTitle( "Create PDF file and send it to the printer")
    _pysp.setWsViewport( "DINA5")
    scan = _pysp.Scan( name = 'PDF Output', nPts = 100, xMin = -1., xMax = 1.,
                           xLabel = 'Position', yLabel = "Counts")
    
    scan.y = _np.sin( scan.x)

    _pysp.setWsViewport( "DINA4")
    _pysp.display()

    _pysp.createPDF( flagPrint = True)
    return 

def example_GaussAndSinusOverlay():
    '''
    overlay 2 scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay Scans")
    _pysp.setWsViewport( "DINA5")
    g = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                    lineColor = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2.*sigma**2))
    t1 = _pysp.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    _pysp.overlay( "sinus", "gauss")
    _pysp.display()

def example_Gauss():
    '''
    gauss plot
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "A simple Gauss curve")
    _pysp.setComment( "Can be used with SSA, calculating derivative and so")
    _pysp.setWsViewport( "DINA5")
    g = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2*sigma**2))
    _pysp.display()
    return 

def example_GaussManyOverlay():
    '''
    gauss plot
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setWsViewport( "DINA5")
    g = _pysp.Scan( name = "gauss", xMin = -10., xMax = 10., nPts = 101)
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
        gqe = _pysp.Scan( name = "gauss%d" % i, xMin = -5., xMax = 5., 
                          nPts = 101)
        gqe.x = g.x + 0.02 * i
        gqe.y = g.y + 0.02 * i
        _pysp.overlay( "gauss%d" % i, "gauss")
        gqe.useTargetWindow = True
        
    _pysp.display()
    return 

def example_GaussNoisy():
    '''
    gauss plot
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "a noisy Gauss")
    _pysp.setComment( "See how SSA behaves with noisy data")
    _pysp.setWsViewport( "DINA5")
    g = _pysp.Scan( name = "gauss_noisy", xMin = -5., xMax = 5., nPts = 101)
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2*sigma**2)) + \
          _np.random.random_sample( (len( g.x), ))*0.05
    _pysp.display()
    return 

def example_Gauss2():
    ''' 
    2 gauss plot
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "Two Gauss curves")
    _pysp.setComment( "To demonstrate how SSA limits can be defined with VLines")
    _pysp.setWsViewport( "DINA5")
    g = _pysp.Scan( name = "gauss", xMin = -10., xMax = 10., nPts = 101)
    mu1 = 0.
    sigma1 = 1.
    mu2 = 6.5
    sigma2 = 1.2
    g.y = 1./(sigma1*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu1)**2/(2*sigma1**2)) + \
          2./(sigma2*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu2)**2/(2*sigma2**2))
    _pysp.display()
    return 

def example_Scanning():
    '''    
    '''
    _pysp.cls()
    _pysp.delete()

    _pysp.setTitle( "scanning, x-axis is fixed")
    _pysp.setWsViewport( "DINA5")
    sinus = _pysp.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, 
                        autoscaleX = False, lineColor = 'red')


    for i in range( sinus.nPts): 
        sinus.setX( i, i/10. + 0.01)
        sinus.setY( i, _math.sin( i/10.))
        _pysp.display( ['sinus'])
        _time.sleep( 0.01)
    return 

def example_ScanningMesh():
    '''    
    '''
    _pysp.cls()
    _pysp.delete()

    (xmin, xmax) = (-2., 1)
    (ymin, ymax) = (-1.5, 1.5)
    (width, height) = (20, 20)
    maxiter = 20
    
    r1 = _np.linspace(xmin, xmax, width)
    r2 = _np.linspace(ymin, ymax, height)
    n3 = _np.zeros((width,height))
            
    m = _pysp.Image( name = "MandelbrotSet", colorMap = 'Greys', 
                     estimatedMax = 20, 
                     xMin = xmin, xMax = xmax, width = width, 
                     yMin = ymin, yMax = ymax, height = height)
    
    _pysp.setTitle( "Simulate a mesh scan")
    _pysp.setWsViewport( "DINA5")
    sinus = _pysp.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = width*height, 
                        autoscaleX = False, lineColor = 'red')
    cosinus = _pysp.Scan( name = 'cosinus', xMin = 0., xMax = 6.0, nPts = width*height, 
                        autoscaleX = False, lineColor = 'red')

    _pysp.display()

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
        _pysp.display()
    _pysp.cls()
    _pysp.display()
    return 

def example_ScanningAutoscaleX():
    '''    
    '''
    _pysp.cls()
    _pysp.delete()
    
    _pysp.setTitle( "scanning, x-axis is re-scaled")
    _pysp.setWsViewport( "DINA5")
    sinus = _pysp.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, 
                        autoscaleX = True, lineColor = 'red')
    for i in range( sinus.nPts): 
        sinus.setX( i, i/10. + 0.01)
        sinus.setY( i, _math.sin( i/10.))
        _pysp.display( ['sinus'])
        _time.sleep( 0.01)
    return 

def example_ScanningReverse():
    '''    
    '''
    _pysp.cls()
    _pysp.delete()
    
    _pysp.setTitle( "scanning in reverse direction, x-axis is fixed")
    _pysp.setWsViewport( "DINA5")
    sinus = _pysp.Scan( name = 'sinus', 
                        xMin = 0., xMax = 6.0, nPts = 101, 
                        autoscaleX = False, 
                        lineColor = 'red')
    sinus.xMax = 10.
    for i in range( sinus.nPts): 
        x = 10. - i/10.
        sinus.setX( i, x)
        sinus.setY( i, _math.sin( i/10.))
        _pysp.display( ['sinus'])
        _time.sleep( 0.05)
    return 

def example_ScanningReverseAutoscaleX():
    '''    
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "scanning in reverse direction, the x-axis is re-scaled")
    _pysp.setWsViewport( "DINA5")
    sinus = _pysp.Scan( name = 'sinus', 
                            xMin = 0., xMax = 6.0, nPts = 101, 
                            autoscaleX = True, 
                            lineColor = 'red')
    for i in range( sinus.nPts): 
        x = 10. - i/10.
        sinus.x[i] = x
        sinus.y[i] = _math.sin( i/10.)
        sinus.currentIndex = i
        _pysp.display( ['sinus'])
        _time.sleep( 0.02)

def example_Lissajous(): 
    '''
    plots and updates a Lissajous figure
    '''
    _pysp.setWsViewport( "DINA5S")
    
    _pysp.cls()
    _pysp.delete()
    scan = _pysp.Scan( name = 'Lissajous', nPts = 1000, xMin = -1., xMax = 1.)
    
    x  = _np.linspace( 0., 6.5, 1000)
    y  = _np.linspace( 0., 6.5, 1000)
    
    scan.x = _np.cos( x)
    scan.y = _np.sin( y)
    
    _pysp.display()
    
    for i in range( 500):
        x = x + 0.005
        scan.plotDataItem.setData(_np.cos( x), _np.sin( y))
        _pysp.processEvents()

def example_Overlay2BothLog(): 
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay Scans, both with log scale")
    _pysp.setComment( "both axes have different ranges")
    _pysp.setWsViewport( "DINA5")
    g1 = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., 
                     yLog = True, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = _pysp.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0.001, 
                     yLog = True, yMax = 1., nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))*100.

    _pysp.overlay( "gauss2", "gauss")

    _pysp.display()

def example_Overlay2FirstLog(): 
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay Scans, first (red) has log scale")
    _pysp.setComment( "Sadly, there are no major tick mark strings at the right axis")
    _pysp.setWsViewport( "DINA5")
    g1 = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., 
                     yLog = True, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = _pysp.Scan( name = "gauss2", xMin = -5., xMax = 5., yLog = False, 
                    yMax = 1., nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))

    _pysp.overlay( "gauss2", "gauss")

    _pysp.display()

def example_Overlay2SecondLog(): 
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay Scans, 2nd (green) has log scale")
    _pysp.setComment( "Sadly, there are no major tick mark strings at the right axis")
    _pysp.setWsViewport( "DINA5")
    g1 = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., 
                     yLog = False, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = _pysp.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0.001, 
                     yLog = True, yMax = 1., nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))

    _pysp.overlay( "gauss2", "gauss")

    _pysp.display()

def example_ImageMB(): 

    _pysp.setWsViewport( 'DINA5S')

    _pysp.cls()
    _pysp.delete()

    (xmin, xmax) = (-2., 0.5)
    (ymin, ymax) = (-1.25, 1.25)
    (width, height) = (500, 500)
    maxiter = 512
    
    m = _pysp.Image( name = "MandelbrotSet",
                     flagAxes = True, 
                     maxIter = maxiter, 
                     xMin = xmin, xMax = xmax, width = width, 
                     yMin = ymin, yMax = ymax, height = height)
    m.flagZoomSlow = False
    m.zoom()
    _pysp.cls()
    _pysp.display()
    return 
"""
def example_ImageMBSlow(): 

    _pysp.setWsViewport( 'DINA5S')

    _pysp.cls()
    _pysp.delete()

    (xmin, xmax) = (-2., 0.5)
    (ymin, ymax) = (-1.25, 1.25)
    (width, height) = (500, 500)
    maxiter = 256
    
    m = _pysp.Image( name = "MandelbrotSet",
                    xMin = xmin, xMax = xmax, width = width, 
                    yMin = ymin, yMax = ymax, height = height)

    m.flagZoomSlow = True
    m.zoom()
    _pysp.cls()
    _pysp.display()
    return 
"""
def example_ImageRandom(): 

    import random
    
    _pysp.setWsViewport( 'DINA5S')

    _pysp.cls()
    _pysp.delete()

    (xmin, xmax) = (-2., 1)
    (ymin, ymax) = (-1.5, 1.5)
    (width, height) = (500, 500)
    
    r1 = _np.linspace(xmin, xmax, width)
    r2 = _np.linspace(ymin, ymax, height)
    n3 = _np.empty((width,height))
    for i in range(width):
        for j in range(height):
            n3[i,j] = i + random.random()*j + 100.
            
    m = _pysp.Image( name = "ImageRandom", data = n3, 
                    xMin = xmin, xMax = xmax, width = width, 
                    yMin = ymin, yMax = ymax, height = height, 
                    xLabel = "x-Axis", yLabel = "y-Axis")

    _pysp.cls()
    _pysp.display()
    return 

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
