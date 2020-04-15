#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/ipython/testIFC.py testIFC.test_create
python ./test/ipython/testIFC.py testIFC.test_cls
python ./test/ipython/testIFC.py testIFC.test_show
python ./test/ipython/testIFC.py testIFC.test_pdf
python ./test/ipython/testIFC.py testIFC.test_createText
python ./test/ipython/testIFC.py testIFC.test_wsViewPort
python ./test/ipython/testIFC.py testIFC.test_overlay
python ./test/ipython/testIFC.py testIFC.test_setText
python ./test/ipython/testIFC.py testIFC.test_setX_Y
python ./test/ipython/testIFC.py testIFC.test_setXY
python ./test/ipython/testIFC.py testIFC.test_y2my
python ./test/ipython/testIFC.py testIFC.test_delete
python ./test/ipython/testIFC.py testIFC.test_setArrowMotor
python ./test/ipython/testIFC.py testIFC.test_execHsh
python ./test/ipython/testIFC.py testIFC.test_execHshScan
python ./test/ipython/testIFC.py testIFC.test_execHshSetPixelImage
python ./test/ipython/testIFC.py testIFC.test_execHshSetPixelWorld
python ./test/ipython/testIFC.py testIFC.test_execHshMonitorSetPixelWorld
python ./test/ipython/testIFC.py testIFC.test_execHshMonitorScan
'''
import sys, time, os, math
import numpy as np
import unittest
import PySpectra
import PySpectra.dMgt.GQE as GQE
import PySpectra.ipython.ifc as ifc
import PySpectra.misc.zmqIfc as zmqIfc


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
        GQE.delete()
        ifc.command( "create s1 0 10 100")
        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 1)
        self.assertEqual( lst[0].name, "s1")
        self.assertEqual( lst[0].nPts, 100)
        self.assertEqual( lst[0].xMin, 0.)
        self.assertEqual( lst[0].xMax, 10.)
        GQE.delete()
        print "testIFC.test_create1 DONE"

        return 

    def test_create( self):

        print "testIFC.test_create"

        PySpectra.cls()
        GQE.delete()
        ifc.command( "create s1")
        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 1)
        self.assertEqual( lst[0].name, "s1")
        ifc.command( "display s1")

        ifc.command( "derivative s1")
        lst = GQE.getGqeList()
        self.assertEqual( lst[1].name, "s1_derivative")
        self.assertEqual( len( lst), 2)

        ifc.command( "antiderivative s1")
        lst = GQE.getGqeList()
        self.assertEqual( lst[2].name, "s1_antiderivative")
        self.assertEqual( len( lst), 3)

        ifc.command( "delete s1")
        ifc.command( "delete s1_derivative")
        ifc.command( "delete s1_antiderivative")
        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 0)
        print "testIFC.test_create DONE"

        return 

    def test_cls( self):

        print "testIFC.test_cls"
        ifc.command( "cls")
        print "testIFC.test_cls DONE"

        return 

    def test_show( self):

        print "testIFC.test_show"

        PySpectra.cls()
        GQE.delete()
        ifc.command( "create s1")
        ifc.command( "show s1")
        print "testIFC.test_show DONE"

        return 

    def test_title( self): 
        print "testIFC.test_title"
        PySpectra.cls()
        GQE.delete()
        ifc.command( "create s1")
        ifc.command( "setTitle hallo")

        ret = GQE.getTitle()
        self.assertEqual( ret, "hallo")
        print "testIFC.test_title DONE"

        return 

    def test_comment( self): 
        print "testIFC.test_comment"
        PySpectra.cls()
        GQE.delete()
        ifc.command( "setComment AComment")

        ret = GQE.getComment()
        self.assertEqual( ret, "AComment")
        print "testIFC.test_comment DONE"

        return 

    def test_y2my( self): 
        print "testIFC.test_y2my"
        PySpectra.cls()
        GQE.delete()
        ifc.command( "create s1")
        ifc.command( "y2my s1")

        lst = GQE.getGqeList()
        self.assertEqual( lst[1].name, "s1_y2my")
        self.assertEqual( len( lst), 2)
        print "testIFC.test_y2my DONE"

        return 

    def test_wsViewPort( self): 
        print "testIFC.test_wsViewPort"
        PySpectra.cls()
        GQE.delete()
        ifc.command( "setWsViewport DINA4")
        PySpectra.procEventsLoop( 1)
        ifc.command( "setWsViewport DINA4P")
        PySpectra.procEventsLoop( 1)
        ifc.command( "setWsViewport DINA5")
        PySpectra.procEventsLoop( 1)
        ifc.command( "setWsViewport DINA5P")
        PySpectra.procEventsLoop( 1)
        ifc.command( "setWsViewport DINA6")
        PySpectra.procEventsLoop( 1)
        ifc.command( "setWsViewport DINA6P")
        PySpectra.procEventsLoop( 1)
        print "testIFC.test_wsViewPort DONE"

        return 

    def test_overlay( self): 
        print "testIFC.test_overlay"
        PySpectra.cls()
        GQE.delete()
        ifc.command( "create s1")
        ifc.command( "create s2")
        ifc.command( "overlay s1 s2")
        s1 = GQE.getGqe( 's1')
        self.assertEqual( s1.overlay, "s2")
        print "testIFC.test_overlay DONE"

        return 

    def test_pdf( self): 
        print "testIFC.test_pdf"
        ifc.command( "cls")
        ifc.command( "delete")
        ifc.command( "create s1")
        ifc.command( "createPDF testPDF")
        self.assertEqual( os.path.exists( 'testPDF.pdf'), True)
        os.remove( 'testPDF.pdf') 
        print "testIFC.test_pdf DONE"

        return 

    def test_setText( self): 
        print "testIFC.test_setText"
        ifc.command( "cls")
        ifc.command( "delete")
        ifc.command( "create s1")
        o = GQE.getGqe( "s1")
        self.assertEqual( len( o.textList), 0)
        ifc.command( "setText s1 comment string \"this is a comment\" x 0.05 y 0.95 hAlign left vAlign top color blue")
        self.assertEqual( len( o.textList), 1)
        self.assertEqual( o.textList[0].text, "this is a comment")
        self.assertEqual( o.textList[0].x, 0.05)
        self.assertEqual( o.textList[0].y, 0.95)
        self.assertEqual( o.textList[0].hAlign, 'left')
        self.assertEqual( o.textList[0].vAlign, 'top')
        self.assertEqual( o.textList[0].color, 'blue')
        
        ifc.command( "display")
        PySpectra.display()
        PySpectra.procEventsLoop( 1)
        print "testIFC.test_setText DONE"

        return 

    def test_setX_Y( self): 
        import random

        print "testIFC.test_setX_Y"
        ifc.command( "cls")
        ifc.command( "delete")

        max = 50
        ifc.command( "create s1 0 10 %d" % max)

        s1 = GQE.getGqe( "s1")
        self.assertEqual( s1.currentIndex, 49)
        self.assertEqual( s1.lastIndex, -1)
        ifc.command( "display")
        self.assertEqual( s1.lastIndex, (max - 1))

        for i in range( max): 
            ifc.command( "setY s1 %d %g" % ( i, random.random()*10))
            ifc.command( "setX s1 %d %g" % ( i, float(i)/100.))
            self.assertEqual( s1.currentIndex, i)
            ifc.command( "display")
            time.sleep(0.1)

        PySpectra.procEventsLoop( 1)
        print "testIFC.test_setX_Y DONE"

        return 

    def test_setXY( self): 
        import random

        print "testIFC.test_setXY"
        ifc.command( "cls")
        ifc.command( "delete")
        max = 20
        ifc.command( "setTitle \"A title\"")
        ifc.command( "setComment \"A comment\"")
        ifc.command( "create s1 0 10 %d" % max)

        for i in range( max): 
            ifc.command( "setXY s1 %d %s %s" % ( i, float(i)/100., random.random()*10))
            ifc.command( "display")
            time.sleep(0.1)
            
        PySpectra.procEventsLoop( 1)
        print "testIFC.test_setXY DONE"
        return 

    def test_delete( self): 

        print "testIFC.test_delete"
        ifc.command( "cls")
        ifc.command( "delete")
        max = 20
        ifc.command( "setTitle \"s1,s2,s3,s4\"")
        ifc.command( "create s1 0 10 %d" % max)
        ifc.command( "create s2 0 10 %d" % max)
        ifc.command( "create s3 0 10 %d" % max)
        ifc.command( "create s4 0 10 %d" % max)
        ifc.command( "display")
        PySpectra.procEventsLoop( 1)
        gqeList = GQE.getGqeList()
        self.assertEqual( len( gqeList), 4)
        self.assertEqual( gqeList[0].name, "s1")
        self.assertEqual( gqeList[1].name, "s2")
        self.assertEqual( gqeList[2].name, "s3")
        self.assertEqual( gqeList[3].name, "s4")

        ifc.command( "cls")
        ifc.command( "delete s2")
        ifc.command( "setTitle \"s1,s3,s4\"")
        ifc.command( "display")
        PySpectra.procEventsLoop( 1)
        gqeList = GQE.getGqeList()
        self.assertEqual( len( gqeList), 3)
        self.assertEqual( gqeList[0].name, "s1")
        self.assertEqual( gqeList[1].name, "s3")
        self.assertEqual( gqeList[2].name, "s4")

        ifc.command( "cls")
        ifc.command( "delete s3 s4")
        ifc.command( "setTitle \"s1\"")
        ifc.command( "display")
        PySpectra.procEventsLoop( 1)
        gqeList = GQE.getGqeList()
        self.assertEqual( len( gqeList), 1)
        self.assertEqual( gqeList[0].name, "s1")
        print "testIFC.test_delete DONE"
        return 

    def test_setArrowMotor( self): 

        print "testIFC.test_setArrowMotor"
        ifc.command( "cls")
        ifc.command( "delete")
        max = 20
        ifc.command( "setComment \"Arrows: Current: 5, Misc: 2, SetPoint: 6\"")
        ifc.command( "create s1 0 10 %d" % max)

        gqe = GQE.getGqe( "s1")
        gqe.motorNameList = ["eh_mot66"] 

        ifc.command( "setArrowMotorCurrent s1 position 5.") 
        ifc.command( "setArrowMotorMisc s1 position 2.") 
        ifc.command( "setArrowMotorSetPoint s1 position 6.") 
        ifc.command( "display")
        PySpectra.procEventsLoop( 1)

        pos = 5
        for i in range( 20): 
            pos = 5 + float(i)*0.05
            ifc.command( "setArrowMotorCurrent s1 position %g" % pos) 
            time.sleep( 0.1)
            
        print "testIFC.test_setArrowMotor DONE"
        return 


    def test_execHshScan( self): 
        import random

        print "testIFC.test_execHsh"
        ret = zmqIfc.execHsh( { 'command': ["cls", "delete"]}) 
        self.assertEqual( ret[ 'result'], 'done')
        
        ret = zmqIfc.execHsh( { 'command': ["setTitle \"An important title\"", 
                                              "setComment \"An interesting comment\""]}) 
        self.assertEqual( ret[ 'result'], 'done')

        max = 101
        name = "TestScan"
        ret = zmqIfc.execHsh( {'Scan': { 'name': name,
                                          'xMin': 0., 'xMax': 100., 
                                          'yMin': 0., 'yMax': 1.,
                                          'symbol': '+','symbolColor': 'red',
                                          'symbolSize': 7, 'lineColor': 'blue',
                                          'nPts': max,
                                          'autoscaleX': False, 'autoscaleY': True}})
        self.assertEqual( ret[ 'result'], 'done')
        o = GQE.getGqe( name)
        self.assertEqual( o.nPts, max)
        self.assertEqual( o.symbol, '+')
        self.assertEqual( o.symbolColor, 'red')
        self.assertEqual( o.symbolSize, 7)
        self.assertEqual( o.lineColor, 'blue')
        self.assertEqual( o.lastIndex, -1)
        self.assertEqual( o.currentIndex, (max - 1))
         
        for i in range( max): 
            pos = float(i)
            posY = random.random()*10
            zmqIfc.execHsh( { 'command': ['setXY %s %d %s %s' % (name, i, repr(pos), repr(posY))]})
            zmqIfc.execHsh( { 'command': ["display"]}) 
            self.assertEqual( o.currentIndex, i)
            time.sleep( 0.1)

        print "testIFC.test_execHsh DONE"

        return 


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
        hsh =  zmqIfc.execHsh( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        if hsh[ 'result'] != "done":
            print "error from ['delete', 'setWsViewport DINA5S', 'cls']"
            return 
        #
        # create the image
        #
        hsh = zmqIfc.execHsh( { 'Image': 
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
                hsh = zmqIfc.execHsh( { 'command': 
                                         ["setPixelImage MandelBrot %d %d %s" % ( i, j, repr( res))]})
                if hsh[ 'result'] != "done":
                    print "error from setPixel"
                    return
            zmqIfc.execHsh( { 'command': ['cls','display']})
        zmqIfc.execHsh( { 'command': ['cls', 'display']})
        PySpectra.procEventsLoop( 1)

        return 

    def test_execHshSetPixelWorld( self): 

        '''
        this examples simulates the toPyspMonitor() interface
        replace execHsh() by toPyspMonitor() to connect to pyspMonitor.py 
        '''
        hsh =  zmqIfc.execHsh( { 'command': ['cls', 'delete', 'setWsViewport DINA5S']})
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
        hsh = zmqIfc.execHsh( { 'Image': 
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
                hsh = zmqIfc.execHsh( { 'command': 
                                         ["setPixelWorld MandelBrot %g %g %s" % ( r1[i], r2[j], repr( res))]})
                if hsh[ 'result'] != "done":
                    print "error from setPixelWorld"
                    return
            zmqIfc.execHsh( { 'command': ['cls','display']})
        zmqIfc.execHsh( { 'command': ['cls']})
        zmqIfc.execHsh( { 'command': ['display']})
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
        hsh =  zmqIfc.toPyspMonitor( { 'isAlive': True})
        if hsh[ 'result'] != "done":
            print "test_toPyspMonitorSetPixelWorld: no pyspMonitor running"
            return 

        hsh =  zmqIfc.toPyspMonitor( { 'command': ['cls', 'delete', 'setWsViewport DINA5S']})
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
        hsh = zmqIfc.toPyspMonitor( { 'Image': 
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
                hsh = zmqIfc.toPyspMonitor( { 'command': 
                                               ["setPixelWorld MandelBrot %g %g %s" % ( r1[i], r2[j], repr( res))]})
                if hsh[ 'result'] != "done":
                    print "error from setPixelWorld"
                    return
            zmqIfc.toPyspMonitor( { 'command': ['cls','display']})
        zmqIfc.toPyspMonitor( { 'command': ['cls']})
        zmqIfc.toPyspMonitor( { 'command': ['display']})

        return 

    def test_toPyspMonitorScan( self): 
        import random

        print "testIFC.test_toPyspMonitorScan"
        #
        # see, if the pyspMonitor is running. If not, return silently
        #
        hsh =  zmqIfc.toPyspMonitor( { 'isAlive': True})
        if hsh[ 'result'] != "done":
            print "test_toPyspMonitorScan: no pyspMonitor running"
            return 

        ret = zmqIfc.toPyspMonitor( { 'command': ["cls", "delete"]}) 
        self.assertEqual( ret[ 'result'], 'done')
        
        ret = zmqIfc.toPyspMonitor( { 'command': ["setTitle \"An important title\"", 
                                                     "setComment \"An interesting comment\""]}) 
        self.assertEqual( ret[ 'result'], 'done')

        max = 101
        name = "TestScan"
        ret = zmqIfc.toPyspMonitor( {'Scan': { 'name': name,
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
            zmqIfc.toPyspMonitor( { 'command': ['setXY %s %d %s %s' % (name, i, repr(pos), repr(posY))]})
            zmqIfc.toPyspMonitor( { 'command': ["display"]}) 
            time.sleep( 0.1)

        print "testIFC.test_toPyspMonitorScan DONE"

        return 

if __name__ == "__main__":
    unittest.main()
