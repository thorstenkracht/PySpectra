#!/usr/bin/env python
'''
the functions in this module are automatically inserted into the 'Examples'
menu of 
  /home/kracht/Misc/pySpectra/PySpectra/pySpectraGuiClass.py 
and they are unittest-executed by
  /home/kracht/Misc/pySpectra/test/examples/testExamples.py

From the command line: 
  python -c 'import PySpectra; PySpectra.example22Scans()'

'''

import PySpectra as _pysp
import numpy as _np
import math as _math
import time as _time

def exampleLogPlotWithText():
    '''
    create 1 scan, y-log scale, one text
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setWsViewport( "DINA6")
    t1 = _pysp.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, 
                     lineColor = 'blue', xLabel='Position', yLabel = 'signal', yLog = True)
    t1.addText( text = "a left/center aligned text, should be in the center", x = 0.05, y = 0.5, hAlign = 'left', vAlign = 'center')
    _pysp.display()

def examplePlotWithSeveralTexts():
    '''
    create 1 scan with several texts
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "Here could be the title")
    _pysp.setComment( "comment: Sinus(), shifted up by 1.1")
    _pysp.setWsViewport( "DINA6")
    t1 = _pysp.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, lineColor = 'blue', xLabel = 'Position', yLabel = 'sin')
    t1.addText( text = "a left/center aligned text", x = 0.05, y = 0.8, hAlign = 'left', vAlign = 'center')
    t1.addText( text = "a right/centeraligned text", x = 0.95, y = 0.8, hAlign = 'right', vAlign = 'center')
    t1.addText( text = "a center/top aligned text, red, fontSize: 10", x = 0.5, y = 0.5, hAlign = 'center', 
                vAlign = 'top', fontSize=10, color = 'red')
    t1.addText( text = "a center/center aligned text", x = 0.5, y = 0.5, hAlign = 'center', vAlign = 'center')
    t1.addText( text = "a center/bottom aligned text", x = 0.5, y = 0.5, hAlign = 'center', vAlign = 'bottom')
    t1.y = _np.sin( t1.x) + 1.001
    _pysp.display()

def exampleOverlay2():
    '''
    create 2 overlaid scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "Overlay 2 Scans")
    _pysp.setComment( "no comment")
    _pysp.setWsViewport( "DINA6")
    g = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2.*sigma**2))
    t1 = _pysp.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    _pysp.overlay( "sinus", "gauss")
    _pysp.display()

def exampleOverlayDoty():
    '''
    create 2 overlaid scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay scans, x-axis tick labels show date")
    _pysp.setWsViewport( "DINA6")
    t1 = _pysp.Scan( name = "t1", xMin = 0, xMax = 10, nPts = 101, lineColor = 'blue', 
                     xLabel = 'Position', yLabel = 'sin', doty = True)
    t1.y = _np.sin( t1.x)
    t2 = _pysp.Scan( "t2", xLabel = 'Position', yLabel = 'cos', 
                     xMin = 0, xMax = 10, nPts = 101, lineColor = 'green', doty = True)
    t2.y = _np.cos( t2.x)
    t2.overlay = "t1"
    _pysp.display()

def examplePlotsWithTextContainer():
    '''
    create 3 scans and a text container
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "here could be a title")
    _pysp.setComment( "this is a comment")
    _pysp.setWsViewport( "DINA6")
    textScan = _pysp.Scan( name = "textContainer", textOnly = True)
    textScan.addText( text = "some information", 
                      x = 0., y = 0.95, color = 'blue')
    textScan.addText( text = "and more infos", 
                      x = 0., y = 0.85, color = 'blue')
    t1 = _pysp.Scan( "t1", lineColor = 'blue', xLabel = 'Position', yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    t2 = _pysp.Scan( "t2", xLabel = 'Position', yLabel = 'cos', symbol = 'o', symbolColor = 'red', symbolSize = 5)
    t2.y = _np.cos( t2.x)
    t3 = _pysp.Scan( "t3", xLabel = 'Position', yLabel = 'tan', symbol = '+', lineColor = 'cyan', symbolColor = 'green', symbolSize = 5)
    t3.y = _np.tan( t3.x)
    _pysp.display()

def exampleCreate5Plots():
    '''
    create 5 scans, different colors, demonstrate overlay feature
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "5 Scans, t5 is overlaid to t3")
    _pysp.setWsViewport( "DINA6")
    t1 = _pysp.Scan( name = "t1", lineColor = 'blue', yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    t2 = _pysp.Scan( "t2", xLabel = 'Position', yLabel = 'cos', symbol = '+')
    t2.y = _np.cos( t2.x)
    t3 = _pysp.Scan( name = "t3", lineColor = 'green', xLabel = 'Position', yLabel = 'tan')
    t3.y = _np.tan( t3.x)
    t4 = _pysp.Scan( name = "t4", lineColor = 'NONE', xLabel = 'Position', yLabel = 'random', 
                     symbol = '+', symbolColor = 'CYAN')
    t4.y = _np.random.random_sample( (len( t4.y), ))
    t5 = _pysp.Scan( name = "t5", lineColor = 'magenta', xLabel = 'Position', yLabel = 'x**2')
    t5.y = t5.x * t5.x
    _pysp.overlay( 't5', 't3')
    _pysp.display()

def exampleCreate22Plots():
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


def example58ScansLogOverlay():
    '''
    create 58 scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "58 Scans, log axis, overlay")
    _pysp.setComment( "and a comment")
    _pysp.setWsViewport( "DINA4")
    textScan = _pysp.Scan( name = "textContainer", textOnly = True)
    textScan.addText( text = "some information", 
                      x = 0., y = 0.95, color = 'blue')
    for i in range( 58): 
        t = _pysp.Scan( name = "t%d" % i, lineColor = 'blue', xLabel = 'Position', yLabel = 'rand', yLog=True)
        t.y = _np.random.random_sample( (len( t.x), ))*150000. + 1
        t1 = _pysp.Scan( name = "tt%d" % i, lineColor = 'red', xLabel = 'Position', yLabel = 'rand', yLog=True)
        t1.y = _np.random.random_sample( (len( t.x), ))*150000. + 1
        t.setLimits()
        t1.setLimits()
        _pysp.overlay( "tt%d" % i, "t%d" % i)
    _pysp.display()

def exampleCreate56Plots():
    '''
    create 56 scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "56 Scans")
    _pysp.setComment( "and a comment")
    _pysp.setWsViewport( "DINA4")
    for i in range( 56): 
        t = _pysp.Scan( name = "t%d_a" % i, lineColor = 'blue', nPts = 200, xLabel = 'Position', yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
    _pysp.display()

def exampleCreate56x3Plots():
    '''
    create 56x3 plots
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "56 x 3 Scans")
    _pysp.setWsViewport( "DINA4")
    for i in range( 56): 
        t = _pysp.Scan( name = "t%d_a" % i, lineColor = 'blue', nPts = 200, yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
        t = _pysp.Scan( name = "t%d_b" % i, lineColor = 'red', nPts = 200, yLabel = 'rand', overlay = "t%d_a" % i)
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
        t = _pysp.Scan( name = "t%d_c" % i, lineColor = 'green', nPts = 200, yLabel = 'rand', overlay = "t%d_a" % i)
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
    _pysp.display()
    return 

def exampleCreatePDF():
    '''
    create a pdf file
    '''
    printer = _os.getenv( "PRINTER")
    if printer is None: 
        print "examplecreatePDF: environment variable PRINTER not defined, returning"
        return 

    _pysp.cls()
    _pysp.delete()

    _pysp.setTitle( "Create PDF file and send it to the printer")
    _pysp.setWsViewport( "DINA6")
    scan = _pysp.Scan( name = 'PDF Output', nPts = 100, xMin = -1., xMax = 1.,
                           xLabel = 'Position', yLabel = "Counts")
    
    scan.y = _np.sin( scan.x)

    _pysp.setWsViewport( "DINA4")
    _pysp.display()

    _pysp.createPDF( flagPrint = True)
    return 

def exampleGaussAndSinusOverlay():
    '''
    overlay 2 scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay Scans")
    _pysp.setWsViewport( "DINA6")
    g = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2.*sigma**2))
    t1 = _pysp.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    _pysp.overlay( "sinus", "gauss")
    _pysp.display()

def exampleGauss():
    '''
    gauss plot
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "This is the position of the title")
    _pysp.setComment( "Here would be the comment")
    _pysp.setWsViewport( "DINA6")
    g = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2*sigma**2))
    _pysp.display()
    return 

def exampleScanning():
    '''    
    '''
    _pysp.cls()
    _pysp.delete()
    
    _pysp.setTitle( "scanning")
    _pysp.setWsViewport( "DINA6")
    sinus = _pysp.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, autoscaleX = False, lineColor = 'red')
    for i in range( sinus.nPts): 
        sinus.setX( i, i/10. + 0.01)
        sinus.setY( i, _math.sin( i/10.))
        _pysp.display( ['sinus'])
        _time.sleep( 0.01)
    return 

def exampleScanningAutoscaleX():
    '''    
    '''
    _pysp.cls()
    _pysp.delete()
    
    _pysp.setTitle( "scanning, x-axis is re-scaled")
    _pysp.setWsViewport( "DINA6")
    sinus = _pysp.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, autoscaleX = True, lineColor = 'red')
    for i in range( sinus.nPts): 
        sinus.setX( i, i/10. + 0.01)
        sinus.setY( i, _math.sin( i/10.))
        _pysp.display( ['sinus'])
        _time.sleep( 0.01)
    return 

def exampleScanningReverse():
    '''    
    '''
    _pysp.cls()
    _pysp.delete()
    
    _pysp.setTitle( "scanning in reverse direction, no re-scale of the x-axis")
    _pysp.setWsViewport( "DINA6")
    sinus = _pysp.Scan( name = 'sinus', 
                        xMin = 0., xMax = 6.0, nPts = 101, 
                        lineColor = 'red')
    sinus.xMax = 10.
    for i in range( sinus.nPts): 
        x = 10. - i/10.
        sinus.setX( i, x)
        sinus.setY( i, _math.sin( i/10.))
        _pysp.display( ['sinus'])
        _time.sleep( 0.05)
    return 

def exampleScanningReverseAutoscaleX():
    '''    
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "scanning in reverse direction, the x-axis is re-scaled")
    _pysp.setWsViewport( "DINA6")
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

def exampleLissajous(): 
    '''
    plots and updates a Lissajous figure
    '''
    _pysp.setWsViewport( "DINA6S")
    
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

def exampleOverlay2BothLog(): 
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay Scans, both with log scale")
    _pysp.setComment( "both axes have different ranges")
    _pysp.setWsViewport( "DINA6")
    g1 = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., yLog = True, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = _pysp.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0.001, yLog = True, 
                    yMax = 1., nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))*100.

    _pysp.overlay( "gauss2", "gauss")

    _pysp.display()

def exampleOverlay2FirstLog(): 
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay Scans, first (red) has log scale")
    _pysp.setComment( "Sadly, there are no major tick mark strings at the right axis")
    _pysp.setWsViewport( "DINA6")
    g1 = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., yLog = True, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = _pysp.Scan( name = "gauss2", xMin = -5., yLog = False, 
                    yMax = 1., nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))

    _pysp.overlay( "gauss2", "gauss")

    _pysp.display()

def exampleOverlay2SecondLog(): 
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay Scans, 2nd (green) has log scale")
    _pysp.setComment( "Sadly, there are no major tick mark strings at the right axis")
    _pysp.setWsViewport( "DINA6")
    g1 = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., yLog = False, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = _pysp.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0.001, yLog = True, 
                    yMax = 1., nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))

    _pysp.overlay( "gauss2", "gauss")

    _pysp.display()

def exampleSimpleLog(): 
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "A simple plot")
    _pysp.setComment( "here would be a comment")
    _pysp.setWsViewport( "DINA6")
    g = _pysp.Scan( name = "linear", 
                   xMin = 0.01, xMax = 5., nPts = 101, 
                   xLabel = "Position", yLabel = 'Signal', 
                   yLog = True, 
                   lineColor = 'red')
    g.y *= 10.
    _pysp.display()

    return 

def exampleSimplePlot(): 
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "A simple plot")
    _pysp.setComment( "here would be a comment")
    _pysp.setWsViewport( "DINA6")
    g = _pysp.Scan( name = "linear", 
                   xMin = 0.01, xMax = 5., nPts = 101, 
                   xLabel = "Position", yLabel = 'Signal', 
                   lineColor = 'red')
    _pysp.display()

    return 

