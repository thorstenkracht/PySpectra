#!/usr/bin/env python
import PySpectra as _pysp
import numpy as _np
import math as _math
import time as _time

def example1LogScanWithText():
    '''
    create 1 scan, y-log scale, one text
    '''
    _pysp.cls()
    _pysp.delete()
    t1 = _pysp.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, lineColor = 'blue', yLabel = 'signal', yLog = True)
    t1.addText( text = "a left/center aligned text, should be in the center", x = 0.05, y = 0.5, hAlign = 'left', vAlign = 'center')
    _pysp.display()

def example1ScanWithTexts():
    '''
    create 1 scan with several texts
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "Here could be the title")
    _pysp.setComment( "comment: Sinus(), shifted up by 1.1")
    t1 = _pysp.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, lineColor = 'blue', yLabel = 'sin')
    t1.addText( text = "a left/center aligned text", x = 0.05, y = 0.8, hAlign = 'left', vAlign = 'center')
    t1.addText( text = "a right/centeraligned text", x = 0.95, y = 0.8, hAlign = 'right', vAlign = 'center')
    t1.addText( text = "a center/top aligned text, red, fontSize: 10", x = 0.5, y = 0.5, hAlign = 'center', 
                vAlign = 'top', fontSize=10, color = 'red')
    t1.addText( text = "a center/center aligned text", x = 0.5, y = 0.5, hAlign = 'center', vAlign = 'center')
    t1.addText( text = "a center/bottom aligned text", x = 0.5, y = 0.5, hAlign = 'center', vAlign = 'bottom')
    t1.y = _np.sin( t1.x) + 1.001
    _pysp.display()

def example2OverlaidDoty():
    '''
    create 2 overlaid scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlaid scans, x-axis tick labels show date")
    t1 = _pysp.Scan( name = "t1", xMin = 0, xMax = 10, nPts = 101, lineColor = 'blue', 
               yLabel = 'sin', doty = True)
    t1.y = _np.sin( t1.x)
    t2 = _pysp.Scan( "t2", yLabel = 'cos', xMin = 0, xMax = 10, nPts = 101, lineColor = 'green', doty = True)
    t2.y = _np.cos( t2.x)
    t2.overlay = "t1"
    _pysp.display()

def example3WithTextContainer():
    '''
    create 3 scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "here could be a title")
    _pysp.setComment( "this is a comment")
    textScan = _pysp.Scan( name = "textContainer", textOnly = True)
    textScan.addText( text = "some information", 
                      x = 0., y = 0.95, color = 'blue')
    textScan.addText( text = "and more infos", 
                      x = 0., y = 0.85, color = 'blue')
    t1 = _pysp.Scan( "t1", lineColor = 'blue', yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    t2 = _pysp.Scan( "t2", yLabel = 'cos', symbol = 'o', symbolColor = 'red', symbolSize = 5)
    t2.y = _np.cos( t2.x)
    t3 = _pysp.Scan( "t3", yLabel = 'tan', symbol = '+', lineColor = 'cyan', symbolColor = 'green', symbolSize = 5)
    t3.y = _np.tan( t3.x)
    _pysp.display()

def example5Scans():
    '''
    create 5 scans, different colors, demonstrate overlay feature
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "5 Scans, t5 is overlaid to t3")
    t1 = _pysp.Scan( name = "t1", lineColor = 'blue', yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    t2 = _pysp.Scan( "t2", yLabel = 'cos', symbol = '+')
    t2.y = _np.cos( t2.x)
    t3 = _pysp.Scan( name = "t3", lineColor = 'green', yLabel = 'tan')
    t3.y = _np.tan( t3.x)
    t4 = _pysp.Scan( name = "t4", lineColor = 'NONE', yLabel = 'random', symbol = '+', symbolColor = 'CYAN')
    t4.y = _np.random.random_sample( (len( t4.y), ))
    t5 = _pysp.Scan( name = "t5", lineColor = 'magenta', yLabel = 'x**2')
    t5.y = t5.x * t5.x
    _pysp.overlay( 't5', 't3')
    _pysp.display()

def example22Scans():
    '''
    create 2 scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "22 Scans")
    for i in range( 22): 
        t = _pysp.Scan( name = "t%d" % i, lineColor = 'blue', yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
    _pysp.display()

def example56Scans():
    '''
    create 56 scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "56 Scans")
    for i in range( 56): 
        t = _pysp.Scan( name = "t%d_a" % i, lineColor = 'blue', nPts = 200, yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
    _pysp.display()

def example56x3Scans():
    '''
    create 56 scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "56 x 3 Scans")
    for i in range( 56): 
        t = _pysp.Scan( name = "t%d_a" % i, lineColor = 'blue', nPts = 200, yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
        t = _pysp.Scan( name = "t%d_b" % i, lineColor = 'red', nPts = 200, yLabel = 'rand', overlay = "t%d_a" % i)
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
        t = _pysp.Scan( name = "t%d_c" % i, lineColor = 'green', nPts = 200, yLabel = 'rand', overlay = "t%d_a" % i)
        t.y = _np.random.random_sample( (len( t.x), ))*1000.
    _pysp.display()

def exampleGaussAndSinusOverlaid():
    '''
    overlay 2 scans
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlaid Scans")
    g = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2.*sigma**2))
    t1 = _pysp.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    _pysp.overlay( "sinus", "gauss")
    _pysp.display()

def example2GaussOverlaidWithLog():
    '''
    create 2 Gauss, overlay the second to the first, log scale for first
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "2 Overlay Scans, with log scale")
    g1 = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., yLog = True, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = _pysp.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0, 
                    yMax = 1, nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))

    _pysp.overlay( "gauss2", "gauss")
    _pysp.display()

def exampleGauss():
    '''
    gauss scan
    '''
    _pysp.cls()
    _pysp.delete()
    _pysp.setTitle( "This is the position of the title")
    _pysp.setComment( "Here would be the comment")
    g = _pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2*sigma**2))
    _pysp.display()

def exampleScanning():
    '''    
    '''
    _pysp.cls()
    _pysp.delete()
    
    _pysp.setTitle( "sinus, shifted by +1.1")
    sinus = _pysp.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red')
    for i in range( sinus.nPts): 
        sinus.setX( i, i/10. + 0.01)
        sinus.setY( i, _math.sin( i/10.) + 1.1)
        _pysp.display( ['sinus'])
        _time.sleep( 0.01)

    #_pysp.launchGui()
    
