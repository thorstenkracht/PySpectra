#!/usr/bin/env python
'''
this Gui uses PySpectra to 
  - display some data, aka scans
  - use a cursor
  - displays scans or single scans
'''
import sys, os, argparse, math, PyTango, time
#from PyQt4 import QtGui, QtCore
from taurus.external.qt import QtGui 
from taurus.external.qt import QtCore
import taurus
import numpy as np
import HasyUtils
import PySpectra as pysp

win = None
ACTIVITY_SYMBOLS = ['|', '/', '-', '\\', '|', '/', '-', '\\'] 
updateTime = 0.5

fileList = None
fileDict = None

def handleFileCallBack( self, fileName): 
    if os.path.isdir( fileName):
        os.chdir( fileName)
        if self is not None:
            self.fillFiles()
    elif fileName.endswith( ".fio") or fileName.endswith( ".dat"):
        pysp.cls()
        pysp.delete()
        pysp.read( fileName)
    else:
        if self is not None:
            self.logWidget.append(  "make_cb_files: bad fileName %s" % fileName)
        return 

def nextFile( fileName): 
    for i in range( len( fileList)):
        if fileName == fileList[i]:
            i = i + 1
            if i < len( fileList):
                return fileDict[fileList[i]]
            else:
                return fileDict[fileList[0]]
    return fileDict[fileList[0]]

def prevFile( fileName): 
    for i in range( len( fileList)):
        if fileName == fileList[i]:
            i = i - 1
            if i > -1:
                return fileDict[fileList[i]]
            else:
                return fileDict[fileList[-1]]
    return fileList[0]
                    
class QPushButtonTK( QtGui.QPushButton):
    mb1 = QtCore.pyqtSignal()
    mb2 = QtCore.pyqtSignal()
    mb3 = QtCore.pyqtSignal()

    def __init__( self, *args, **kwargs):
        QtGui.QWidget.__init__( self, *args, **kwargs)

    def mousePressEvent( self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mb1.emit()
        elif event.button() == QtCore.Qt.MiddleButton:
            self.mb2.emit()
        elif event.button() == QtCore.Qt.RightButton:
            self.mb3.emit()

    def keyPressEvent(self, event):
        key = event.key()
        if key == 32: 
            handleFileCallBack( None, str( self.text()))
            pysp.display()
            return 

        if key == QtCore.Qt.Key_Left:
            print('Left Arrow Pressed')
        elif key == QtCore.Qt.Key_Right:
            print('Right Arrow Pressed')
        elif key == QtCore.Qt.Key_Up:
            obj = prevFile( str(self.text()))
            obj.setFocus()
            print 'Up Arrow Pressed', obj.text()
        elif key == QtCore.Qt.Key_Down:
            obj = nextFile( str(self.text()))
            obj.setFocus()
            print 'Down Arrow Pressed', obj.text()
        else:
            print "QPush.keyPressEvent", key, self.text()
#
#
#
class ScanAttributes( QtGui.QMainWindow):
    def __init__( self, parent = None, name = None):
        super( ScanAttributes, self).__init__( parent)
        self.parent = parent

        if name is None:
            raise ValueError( "pyspFio.ScanAttributes: name not specified")
        self.name = name
        self.scan = pysp.getScan( self.name)
        self.setWindowTitle( "ScanAttributes")
        #geo = QtGui.QDesktopWidget().screenGeometry(-1)
        # size
        #self.setGeometry( geo.width() - 680, 30, 650, 500)
        self.prepareWidgets()

        self.menuBar = QtGui.QMenuBar()
        self.setMenuBar( self.menuBar)
        self.prepareMenuBar()

        #
        # Status Bar
        #
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar( self.statusBar)
        self.prepareStatusBar()

        self.paused = False
        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect( self.cb_refreshMain)
        self.updateTimer.start( int( updateTime*1000))
        self.show()
        
    def prepareWidgets( self):
        w = QtGui.QWidget()
        #
        # start with a vertical layout
        #
        self.layout_v = QtGui.QVBoxLayout()
        w.setLayout( self.layout_v)
        self.setCentralWidget( w)
        hBox = QtGui.QHBoxLayout()
        #
        # name
        #
        hBox.addWidget( QtGui.QLabel( "Name"))
        hBox.addWidget( QtGui.QLabel( self.name))
        self.layout_v.addLayout( hBox)
        #
        # doty
        #
        hBox = QtGui.QHBoxLayout()
        hBox.addWidget( QtGui.QLabel( "DOTY"))
        self.w_dotyCheckBox = QtGui.QCheckBox()
        self.w_dotyCheckBox.setChecked( self.scan.doty)
        self.w_dotyCheckBox.setToolTip( "x-axis is day-of-the-year")
        hBox.addWidget( self.w_dotyCheckBox) 
        self.layout_v.addLayout( hBox)

        self.w_dotyCheckBox.stateChanged.connect( self.cb_dotyChanged)

    #
    # the menu bar
    #
    def prepareMenuBar( self): 

        self.fileMenu = self.menuBar.addMenu('&File')

        self.exitAction = QtGui.QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect( sys.exit)
        self.fileMenu.addAction( self.exitAction)

        #
        # the activity menubar: help and activity
        #
        self.menuBarActivity = QtGui.QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarActivity, QtCore.Qt.TopRightCorner)

        #
        # Help menu (bottom part)
        #
        self.helpMenu = self.menuBarActivity.addMenu('Help')
        self.widgetAction = self.helpMenu.addAction(self.tr("Widget"))
        self.widgetAction.triggered.connect( self.cb_helpWidget)

        self.activityIndex = 0
        self.activity = self.menuBarActivity.addMenu( "|")

    #
    # the status bar
    #
    def prepareStatusBar( self): 

        self.display = QtGui.QPushButton(self.tr("&Display")) 
        self.statusBar.addPermanentWidget( self.display) # 'permanent' to shift it right
        self.display.clicked.connect( self.cb_display)
        self.display.setShortcut( "Alt+d")

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( self.close)
        self.exit.setShortcut( "Alt+x")
        
    def cb_refreshMain( self):

        if self.isMinimized(): 
            return
        
        self.activityIndex += 1
        if self.activityIndex > (len( ACTIVITY_SYMBOLS) - 1):
            self.activityIndex = 0
        self.activity.setTitle( ACTIVITY_SYMBOLS[ self.activityIndex])
        self.updateTimer.stop()
        
        self.updateTimer.start( int( updateTime*1000))

    def cb_display( self): 
        pysp.cls()
        pysp.display( [self.scan.name])

    def cb_helpWidget(self):
        QtGui.QMessageBox.about(self, self.tr("Help Widget"), self.tr(
                "<h3> ScanAttributes</h3>"
                "The attributes of a scan"
                "<ul>"
                "<li> some remarks</li>"
                "</ul>"
                ))

    def cb_dotyChanged( self):
        self.scan.doty = self.w_dotyCheckBox.isChecked()

        return 
#
# ===
#
class pySpectraGui( QtGui.QMainWindow):
    '''
    the main class of the SardanaMotorMenu application
    '''
    def __init__( self, parent = None):
        super( pySpectraGui, self).__init__( parent)

        self.setWindowTitle( "PySpectraGui")
        geo = QtGui.QDesktopWidget().screenGeometry(-1)
        self.widthMax = geo.width()
        self.heighthMax = geo.height()
        # size
        self.setGeometry( geo.width() - 680, 30, 650, 500)

        # used by cb_postscript
        self.lastFileWritten = None

        self.baseFiles = None
        self.baseScans = None
        self.scanList = None
        self.scanAttributes = None

        self.prepareWidgets()

        self.menuBar = QtGui.QMenuBar()
        self.setMenuBar( self.menuBar)
        self.prepareMenuBar()

        #
        # Status Bar
        #
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar( self.statusBar)
        self.prepareStatusBar()

        self.paused = False
        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect( self.cb_refreshMain)
        self.updateTimer.start( int( updateTime*1000))
        #self.installEventFilter( self)

        #self.resize( 600, 600)

    #def keyPressEvent(self, event):

    #key = event.key()

    #   if key == QtCore.Qt.Key_Left:
    #       print('Left Arrow Pressed')

    def eventFilter(self, obj, event):
        print "", repr( event), event.type()
        print "   ", dir( event)
        #
        # Only watch for specific slider keys.
        # Everything else is pass-thru
        #
        if obj is self.scrollAreaFiles and event.type() == event.KeyPress:
            key = event.key()
            if key == QtCore.Qt.Key_Up:
                return True
            elif key == QtCore.Qt.Key_Down:
                return True
            elif key == QtCore.Qt.Key_Right:
                self.cb_cursorRight()
                return True
            elif key == QtCore.Qt.Key_Left:
                self.cb_cursorLeft()
                return True
            return False
        return False

    #
    # the central widgets
    #
    def prepareWidgets( self):
        w = QtGui.QWidget()
        #
        # start with a vertical layout
        #
        self.layout_v = QtGui.QVBoxLayout()
        w.setLayout( self.layout_v)
        self.setCentralWidget( w)

        #
        # scroll areas: left: file view, right: scans
        #
        hBox = QtGui.QHBoxLayout()

        self.scrollAreaFiles = QtGui.QScrollArea()
        hBox.addWidget( self.scrollAreaFiles)

        self.fillFiles()

        self.scrollAreaScans = QtGui.QScrollArea()
        hBox.addWidget( self.scrollAreaScans)

        #self.fillScans()

        self.vBoxScans = QtGui.QVBoxLayout()
        self.baseScans = QtGui.QWidget()
        self.baseScans.setLayout( self.vBoxScans)

        self.scrollAreaScans.setWidget( self.baseScans)
        self.layout_v.addLayout( hBox)
        #
        # the log widget
        #
        self.logWidget = QtGui.QTextEdit()
        self.logWidget.setMaximumHeight( 100)
        self.logWidget.setReadOnly( 1)
        self.layout_v.addWidget( self.logWidget)

        #
        # the lineEdit line
        #
        hBox = QtGui.QHBoxLayout()
        self.lineEdit = QtGui.QLineEdit()
        hBox.addWidget( self.lineEdit)
        self.layout_v.addLayout( hBox)

        QtCore.QObject.connect( self.lineEdit, 
                                QtCore.SIGNAL("returnPressed()"),self.cb_lineEdit)

        hBox = QtGui.QHBoxLayout()

        hBox.addStretch()            

        self.prev = QtGui.QPushButton(self.tr("&Prev"))
        hBox.addWidget( self.prev)
        self.prev.clicked.connect( self.cb_prev)
        self.prev.setShortcut( "Alt+p")

        self.all = QtGui.QPushButton(self.tr("&All"))
        hBox.addWidget( self.all)
        self.all.clicked.connect( self.cb_all)
        self.all.setShortcut( "Alt+a")

        self.next = QtGui.QPushButton(self.tr("&Next"))
        hBox.addWidget( self.next)
        self.next.clicked.connect( self.cb_next)
        self.next.setShortcut( "Alt+n")

        hBox.addStretch()            

        self.layout_v.addLayout( hBox)

    def cb_refreshMain( self):

        if self.isMinimized(): 
            return
        
        self.activityIndex += 1
        if self.activityIndex > (len( ACTIVITY_SYMBOLS) - 1):
            self.activityIndex = 0
        self.activity.setTitle( ACTIVITY_SYMBOLS[ self.activityIndex])
        self.updateTimer.stop()
        #
        # the scan layout is updated
        #   - nothing has been created before self.scanList == None
        #   - the current scanList and the displayed scanList are different
        #
        scanList = pysp.getScanList()[:]
        
        flagUpdate = False
        if self.scanList is None:
            flagUpdate = True
            if self.baseScans is not None:
                self.baseScans.close()
        else:
            if len( scanList) != len( self.scanList):
                flagUpdate = True
            else:
                for i in range( len( scanList)):
                    if scanList[i] != self.scanList[i]:
                        flagUpdate = True
                        break

        if not flagUpdate: 
            self.updateTimer.start( int( updateTime*1000))
            return 
       
        self.scanList = scanList
        if self.baseScans is not None:
            self.baseScans.close()

        if len( self.scanList) == 0:
            self.updateTimer.start( int( updateTime*1000))
            return 
            
        self.vBoxScans = QtGui.QVBoxLayout()
        self.baseScans = QtGui.QWidget()
        self.baseScans.setLayout( self.vBoxScans)

        if len( self.scanList) > 0:
            if self.scanList[0].fileName is not None:
                self.vBoxScans.addWidget( QtGui.QLabel( self.scanList[0].fileName))
        

        for scan in self.scanList:
            btn = QPushButtonTK( scan.name)
            btn.setStyleSheet( "QPushButton { text-align: left}")
            btn.mb1.connect( self.make_cb_scan( scan.name))
            self.vBoxScans.addWidget( btn)

        self.scrollAreaScans.setWidget( self.baseScans)
        
        self.updateTimer.start( int( updateTime*1000))

   
    def make_cb_files( self, fileName):
        def f():
            handleFileCallBack( self, fileName)
            if self.dotyAction.isChecked():
                for elm in pysp.getScanList(): 
                    elm.doty = True
            pysp.display()

            return 
        return f

    def fillFiles( self):
        global fileList, fileDict
        if self.baseFiles is not None:
            self.baseFiles.destroy( True, True)
            self.vBoxFiles = None

        self.vBoxFiles = QtGui.QVBoxLayout()

        self.baseFiles = QtGui.QWidget()
        self.baseFiles.setLayout( self.vBoxFiles)


        self.vBoxFiles.addWidget( QtGui.QLabel( os.getcwd()))

        btn = QPushButtonTK( "../")
        btn.setStyleSheet( "QPushButton { text-align: left}")
        btn.mb1.connect( self.make_cb_files( "../"))
        self.vBoxFiles.addWidget( btn)
        lst = os.listdir( "./")
        lst.sort()
        
        fileList = []
        fileDict = {}
        for file in lst:
            if file.endswith( ".fio") or file.endswith( ".dat"):
                btn = QPushButtonTK( file)
                btn.setStyleSheet( "QPushButton { text-align: left}")
                btn.mb1.connect( self.make_cb_files( file))
                self.vBoxFiles.addWidget( btn)
                fileList.append( file)
                fileDict[ file] = btn
            elif file.startswith( "."):
                continue
            elif os.path.isdir( file):
                btn = QPushButtonTK( file)
                btn.setStyleSheet( "QPushButton { text-align: left}")
                btn.mb1.connect( self.make_cb_files( file))
                self.vBoxFiles.addWidget( btn)
                fileList.append( file)
                fileDict[ file] = btn
        self.scrollAreaFiles.setWidget( self.baseFiles)
        #self.scrollAreaFiles.setFocusPolicy( QtCore.Qt.StrongFocus)


    def make_cb_scan( self, name):
        def f():
            pysp.cls()
            pysp.display( [name])
            #if self.scanAttributes is not None:
            #    self.scanAttributes.close()
            #self.scanAttributes = ScanAttributes( self, name)
            return 
        return f

    def cb_all( self): 
        pysp.cls()
        pysp.display()

    def cb_prev( self): 
        scan = pysp.prevScan()
        pysp.cls()
        pysp.display( [ scan.name])

    def cb_next( self): 
        scan = pysp.nextScan()
        pysp.cls()
        pysp.display( [ scan.name])

    def cb_lineEdit( self): 
        pysp.ipython.ifc.command( str(self.lineEdit.text()))
        self.lineEdit.clear()
    #
    # the menu bar
    #
    def prepareMenuBar( self): 
        #
        # file
        #
        self.fileMenu = self.menuBar.addMenu('&File')

        self.writeFileAction = QtGui.QAction('Write .fio file', self)        
        self.writeFileAction.setStatusTip('Write .fio file')
        self.writeFileAction.triggered.connect( self.cb_writeFile)
        self.fileMenu.addAction( self.writeFileAction)

        self.utilsMenu = self.menuBar.addMenu('&Utils')

        self.derivativeAction = QtGui.QAction('Derivative', self)        
        self.derivativeAction.triggered.connect( self.cb_derivative)
        self.utilsMenu.addAction( self.derivativeAction)

        self.antiderivativeAction = QtGui.QAction('AntiDerivative', self)        
        self.antiderivativeAction.triggered.connect( self.cb_antiderivative)
        self.utilsMenu.addAction( self.antiderivativeAction)

        self.y2myAction = QtGui.QAction('Y -> -Y', self)        
        self.y2myAction.triggered.connect( self.cb_y2my)
        self.utilsMenu.addAction( self.y2myAction)

        self.ssaAction = QtGui.QAction('SSA', self)        
        self.ssaAction.triggered.connect( self.cb_ssa)
        self.utilsMenu.addAction( self.ssaAction)
        #
        # options
        #
        self.optionsMenu = self.menuBar.addMenu('&Options')

        self.dotyAction = QtGui.QAction('DOTY', self, checkable = True)        
        self.dotyAction.triggered.connect( self.cb_doty)
        self.optionsMenu.addAction( self.dotyAction)
        #
        # scan lists
        #
        self.scanListsMenu = self.menuBar.addMenu('&ScanLists')

        self.sl1Action = QtGui.QAction('1 Scan', self)        
        self.sl1Action.triggered.connect( self.cb_sl1)
        self.scanListsMenu.addAction( self.sl1Action)

        self.sl2Action = QtGui.QAction('5 Scans', self)        
        self.sl2Action.triggered.connect( self.cb_sl2)
        self.scanListsMenu.addAction( self.sl2Action)

        self.sl3Action = QtGui.QAction('10 Scans', self)        
        self.sl3Action.triggered.connect( self.cb_sl3)
        self.scanListsMenu.addAction( self.sl3Action)

        self.sl4Action = QtGui.QAction('Gauss Scan', self)        
        self.sl4Action.triggered.connect( self.cb_sl4)
        self.scanListsMenu.addAction( self.sl4Action)

        self.exitAction = QtGui.QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect( sys.exit)
        self.fileMenu.addAction( self.exitAction)

        #
        # the activity menubar: help and activity
        #
        self.menuBarActivity = QtGui.QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarActivity, QtCore.Qt.TopRightCorner)

        #
        # Help menu (bottom part)
        #
        self.helpMenu = self.menuBarActivity.addMenu('Help')
        self.widgetAction = self.helpMenu.addAction(self.tr("Widget"))
        self.widgetAction.triggered.connect( self.cb_helpWidget)

        self.activityIndex = 0
        self.activity = self.menuBarActivity.addMenu( "|")
    #
    # the status bar
    #
    def prepareStatusBar( self): 

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( sys.exit)
        self.exit.setShortcut( "Alt+x")

    def cb_doty( self):
        lst = pysp.getScanList()
        if self.dotyAction.isChecked():
            for elm in lst:
                elm.doty = True
        else:
            for elm in lst:
                elm.doty = False
        pysp.cls()
        pysp.display()

    def cb_derivative( self):
        displayList = pysp.getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append(  "cb_derivative: expecting 1 displayed scan")
            return 
        pysp.derivative( displayList[0].name)

    def cb_antiderivative( self):
        displayList = pysp.getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append(  "cb_antiderivative: expecting 1 displayed scan")
            return 
        pysp.antiderivative( displayList[0].name)

    def cb_y2my( self):
        displayList = pysp.getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append(  "cb_y2my: expecting 1 displayed scan")
            return 
        pysp.yToMinusY( displayList[0].name)

    def cb_ssa( self):
        displayList = pysp.getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append( "cb_ssa: expecting 1 displayed scan")
            return 
        scan = displayList[0]
        hsh = pysp.ssa( scan.x, scan.y)
        if hsh[ 'status'] != 1:
            self.logWidget.append( "cb_ssa: ssa failed")
            return

        scan.addText( text = "midpoint: %g" % hsh[ 'midpoint'], x = 0.05, y = 0.95, hAlign = 'left', vAlign = 'top')
        scan.addText( text = "peak-x:   %g" % hsh[ 'peak_x'], x = 0.05, y = 0.88, hAlign = 'left', vAlign = 'top')
        scan.addText( text = "cms:      %g" % hsh[ 'cms'], x = 0.05, y = 0.81, hAlign = 'left', vAlign = 'top')
        scan.addText( text = "fwhm:     %g" % hsh[ 'fwhm'], x = 0.05, y = 0.74, hAlign = 'left', vAlign = 'top')
        pysp.cls()
        pysp.display( [scan.name])

    def cb_sl1( self):
        pysp.cls()
        pysp.delete()
        t1 = pysp.Scan( name = "t1", color = 'blue', yLabel = 'sin')
        t1.y = np.sin( t1.x)
        pysp.display()

    def cb_sl2( self):
        pysp.cls()
        pysp.delete()
        t1 = pysp.Scan( name = "t1", color = 'blue', yLabel = 'sin')
        t1.y = np.sin( t1.x)
        t2 = pysp.Scan( "t2", yLabel = 'cos')
        t2.y = np.cos( t2.x)
        t3 = pysp.Scan( name = "t3", color = 'green', yLabel = 'tan')
        t3.y = np.tan( t3.x)
        t4 = pysp.Scan( name = "t4", color = 'cyan', yLabel = 'random')
        t4.y = np.random.random_sample( (len( t4.y), ))
        t5 = pysp.Scan( name = "t5", color = 'magenta', yLabel = 'x**2')
        t5.y = t5.x * t5.x
        pysp.overlay( 't5', 't3')
        pysp.display()

    def cb_sl3( self):
        pysp.cls()
        pysp.delete()
        for i in range( 10): 
            t = pysp.Scan( name = "t%d" % i, color = 'blue', yLabel = 'rand')
            t.y = np.random.random_sample( (len( t.x), ))

    def cb_sl4( self):
        '''
        gauss scan
        '''
        pysp.cls()
        pysp.delete()
        g = pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
        mu = 0.
        sigma = 1.
        g.y = 1/(sigma * np.sqrt(2 * np.pi)) * \
              np.exp( - (g.y - mu)**2 / (2 * sigma**2))

        pysp.display()

    def cb_writeFile( self):
        pass

    def cb_helpWidget(self):
        QtGui.QMessageBox.about(self, self.tr("Help Widget"), self.tr(
                "<h3> PySpectraGui</h3>"
                "The Python Spectra Gui"
                "<ul>"
                "<li> some remarks</li>"
                "</ul>"
                ))

def parseCLI():
    parser = argparse.ArgumentParser( 
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description="PySpectraGui", 
        epilog='''\
Examples:
  PySpectRAGui

    ''')
    # parser.add_argument('-n', dest='np', default = 2000, help='the no. of points per plot')

    args = parser.parse_args()

    return args


def main():
    global win
    args = parseCLI()
    sys.argv = []
    
    if os.getenv( "DISPLAY") != ':0':
        QtGui.QApplication.setStyle( 'Cleanlooks')

    (app, win) = pysp.initGraphic()

    #app = QtGui.QApplication(sys.argv)

    o = pySpectraGui()
    o.show()

    #import sys
    #sys.path.append( '/home/kracht/Misc/Sardana/hasyutils/HasyUtils')

    import pyspSpectraDoor

    localDoors = HasyUtils.getLocalDoorNames()

    doorName = localDoors[0]

    try:
        door = taurus.Device( doorName)
    except Exception, e:
        print "SardanaMonitor.main: trouble connecting to door", doorName
        print repr( e)
        sys.exit(255)


    #pysp.cls()
    #pysp.delete()

    #square = pysp.Scan( name = 'square', xMin = 0., xMax = 1.0, nPts = 101, autorangeX = True)
    #for i in range( square.nPts): 
    #    square.setX( i, i/10.)
    #    square.setY( i, i*i/100.)
    #    pysp.display()
    #    time.sleep( 0.1)

    try:
        sys.exit( app.exec_())
    except Exception, e:
        print repr( e)

if __name__ == "__main__":
    main()
    

