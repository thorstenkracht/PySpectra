#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/testZmqIfc.py testZmqIfc.testExecHsh1
python ./test/testZmqIfc.py testZmqIfc.testExecHsh2
python ./test/testZmqIfc.py testZmqIfc.testExecHsh3
python ./test/testZmqIfc.py testZmqIfc.testExecHsh4
python ./test/testZmqIfc.py testZmqIfc.testExecHsh5
python ./test/testZmqIfc.py testZmqIfc.testExecHsh6
python ./test/testZmqIfc.py testZmqIfc.testExecHsh7
'''
import sys
#pySpectraPath = "/home/kracht/Misc/pySpectra"
pySpectraPath = "."
sys.path.append( pySpectraPath)

import PySpectra
import PySpectra.GQE as GQE
import PySpectra.zmqIfc as zmqIfc
import numpy as np
import unittest

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
        pass

    @classmethod
    def tearDownClass( testZmqIfc): 
        PySpectra.close()

    def testExecHsh1( self) : 
        import random
        print "testZmqIfc.testExecHsh1"

        hsh = zmqIfc.execHsh( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')

        MAX = 25
        pos = [float(n)/MAX for n in range( MAX)]
        d1 = [random.random() for n in range( MAX)]
        d2 = [random.random() for n in range( MAX)]
        hsh = zmqIfc.execHsh( { 'putData': {'title': "Important Data", 
                                              'comment': "a comment", 
                                              'columns': 
                                              [ { 'name': "eh_mot01", 'data' : pos},
                                                { 'name': "eh_c01", 'data' : d1},
                                                { 'name': "eh_c02", 'data' : d2, 
                                                  'symbolColor': 'blue', 'symbol': '+', 'symbolSize': 5, 
                                                  'xLog': False, 'yLog': False, 
                                                  'showGridX': False, 'showGridY': False}]}})
        self.assertEqual( hsh[ 'result'], 'done')
        zmqIfc.execHsh( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)
        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 2)
        self.assertEqual( lst[0].name, "eh_c01")
        self.assertEqual( lst[1].name, "eh_c02")
        
        #
        # retrieve the data 
        #
        hsh = zmqIfc.execHsh( { 'getData': True})
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # ... and compare.
        #
        for i in range( MAX):
            self.assertEqual( pos[i], hsh[ 'getData']['EH_C01']['x'][i])
            self.assertEqual( d1[i], hsh[ 'getData']['EH_C01']['y'][i])
            self.assertEqual( d2[i], hsh[ 'getData']['EH_C02']['y'][i])
        print "testZmqIfc.testExecHsh1 DONE"
        return 
        
    def testExecHsh2( self) : 
        import random
        print "testZmqIfc.testExecHsh1"

        hsh = zmqIfc.execHsh( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        MAX = 25
        pos = [float(n)/MAX for n in range( MAX)]
        d1 = [random.random() for n in range( MAX)]
        d2 = [random.random() for n in range( MAX)]
        hsh = zmqIfc.execHsh( { 'Scan': { 'name': "d1", 'x': pos, 'y': d1}})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = zmqIfc.execHsh( { 'Scan': { 'name': "d2", 'x': pos, 'y': d2}})
        self.assertEqual( hsh[ 'result'], 'done')

        zmqIfc.execHsh( { 'command': ['setTitle \"a title\"']})
        self.assertEqual( hsh[ 'result'], 'done')
        zmqIfc.execHsh( { 'command': ['setComment \"a comment\"']})
        self.assertEqual( hsh[ 'result'], 'done')
        zmqIfc.execHsh( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)
        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 2)
        self.assertEqual( lst[0].name, "d1")
        self.assertEqual( lst[1].name, "d2")

        #
        # retrieve the data and compare
        #
        hsh = zmqIfc.execHsh( { 'getData': True})
        for i in range( MAX):
            self.assertEqual( pos[i], hsh[ 'getData']['D1']['x'][i])
            self.assertEqual( d1[i], hsh[ 'getData']['D1']['y'][i])
            self.assertEqual( d2[i], hsh[ 'getData']['D2']['y'][i])
        #
        # set y-values 
        #
        for i in range( MAX):
            zmqIfc.execHsh( { 'command': ['setY d1 %d %g' % (i, float(i)/10.)]})
        #
        # and compare
        #
        o = GQE.getGqe( 'd1')
        for i in range( MAX):
            self.assertEqual( o.y[i], float(i)/10.)
        
        zmqIfc.execHsh( { 'command': ['cls', 'display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)

        
        print "testZmqIfc.testExecHsh2 DONE"
        return 

    def testExecHsh3( self) : 
        '''
        set the mandelbrot pixel in pixel numbers (whole numbers)
        '''
        hsh = zmqIfc.execHsh( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = zmqIfc.execHsh( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # do the clean-up before we start
        #
        hsh =  zmqIfc.execHsh( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        self.assertEqual( hsh[ 'result'], 'done')

        #
        # create the image
        #
        hsh = { 'Image': 
                { 'name': "MandelBrot",
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}

        hsh = zmqIfc.execHsh( hsh)
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
                hsh = zmqIfc.execHsh( hsh)
                self.assertEqual( hsh[ 'result'], 'done')
            hsh =  zmqIfc.execHsh( { 'command': ['cls', 'display']})
            self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)

    def testExecHsh4( self) : 
        '''
        set the mandelbrot pixel in world coordinates
        '''
        hsh = zmqIfc.execHsh( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = zmqIfc.execHsh( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # do the clean-up before we start
        #
        hsh =  zmqIfc.execHsh( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        self.assertEqual( hsh[ 'result'], 'done')

        #
        # create the image
        #
        hsh = { 'Image': 
                { 'name': "MandelBrot",
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}

        hsh = zmqIfc.execHsh( hsh)
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
                hsh = zmqIfc.execHsh( hsh)
                self.assertEqual( hsh[ 'result'], 'done')
            hsh =  zmqIfc.execHsh( { 'command': ['cls', 'display']})
            self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)

    def testExecHsh5( self) : 
        hsh = zmqIfc.execHsh( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = zmqIfc.execHsh( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # do the clean-up before we start
        #
        hsh =  zmqIfc.execHsh( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        self.assertEqual( hsh[ 'result'], 'done')

        #
        # create the image
        #
        hsh = { 'Image': 
                { 'name': "MandelBrot",
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}

        hsh = zmqIfc.execHsh( hsh)
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = { 'command': "setPixelWorld Mandelbrot %g %g %g" %  ( r1[i], r2[j], res)}
                hsh = zmqIfc.execHsh( hsh)
                self.assertEqual( hsh[ 'result'], 'done')
            hsh =  zmqIfc.execHsh( { 'command': ['cls', 'display']})
            self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)

    def testExecHsh6( self) : 
        '''
        use putData to transfer a complete image at once
        '''
        hsh = zmqIfc.execHsh( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = zmqIfc.execHsh( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # do the clean-up before we start
        #
        hsh =  zmqIfc.execHsh( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        self.assertEqual( hsh[ 'result'], 'done')

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

        hsh = zmqIfc.execHsh( { 'putData': 
                                { 'images': [{'name': "MandelBrot", 'data': data,
                                              'xMin': xmin, 'xMax': xmax, 
                                              'yMin': ymin, 'yMax': ymax}]}})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  zmqIfc.execHsh( { 'command': ['cls', 'display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.processEventsLoop( 1)

    def testExecHsh7( self) : 
        '''
        use Image to transfer a complete image at once
        '''
        hsh = zmqIfc.execHsh( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = zmqIfc.execHsh( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # do the clean-up before we start
        #
        hsh =  zmqIfc.execHsh( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        self.assertEqual( hsh[ 'result'], 'done')

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

        hsh = zmqIfc.execHsh( { 'Image': 
                                          { 'name': "MandelBrot", 'data': data, 
                                            'xMin': xmin, 'xMax': xmax, 
                                            'yMin': ymin, 'yMax': ymax, 
                                          }})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  zmqIfc.execHsh( { 'command': ['cls', 'display']})
        self.assertEqual( hsh[ 'result'], 'done')
        o = GQE.getGqe( "Mandelbrot")
        self.assertEqual( o.height, 100)
        self.assertEqual( o.width, 100)
        self.assertEqual( o.xMin, xmin)
        self.assertEqual( o.xMax, xmax)
        self.assertEqual( o.yMin, ymin)
        self.assertEqual( o.yMax, ymax)
        PySpectra.processEventsLoop( 1)

if __name__ == "__main__":
    unittest.main()
