#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/ipython/testIFC.py testIFC.test_create
python ./test/ipython/testIFC.py testIFC.test_pdf
python ./test/ipython/testIFC.py testIFC.test_createText
python ./test/ipython/testIFC.py testIFC.test_wsViewPort
python ./test/ipython/testIFC.py testIFC.test_overlay
python ./test/ipython/testIFC.py testIFC.test_setText
python ./test/ipython/testIFC.py testIFC.test_setX_Y
python ./test/ipython/testIFC.py testIFC.test_setXY
python ./test/ipython/testIFC.py testIFC.test_y2my
python ./test/ipython/testIFC.py testIFC.test_delete
python ./test/ipython/testIFC.py testIFC.test_execHsh
python ./test/ipython/testIFC.py testIFC.test_execHshSetPixelImage
python ./test/ipython/testIFC.py testIFC.test_execHshSetPixelWorld
python ./test/ipython/testIFC.py testIFC.test_execHshMonitorSetPixelWorld
python ./test/ipython/testIFC.py testIFC.test_execHshMonitorScan
'''
import sys, time, os, math
import numpy as np
import unittest
import PySpectra
import PySpectra.dMgt.GQE as _gqe
import PySpectra.ipython.ifc as _ifc
import PySpectra.misc.zmqIfc as _zmqIfc


def mandelbrot( c, maxiter):
    z = c
    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return 0

class testIFC( unittest.TestCase):

    @classmethod
    def setUpClass( testIFC):
        pass

    @classmethod
    def tearDownClass( testIFC): 
        PySpectra.close()

    def test_create1( self):
        print "testIFC.test_create1"
        PySpectra.cls()
        _gqe.delete()
        _ifc.command( "create s1 0 10 100")
        lst = _gqe.getGqeList()
        self.assertEqual( len( lst), 1)
        self.assertEqual( lst[0].name, "s1")
        self.assertEqual( lst[0].nPts, 100)
        self.assertEqual( lst[0].xMin, 0.)
        self.assertEqual( lst[0].xMax, 10.)
        _gqe.delete()
        print "testIFC.test_create1 DONE"

    def test_create( self):

        print "testIFC.test_create"

        PySpectra.cls()
        _gqe.delete()
        _ifc.command( "create s1")
        lst = _gqe.getGqeList()
        self.assertEqual( len( lst), 1)
        self.assertEqual( lst[0].name, "s1")
        _ifc.command( "display s1")

        _ifc.command( "derivative s1")
        lst = _gqe.getGqeList()
        self.assertEqual( lst[1].name, "s1_derivative")
        self.assertEqual( len( lst), 2)

        _ifc.command( "antiderivative s1")
        lst = _gqe.getGqeList()
        self.assertEqual( lst[2].name, "s1_antiderivative")
        self.assertEqual( len( lst), 3)

        _ifc.command( "delete s1")
        _ifc.command( "delete s1_derivative")
        _ifc.command( "delete s1_antiderivative")
        lst = _gqe.getGqeList()
        self.assertEqual( len( lst), 0)
        print "testIFC.test_create DONE"

    def test_cls( self):

        print "testIFC.test_cls"
        _ifc.command( "cls")
        print "testIFC.test_cls DONE"

    def test_show( self):

        print "testIFC.test_show"

        PySpectra.cls()
        _gqe.delete()
        _ifc.command( "create s1")
        _ifc.command( "show s1")
        print "testIFC.test_show DONE"

    def test_title( self): 
        print "testIFC.test_title"
        PySpectra.cls()
        _gqe.delete()
        _ifc.command( "create s1")
        _ifc.command( "setTitle hallo")

        ret = _gqe.getTitle()
        self.assertEqual( ret, "hallo")
        print "testIFC.test_title DONE"

    def test_comment( self): 
        print "testIFC.test_comment"
        PySpectra.cls()
        _gqe.delete()
        _ifc.command( "setComment AComment")

        ret = _gqe.getComment()
        self.assertEqual( ret, "AComment")
        print "testIFC.test_comment DONE"

    def test_y2my( self): 
        print "testIFC.test_y2my"
        PySpectra.cls()
        _gqe.delete()
        _ifc.command( "create s1")
        _ifc.command( "y2my s1")

        lst = _gqe.getGqeList()
        self.assertEqual( lst[1].name, "s1_y2my")
        self.assertEqual( len( lst), 2)
        print "testIFC.test_y2my DONE"

    def test_wsViewPort( self): 
        print "testIFC.test_wsViewPort"
        PySpectra.cls()
        _gqe.delete()
        _ifc.command( "setWsViewport DINA4")
        PySpectra.procEventsLoop( 1)
        _ifc.command( "setWsViewport DINA4P")
        PySpectra.procEventsLoop( 1)
        _ifc.command( "setWsViewport DINA5")
        PySpectra.procEventsLoop( 1)
        _ifc.command( "setWsViewport DINA5P")
        PySpectra.procEventsLoop( 1)
        _ifc.command( "setWsViewport DINA6")
        PySpectra.procEventsLoop( 1)
        _ifc.command( "setWsViewport DINA6P")
        PySpectra.procEventsLoop( 1)
        print "testIFC.test_wsViewPort DONE"

    def test_overlay( self): 
        print "testIFC.test_overlay"
        PySpectra.cls()
        _gqe.delete()
        _ifc.command( "create s1")
        _ifc.command( "create s2")
        _ifc.command( "overlay s1 s2")
        s1 = _gqe.getGqe( 's1')
        self.assertEqual( s1.overlay, "s2")
        print "testIFC.test_overlay DONE"

    def test_pdf( self): 
        print "testIFC.test_pdf"
        _ifc.command( "cls")
        _ifc.command( "delete")
        _ifc.command( "create s1")
        _ifc.command( "createPDF testPDF")
        self.assertEqual( os.path.exists( 'testPDF.pdf'), True)
        os.remove( 'testPDF.pdf') 
        print "testIFC.test_pdf DONE"

    def test_setText( self): 
        print "testIFC.test_setText"
        _ifc.command( "cls")
        _ifc.command( "delete")
        _ifc.command( "create s1")
        o = _gqe.getGqe( "s1")
        self.assertEqual( len( o.textList), 0)
        _ifc.command( "setText s1 comment string \"this is a comment\" x 0.05 y 0.95 hAlign left vAlign top color blue")
        self.assertEqual( len( o.textList), 1)
        self.assertEqual( o.textList[0].text, "this is a comment")
        self.assertEqual( o.textList[0].x, 0.05)
        self.assertEqual( o.textList[0].y, 0.95)
        self.assertEqual( o.textList[0].hAlign, 'left')
        self.assertEqual( o.textList[0].vAlign, 'top')
        self.assertEqual( o.textList[0].color, 'blue')
        
        _ifc.command( "display")
        PySpectra.display()
        PySpectra.procEventsLoop( 1)
        print "testIFC.test_setText DONE"

    def test_setX_Y( self): 
        import random

        print "testIFC.test_setX_Y"
        _ifc.command( "cls")
        _ifc.command( "delete")

        max = 50
        _ifc.command( "create s1 0 10 %d" % max)

        s1 = _gqe.getGqe( "s1")
        self.assertEqual( s1.currentIndex, 49)
        self.assertEqual( s1.lastIndex, 0)
        _ifc.command( "display")
        self.assertEqual( s1.lastIndex, (max - 1))

        for i in range( max): 
            _ifc.command( "setY s1 %d %g" % ( i, random.random()*10))
            _ifc.command( "setX s1 %d %g" % ( i, float(i)/100.))
            self.assertEqual( s1.currentIndex, i)
            _ifc.command( "display")
            time.sleep(0.1)

        PySpectra.procEventsLoop( 1)
        print "testIFC.test_setX_Y DONE"

    def test_setXY( self): 
        import random

        print "testIFC.test_setXY"
        _ifc.command( "cls")
        _ifc.command( "delete")
        max = 20
        _ifc.command( "setTitle \"A title\"")
        _ifc.command( "setComment \"A comment\"")
        _ifc.command( "create s1 0 10 %d" % max)

        for i in range( max): 
            _ifc.command( "setXY s1 %d %s %s" % ( i, float(i)/100., random.random()*10))
            _ifc.command( "display")
            time.sleep(0.1)
            
        PySpectra.procEventsLoop( 1)
        print "testIFC.test_setXY DONE"

    def test_delete( self): 

        print "testIFC.test_delete"
        _ifc.command( "cls")
        _ifc.command( "delete")
        max = 20
        _ifc.command( "setTitle \"s1,s2,s3,s4\"")
        _ifc.command( "create s1 0 10 %d" % max)
        _ifc.command( "create s2 0 10 %d" % max)
        _ifc.command( "create s3 0 10 %d" % max)
        _ifc.command( "create s4 0 10 %d" % max)
        _ifc.command( "display")
        PySpectra.procEventsLoop( 1)
        gqeList = _gqe.getGqeList()
        self.assertEqual( len( gqeList), 4)
        self.assertEqual( gqeList[0].name, "s1")
        self.assertEqual( gqeList[1].name, "s2")
        self.assertEqual( gqeList[2].name, "s3")
        self.assertEqual( gqeList[3].name, "s4")

        _ifc.command( "cls")
        _ifc.command( "delete s2")
        _ifc.command( "setTitle \"s1,s3,s4\"")
        _ifc.command( "display")
        PySpectra.procEventsLoop( 1)
        gqeList = _gqe.getGqeList()
        self.assertEqual( len( gqeList), 3)
        self.assertEqual( gqeList[0].name, "s1")
        self.assertEqual( gqeList[1].name, "s3")
        self.assertEqual( gqeList[2].name, "s4")

        _ifc.command( "cls")
        _ifc.command( "delete s3 s4")
        _ifc.command( "setTitle \"s1\"")
        _ifc.command( "display")
        PySpectra.procEventsLoop( 1)
        gqeList = _gqe.getGqeList()
        self.assertEqual( len( gqeList), 1)
        self.assertEqual( gqeList[0].name, "s1")
        print "testIFC.test_delete DONE"


    def test_execHshScan( self): 
        import random

        print "testIFC.test_execHsh"
        ret = _zmqIfc.execHsh( { 'command': ["cls", "delete"]}) 
        self.assertEqual( ret[ 'result'], 'done')
        
        ret = _zmqIfc.execHsh( { 'command': ["setTitle \"An important title\"", 
                                              "setComment \"An interesting comment\""]}) 
        self.assertEqual( ret[ 'result'], 'done')

        max = 101
        name = "TestScan"
        ret = _zmqIfc.execHsh( {'Scan': { 'name': name,
                                          'xMin': 0., 'xMax': 100., 
                                          'yMin': 0., 'yMax': 1.,
                                          'symbol': '+','symbolColor': 'red',
                                          'symbolSize': 7, 'lineColor': 'blue',
                                          'nPts': max,
                                          'autoscaleX': False, 'autoscaleY': True}})
        self.assertEqual( ret[ 'result'], 'done')
        o = _gqe.getGqe( name)
        self.assertEqual( o.nPts, max)
        self.assertEqual( o.symbol, '+')
        self.assertEqual( o.symbolColor, 'red')
        self.assertEqual( o.symbolSize, 7)
        self.assertEqual( o.lineColor, 'blue')
        self.assertEqual( o.lastIndex, 0)
        self.assertEqual( o.currentIndex, (max - 1))
         
        for i in range( max): 
            pos = float(i)
            posY = random.random()*10
            _zmqIfc.execHsh( { 'command': ['setXY %s %d %s %s' % (name, i, repr(pos), repr(posY))]})
            _zmqIfc.execHsh( { 'command': ["display"]}) 
            self.assertEqual( o.currentIndex, i)
            time.sleep( 0.1)

        print "testIFC.test_execHsh DONE"


    def test_execHshSetPixelImage( self): 

        '''
        this examples simulates the toPyspMonitor() interface
        
        replace execHsh() by toPyspMonitor() to connect to pyspMonitor.py 
        '''
        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25
        
        #
        # do the clean-up before we start
        #
        hsh =  _zmqIfc.execHsh( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        if hsh[ 'result'] != "done":
            print "error from ['delete', 'setWsViewport DINA5S', 'cls']"
            return 
        #
        # create the image
        #
        hsh = _zmqIfc.execHsh( { 'Image': 
                                 { 'name': "MandelBrot",
                                   'xMin': xmin, 'xMax': xmax, 'width': width, 
                                   'yMin': ymin, 'yMax': ymax, 'height': height}})
        if hsh[ 'result'] != "done":
            print "error from putData", repr( hsh)
            return 
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = _zmqIfc.execHsh( { 'command': 
                                         ["setPixelImage MandelBrot %d %d %s" % ( i, j, repr( res))]})
                if hsh[ 'result'] != "done":
                    print "error from setPixel"
                    return
            _zmqIfc.execHsh( { 'command': ['cls','display']})
        _zmqIfc.execHsh( { 'command': ['cls', 'display']})
        PySpectra.procEventsLoop( 1)

        return 

    def test_execHshSetPixelWorld( self): 

        '''
        this examples simulates the toPyspMonitor() interface
        replace execHsh() by toPyspMonitor() to connect to pyspMonitor.py 
        '''
        hsh =  _zmqIfc.execHsh( { 'command': ['cls', 'delete', 'setWsViewport DINA5S']})
        if hsh[ 'result'] != "done":
            print "error from ['delete', 'setWsViewport DINA5S', 'cls']"
            return 
        
        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25
        
        #
        # create the image
        #
        hsh = _zmqIfc.execHsh( { 'Image': 
                                 { 'name': "MandelBrot",
                                   'xMin': xmin, 'xMax': xmax, 'width': width, 
                                   'yMin': ymin, 'yMax': ymax, 'height': height}})
        if hsh[ 'result'] != "done":
            print "error from Image", repr( hsh)
            return 
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = _zmqIfc.execHsh( { 'command': 
                                         ["setPixelWorld MandelBrot %g %g %s" % ( r1[i], r2[j], repr( res))]})
                if hsh[ 'result'] != "done":
                    print "error from setPixelWorld"
                    return
            _zmqIfc.execHsh( { 'command': ['cls','display']})
        _zmqIfc.execHsh( { 'command': ['cls']})
        _zmqIfc.execHsh( { 'command': ['display']})
        PySpectra.procEventsLoop( 1)

        return 

    def test_execHshMonitorSetPixelWorld( self): 

        '''
        this examples simulates the toPyspMonitor() interface
        replace execHsh() by toPyspMonitor() to connect to pyspMonitor.py 
        '''
        #
        # see, if the pyspMonitor is running. If not, return silently
        #
        hsh =  _zmqIfc.toPyspMonitor( { 'isAlive': True})
        if hsh[ 'result'] != "done":
            print "test_toPyspMonitorSetPixelWorld: no pyspMonitor running"
            return 

        hsh =  _zmqIfc.toPyspMonitor( { 'command': ['cls', 'delete', 'setWsViewport DINA5S']})
        if hsh[ 'result'] != "done":
            print "error from ['delete', 'setWsViewport DINA5S', 'cls']"
            return 
        
        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25
        
        #
        # create the image
        #
        hsh = _zmqIfc.toPyspMonitor( { 'Image': 
                                       { 'name': "MandelBrot",
                                         'xMin': xmin, 'xMax': xmax, 'width': width, 
                                         'yMin': ymin, 'yMax': ymax, 'height': height}})
        if hsh[ 'result'] != "done":
            print "error from Image", repr( hsh)
            return 
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = _zmqIfc.toPyspMonitor( { 'command': 
                                               ["setPixelWorld MandelBrot %g %g %s" % ( r1[i], r2[j], repr( res))]})
                if hsh[ 'result'] != "done":
                    print "error from setPixelWorld"
                    return
            _zmqIfc.toPyspMonitor( { 'command': ['cls','display']})
        _zmqIfc.toPyspMonitor( { 'command': ['cls']})
        _zmqIfc.toPyspMonitor( { 'command': ['display']})

        return 

    def test_toPyspMonitorScan( self): 
        import random

        print "testIFC.test_toPyspMonitorScan"
        #
        # see, if the pyspMonitor is running. If not, return silently
        #
        hsh =  _zmqIfc.toPyspMonitor( { 'isAlive': True})
        if hsh[ 'result'] != "done":
            print "test_toPyspMonitorScan: no pyspMonitor running"
            return 

        ret = _zmqIfc.toPyspMonitor( { 'command': ["cls", "delete"]}) 
        self.assertEqual( ret[ 'result'], 'done')
        
        ret = _zmqIfc.toPyspMonitor( { 'command': ["setTitle \"An important title\"", 
                                                     "setComment \"An interesting comment\""]}) 
        self.assertEqual( ret[ 'result'], 'done')

        max = 101
        name = "TestScan"
        ret = _zmqIfc.toPyspMonitor( {'Scan': { 'name': name,
                                           'xMin': 0., 'xMax': 100., 
                                           'yMin': 0., 'yMax': 1.,
                                           'symbol': '+','symbolColor': 'red',
                                           'symbolSize': 7, 'lineColor': 'blue',
                                           'nPts': max,
                                           'autoscaleX': False, 'autoscaleY': True}})
        self.assertEqual( ret[ 'result'], 'done')
         
        for i in range( max): 
            pos = float(i)
            posY = random.random()*10
            _zmqIfc.toPyspMonitor( { 'command': ['setXY %s %d %s %s' % (name, i, repr(pos), repr(posY))]})
            _zmqIfc.toPyspMonitor( { 'command': ["display"]}) 
            time.sleep( 0.1)

        print "testIFC.test_toPyspMonitorScan DONE"

if __name__ == "__main__":
    unittest.main()
