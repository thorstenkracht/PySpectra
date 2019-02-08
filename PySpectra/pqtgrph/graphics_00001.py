#!/usr/bin/env python

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import time

QApp = None
win = None

paused = False

def initGraphic():
    global QApp
    global win

    if QApp is not None: 
        return 

    pg.setConfigOption( 'background', 'w')
    pg.setConfigOption( 'foreground', 'k')
    QApp = pg.mkQApp()

    win = pg.GraphicsWindow( title="PySpectra Application")
    win.clear()

    
def displaySingle( scan): 
    if QApp is None: 
        initGraphic()

    plotWidget = win.addPlot()
    plotWidget.showGrid( x = True, y = True)
    plotWidget.setTitle( title = "Dies ist ein Titel")
    plotWidget.enableAutoRange( x = True, y = True)
    plotWidget.clear()
    plotWidget.plot( scan.x, scan.y, pen = (255, 0, 0))

    print "+++ here we go-11"
    QApp.processEvents()
    time.sleep(0.1)
    QApp.processEvents()
    #time.sleep(5)
    print "+++ END"
    return


class Application( object):
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if Application.__instance == None:
            Application()
        return Application.__instance 

    def __init__(self):
        if Application.__instance != None:
            raise Exception("Application class is a singleton!")
        else:
            Application.__instance = self    
            self.QApp = QtGui.QApplication.instance()
            if self.QApp is None:
                pg.setConfigOption( 'background', 'w')
                pg.setConfigOption( 'foreground', 'k')
                self.QApp = pg.mkQApp()
            self.win = pg.GraphicsWindow( title="PySpectra Application")
            self.win.clear()
            self.createBottomLine(1, 1)

    def createBottomLine( self, nrow, ncol):

        self.bottomLabel = self.win.addLabel( "", row= int(nrow + 1), col=0, colspan = int(ncol))

        self.pausedBtnProxy = QtGui.QGraphicsProxyWidget()
        self.pausedBtn = QtGui.QPushButton( "Pause")
        self.pausedBtnProxy.setWidget( self.pausedBtn)
        self.bottomLayout = self.win.addLayout( row=int(nrow + 2), col = 0)
        self.bottomLayout.addItem( self.pausedBtnProxy)

        self.exitBtnProxy = QtGui.QGraphicsProxyWidget()
        self.exitBtn = QtGui.QPushButton( "Exit")
        self.exitBtnProxy.setWidget( self.exitBtn)
        self.bottomLayout.addItem( self.exitBtnProxy)

        self.pausedBtn.clicked.connect( self.pausedFunc)
        self.exitBtn.clicked.connect( self.exitFunc)

    def pausedFunc( self): 
        global paused
        if not paused:
            paused = True
        else:
            paused = False

    def exitFunc( self): 
        sys.exit( 0)
        
class Display():
    def __init__( self):
        self.app = Application.getInstance()

    def displaySlot( self, scan):

        #self.plotWidget = self.app.win.addPlot( row = 1, col = 1)
        self.plotWidget = self.app.win.addPlot( row = 2, col = 3)
        print str(dir(self.plotWidget.plot))
        self.plotWidget.showGrid( x = True, y = True)
        self.plotWidget.setTitle( title = "Dies ist ein Titel")
        self.plotWidget.enableAutoRange( x = True, y = True)
        self.plotWidget.clear()
        a = self.plotWidget.plot( scan.x,
                                  scan.y, pen = (255, 0, 0))
        print str(dir(a))

        print "+++ here we go-11"
        self.app.QApp.processEvents()
        time.sleep(0.1)
        self.app.QApp.processEvents()
        #time.sleep(5)
        print "+++ END"
        return
    
        xMin = 0.
        xMax = 6.
        xDelta = 0.1
        x = np.arange( xMin, xMax, xDelta)
        t = np.tan(2*np.pi*x)
        tan = self.app.win.addPlot( row = 2, col = 1)
        tan.clear()
        tan.showGrid( x = True, y = True)
        tan.setTitle( title = "The tan() Function")
        tan.setLabel( 'left', 'tan')
        tan.setLabel( 'bottom', 'phase')
        tan.enableAutoRange( x = False, y = True)
        tan.setXRange( xMin - 0.25, xMax + 0.25)
        tan.plot( x, t, pen = ( 0, 0, 255))

        
        return

        

