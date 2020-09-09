#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/testCalc.py testCalc.testYToMinusY
python ./test/testCalc.py testCalc.testDerivative
python ./test/testCalc.py testCalc.testAntiDerivative
python ./test/testCalc.py testCalc.testDerivativeAntiDerivative
python ./test/testCalc.py testCalc.testSSAErrors
python ./test/testCalc.py testCalc.testFSA
'''
import sys
sys.path.append( "/home/kracht/Misc/pySpectra")

import PySpectra
import numpy as np
import unittest
import time, sys
import math 
import PySpectra.calc as calc

class testCalc( unittest.TestCase):

    @classmethod
    def setUpClass( testCalc):
        pass

    @classmethod
    def tearDownClass( testCalc): 
        PySpectra.close()

    def testYToMinusY( self):

        print "testCalc.testYToMinusY"

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 2., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)

        with self.assertRaises( ValueError) as context:
            calc.yToMinusY( name = None)
        #print("testSetXY: %s" %  repr( context.exception))
        self.assertTrue( "calc.yToMinusY: name not specified"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            calc.yToMinusY( name = "notExist")
        #print("testSetXY: %s" %  repr( context.exception))
        self.assertTrue( "calc.yToMinusY: failed to find notExist"
                         in context.exception)

        scanMY = calc.yToMinusY( name = scan.name, nameNew = "t1_y2MinusY")
        self.assertEqual( len( scan.y), len( scanMY.y))
        self.assertEqual( len( scan.x), len( scanMY.x))
        
        for i in range( len( scan.y)):
            self.assertEqual( scan.y[i], - scanMY.y[i])
            self.assertEqual( scan.x[i], scanMY.x[i])
        
        PySpectra.display()
        #PySpectra.show()
        PySpectra.processEventsLoop( 1)

        print "testCalc.testYToMinusY, DONE"
        
    def testDerivative( self):
        '''
        This test case produces this error, maybe it is related to the fact
        that the derivative is from 0.025 to 9.975 and one point less.

        Traceback (most recent call last):
        File "/usr/lib/python2.7/dist-packages/pyqtgraph/graphicsItems/AxisItem.py", line 412, in paint
        specs = self.generateDrawSpecs(painter)
        File "/usr/lib/python2.7/dist-packages/pyqtgraph/graphicsItems/AxisItem.py", line 819, in generateDrawSpecs
        textSize2 = np.max([r.height() for r in textRects])
        File "/usr/lib/python2.7/dist-packages/numpy/core/fromnumeric.py", line 2125, in amax
        out=out, keepdims=keepdims)
        File "/usr/lib/python2.7/dist-packages/numpy/core/_methods.py", line 17, in _amax
        out=out, keepdims=keepdims)
        ValueError: zero-size array to reduction operation maximum which has no identity
        '''

        print "testCalc.testDerivative"


        with self.assertRaises( ValueError) as context:
            calc.derivative( name = None)
        #print("testSetXY: %s" %  repr( context.exception))
        self.assertTrue( "calc.derivative: name not specified"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            calc.derivative( name = "notExist")
        #print("testSetXY: %s" %  repr( context.exception))
        self.assertTrue( "calc.derivative: failed to find notExist"
                         in context.exception)


        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        calc.derivative( name = scan.name, nameNew = "t1_d")
        PySpectra.display()
        #PySpectra.show()
        PySpectra.processEventsLoop( 1)

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.cos( scan.y)
        calc.derivative( name = scan.name)
        PySpectra.display()
        #PySpectra.show()
        PySpectra.processEventsLoop( 1)

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.tan( scan.y)
        calc.derivative( scan.name, "t1_d")
        PySpectra.display()
        #PySpectra.show()
        PySpectra.processEventsLoop( 1)

        print "testCalc.testDerivative, DONE"
        
    def testAntiDerivative( self):

        print "testCalc.testAntiDerivative"


        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)

        with self.assertRaises( ValueError) as context:
            calc.antiderivative( name = None)
        #print("testSetXY: %s" %  repr( context.exception))
        self.assertTrue( "calc.antiderivative: name not specified"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            calc.derivative( name = "notExist")
        self.assertTrue( "calc.derivative: failed to find notExist"
                         in context.exception)
        calc.antiderivative( name = scan.name, nameNew = "t1_ad")
        PySpectra.display()
        #PySpectra.show()
        PySpectra.processEventsLoop( 1)

        print "testCalc.testAntiDerivative, DONE"
        
    def testDerivativeAntiDerivative( self):

        print "testCalc.testDerivativeAntiDerivative"

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        derivative = calc.derivative( name = scan.name, nameNew = "t1_d")
        stamm = calc.antiderivative( name = derivative.name, nameNew = "t1_ad")

        self.assertEqual( len( scan.y), len( stamm.y))
        self.assertEqual( len( scan.x), len( stamm.x))
        
        for i in range( len( scan.y)):
            self.assertEqual( scan.x[i], stamm.x[i])
        
        diff = 0.
        for i in range( len( scan.y) - 1):
            diff = diff + math.fabs( scan.y[i] - stamm.y[i])

        self.assertLess( diff, 0.08)

        stamm.lineColor = 'blue'
        PySpectra.delete( "t1_d")

        PySpectra.overlay( "t1_ad", "t1") 

        PySpectra.cls()
        PySpectra.display()

        #PySpectra.launchGui()
        PySpectra.processEventsLoop( 3)

        print "testCalc.testDerivativeAntiDerivative, DONE"

        return 

    def testSSAErrors( self):

        import HasyUtils

        print "testCalc.testSSA1"

        PySpectra.cls()
        PySpectra.delete()

        ret = HasyUtils.ssa( [1, 2, 3], [4, 5, 6])

        self.assertEqual( ret[ 'status'], 0)
        self.assertEqual( ret[ 'reason'], 7)
        self.assertEqual( ret[ 'reasonString'], "not a numpy array")

        ret = HasyUtils.ssa( np.asarray( [3, 2, 1]), np.asarray([4, 5, 6]))
        self.assertEqual( ret[ 'status'], 0)
        self.assertEqual( ret[ 'reason'], 1)
        self.assertEqual( ret[ 'reasonString'], "np < 6")

        print( "%s" % repr( ret))
        print "testCalc.testSSA1 DONE"
        return 

    def testFSA( self):
        import HasyUtils

        xStep = [ 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25,
                  3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0, 5.25, 5.5, 5.75, 6.0, 6.25, 6.5, 6.75,
                  7.0, 7.25, 7.5, 7.75, 8.0, 8.25, 8.5, 8.75, 9.0, 9.25, 9.5, 9.75, 10.0]

        yStep = [17.3459918372, 16.9313967417, 15.9651547963, 17.0004691241, 17.2492800434, 16.2623471323, 
                 15.3173025351, 16.759504276, 16.835155311, 16.0834967856, 17.5422444506, 16.7609800255, 
                 17.5440253556, 17.4648421542, 15.3980036417, 16.8288370033, 17.2743636309, 15.9754000962, 
                 14.5952468464, 14.9124907599, 14.4373360429, 14.0162194209, 13.765833739, 10.585919907, 
                 8.94777710199, 3.82560434687, -2.88635637185, -7.58604812865, -10.0714002366, -10.292867558, 
                 -10.1427735622, -10.63666237, -10.8981355703, -12.1906796316, -12.5912225387, -12.9529943226, 
                 -12.8533949897, -11.6929638382, -13.6873233405, -12.492016025, -12.7775621703]

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xStep, yStep, 'step')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 6.25, 3)
        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xStep, yStep, 'stepc')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 6.338455, 4)
        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xStep, yStep, 'stepm')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 5.49656, 4)

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xStep, yStep, 'stepssa')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 6.25, 3)
        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xStep, yStep, 'stepcssa')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 6.36096, 4)
        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xStep, yStep, 'stepmssa')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 6.3678, 4)

        xNoisyGauss = [ -5.0, -4.9, -4.8, -4.7, -4.6, -4.5, -4.4, -4.3, -4.2, -4.1, -4.0, -3.9, -3.8, -3.7,
                        -3.6, -3.5, -3.4, -3.3, -3.2, -3.1, -3.0, -2.9, -2.8, -2.7, -2.6, -2.5, -2.4, -2.3,
                        -2.2, -2.1, -2.0, -1.9, -1.8, -1.7, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1.0, -0.9,
                        -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                        0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3,
                        2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0,
                        4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0]

        yNoisyGauss = [0.0299147957547, .0168968636839,0.0145305261865,0.0306594896256,0.046335616252,0.00920741233747,0.00331724298224,
                       0.0203503190909,0.00123096854558,0.0318488276838,0.0173356288839,0.0273562413695,0.0178579590509,0.0143894191057,
                       .0255538820742,0.0310892181983,0.0150783725347,0.0191122737592,0.0487901438742,0.0175936469785,0.038682823054,
                       0.0372402539836,0.00921153292341,0.033558334358,0.0459610547927,0.0425260231937,0.0508766820508,0.0744637574022,
                       0.0720808295356,0.0878253201221,0.100399806851,0.0787165563411,0.0810949160214,0.132047325028,0.121007579296,
                       0.141921831357,0.190961819975,0.177911108281,0.198357909089,0.247150221877,0.265818718392,0.293427173383,
                       0.298179329616,0.35846981134,0.342494387515,0.352795882445,0.415925459061,0.388352917228,0.412810506375,
                       0.420419140245,0.411610324772,0.403501250267,0.435998838112,0.394319432585,0.378976465578,0.401841879225,
                       0.375207006284,0.359740415467,0.335141039704,0.291289150217,0.273846493299,0.241130108697,0.203804166004,
                       0.185181236659,0.182915802388,0.132053481055,0.14413810589,0.128147658334,0.0818619552257,0.0953306252548,
                       0.0981032703333,0.0675792502097,0.0446618078713,0.0358566328542,0.0459994339,0.0488523349758,0.0180195757756,
                       0.0106551224445,0.0445115136198,0.0190188486393,0.00833806392824,0.0362300534186,0.0398946125237,0.0191328682554,
                       0.00747828335653,0.0108836352256,0.0431935243891,0.0377918546986,0.0446413393484,0.0048989901671,0.017830714998,
                       0.0438412039254,0.029357193764,0.0175577280098,0.00604122347099,0.029937194221,0.000334614207852,0.0123354699032,
                       0.00833822923928,0.0151228204788,0.040092423947]


        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xNoisyGauss, yNoisyGauss, 'peak')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 0.2, 4)

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xNoisyGauss, yNoisyGauss, 'cen')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 0.011957415, 4)

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xNoisyGauss, yNoisyGauss, 'cms')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, -0.01465730, 4)


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

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xArr, yArr, 'stepssa')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, -2.1298828125, 4)

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xArr, yArr, 'stepcssa')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, -1.980878, 4)

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xArr, yArr, 'stepmssa')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, -1.992848, 4)

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( [1, 2,3], [4, 5, 6], 'peak')
        self.assertTrue( message, 'Not enough scan data points. Please scan over at least 9 points!')

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( [1,2,3], [ 5, 6], 'peak')
        self.assertTrue( message, 'Error: Input vectors are not of identical length!')


        yNoisyGauss = [ -yNoisyGauss[i] for i in range( len( yNoisyGauss))]

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xNoisyGauss, yNoisyGauss, 'dip')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 0.2, 4)

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xNoisyGauss, yNoisyGauss, 'dipc')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 0.0119574157, 4)

        (message, xpos, xpeak, xcms, xcen) = HasyUtils.fastscananalysis( xNoisyGauss, yNoisyGauss, 'dipm')
        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, -0.0146573, 4)

        return 



if __name__ == "__main__":
    unittest.main()
