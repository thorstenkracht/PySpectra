#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/testZmqIfc.py testZmqIfc.testToPyspLocalColumns
python ./test/testZmqIfc.py testZmqIfc.testToPyspLocalScan
python ./test/testZmqIfc.py testZmqIfc.testToPyspLocalSetPixelImage
python ./test/testZmqIfc.py testZmqIfc.testToPyspLocalSetPixelWorld
python ./test/testZmqIfc.py testZmqIfc.testToPyspLocalCompleteImagePutData
python ./test/testZmqIfc.py testZmqIfc.testToPyspLocalCompleteImageByImage
python ./test/testZmqIfc.py testZmqIfc.testToPyspLocalCompleteImageWithGetData
python ./test/testZmqIfc.py testZmqIfc.testToPyspMonitorColumns
python ./test/testZmqIfc.py testZmqIfc.testToPyspMonitorScan
python ./test/testZmqIfc.py testZmqIfc.testToPyspMonitorSetPixelImage
python ./test/testZmqIfc.py testZmqIfc.testToPyspMonitorSetPixelWorld
python ./test/testZmqIfc.py testZmqIfc.testToPyspMonitorCompleteImagePutData
python ./test/testZmqIfc.py testZmqIfc.testToPyspMonitorCompleteImageByImage
'''
import sys
#pySpectraPath = "/home/kracht/Misc/pySpectra"
pySpectraPath = "."
sys.path.append( pySpectraPath)

import PySpectra
import PySpectra.utils as utils
import PySpectra.definitions as definitions
import numpy as np
import unittest, time

wasLaunched = False

def mandelbrot( c, maxiter):
    z = c
    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return 0

class testZmqIfc( unittest.TestCase):

    @classmethod
    def setUpClass( testZmqIfc):
        global wasLaunched
        (status, wasLaunched) = PySpectra.assertPyspMonitorRunning()

    @classmethod
    def tearDownClass( testZmqIfc): 
        if wasLaunched:
            PySpectra.killPyspMonitor()
        PySpectra.close()

    def testToPyspLocalColumns( self) : 
        import random
        print "testZmqIfc.testToPyspLocalColumns"

        hsh = PySpectra.toPyspLocal( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')

        MAX = 25
        pos = np.linspace(0, 10, MAX)
        d1 = np.random.random_sample( (len( pos), ))*1000.
        d2 = np.random.random_sample( (len( pos), ))*1000.

        hsh = PySpectra.toPyspLocal( { 'putData': {'title': "testing putData & columns", 
                                            'comment': "a comment", 
                                            'columns': 
                                            [ { 'name': "eh_mot01", 'data' : pos},
                                              { 'name': "eh_c01", 'data' : d1},
                                              { 'name': "eh_c02", 'data' : d2, 
                                                'symbolColor': 'blue', 'symbol': '+', 'symbolSize': 5, 
                                                'xLog': False, 'yLog': False, 
                                                'showGridX': False, 'showGridY': False}]}})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.toPyspLocal( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 2)
        self.assertEqual( lst[0].name, "eh_c01")
        self.assertEqual( lst[1].name, "eh_c02")
        
        #
        # retrieve the data 
        #
        hsh = PySpectra.toPyspLocal( { 'getData': True})
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # ... and compare.
        #
        for i in range( MAX):
            self.assertEqual( pos[i], hsh[ 'getData']['EH_C01']['x'][i])
            self.assertEqual( d1[i], hsh[ 'getData']['EH_C01']['y'][i])
            self.assertEqual( d2[i], hsh[ 'getData']['EH_C02']['y'][i])

        print "testZmqIfc.testToPyspLocalColumns DONE"
        return 
        
    def testToPyspLocalScan( self) : 
        import random
        print "testZmqIfc.testToPyspLocalScan"

        hsh = PySpectra.toPyspLocal( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')

        MAX = 25
        pos = np.linspace(0, 10, MAX)
        d1 = np.random.random_sample( (len( pos), ))*1000.
        d2 = np.random.random_sample( (len( pos), ))*1000.

        PySpectra.toPyspLocal( { 'command': ['setTitle "testing Scan command"']})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh = PySpectra.toPyspLocal( { 'Scan': { 'name': "d1", 'x': pos, 'y': d1}})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspLocal( { 'Scan': { 'name': "d2", 'x': pos, 'y': d2}})
        self.assertEqual( hsh[ 'result'], 'done')

        PySpectra.toPyspLocal( { 'command': ['setComment \"a comment\"']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.toPyspLocal( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 2)
        self.assertEqual( lst[0].name, "d1")
        self.assertEqual( lst[1].name, "d2")

        #
        # retrieve the data and compare
        #
        hsh = PySpectra.toPyspLocal( { 'getData': True})
        for i in range( MAX):
            self.assertEqual( pos[i], hsh[ 'getData']['D1']['x'][i])
            self.assertEqual( d1[i], hsh[ 'getData']['D1']['y'][i])
            self.assertEqual( d2[i], hsh[ 'getData']['D2']['y'][i])
        #
        # set y-values 
        #
        PySpectra.toPyspLocal( { 'command': ['setTitle "set y-values to linear"']})
        self.assertEqual( hsh[ 'result'], 'done')
        for i in range( MAX):
            PySpectra.toPyspLocal( { 'command': ['setY d1 %d %g' % (i, float(i)/10.)]})
        #
        # and compare
        #
        o = PySpectra.getGqe( 'd1')
        for i in range( MAX):
            self.assertEqual( o.y[i], float(i)/10.)
        
        PySpectra.toPyspLocal( { 'command': ['cls', 'display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)
        
        print "testZmqIfc.testToPyspLocalScan DONE"
        return 

    def testToPyspLocalSetPixelImage( self) : 
        '''
        set the mandelbrot pixel in pixel numbers (whole numbers)
        '''
        print "testZmqIfc.testToPyspLocalSetPixelImage"
        hsh = PySpectra.toPyspLocal( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspLocal( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # title: set pixels using pixel coordinates
        #
        hsh =  PySpectra.toPyspLocal( { 'command': ['setTitle "set pixels using pixel coordinates"']})
        self.assertEqual( hsh[ 'result'], 'done')

        #
        # create the image
        #
        hsh = { 'Image': 
                { 'name': "MandelBrot",
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}

        hsh = PySpectra.toPyspLocal( hsh)
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = { 'command': [ 'setPixelImage MandelBrot %d %d %g' % ( i, j, res)]}
                hsh = PySpectra.toPyspLocal( hsh)
                self.assertEqual( hsh[ 'result'], 'done')
            hsh =  PySpectra.toPyspLocal( { 'command': ['display']})
            self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)
        print "testZmqIfc.testToPyspLocalSetPixelImage DONE"
        return 

    def testToPyspLocalSetPixelWorld( self) : 
        '''
        set the mandelbrot pixel in world coordinates
        '''
        print "testZmqIfc.testToPyspLocalSetPixelWorld"
        hsh = PySpectra.toPyspLocal( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspLocal( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # title: set pixels using world coordinates
        #
        hsh =  PySpectra.toPyspLocal( { 'command': ['setTitle "set pixels using world coordinates"']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25
        #
        # create the image
        #
        hsh = { 'Image': 
                { 'name': "MandelBrot",
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}

        hsh = PySpectra.toPyspLocal( hsh)
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = { 'command': [ 'setPixelWorld MandelBrot %g %g %g' % ( r1[i], r2[j], res)]}
                hsh = PySpectra.toPyspLocal( hsh)
                self.assertEqual( hsh[ 'result'], 'done')
            hsh =  PySpectra.toPyspLocal( { 'command': ['display']})
            self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)

        print "testZmqIfc.testToPyspLocalSetPixelWorld DONE"
        return 

    def testToPyspLocalCompleteImagePutData( self) : 
        '''
        use putData to transfer a complete image at once
        '''
        print "testZmqIfc.testToPyspLocalCompleteImagePutData"
        hsh = PySpectra.toPyspLocal( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspLocal( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        data = np.ndarray( (width, height), np.float64)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                data[i][j] = int( res)
        #
        # title: putData transfers the complete image at once
        #
        hsh =  PySpectra.toPyspLocal( { 'command': ['setTitle "putData transfers the complete image at once"']})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh = PySpectra.toPyspLocal( { 'putData': 
                                { 'images': [{'name': "MandelBrot", 'data': data,
                                              'xMin': xmin, 'xMax': xmax, 
                                              'yMin': ymin, 'yMax': ymax}]}})
        self.assertEqual( hsh[ 'result'], 'done')


        hsh =  PySpectra.toPyspLocal( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 2)

        print "testZmqIfc.testToPyspLocalCompleteImagePutData DONE"
        return 

    def testToPyspLocalCompleteImageByImage( self) : 
        '''
        use Image to transfer a complete image at once
        '''
        print "testZmqIfc.testToPyspLocalCompleteImageByImage"
        hsh = PySpectra.toPyspLocal( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspLocal( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # setTitle
        #
        hsh =  PySpectra.toPyspLocal( { 'command': ['setTitle "use Imageto transfer the complete image at once"']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        data = np.ndarray( (width, height), np.float64)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                data[i][j] = int( res)

        hsh = PySpectra.toPyspLocal( { 'Image': 
                                { 'name': "MandelBrot", 'data': data, 
                                  'xMin': xmin, 'xMax': xmax, 
                                  'yMin': ymin, 'yMax': ymax, 
                                }})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  PySpectra.toPyspLocal( { 'command': ['cls', 'display']})
        self.assertEqual( hsh[ 'result'], 'done')
        o = PySpectra.getGqe( "Mandelbrot")
        self.assertEqual( o.height, 100)
        self.assertEqual( o.width, 100)
        self.assertEqual( o.xMin, xmin)
        self.assertEqual( o.xMax, xmax)
        self.assertEqual( o.yMin, ymin)
        self.assertEqual( o.yMax, ymax)
        PySpectra.processEventsLoop( 2)

        print "testZmqIfc.testToPyspLocalCompleteImageByImage DONE"
        return 

    def testToPyspLocalCompleteImageWithGetData( self) : 
        '''
        use Image to transfer a complete image at once
        '''
        print "testZmqIfc.testToPyspLocalCompleteImageWithGetData"

        hsh = PySpectra.toPyspLocal( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspLocal( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')
        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (20, 20)
        maxiter = 25
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        data = np.ndarray( (width, height), np.float64)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                data[i][j] = int( res)

        hsh = PySpectra.toPyspLocal( { 'Image': 
                                       { 'name': "MandelBrot", 'data': data, 
                                         'xMin': xmin, 'xMax': xmax, 
                                         'yMin': ymin, 'yMax': ymax, 
                                       }})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh = PySpectra.toPyspLocal( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh = PySpectra.toPyspLocal({'getData': True}) 
        print( "testZmqIfc: %s" % repr( hsh))
        PySpectra.processEventsLoop( 2)

        print "testZmqIfc.testToPyspLocalCompleteImageWithGetData DONE"
        return 

    def testToPyspMonitorColumns( self) : 
        import random
        print "testZmqIfc.testToPyspMonitor1"

        if utils.getHostname() != definitions.hostTK: 
            return 

        hsh = PySpectra.toPyspMonitor( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')

        MAX = 25
        pos = np.linspace(0, 10, MAX)
        d1 = np.random.random_sample( (len( pos), ))*1000.
        d2 = np.random.random_sample( (len( pos), ))*1000.

        hsh = PySpectra.toPyspMonitor( { 'putData': {'title': "testing putData & columns", 
                                            'comment': "a comment", 
                                            'columns': 
                                            [ { 'name': "eh_mot01", 'data' : pos},
                                              { 'name': "eh_c01", 'data' : d1},
                                              { 'name': "eh_c02", 'data' : d2, 
                                                'symbolColor': 'blue', 'symbol': '+', 'symbolSize': 5, 
                                                'xLog': False, 'yLog': False, 
                                                'showGridX': False, 'showGridY': False}]}})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.toPyspMonitor( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')
        time.sleep( 1)
        
        #
        # retrieve the data 
        #
        hsh = PySpectra.toPyspMonitor( { 'getData': True})
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # ... and compare.
        #
        for i in range( MAX):
            self.assertEqual( pos[i], hsh[ 'getData']['EH_C01']['x'][i])
            self.assertEqual( d1[i], hsh[ 'getData']['EH_C01']['y'][i])
            self.assertEqual( d2[i], hsh[ 'getData']['EH_C02']['y'][i])

        print "testZmqIfc.testToPyspMonitorColumns DONE"
        return 
        
    def testToPyspMonitorScan( self) : 
        import random
        print "testZmqIfc.testToPyspMonitor2"

        if utils.getHostname() != definitions.hostTK: 
            return 

        hsh = PySpectra.toPyspMonitor( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')

        MAX = 25
        pos = np.linspace(0, 10, MAX)
        d1 = np.random.random_sample( (len( pos), ))*1000.
        d2 = np.random.random_sample( (len( pos), ))*1000.

        PySpectra.toPyspMonitor( { 'command': ['setTitle "testing Scan command"']})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh = PySpectra.toPyspMonitor( { 'Scan': { 'name': "d1", 'x': pos, 'y': d1}})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspMonitor( { 'Scan': { 'name': "d2", 'x': pos, 'y': d2}})
        self.assertEqual( hsh[ 'result'], 'done')

        PySpectra.toPyspMonitor( { 'command': ['setComment \"a comment\"']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.toPyspMonitor( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')
        time.sleep( 1)
        #
        # retrieve the data and compare
        #
        hsh = PySpectra.toPyspMonitor( { 'getData': True})
        for i in range( MAX):
            self.assertEqual( pos[i], hsh[ 'getData']['D1']['x'][i])
            self.assertEqual( d1[i], hsh[ 'getData']['D1']['y'][i])
            self.assertEqual( d2[i], hsh[ 'getData']['D2']['y'][i])
        #
        # set y-values 
        #
        PySpectra.toPyspMonitor( { 'command': ['setTitle "set y-values to linear"']})
        self.assertEqual( hsh[ 'result'], 'done')
        for i in range( MAX):
            PySpectra.toPyspMonitor( { 'command': ['setY d1 %d %g' % (i, float(i)/10.)]})
        
        PySpectra.toPyspMonitor( { 'command': ['cls', 'display']})
        self.assertEqual( hsh[ 'result'], 'done')
        time.sleep( 1)
        
        print "testZmqIfc.testToPyspMonitorScan DONE"
        return 

    def testToPyspMonitorSetPixelImage( self) : 
        '''
        set the mandelbrot pixel in pixel numbers (whole numbers)
        '''
        print "testZmqIfc.testToPyspMonitor3"

        if utils.getHostname() != definitions.hostTK: 
            return 

        hsh = PySpectra.toPyspMonitor( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspMonitor( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = ( 50, 50)
        maxiter = 25

        #
        # title: set pixels using pixel coordinates
        #
        hsh =  PySpectra.toPyspMonitor( { 'command': ['setTitle "set pixels using pixel coordinates"']})
        self.assertEqual( hsh[ 'result'], 'done')

        #
        # create the image
        #
        hsh = { 'Image': 
                { 'name': "MandelBrot",
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}

        hsh = PySpectra.toPyspMonitor( hsh)
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        startTime = time.time()
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = { 'command': [ 'setPixelImage MandelBrot %d %d %g' % ( i, j, res)]}
                hsh = PySpectra.toPyspMonitor( hsh)
                self.assertEqual( hsh[ 'result'], 'done')
            hsh =  PySpectra.toPyspMonitor( { 'command': ['display']})
            self.assertEqual( hsh[ 'result'], 'done')
        self.assertLess( (time.time() - startTime), 5)

        time.sleep( 1)

        print "testZmqIfc.testToPyspMonitorSetPixelImage DONE"
        return 

    def testToPyspMonitorSetPixelWorld( self) : 
        '''
        set the mandelbrot pixel in world coordinates
        '''
        print "testZmqIfc.testToPyspMonitor4"

        if utils.getHostname() != definitions.hostTK: 
            return 

        hsh = PySpectra.toPyspMonitor( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspMonitor( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # title: set pixels using world coordinates
        #
        hsh =  PySpectra.toPyspMonitor( { 'command': ['setTitle "set pixels using world coordinates"']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (50, 50)
        maxiter = 25
        #
        # create the image
        #
        hsh = { 'Image': 
                { 'name': "MandelBrot",
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}

        hsh = PySpectra.toPyspMonitor( hsh)
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        startTime = time.time()
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                #
                # Speed: 
                #   (50, 50) need 3.9s
                #   (50, 50) need 7s, with testAlive = True
                #
                hsh = { 'command': [ 'setPixelWorld MandelBrot %g %g %g' % ( r1[i], r2[j], res)]}
                hsh = PySpectra.toPyspMonitor( hsh)
                self.assertEqual( hsh[ 'result'], 'done')
            hsh =  PySpectra.toPyspMonitor( { 'command': ['display']})
            self.assertEqual( hsh[ 'result'], 'done')
        self.assertLess( (time.time() - startTime), 5)
        time.sleep( 1)
        print "testZmqIfc.testToPyspMonitorSetPixelWorld DONE"
        return

    def testToPyspMonitorCompleteImagePutData( self) : 
        '''
        use putData to transfer a complete image at once
        '''
        print "testZmqIfc.testToPyspMonitor6"

        if utils.getHostname() != definitions.hostTK: 
            return 

        hsh = PySpectra.toPyspMonitor( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspMonitor( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        data = np.ndarray( (width, height), np.float64)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                data[i][j] = int( res)

        #
        # title: putData transfers the complete image at once
        #
        hsh =  PySpectra.toPyspMonitor( { 'command': ['setTitle "putData transfers the complete image at once"']})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh = PySpectra.toPyspMonitor( { 'putData': 
                                         { 'images': [{'name': "MandelBrot", 'data': data,
                                                       'xMin': xmin, 'xMax': xmax, 
                                                       'yMin': ymin, 'yMax': ymax}]}})
        self.assertEqual( hsh[ 'result'], 'done')


        hsh =  PySpectra.toPyspMonitor( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')
        time.sleep( 2)

        print "testZmqIfc.testToPyspMonitorCompleteImagePutData DONE"

        return 

    def testToPyspMonitorCompleteImageByImage( self) : 
        '''
        use Image to transfer a complete image at once
        '''
        print "testZmqIfc.testToPyspMonitor7"

        if utils.getHostname() != definitions.hostTK: 
            return 

        hsh = PySpectra.toPyspMonitor( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPyspMonitor( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # setTitle
        #
        hsh =  PySpectra.toPyspMonitor( { 'command': 
                                       ['setTitle "use Imageto transfer the complete image at once"']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        data = np.ndarray( (width, height), np.float64)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                data[i][j] = int( res)

        hsh = PySpectra.toPyspMonitor( { 'Image': 
                                      { 'name': "MandelBrot", 'data': data, 
                                        'xMin': xmin, 'xMax': xmax, 
                                        'yMin': ymin, 'yMax': ymax, 
                                      }})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  PySpectra.toPyspMonitor( { 'command': ['cls', 'display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 2)

        print "testZmqIfc.testToPyspMonitorCompleteImageByImage DONE"

        return 

if __name__ == "__main__":
    unittest.main()
