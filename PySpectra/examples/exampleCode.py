#!/usr/bin/env python
'''
the functions in this module are automatically inserted into the 'Examples' menu of 
  /home/kracht/Misc/pySpectra/PySpectra/pySpectraGuiClass.py 
and they are unittest-executed by
  /home/kracht/Misc/pySpectra/test/examples/testExamples.py

From the command line: 
  python -c 'import PySpectra; PySpectra.example22Scans()'

'''

import numpy as np
import os, time, math
import PySpectra 
import PySpectra.utils as utils


def exampleDataVia_toPyspLocal(): 
    '''
    replace toPyspLocal() with toPyspMonitor() to connect to pyspMonitor.py
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

    hsh = PySpectra.toPyspLocal( hsh)
    print( "exampleDataVia_toPyspLocal: putData returns %s" % repr( hsh) )

    #
    # retrieve the data 
    #
    hsh = PySpectra.toPyspLocal( { 'getData': True})
    #
    # ... and compare.
    #
    for i in range( MAX):
        if pos[i] != hsh[ 'getData']['EH_C01']['x'][i]:
            print( "error: pos[i] != x[i]")
        if d1[i] != hsh[ 'getData'][ 'EH_C01'][ 'y'][i]:
            print( "error: d1[i] != y[i]")
        
    print( "exampleDataVia_toPyspLocal: getData returns x(EH_C01) %s " % hsh[ 'getData']['EH_C01']['x'])
    print( "exampleDataVia_toPyspLocal: getData returns y(EH_C01) %s" % hsh[ 'getData']['EH_C01']['y'])
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

def exampleImageMBVia_toPyspLocal(): 
    '''
    this examples simulates the toPyspMonitor() interface

    replace toPyspLocal() by toPyspMonitor() to connect to pyspMonitor.py 
    '''
    PySpectra.setWsViewport( 'DINA5S')

    PySpectra.cls()
    PySpectra.delete()

    (xmin, xmax) = (-2.,-0.5)
    (ymin, ymax) = (0, 1.5)
    (width, height) = (10, 10)
    maxiter = 25

    #
    # do the clean-up before we start
    #
    hsh =  PySpectra.toPyspLocal( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
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

    hsh = PySpectra.toPyspLocal( hsh)
    if hsh[ 'result'] != "done":
        print( "error from putData")
        return 
    #
    # fill the image, pixel by pixel
    #
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    for i in range(width):
        for j in range(height):
            res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
            hsh = { 'command': [ 'setPixelImage Mandelbrot %d %d %g' % ( i, j, res)]}
            hsh = PySpectra.toPyspLocal( hsh)
            if hsh[ 'result'] != "done":
                print( "error from setPixel")
                return
        PySpectra.cls()
        PySpectra.display()

    return 

def exampleImageMBVia_toPyspLocal_OneChunk(): 
    '''
    this examples simulates the toPyspMonitor() interface

    replace toPyspLocal() by toPyspMonitor() to connect to pyspMonitor.py 
    '''
    print( "toPyspLocal_OneChunk") 
    PySpectra.setWsViewport( 'DINA5S')

    PySpectra.cls()
    PySpectra.delete()

    (xmin, xmax) = (-2., 1.0)
    (ymin, ymax) = ( -1.5, 1.5)
    (width, height) = (500, 500)
    maxiter = 128

    #
    # do the clean-up before we start
    #
    hsh =  PySpectra.toPyspLocal( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
    if hsh[ 'result'] != "done":
        print( "error from ['delete', 'setWsViewport DINA5S', 'cls']")
        return 
    #
    # fill the image, pixel by pixel
    #
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    #data = np.ndarray( (width, height), np.int32)
    data = np.ndarray( (width, height), np.float64)
    for i in range(width):
        for j in range(height):
            res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
            data[i][j] = int( res)

    PySpectra.toPyspLocal( { 'putData': 
                    { 'images': [{'name': "Mandelbrot", 'data': data,
                                  'xMin': xmin, 'xMax': xmax, 
                                  'yMin': ymin, 'yMax': ymax}]}})
    PySpectra.cls()
    PySpectra.display()
    print( "toPyspLocal_OneChunk DONE") 

    return 


def example_LogPlotWithText():
    '''
    create 1 scan, y-log scale, one text
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setWsViewport( "DINA5")
    t1 = PySpectra.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, 
                     lineColor = 'blue', xLabel='Position', 
                     yLabel = 'signal', yLog = True)
    t1.addText( text = "a left/center aligned text, should be in the center", 
                x = 0.05, y = 0.5, hAlign = 'left', vAlign = 'center')
    PySpectra.display()

def example_LogXScale():
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setWsViewport( "DINA5")
    PySpectra.setTitle( "log x-scale")
    t1 = PySpectra.Scan( name = "t1", xMin = 0.01, xMax = 100., nPts = 101, 
                    lineColor = 'blue', xLabel='Position', yLabel = 'signal', 
                     yLog = False, xLog = True)
    PySpectra.display()


def example_PlotWithSeveralTexts():
    '''
    create 1 scan with several texts
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "Here could be the title")
    PySpectra.setComment( "comment: Sinus(), shifted up by 1.1")
    PySpectra.setWsViewport( "DINA5")
    t1 = PySpectra.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, 
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
    t1.y = np.sin( t1.x) + 1.001
    PySpectra.display()

def example_Overlay2():
    '''
    create 2 overlaid scans
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "Overlay 2 Scans")
    PySpectra.setComment( "no comment")
    PySpectra.setWsViewport( "DINA5")
    g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)
    t1 = PySpectra.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = np.sin( t1.x)
    PySpectra.overlay( "sinus", "gauss")
    PySpectra.display()

def example_OverlayDoty():
    '''
    create 2 overlaid scans
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "2 Overlay scans, x-axis tick labels show date")
    PySpectra.setWsViewport( "DINA5")
    t1 = PySpectra.Scan( name = "t1", xMin = 0, xMax = 10, nPts = 101, 
                     lineColor = 'blue', 
                     xLabel = 'Position', yLabel = 'sin', doty = True)
    t1.y = np.sin( t1.x)
    t2 = PySpectra.Scan( "t2", xLabel = 'Position', yLabel = 'cos', 
                     xMin = 0, xMax = 10, nPts = 101, 
                     lineColor = 'green', doty = True)
    t2.y = np.cos( t2.x)
    t2.overlay = "t1"
    PySpectra.display()

def example_PlotsWithTextContainer():
    '''
    create 3 scans and a text container
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "here could be a title")
    PySpectra.setComment( "this is a comment")
    PySpectra.setWsViewport( "DINA5")
    textScan = PySpectra.Scan( name = "textContainer", textOnly = True)
    textScan.addText( text = "some information", 
                      x = 0., y = 0.95, color = 'blue')
    textScan.addText( text = "and more infos", 
                      x = 0., y = 0.85, color = 'blue')
    t1 = PySpectra.Scan( "t1", lineColor = 'blue', xLabel = 'Position', 
                     yLabel = 'sin')
    t1.y = np.sin( t1.x)
    t2 = PySpectra.Scan( "t2", xLabel = 'Position', yLabel = 'cos', 
                     symbol = 'o', symbolColor = 'red', symbolSize = 5)
    t2.y = np.cos( t2.x)
    t3 = PySpectra.Scan( "t3", xLabel = 'Position', yLabel = 'tan', 
                     symbol = '+', lineColor = 'cyan', 
                     symbolColor = 'green', symbolSize = 5)
    t3.y = np.tan( t3.x)
    PySpectra.display()

def example_Create5Plots():
    '''
    create 5 scans, different colors, demonstrate overlay feature
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "5 Scans, t5 is overlaid to t3")
    PySpectra.setWsViewport( "DINA5")
    t1 = PySpectra.Scan( name = "t1", lineColor = 'blue', yLabel = 'sin')
    t1.y = np.sin( t1.x)
    t2 = PySpectra.Scan( "t2", xLabel = 'Position', yLabel = 'cos', symbol = '+')
    t2.y = np.cos( t2.x)
    t3 = PySpectra.Scan( name = "t3", lineColor = 'green', 
                     xLabel = 'Position', yLabel = 'tan')
    t3.y = np.tan( t3.x)
    t4 = PySpectra.Scan( name = "t4", lineColor = 'NONE', 
                     xLabel = 'Position', yLabel = 'random', 
                     symbol = '+', symbolColor = 'CYAN')
    t4.y = np.random.random_sample( (len( t4.y), ))
    t5 = PySpectra.Scan( name = "t5", lineColor = 'magenta', 
                     xLabel = 'Position', yLabel = 'x**2')
    t5.y = t5.x * t5.x
    PySpectra.overlay( 't5', 't3')
    PySpectra.display()

def example_Create22Plots():
    '''
    create 22 plots
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "22 Scans")
    PySpectra.setComment( "and a comment")
    PySpectra.setWsViewport( "DINA4")
    for i in range( 22): 
        t = PySpectra.Scan( name = "t%d" % i, lineColor = 'blue',
                        xLabel = 'Position', yLabel = 'rand')
        t.y = np.random.random_sample( (len( t.x), ))*1000.
    PySpectra.display()

def example_Create56x3Plots():
    '''
    create 56x3 plots
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "56 x 3 Scans")
    PySpectra.setComment( "Display many Scans")
    PySpectra.setWsViewport( "DINA4")
    for i in range( 56): 
        t = PySpectra.Scan( name = "t%d_a" % i, lineColor = 'blue', nPts = 200, 
                        yLabel = 'rand')
        t.y = np.random.random_sample( (len( t.x), ))*1000.
        t = PySpectra.Scan( name = "t%d_b" % i, lineColor = 'red', nPts = 200, 
                        yLabel = 'rand', overlay = "t%d_a" % i)
        t.y = np.random.random_sample( (len( t.x), ))*1000.
        t = PySpectra.Scan( name = "t%d_c" % i, lineColor = 'green', nPts = 200, 
                        yLabel = 'rand', overlay = "t%d_a" % i)
        t.y = np.random.random_sample( (len( t.x), ))*1000.
    PySpectra.display()
    return 

def example_CreatePDF():
    '''
    create a pdf file
    '''
    printer = os.getenv( "PRINTER")
    if printer is None: 
        print( "examplecreatePDF: environment variable PRINTER not defined, returning")
        return 

    PySpectra.cls()
    PySpectra.delete()

    PySpectra.setTitle( "Create PDF file and send it to the printer")
    PySpectra.setWsViewport( "DINA5")
    scan = PySpectra.Scan( name = 'PDF Output', nPts = 100, xMin = -1., xMax = 1.,
                           xLabel = 'Position', yLabel = "Counts")
    
    scan.y = np.sin( scan.x)

    PySpectra.setWsViewport( "DINA4")
    PySpectra.display()

    PySpectra.createPDF( flagPrint = True)
    return 

def example_GaussAndSinusOverlay():
    '''
    overlay 2 scans
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "2 Overlay Scans")
    PySpectra.setWsViewport( "DINA5")
    g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)
    t1 = PySpectra.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = np.sin( t1.x)
    PySpectra.overlay( "sinus", "gauss")
    PySpectra.display()

def example_Gauss():
    '''
    gauss plot
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "A simple Gauss curve")
    PySpectra.setComment( "Can be used with SSA, calculating derivative and so")
    PySpectra.setWsViewport( "DINA5")
    g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)
    PySpectra.display()
    return 

def example_GaussManyOverlay():
    '''
    gauss plot
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setWsViewport( "DINA5")
    g = PySpectra.Scan( name = "gauss", xMin = -10., xMax = 10., nPts = 101)
    #mu = 0.
    #sigma = 1.
    #g.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu)**2/(2*sigma**2))
    mu1 = 0.
    sigma1 = 1.
    mu2 = 6.5
    sigma2 = 1.2
    g.y = 1./(sigma1*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu1)**2/(2*sigma1**2)) + \
          2./(sigma2*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu2)**2/(2*sigma2**2))
    g.autoscaleX = False
    g.autoscaleY = False
    g.xMax = 11
    g.xMin = -4
    g.yMin = 0
    g.yMax = 2
    for i in range( 1,50):  # don't want i == 0
        gqe = PySpectra.Scan( name = "gauss%d" % i, xMin = -5., xMax = 5., 
                          nPts = 101)
        gqe.x = g.x + 0.02 * i
        gqe.y = g.y + 0.02 * i
        PySpectra.overlay( "gauss%d" % i, "gauss")
        gqe.useTargetWindow = True
        
    PySpectra.display()
    return 

def example_GaussNoisy():
    '''
    gauss plot
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "a noisy Gauss at 0.12345")
    PySpectra.setComment( "See how FSA/SSA behaves with noisy data")
    PySpectra.setWsViewport( "DINA5")
    g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'red', x0 = 0.12345, sigma = 1., amplitude = 1.)
    g.y += np.random.random_sample( (len( g.x), ))*0.05
    PySpectra.display()
    return 

def example_DipNoisy():
    '''
    gauss plot
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "a noisy Dip at 0.25")
    PySpectra.setComment( "See how FSA behaves with noisy data")
    PySpectra.setWsViewport( "DINA5")
    g = utils.createGauss( name = "dip", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'red', x0 = 0.25, sigma = 1., amplitude = 1.)
    g.y += np.random.random_sample( (len( g.x), ))*0.05
    g.y = -g.y + 1.
    PySpectra.display()
    return 

def example_GaussVeryNoisy():
    '''
    gauss plot
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "a very noisy Gauss at 0.12345")
    PySpectra.setComment( "See how FSA/SSA behaves with noisy data")
    PySpectra.setWsViewport( "DINA5")
    g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'red', x0 = 0.12345, sigma = 1., amplitude = 1.)
    g.y += np.random.random_sample( (len( g.x), ))*0.3
    PySpectra.display()
    return 

def example_StepNoisy():
    '''
    step function
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "a noisy Step")
    PySpectra.setComment( "See how FSA behaves with noisy data")
    PySpectra.setWsViewport( "DINA5")
    g = utils.createStep( name = "step", xMin = -10., xMax = 10., nPts = 101, 
                          lineColor = 'red', amplitude = 3.)
    g.y += np.random.random_sample( (len( g.x), ))*0.5
    PySpectra.display()
    return 

def example_StepRealData():
    '''
    step function from P23 data
    '''

    data = [ "-2.4298828125 37681148972.8", 
             "-2.4048828125 38401871477.4", 
             "-2.3798828125 38288686270.4", 
             "-2.3548828125 39185991728.4", 
             "-2.3298828125 38456517187.0", 
             "-2.3048828125 39194360929.6", 
             "-2.2798828125 37675200637.4", 
             "-2.2548828125 38996830621.8", 
             "-2.2298828125 38551627446.6", 
             "-2.2048828125 37100623732.0", 
             "-2.1798828125 36825602737.3", 
             "-2.1548828125 34963557105.2", 
             "-2.1298828125 32163944722.6", 
             "-2.1048828125 29299318167.0", 
             "-2.0798828125 27794769897.0", 
             "-2.0548828125 26176477795.0", 
             "-2.0298828125 24897579745.6", 
             "-2.0048828125 22452187722.0", 
             "-1.9798828125 20009478027.1", 
             "-1.9548828125 17694863875.7", 
             "-1.9298828125 15497083354.3", 
             "-1.9048828125 12901608052.8", 
             "-1.8798828125 10673203037.1", 
             "-1.8548828125 7980209447.64", 
             "-1.8298828125 5662638085.9", 
             "-1.8048828125 3098076234.4", 
             "-1.7798828125 1296338340.95", 
             "-1.7548828125 708398132.123", 
             "-1.7298828125 592764964.744", 
             "-1.7048828125 252664555.849", 
             "-1.6798828125 81626386.5509", 
             "-1.6548828125 971789.900217", 
             "-1.6298828125 3887184.77659", 
             "-1.6048828125 0.0", 
             "-1.5798828125 0.0", 
             "-1.5548828125 3887285.48112", 
             "-1.5298828125 0.0", 
             "-1.5048828125 4858729.21921", 
             "-1.4798828125 2915256.41246", 
             "-1.4548828125 0.0", 
             "-1.4298828125 0.0"]

    xArr = []
    yArr = []
    for line in data: 
        (x, y) = line.split( ' ')
        xArr.append( float( x))
        yArr.append( float( y))

    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "Real data")
    PySpectra.setComment( "See that FSA(stepm) failes but FSA(stepmssa) produces a result")
    PySpectra.setWsViewport( "DINA5")


    g = PySpectra.Scan( name = 'realdata', x = xArr, y = yArr)

    PySpectra.display()
    return 

def example_Gauss2():
    ''' 
    2 gauss plot
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "Two Gauss curves")
    PySpectra.setComment( "To demonstrate how SSA limits can be defined with VLines")
    PySpectra.setWsViewport( "DINA5")
    g = PySpectra.Scan( name = "gauss", xMin = -10., xMax = 10., nPts = 101)
    mu1 = 0.
    sigma1 = 1.
    mu2 = 6.5
    sigma2 = 1.2
    g.y = 1./(sigma1*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu1)**2/(2*sigma1**2)) + \
          2./(sigma2*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu2)**2/(2*sigma2**2))
    PySpectra.display()
    return 

def example_Scanning():
    '''    
    '''
    PySpectra.cls()
    PySpectra.delete()

    PySpectra.setTitle( "scanning, x-axis is fixed")
    PySpectra.setWsViewport( "DINA5")
    sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, 
                        autoscaleX = False, lineColor = 'red')


    for i in range( sinus.nPts): 
        sinus.setX( i, i/10. + 0.01)
        sinus.setY( i, math.sin( i/10.))
        PySpectra.display( ['sinus'])
        time.sleep( 0.01)
    return 

def example_ScanningMesh():
    '''    
    '''
    PySpectra.cls()
    PySpectra.delete()

    (xmin, xmax) = (-2., 1)
    (ymin, ymax) = (-1.5, 1.5)
    (width, height) = (20, 20)
    maxiter = 20
    
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.zeros((width,height))
            
    m = PySpectra.Image( name = "MandelbrotSet", colorMap = 'Greys', 
                     estimatedMax = 20, 
                     xMin = xmin, xMax = xmax, width = width, 
                     yMin = ymin, yMax = ymax, height = height)
    
    PySpectra.setTitle( "Simulate a mesh scan")
    PySpectra.setWsViewport( "DINA5")
    sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = width*height, 
                        autoscaleX = False, lineColor = 'red')
    cosinus = PySpectra.Scan( name = 'cosinus', xMin = 0., xMax = 6.0, nPts = width*height, 
                        autoscaleX = False, lineColor = 'red')

    PySpectra.display()

    (iI, jI) = (0, 0)
    for i in range( sinus.nPts): 
        x = float(i)*6.28/float(sinus.nPts)
        sinus.setX( i, x)
        cosinus.setX( i, x)
        sinus.setY( i, math.sin( x))
        cosinus.setY( i, math.cos( x))
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
    PySpectra.delete()
    
    PySpectra.setTitle( "scanning, x-axis is re-scaled")
    PySpectra.setWsViewport( "DINA5")
    sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, 
                        autoscaleX = True, lineColor = 'red')
    for i in range( sinus.nPts): 
        sinus.setX( i, i/10. + 0.01)
        sinus.setY( i, math.sin( i/10.))
        PySpectra.display( ['sinus'])
        time.sleep( 0.01)
    return 

def example_ScanningReverse():
    '''    
    '''
    PySpectra.cls()
    PySpectra.delete()
    
    PySpectra.setTitle( "scanning in reverse direction, x-axis is fixed")
    PySpectra.setWsViewport( "DINA5")
    sinus = PySpectra.Scan( name = 'sinus', 
                        xMin = 0., xMax = 6.0, nPts = 101, 
                        autoscaleX = False, 
                        lineColor = 'red')
    sinus.xMax = 10.
    for i in range( sinus.nPts): 
        x = 10. - i/10.
        sinus.setX( i, x)
        sinus.setY( i, math.sin( i/10.))
        PySpectra.display( ['sinus'])
        time.sleep( 0.05)
    return 

def example_ScanningReverseAutoscaleX():
    '''    
    '''
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "scanning in reverse direction, the x-axis is re-scaled")
    PySpectra.setWsViewport( "DINA5")
    sinus = PySpectra.Scan( name = 'sinus', 
                            xMin = 0., xMax = 6.0, nPts = 101, 
                            autoscaleX = True, 
                            lineColor = 'red')
    for i in range( sinus.nPts): 
        x = 10. - i/10.
        sinus.x[i] = x
        sinus.y[i] = math.sin( i/10.)
        sinus.currentIndex = i
        PySpectra.display( ['sinus'])
        time.sleep( 0.02)

def example_Lissajous(): 
    '''
    plots and updates a Lissajous figure
    '''
    PySpectra.setWsViewport( "DINA5S")
    
    PySpectra.cls()
    PySpectra.delete()
    scan = PySpectra.Scan( name = 'Lissajous', nPts = 1000, xMin = -1., xMax = 1.)
    
    x  = np.linspace( 0., 6.5, 1000)
    y  = np.linspace( 0., 6.5, 1000)
    
    scan.x = np.cos( x)
    scan.y = np.sin( y)
    
    PySpectra.display()
    
    for i in range( 500):
        x = x + 0.005
        scan.smartUpdateDataAndDisplay( np.cos( x), np.sin( y))

def example_Overlay2BothLog(): 
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "2 Overlay Scans, both with log scale")
    PySpectra.setComment( "both axes have different ranges")
    PySpectra.setWsViewport( "DINA5")
    g1 = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)
    g1.yLog = True
    g2 = utils.createGauss( name = "gauss2", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'green', x0 = 0.5, sigma = 1.2, amplitude = 1.)
    g2.yLog = True
    g2.yMin = 0.001
    g2.yMax = 1.

    PySpectra.overlay( "gauss2", "gauss")

    PySpectra.display()

def example_Overlay2FirstLog(): 
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "2 Overlay Scans, first (red) has log scale")
    PySpectra.setComment( "Sadly, there are no major tick mark strings at the right axis")
    PySpectra.setWsViewport( "DINA5")

    g1 = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)

    g1.yLog = True

    g2 = utils.createGauss( name = "gauss2", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'green', x0 = 0.5, sigma = 1.2, amplitude = 1.)

    PySpectra.overlay( "gauss2", "gauss")

    PySpectra.display()

def example_Overlay2SecondLog(): 
    PySpectra.cls()
    PySpectra.delete()
    PySpectra.setTitle( "2 Overlay Scans, 2nd (green) has log scale")
    PySpectra.setComment( "Sadly, there are no major tick mark strings at the right axis")
    PySpectra.setWsViewport( "DINA5")

    g1 = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)
    g2 = utils.createGauss( name = "gauss2", xMin = -5., xMax = 5., nPts = 101, 
                           lineColor = 'green', x0 = 0.5, sigma = 1.2, amplitude = 1.)

    g2.yLog = True

    PySpectra.overlay( "gauss2", "gauss")

    PySpectra.display()

def example_ImageMB(): 

    PySpectra.setWsViewport( 'DINA5S')

    PySpectra.cls()
    PySpectra.delete()

    (xmin, xmax) = (-2., 0.5)
    (ymin, ymax) = (-1.25, 1.25)
    (width, height) = (750, 750)
    maxiter = 512
    
    m = PySpectra.Image( name = "MandelbrotSet",
                   flagAxes = True, 
                   maxIter = maxiter, 
                   xMin = xmin, xMax = xmax, width = width, 
                   yMin = ymin, yMax = ymax, height = height)
    m.flagZoomMbSlow = False
    m.zoomMb()
    PySpectra.cls()
    PySpectra.display()
    return 

def example_ImageRandom(): 

    import random
    
    PySpectra.setWsViewport( 'DINA5S')

    PySpectra.cls()
    PySpectra.delete()

    (xmin, xmax) = (-2., 1)
    (ymin, ymax) = (-1.5, 1.5)
    (width, height) = (500, 500)
    
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.empty((width,height))
    for i in range(width):
        for j in range(height):
            n3[i,j] = i + random.random()*j + 100.
            
    m = PySpectra.Image( name = "ImageRandom", data = n3, 
                    xMin = xmin, xMax = xmax, width = width, 
                    yMin = ymin, yMax = ymax, height = height, 
                    xLabel = "x-Axis", yLabel = "y-Axis")

    PySpectra.cls()
    PySpectra.display()
    return 


