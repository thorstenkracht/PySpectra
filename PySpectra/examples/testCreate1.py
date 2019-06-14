#!/usr/bin/env python
import PySpectra as _pysp
import numpy as _np

def testCreate1( self):
    '''
    create 1 scan with several texts
    '''
    _pysp.cls()
    delete()
    setTitle( "Ein Titel")
    setComment( "Sinus(), nach oben verschoben")
    t1 = Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, lineColor = 'blue', yLabel = 'sin')
    t1.addText( text = "a left/center aligned text", x = 0.05, y = 0.8, hAlign = 'left', vAlign = 'center')
    t1.addText( text = "a right/centeraligned text", x = 0.95, y = 0.8, hAlign = 'right', vAlign = 'center')
    t1.addText( text = "a center/top aligned text, red, fontSize: 10", x = 0.5, y = 0.5, hAlign = 'center', 
                vAlign = 'top', fontSize=10, color = 'red')
    t1.addText( text = "a center/center aligned text", x = 0.5, y = 0.5, hAlign = 'center', vAlign = 'center')
    t1.addText( text = "a center/bottom aligned text", x = 0.5, y = 0.5, hAlign = 'center', vAlign = 'bottom')
    t1.y = _np.sin( t1.x) + 1.001
    _pysp.display()


def testCreate2OverlayDoty():
    '''
    create 2 overlaid scans
    '''
    _pysp.cls()
    delete()
    setTitle( "2 Overlaid Scans")
    t1 = Scan( name = "t1", xMin = 0, xMax = 10, nPts = 101, lineColor = 'blue', 
               yLabel = 'sin', doty = True)
    t1.y = _np.sin( t1.x)
    t2 = Scan( "t2", yLabel = 'cos', xMin = 0, xMax = 10, nPts = 101, lineColor = 'green', doty = True)
    t2.y = _np.cos( t2.x)
    t2.overlay = "t1"
    _pysp.display()

def testCreate3():
    '''
    create 3 scans
    '''
    _pysp.cls()
    delete()
    setTitle( "Ein Titel")
    setComment( "Ein Kommentar")
    textScan = Scan( name = "textContainer", textOnly = True)
    textScan.addText( text = "some information", 
                      x = 0., y = 0.95, color = 'blue')
    textScan.addText( text = "and more infos", 
                      x = 0., y = 0.85, color = 'blue')
    t1 = Scan( name = "t1", lineColor = 'blue', yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    t2 = Scan( "t2", yLabel = 'cos', symbol = 'o', symbolColor = 'red', symbolSize = 5)
    t2.y = _np.cos( t2.x)
    t3 = Scan( "t3", yLabel = 'tan', symbol = '+', lineColor = 'cyan', symbolColor = 'green', symbolSize = 5)
    t3.y = _np.tan( t3.x)
    _pysp.display()

def testCreate5():
    '''
    create 5 scans, different colors, demonstrate overly feature
    '''
    _pysp.cls()
    delete()
    setTitle( "Ein Titel")
    setComment( "Ein Kommentar")
    t1 = Scan( name = "t1", lineColor = 'blue', yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    t2 = Scan( "t2", yLabel = 'cos', symbol = '+')
    t2.y = _np.cos( t2.x)
    t3 = Scan( name = "t3", lineColor = 'green', yLabel = 'tan')
    t3.y = _np.tan( t3.x)
    t4 = Scan( name = "t4", lineColor = 'NONE', yLabel = 'random', symbol = '+', symbolColor = 'CYAN')
    t4.y = _np.random.random_sample( (len( t4.y), ))
    t5 = Scan( name = "t5", lineColor = 'magenta', yLabel = 'x**2')
    t5.y = t5.x * t5.x
    overlay( 't5', 't3')
    _pysp.display()

def testCreate10():
    '''
    create 10 scans
    '''
    _pysp.cls()
    delete()
    setTitle( "Ein Titel")
    setComment( "Ein Kommentar")
    for i in range( 10): 
        t = Scan( name = "t%d" % i, lineColor = 'blue', yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))
    _pysp.display()

def testCreate22():
    '''
    create 2 scans
    '''
    _pysp.cls()
    delete()
    setTitle( "22 Scans")
    #setComment( "Ein Kommentar")
    for i in range( 22): 
        t = Scan( name = "t%d" % i, lineColor = 'blue', yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))
    _pysp.display()

def testCreate56():
    '''
    create 56 scans
    '''
    _pysp.cls()
    delete()
    setTitle( "56 Scans")
    for i in range( 56): 
        t = Scan( name = "t%d" % i, lineColor = 'blue', yLabel = 'rand')
        t.y = _np.random.random_sample( (len( t.x), ))
    _pysp.display()

def testCreateOverlaid( self):
    '''
    overlay 2 scans
    '''
    _pysp.cls()
    delete()
    setTitle( "2 Overlay Scans")
    g = Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2.*sigma**2))
    t1 = Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = _np.sin( t1.x)
    overlay( "sinus", "gauss")
    _pysp.display()

def testCreateOverlaidWithLog():
    '''
    create 2 Gauss, overlay the second to the first, log scale for first
    '''
    _pysp.cls()
    delete()
    setTitle( "2 Overlay Scans, with log scale")
    g1 = Scan( name = "gauss", xMin = -5., xMax = 5., yLog = True, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0, 
                    yMax = 1, nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g2.y-mu)**2/(2.*sigma**2))

    overlay( "gauss2", "gauss")
    _pysp.display()

def testCreateGauss():
    '''
    gauss scan
    '''
    _pysp.cls()
    delete()
    setTitle( "This is the position of the title")
    setComment( "Here would be the comment")
    g = Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*_np.sqrt(2.*_np.pi))*_np.exp( -(g.y-mu)**2/(2*sigma**2))
    _pysp.display()

    
