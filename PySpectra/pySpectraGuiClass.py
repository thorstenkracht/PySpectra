#!/usr/bin/env python
'''

This is the main PySpectra Gui class. It is used by pyspMonitor, pyspViewer. 
Both applications select the graphics library in their first code lines. 
'''
import sys, os, argparse, math, PyTango, time
from PyQt4 import QtGui, QtCore
import numpy as np
import HasyUtils
import __builtin__

import PySpectra as pysp

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

win = None
ACTIVITY_SYMBOLS = ['|', '/', '-', '\\', '|', '/', '-', '\\'] 
updateTime = 1.0

class QListWidgetTK( QtGui.QListWidget): 
    '''
    newItemSelected is called, if a new item is selected, 
    can be a file, a directory or a scan
    '''
    def __init__( self, parent, newItemSelected): 
        QtGui.QListWidget.__init__(self)
        self.parent = parent
        self.newItemSelected = newItemSelected

    def keyPressEvent (self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == QtCore.Qt.Key_Left:
            if self.parent.filesListWidget.count() > 0:
                self.parent.filesListWidget.setFocus()
                self.parent.filesListWidget.setCurrentRow( 0)
        elif key == QtCore.Qt.Key_Right:
            if self.parent.scansListWidget.count() > 0:
                self.parent.scansListWidget.setFocus()
                self.parent.scansListWidget.setCurrentRow( 0)
        elif key == QtCore.Qt.Key_Down:
            pass
        elif key == QtCore.Qt.Key_Up:
            pass
        elif key == QtCore.Qt.Key_Return or key == 32:
            item = self.currentItem()
            self.newItemSelected( str(item.text()))
        else: 
            print "key", key

        return QtGui.QListWidget.keyPressEvent(self, eventQKeyEvent)

    def mouseReleaseEvent( self, event): 
        if event.button() == QtCore.Qt.LeftButton:
            item = self.currentItem()
            if item is not None:
                self.newItemSelected( str( item.text()))
        if event.button() == QtCore.Qt.RightButton:
            item = self.currentItem()
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)       
            else:
                item.setCheckState(QtCore.Qt.Checked)       
            if item is not None:
                self.parent.displayChecked()
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
        self.updateTimer.timeout.connect( self.cb_refreshAttr)
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
        
    def cb_refreshAttr( self):

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
#
#
class MplWidget( QtGui.QMainWindow):
    def __init__( self, logWidget, parent = None):
        super( MplWidget, self).__init__( parent)
        self.parent = parent
        self.logWidget = logWidget
        self.setWindowTitle( "Matplotlib Widget")
        #geo = QtGui.QDesktopWidget().screenGeometry(-1)
        # size
        #self.setGeometry( geo.width() - 680, 30, 650, 500)
        self.prepareWidgets()

        #self.menuBar = QtGui.QMenuBar()
        #self.setMenuBar( self.menuBar)
        #self.prepareMenuBar()

        #
        # Status Bar
        #
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar( self.statusBar)
        self.prepareStatusBar()
        pysp.cls()
        pysp.mpl_graphics.display()

    def prepareWidgets( self):
        w = QtGui.QWidget()
        #
        # start with a vertical layout
        #
        self.layout_v = QtGui.QVBoxLayout()
        w.setLayout( self.layout_v)
        self.setCentralWidget( w)

        self.figure = Figure( figsize=(29.7/2.54, 21.0/2.54))
        #self.figure = Figure( figsize=(21./2.54, 14.85/2.54))

        self.canvas = FigureCanvas( self.figure)
        
        pysp.mpl_graphics.initGraphic( self.figure, self.canvas)

        self.toolbarMpl = NavigationToolbar(self.canvas, self)
        self.layout_v.addWidget(self.toolbarMpl)
        self.layout_v.addWidget(self.canvas)
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
        self.menuBarHelp = QtGui.QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarHelp, QtCore.Qt.TopRightCorner)


        #
        # Help menu (bottom part)
        #
        self.helpMenu = self.menuBarHelp.addMenu('Help')
        self.widgetAction = self.helpMenu.addAction(self.tr("Widget"))
        self.widgetAction.triggered.connect( self.cb_helpWidget)

    #
    # the status bar
    #
    def prepareStatusBar( self): 

        self.display = QtGui.QPushButton(self.tr("&Display")) 
        self.statusBar.addPermanentWidget( self.display) # 'permanent' to shift it right
        self.display.clicked.connect( self.cb_display)
        self.display.setShortcut( "Alt+d")

        self.pdf = QtGui.QPushButton(self.tr("&PDF")) 
        self.statusBar.addPermanentWidget( self.pdf) # 'permanent' to shift it right
        self.pdf.clicked.connect( self.cb_pdf)
        self.pdf.setShortcut( "Alt+p")

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( self.close)
        self.exit.setShortcut( "Alt+x")
        
    def cb_helpWidget(self):
        QtGui.QMessageBox.about(self, self.tr("Help Widget"), self.tr(
                "<h3> matplotlib viewer</h3>"
                "A list with "
                "<ul>"
                "<li> some remarks</li>"
                "</ul>"
                ))

    def cb_display( self): 
        pysp.cls()
        pysp.mpl_graphics.cls()
        pysp.mpl_graphics.display()

    def cb_pdf( self): 
        fileName = pysp.mpl_graphics.createPDF()
        if fileName:
            self.logWidget.append( "created %s" % fileName)
            os.system( "evince %s &" % fileName)
        else:
            self.logWidget.append( "failed to create PDF file")
        
    def cb_dotyChanged( self):
        self.scan.doty = self.w_dotyCheckBox.isChecked()

        return 
#
# ===
#
class pySpectraGui( QtGui.QMainWindow):
    '''
    '''
    def __init__( self, files = None, parent = None):
        #print "pySpectraGui.__init__"
        super( pySpectraGui, self).__init__( parent)

        self.setWindowTitle( "PySpectraGui")

        # used by cb_postscript
        self.lastFileWritten = None

        self.scanList = None
        self.scanAttributes = None

        #
        # 'files' come from the command line. If nothing is supplied
        # files == []
        #
        self.files = None
        if files is not None and len( files) > 0:
            self.files = self.getMatchingFiles( files)
            if len( self.files) > 0:
                pysp.read( [self.files[0]])
            pysp.display()

        self.prepareCentralWidgets()

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
        self.updateTimerPySpectraGui = QtCore.QTimer(self)
        self.updateTimerPySpectraGui.timeout.connect( self.cb_refreshPySpectraGui)
        self.updateTimerPySpectraGui.start( int( updateTime*1000))
        #
        # (1) if the matplotlib widget is created within QtGui, we canoot 
        #     change the size (so far)
        # (2) if we create it outside QtGui, the mouse is not active inside the widget 
        #
        # compromise: start with a big widget (DINA4) in QtGui
        #
        if __builtin__.__dict__[ 'graphicsLib'] == 'matplotlib':
            self.mplWidget = MplWidget( self.logWidget)        
            self.mplWidget.show()
        #
        # after show() we see where we are. then we move the widget
        #
        geoWin = self.geometry()
        geo = QtGui.QDesktopWidget().screenGeometry(-1)
        #self.widthMax = geo.width()
        #self.heighthMax = geo.height()
        self.show()
        geoWin = self.geometry()
        self.setGeometry( geo.width() - 710, 30, geoWin.width(), geoWin.height())

    #
    # the central widgets
    #
    def prepareCentralWidgets( self):
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

        #
        # the files ListWidget
        #
        vBox = QtGui.QVBoxLayout()
        self.dirNameLabel = QtGui.QLabel( "dirName")
        vBox.addWidget( self.dirNameLabel)
        self.scrollAreaFiles = QtGui.QScrollArea()
        vBox.addWidget( self.scrollAreaFiles)
        self.filesListWidget = QListWidgetTK( self, self.newPathSelected)
        self.scrollAreaFiles.setWidget( self.filesListWidget)
        hBox.addLayout( vBox)
        #
        # the scans ListWidget
        #
        vBox = QtGui.QVBoxLayout()
        self.fileNameLabel = QtGui.QLabel( "fileName")
        vBox.addWidget( self.fileNameLabel)
        self.scrollAreaScans = QtGui.QScrollArea()
        vBox.addWidget( self.scrollAreaScans)
        self.scansListWidget = QListWidgetTK( self, self.newScanSelected)
        self.scrollAreaScans.setWidget( self.scansListWidget)
        hBox.addLayout( vBox)

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
        self.all.setToolTip( "Display all scans")
        self.all.setShortcut( "Alt+a")

        self.checked = QtGui.QPushButton(self.tr("&Checked"))
        hBox.addWidget( self.checked)
        self.checked.clicked.connect( self.displayChecked)
        self.checked.setToolTip( "Display checked scans. MB-3 checks.")
        self.checked.setShortcut( "Alt+c")

        self.next = QtGui.QPushButton(self.tr("&Next"))
        hBox.addWidget( self.next)
        self.next.clicked.connect( self.cb_next)
        self.next.setShortcut( "Alt+n")

        hBox.addStretch()            

        self.layout_v.addLayout( hBox)

        self.updateFilesList()

    def displayChecked( self): 
        pysp.cls()
        pysp.display( self.getCheckedNameList())

    def newPathSelected( self, pathName): 
        '''
        can be called with a dir name or a file name
        '''
        #
        # pathName is a directory: update filesList
        #
        if os.path.isdir( pathName):
            os.chdir( pathName)
            if self is not None:
                self.updateFilesList()
                return
        #
        # pathName is a file: update scansList
        #
        elif pathName.endswith( ".fio") or pathName.endswith( ".dat"):
            pysp.cls()
            pysp.delete()
            try: 
                pysp.read( [pathName])
            except Exception, e:
                print "pySpectraGui.newPathSelected: trouble reading", pathName
                print repr( e)
                return 

            pysp.setTitle( pathName)
            pysp.display()
            self.updateScansList()
        else:
            if self is not None:
                self.logWidget.append(  "newItemSelected: bad pathName %s" % pathName)
        return 

    def newScanSelected( self, scanName): 
        '''
        called with the name of a scan
        '''
        pysp.cls()
        pysp.display( [scanName])

        return 

    def cb_refreshPySpectraGui( self):

        if self.isMinimized(): 
            return
        
        self.activityIndex += 1
        if self.activityIndex > (len( ACTIVITY_SYMBOLS) - 1):
            self.activityIndex = 0
        self.activity.setTitle( ACTIVITY_SYMBOLS[ self.activityIndex])

        #self.updateTimerPySpectraGui.stop()        
        
        #self.updateFilesList()
        self.updateScansList()

        #self.updateTimerPySpectraGui.start( int( updateTime*1000))
        return 
   
    def updateScansList( self):
        #
        # the scan layout is updated, if
        #   - nothing has been created before self.scanList == None
        #   - the current scanList and the displayed scanList are different
        #

        scanList = pysp.getScanList()[:]
        
        flagUpdate = False
        if self.scanList is None:
            flagUpdate = True
        else:
            if len( scanList) != len( self.scanList):
                flagUpdate = True
            else:
                for i in range( len( scanList)):
                    if scanList[i] != self.scanList[i]:
                        flagUpdate = True
                        break

        if not flagUpdate: 
            self.updateTimerPySpectraGui.start( int( updateTime*1000))
            return 
        #
        # so we have to make an update, clear the scanListWidget first
        #
        if self.scansListWidget.count() > 0:
            self.scansListWidget.clear()
       
        self.scanList = scanList[:]

        if len( self.scanList) == 0:
            return 
            

        if len( self.scanList) > 0:
            if self.scanList[0].fileName is not None:
                self.fileNameLabel.setText( self.scanList[0].fileName)
        for scan in self.scanList:
            item = QtGui.QListWidgetItem( scan.name)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)       
            self.scansListWidget.addItem( item)

    def updateFilesList( self):
        '''
        file the file list in the scrolling area
        '''
        #print "updateFilesList, count", self.filesListWidget.count()

        if self.filesListWidget.count() > 0:
            self.filesListWidget.clear()

        self.dirNameLabel.setText( os.getcwd())
        #
        # if 'files' were supplied from the command line, do not offer '../'
        #
        if self.files is None:
            self.filesListWidget.addItem( "../")

        if self.files is None:
            lst = os.listdir( "./")
            lst.sort()
        else:
            lst = self.files
        
        for file in lst:
            if file.endswith( ".fio") or file.endswith( ".dat"):
                self.filesListWidget.addItem( file)
            elif file.startswith( "."):
                continue
            elif self.files is None and os.path.isdir( file):
                self.filesListWidget.addItem( file)
        #print "updateFilesList DONE"
        #self.scrollAreaFiles.setFocusPolicy( QtCore.Qt.StrongFocus)

    def getMatchingFiles( self, patternList):
        '''
        patternList is specified on the command line
        '''
        argout = []
        for file in os.listdir( "."):
            if file.upper().endswith( ".DAT") or file.upper().endswith( ".FIO"):
                for pat in patternList:
                    if HasyUtils.match( file, pat): 
                        argout.append( file)
        return argout

    def cb_all( self): 
        pysp.cls()
        pysp.display()

    def cb_prev( self): 
        scan = pysp.prevScan()
        index = pysp.getIndex( scan.name)
        pysp.cls()
        pysp.display( [ scan.name])
        self.scansListWidget.setCurrentRow( index)

    def cb_next( self): 
        scan = pysp.nextScan()
        index = pysp.getIndex( scan.name)
        pysp.cls()
        pysp.display( [ scan.name])
        self.scansListWidget.setCurrentRow( index)

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

        if __builtin__.__dict__[ 'graphicsLib'] != 'matplotlib':
            self.matplotlibAction = QtGui.QAction('matplotlib', self)        
            self.matplotlibAction.setStatusTip('Launch matplotlib to create ps or pdf output')
            self.matplotlibAction.triggered.connect( self.cb_matplotlib)
            self.fileMenu.addAction( self.matplotlibAction)

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

        self.gridAction = QtGui.QAction('GRID', self, checkable = True)        
        self.gridAction.triggered.connect( self.cb_grid)
        self.optionsMenu.addAction( self.gridAction)

        self.dina4Action = QtGui.QAction('DINA4', self)        
        self.dina4Action.triggered.connect( lambda : pysp.setWsViewport( 'dina4'))
        self.optionsMenu.addAction( self.dina4Action)

        self.dina5Action = QtGui.QAction('DINA5', self)        
        self.dina5Action.triggered.connect( lambda : pysp.setWsViewport( 'dina5'))
        self.optionsMenu.addAction( self.dina5Action)

        self.dina6Action = QtGui.QAction('DINA6', self)        
        self.dina6Action.triggered.connect( lambda : pysp.setWsViewport( 'dina6'))
        self.optionsMenu.addAction( self.dina6Action)
        #
        # scan lists
        #
        self.scanListsMenu = self.menuBar.addMenu('&ScanLists')

        self.sl1Action = QtGui.QAction('1 Scan', self)        
        self.sl1Action.triggered.connect( self.cb_sl1)
        self.scanListsMenu.addAction( self.sl1Action)

        self.sl2Action = QtGui.QAction('2 Scans', self)        
        self.sl2Action.triggered.connect( self.cb_sl2)
        self.scanListsMenu.addAction( self.sl2Action)

        self.sl3Action = QtGui.QAction('5 Scans', self)        
        self.sl3Action.triggered.connect( self.cb_sl3)
        self.scanListsMenu.addAction( self.sl3Action)

        self.sl4Action = QtGui.QAction('10 Scans', self)        
        self.sl4Action.triggered.connect( self.cb_sl4)
        self.scanListsMenu.addAction( self.sl4Action)

        self.sl5Action = QtGui.QAction('Gauss Scan', self)        
        self.sl5Action.triggered.connect( self.cb_sl5)
        self.scanListsMenu.addAction( self.sl5Action)

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

        self.clsBtn = QtGui.QPushButton(self.tr("&Cls")) 
        self.statusBar.addWidget( self.clsBtn) 
        self.clsBtn.clicked.connect( self.cb_cls)
        self.clsBtn.setShortcut( "Alt+c")

        self.deleteBtn = QtGui.QPushButton(self.tr("&Delete")) 
        self.statusBar.addWidget( self.deleteBtn) 
        self.deleteBtn.clicked.connect( self.cb_delete)
        self.deleteBtn.setToolTip( "Delete checked scans")
        self.deleteBtn.setShortcut( "Alt+d")

        if __builtin__.__dict__[ 'graphicsLib'] != 'matplotlib':
            self.matplotlibBtn = QtGui.QPushButton(self.tr("&matplotlib")) 
            self.statusBar.addWidget( self.matplotlibBtn) 
            self.matplotlibBtn.clicked.connect( self.cb_matplotlib)
            self.matplotlibBtn.setShortcut( "Alt+m")
            self.matplotlibBtn.setToolTip( "Launch matplotlib widget to create PDF")
        else: 
            self.pdfBtn = QtGui.QPushButton(self.tr("&PDF")) 
            self.statusBar.addWidget( self.pdfBtn) 
            self.pdfBtn.clicked.connect( self.cb_pdf)
            self.pdfBtn.setShortcut( "Alt+p")
            self.pdfBtn.setToolTip( "Create PDF file")

        self.pausedBtn = QtGui.QPushButton(self.tr("Pause")) 
        self.statusBar.addPermanentWidget( self.pausedBtn) # 'permanent' to shift it right
        self.pausedBtn.clicked.connect( self.cb_paused)

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( sys.exit)
        self.exit.setShortcut( "Alt+x")

    def cb_paused( self): 
        if self.paused: 
            self.paused = False
            self.pausedBtn.setText( "Pause")
        else: 
            self.paused = True
            self.pausedBtn.setText( "Start")
            
    def cb_cls( self):
        '''
        clear screen
        '''
        pysp.cls()
        
    def getCheckedNameList( self): 
        nameList = []
        for row in range( self.scansListWidget.count()):
            item = self.scansListWidget.item( row)
            if item.checkState() == QtCore.Qt.Checked:
                nameList.append( item.text())
        return nameList

    def cb_delete( self): 
        '''
        delete the scans, internally
        '''
        lst = self.getCheckedNameList()
        for name in lst: 
            self.logWidget.append(  "Deleting %s" % name)
        pysp.delete( lst)
        pysp.cls()
        pysp.display()
        return 

    def cb_pdf( self): 
        fileName = pysp.mpl_graphics.createPDF()
        if fileName:
            self.logWidget.append( "created %s" % fileName)
            os.system( "evince %s &" % fileName)
        else:
            self.logWidget.append( "failed to create PDF file")
        
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

    def cb_grid( self): 
        lst = pysp.getScanList()
        if self.gridAction.isChecked():
            for scan in lst:
                scan.showGridX = True
                scan.showGridY = True
        else:
            for scan in lst:
                scan.showGridX = False
                scan.showGridY = False
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
        pysp.setTitle( "Ein Titel")
        pysp.setComment( "Ein Kommentar")
        t1 = pysp.Scan( name = "t1", color = 'blue', yLabel = 'sin')
        t1.y = np.sin( t1.x)
        pysp.display()

    def cb_sl2( self):
        pysp.cls()
        pysp.delete()
        pysp.setTitle( "Ein Titel")
        pysp.setComment( "Ein Kommentar")
        t1 = pysp.Scan( name = "t1", color = 'blue', yLabel = 'sin')
        t1.y = np.sin( t1.x)
        t2 = pysp.Scan( "t2", yLabel = 'cos')
        t2.y = np.cos( t2.x)
        pysp.display()

    def cb_sl3( self):
        pysp.cls()
        pysp.delete()
        pysp.setTitle( "Ein Titel")
        pysp.setComment( "Ein Kommentar")
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

    def cb_sl4( self):
        pysp.cls()
        pysp.delete()
        pysp.setTitle( "Ein Titel")
        pysp.setComment( "Ein Kommentar")
        for i in range( 10): 
            t = pysp.Scan( name = "t%d" % i, color = 'blue', yLabel = 'rand')
            t.y = np.random.random_sample( (len( t.x), ))
        pysp.display()

    def cb_sl5( self):
        '''
        gauss scan
        '''
        pysp.cls()
        pysp.delete()
        pysp.setTitle( "Ein Titel")
        pysp.setComment( "Ein Kommentar")
        g = pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
        mu = 0.
        sigma = 1.
        g.y = 1/(sigma * np.sqrt(2 * np.pi)) * \
              np.exp( - (g.y - mu)**2 / (2 * sigma**2))
        pysp.display()

    def cb_writeFile( self):
        pysp.write()

    def cb_matplotlib( self):
        self.mplWidget = MplWidget( self.logWidget)
        self.mplWidget.show()
        pysp.mpl_graphics.display()

    def cb_helpWidget(self):
        QtGui.QMessageBox.about(self, self.tr("Help Widget"), self.tr(
                "<h3> PySpectraGui</h3>"
                "The Python Spectra Gui"
                "<ul>"
                "<li> some remarks</li>"
                "</ul>"
                ))


