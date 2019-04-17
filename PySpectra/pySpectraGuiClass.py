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
import PySpectra.definitions as defs

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

win = None
ACTIVITY_SYMBOLS = ['|', '/', '-', '\\', '|', '/', '-', '\\'] 
updateTime = 0.5

class HLineTK( QtGui.QFrame):
    def __init__( self):
        QtGui.QFrame.__init__(self)
        self.setFrameShape( QtGui.QFrame.HLine)
        self.setFrameShadow(QtGui.QFrame.Sunken)

class QListWidgetTK( QtGui.QListWidget): 
    '''
    newItemSelected is called, if a new item is selected, 
    can be a file, a directory or a scan
    '''
    def __init__( self, parent, newItemSelected, name): 
        QtGui.QListWidget.__init__(self)
        self.parent = parent
        self.newItemSelected = newItemSelected
        self.name = name
        self.connect( self, QtCore.SIGNAL("itemDoubleClicked (QListWidgetItem *)"),self.cb_doubleClicked)

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

    def cb_doubleClicked( self, item): 
        '''
        double click: reads a file
        '''
        print "doubleClicket", item.text()

        if self.name == "filesListWidget":
            self.newItemSelected( str( item.text()))
        return 

    def mouseReleaseEvent( self, event): 
        '''
        left-MB:  change checkState of a scan
        right-MB: opens the attributesWidget
        '''
        if self.name == "filesListWidget":
            return 
        if event.button() == QtCore.Qt.LeftButton:
            item = self.currentItem()
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)       
            else:
                item.setCheckState(QtCore.Qt.Checked)       
            if item is not None:
                self.parent.displayChecked()
        if event.button() == QtCore.Qt.RightButton:
            item = self.currentItem()
            self.scanAttributes = ScanAttributes( self.parent, item.text())
        return 

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
        #pysp.show( self.name)
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
        #
        # name
        #
        hBox = QtGui.QHBoxLayout()
        self.nameLabel = QtGui.QLabel( "Name:")
        hBox.addWidget( self.nameLabel)
        self.nameValue = QtGui.QLabel( self.name)
        hBox.addWidget( self.nameValue)
        self.layout_v.addLayout( hBox)
        #
        # length
        #
        hBox = QtGui.QHBoxLayout()
        self.lengthLabel = QtGui.QLabel( "Length:")
        hBox.addWidget( self.lengthLabel)
        self.lengthValue = QtGui.QLabel( "%d" % len(self.scan.x))
        hBox.addWidget( self.lengthValue)
        self.layout_v.addLayout( hBox)
        #
        # xMin
        #
        hBox = QtGui.QHBoxLayout()
        self.xMinLabel = QtGui.QLabel( "xMin:")
        hBox.addWidget( self.xMinLabel)
        self.xMinValue = QtGui.QLabel( "%g" % (self.scan.xMin))
        hBox.addWidget( self.xMinValue)
        hBox.addStretch()            
        self.xMinLineEdit = QtGui.QLineEdit()
        hBox.addWidget( self.xMinLineEdit)
        self.layout_v.addLayout( hBox)
        #
        # xMax
        #
        hBox = QtGui.QHBoxLayout()
        self.xMaxLabel = QtGui.QLabel( "xMax:")
        hBox.addWidget( self.xMaxLabel)
        self.xMaxValue = QtGui.QLabel( "%g" % (self.scan.xMax))
        hBox.addWidget( self.xMaxValue)
        hBox.addStretch()            
        self.xMaxLineEdit = QtGui.QLineEdit()
        hBox.addWidget( self.xMaxLineEdit)
        self.layout_v.addLayout( hBox)
        #
        # yMin
        #
        hBox = QtGui.QHBoxLayout()
        self.yMinLabel = QtGui.QLabel( "yMin:")
        hBox.addWidget( self.yMinLabel)
        if self.scan.yMin is None:
            self.yMinValue = QtGui.QLabel( "None")
        else:
            self.yMinValue = QtGui.QLabel( "%g" % (self.scan.yMin))
        hBox.addWidget( self.yMinValue)
        hBox.addStretch()            
        self.yMinLineEdit = QtGui.QLineEdit()
        hBox.addWidget( self.yMinLineEdit)
        self.layout_v.addLayout( hBox)
        #
        # yMax
        #
        hBox = QtGui.QHBoxLayout()
        self.yMaxLabel = QtGui.QLabel( "yMax:")
        hBox.addWidget( self.yMaxLabel)
        if self.scan.yMax is None:
            self.yMaxValue = QtGui.QLabel( "None")
        else:
            self.yMaxValue = QtGui.QLabel( "%g" % (self.scan.yMax))
        hBox.addWidget( self.yMaxValue)
        hBox.addStretch()            
        self.yMaxLineEdit = QtGui.QLineEdit()
        hBox.addWidget( self.yMaxLineEdit)
        self.layout_v.addLayout( hBox)
        #
        # autorangeX
        #
        hBox = QtGui.QHBoxLayout()
        self.autorangeXLabel = QtGui.QLabel( "autorangeX:")
        hBox.addWidget( self.autorangeXLabel)
        self.autorangeXCheckBox = QtGui.QCheckBox()
        self.autorangeXCheckBox.setChecked( self.scan.autorangeX)
        hBox.addWidget( self.autorangeXCheckBox)
        hBox.addStretch()            
        self.autorangeXCheckBox.stateChanged.connect( self.cb_autorangeXChanged)
        self.layout_v.addLayout( hBox)
        #
        # autorangeY
        #
        hBox = QtGui.QHBoxLayout()
        self.autorangeYLabel = QtGui.QLabel( "autorangeY:")
        hBox.addWidget( self.autorangeYLabel)
        self.autorangeYCheckBox = QtGui.QCheckBox()
        self.autorangeYCheckBox.setChecked( self.scan.autorangeY)
        hBox.addWidget( self.autorangeYCheckBox)
        hBox.addStretch()            
        self.autorangeYCheckBox.stateChanged.connect( self.cb_autorangeYChanged)
        self.layout_v.addLayout( hBox)
        #
        # xLog
        #
        hBox = QtGui.QHBoxLayout()
        self.xLogLabel = QtGui.QLabel( "xLog:")
        hBox.addWidget( self.xLogLabel)
        self.xLogCheckBox = QtGui.QCheckBox()
        self.xLogCheckBox.setChecked( self.scan.xLog)
        hBox.addWidget( self.xLogCheckBox)
        hBox.addStretch()            
        self.xLogCheckBox.stateChanged.connect( self.cb_xLogChanged)
        self.layout_v.addLayout( hBox)
        #
        # yLog
        #
        hBox = QtGui.QHBoxLayout()
        self.yLogLabel = QtGui.QLabel( "yLog:")
        hBox.addWidget( self.yLogLabel)
        self.yLogCheckBox = QtGui.QCheckBox()
        self.yLogCheckBox.setChecked( self.scan.yLog)
        hBox.addWidget( self.yLogCheckBox)
        hBox.addStretch()            
        self.yLogCheckBox.stateChanged.connect( self.cb_yLogChanged)
        self.layout_v.addLayout( hBox)
        #
        # doty
        #
        hBox = QtGui.QHBoxLayout()
        self.dotyLabel = QtGui.QLabel( "DOTY")
        hBox.addWidget( self.dotyLabel)
        self.w_dotyCheckBox = QtGui.QCheckBox()
        self.w_dotyCheckBox.setChecked( self.scan.doty)
        self.w_dotyCheckBox.setToolTip( "x-axis is day-of-the-year")
        hBox.addWidget( self.w_dotyCheckBox) 
        hBox.addStretch()            
        self.layout_v.addLayout( hBox)
        self.w_dotyCheckBox.stateChanged.connect( self.cb_dotyChanged)
        #
        # GridX
        #
        hBox = QtGui.QHBoxLayout()
        self.gridXLabel = QtGui.QLabel( "GridX")
        hBox.addWidget( self.gridXLabel)
        self.w_gridXCheckBox = QtGui.QCheckBox()
        self.w_gridXCheckBox.setChecked( self.scan.showGridX)
        hBox.addWidget( self.w_gridXCheckBox) 
        self.w_gridXCheckBox.stateChanged.connect( self.cb_gridXChanged)
        hBox.addStretch()            
        self.layout_v.addLayout( hBox)
        #
        # GridY
        #
        hBox = QtGui.QHBoxLayout()
        self.gridYLabel = QtGui.QLabel( "GridY")
        hBox.addWidget( self.gridYLabel)
        self.w_gridYCheckBox = QtGui.QCheckBox()
        self.w_gridYCheckBox.setChecked( self.scan.showGridY)
        hBox.addWidget( self.w_gridYCheckBox) 
        self.w_gridYCheckBox.stateChanged.connect( self.cb_gridYChanged)
        hBox.addStretch()            
        self.layout_v.addLayout( hBox)
        #
        # color
        #
        hBox = QtGui.QHBoxLayout()
        self.colorLabel = QtGui.QLabel( "Color")
        hBox.addWidget( self.colorLabel)
        hBox.addStretch()            
        self.w_colorComboBox = QtGui.QComboBox()
        for color in pysp.colorArr:
            self.w_colorComboBox.addItem( color)
        self.w_colorComboBox.currentIndexChanged.connect( self.cb_color)
        self.w_colorComboBox.setCurrentIndex( pysp.colorDct[ self.scan.color.upper()])
        hBox.addWidget( self.w_colorComboBox) 
        self.layout_v.addLayout( hBox)
        #
        # style
        #
        hBox = QtGui.QHBoxLayout()
        self.styleLabel = QtGui.QLabel( "Style")
        hBox.addWidget( self.styleLabel)
        hBox.addStretch()            
        self.w_styleComboBox = QtGui.QComboBox()
        for style in pysp.styleArr:
            self.w_styleComboBox.addItem( style)
        self.w_styleComboBox.currentIndexChanged.connect( self.cb_style)
        self.w_styleComboBox.setCurrentIndex( pysp.styleDct[ self.scan.style.upper()])
        hBox.addWidget( self.w_styleComboBox) 
        self.layout_v.addLayout( hBox)
        #
        # width
        #
        hBox = QtGui.QHBoxLayout()
        self.widthLabel = QtGui.QLabel( "Width")
        hBox.addWidget( self.widthLabel)
        hBox.addStretch()            
        self.w_widthComboBox = QtGui.QComboBox()
        if str( self.scan.width) not in pysp.widthDct.keys():
            self.scan.width = 1.0
        for width in pysp.widthArr:
            self.w_widthComboBox.addItem( width)
        self.w_widthComboBox.currentIndexChanged.connect( self.cb_width)
        self.w_widthComboBox.setCurrentIndex( pysp.widthDct[ str( self.scan.width)])
        hBox.addWidget( self.w_widthComboBox) 
        self.layout_v.addLayout( hBox)
        #
        # overlay
        #
        hBox = QtGui.QHBoxLayout()
        self.overlayLabel = QtGui.QLabel( "Overlay")
        hBox.addWidget( self.overlayLabel)
        hBox.addStretch()            
        self.w_overlayComboBox = QtGui.QComboBox()
        self.w_overlayComboBox.addItem( "None")
        count = 1 
        countTemp = -1
        for scan in pysp.getScanList(): 
            if scan.name == self.name:
                continue
            if self.scan.overlay is not None and self.scan.overlay == scan.name:
                countTemp = count
            self.w_overlayComboBox.addItem( scan.name)
            count += 1
        if countTemp > 0: 
            self.w_overlayComboBox.setCurrentIndex( countTemp)
        self.w_overlayComboBox.currentIndexChanged.connect( self.cb_overlay)
        hBox.addWidget( self.w_overlayComboBox) 
        self.layout_v.addLayout( hBox)


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

        self.apply = QtGui.QPushButton(self.tr("&Apply")) 
        self.statusBar.addPermanentWidget( self.apply) # 'permanent' to shift it right
        self.apply.clicked.connect( self.cb_apply)
        self.apply.setShortcut( "Alt+a")

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( self.close)
        self.exit.setShortcut( "Alt+x")

    def cb_autorangeXChanged( self): 
        self.scan.autorangeX = self.autorangeXCheckBox.isChecked()
        pysp.cls()
        pysp.display()

    def cb_autorangeYChanged( self): 
        self.scan.autorangeY = self.autorangeYCheckBox.isChecked()
        pysp.cls()
        pysp.display()

    def cb_xLogChanged( self): 
        self.scan.xLog = self.xLogCheckBox.isChecked()
        pysp.cls()
        pysp.display()

    def cb_yLogChanged( self): 
        self.scan.yLog = self.yLogCheckBox.isChecked()
        pysp.cls()
        pysp.display()

    def cb_apply( self):
        line = str(self.xMinLineEdit.text())
        if len(line.strip()) > 0: 
            self.scan.xMin = float( line.strip())
            self.xMinValue.setText( "%g" % self.scan.xMin)
            self.xMinLineEdit.clear()

        line = str(self.xMaxLineEdit.text())
        if len(line.strip()) > 0: 
            self.scan.xMax = float( line.strip())
            self.xMaxValue.setText( "%g" % self.scan.xMax)
            self.xMaxLineEdit.clear()

        line = str(self.yMinLineEdit.text())
        if len(line.strip()) > 0: 
            self.scan.yMin = float( line.strip())
            self.yMinValue.setText( "%g" % self.scan.yMin)
            self.yMinLineEdit.clear()

        line = str(self.yMaxLineEdit.text())
        if len(line.strip()) > 0: 
            self.scan.yMax = float( line.strip())
            self.yMaxValue.setText( "%g" % self.scan.yMax)
            self.yMaxLineEdit.clear()
        pysp.cls()
        pysp.display()
        
    def cb_color( self): 
        temp = self.w_colorComboBox.currentText()
        self.scan.color = str( temp)
        pysp.cls()
        pysp.display()
        return

    def cb_style( self): 
        temp = self.w_styleComboBox.currentText()
        self.scan.style = str( temp)
        pysp.cls()
        pysp.display()
        return

    def cb_width( self): 
        temp = self.w_widthComboBox.currentText()
        self.scan.width = float( temp)
        pysp.cls()
        pysp.display()
        return

    def cb_overlay( self): 
        temp = str( self.w_overlayComboBox.currentText())
        if temp == 'None': 
            temp = None
        self.scan.overlay = temp
        pysp.cls()
        pysp.display()
        return
        
    def cb_refreshAttr( self):

        if self.isMinimized(): 
            return
        
        self.activityIndex += 1
        if self.activityIndex > (len( ACTIVITY_SYMBOLS) - 1):
            self.activityIndex = 0
        self.activity.setTitle( ACTIVITY_SYMBOLS[ self.activityIndex])
        self.updateTimer.stop()

        #self.w_gridXCheckBox.setCheckState( self.scan.showGridX) 
        #self.w_gridYCheckBox.setCheckState( self.scan.showGridY) 
        self.updateTimer.start( int( updateTime*1000))

    def cb_display( self): 
        pysp.cls()
        pysp.display()

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
        pysp.cls()
        pysp.display()

        return 

    def cb_gridXChanged( self):
        self.scan.showGridX = self.w_gridXCheckBox.isChecked()
        pysp.cls()
        pysp.display()

        return 

    def cb_gridYChanged( self):
        self.scan.showGridY = self.w_gridYCheckBox.isChecked()
        pysp.cls()
        pysp.display()

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

        self.prepareWidgets()

        #
        # Status Bar
        #
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar( self.statusBar)
        self.prepareStatusBar()
        pysp.mpl_graphics.cls()

    def prepareWidgets( self):
        w = QtGui.QWidget()
        #
        # start with a vertical layout
        #
        self.layout_v = QtGui.QVBoxLayout()
        w.setLayout( self.layout_v)
        self.setCentralWidget( w)

        self.figure = Figure( figsize=(29.7/2.54, 21.0/2.54))

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
    def __init__( self, files = None, parent = None, calledFromMonitorApp = False):
        #print "pySpectraGui.__init__"
        super( pySpectraGui, self).__init__( parent)

        self.calledFromMonitorApp = calledFromMonitorApp

        
        self.setWindowTitle( "PySpectraGui")

        # used by cb_postscript
        self.lastFileWritten = None

        self.scanList = None
        self.scanAttributes = None
        self.proxyDoor = None
        self.nMotor = 0

        #
        # 'files' come from the command line. If nothing is supplied
        # files == []
        #
        self.files = None
        if files is not None and len( files) > 0:
            self.files = self.getMatchingFiles( files)
            for f in self.files:
                pysp.read( f)
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
        self.filesListWidget = QListWidgetTK( self, self.newPathSelected, "filesListWidget")
        self.scrollAreaFiles.setWidget( self.filesListWidget)
        hBox.addLayout( vBox)
        #
        # the scans ListWidget
        #
        vBox = QtGui.QVBoxLayout()
        self.fileNameLabel = QtGui.QLabel( "ScanName")
        vBox.addWidget( self.fileNameLabel)
        self.scrollAreaScans = QtGui.QScrollArea()
        vBox.addWidget( self.scrollAreaScans)
        self.scansListWidget = QListWidgetTK( self, self.newScanSelected, "scansListWidget")
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
        # motors and Macroserver
        #
        if self.calledFromMonitorApp: 
            self.addHardwareFrame()

        self.addScanFrame()
        self.layout_v.addWidget( HLineTK())

        self.updateFilesList()

    def addHardwareFrame( self): 

        frame = QtGui.QFrame()
        frame.setFrameShape( QtGui.QFrame.Box)
        self.layout_v.addWidget( frame)
        self.layout_frame_v = QtGui.QVBoxLayout()
        frame.setLayout( self.layout_frame_v)

        '''
        mot1: pos | mot2: pos | mot3: pos
        '''
        hBox = QtGui.QHBoxLayout()

        hBox.addStretch()            
        self.motProxies = []
        self.motNameLabels = []
        self.motPosLabels = []
        names = [ 'mot1', 'mot2', 'mot3']
        for i in range( len( names)):
            w = QtGui.QLabel( names[i])
            self.motNameLabels.append( w)
            hBox.addWidget( w)
            w.hide()

            w = QtGui.QLabel( "pos")
            w.setMinimumWidth( 70)

            self.motPosLabels.append( w)
            hBox.addWidget( w)
            self.motProxies.append( None)
            w.hide()

        hBox.addStretch()            

        self.layout_frame_v.addLayout( hBox)

        '''
        Abort | Stop | StopAllMoves | RequestStop
        '''
        hBox = QtGui.QHBoxLayout()

        hBox.addStretch()            

        self.abort = QtGui.QPushButton(self.tr("Abort"))
        hBox.addWidget( self.abort)
        self.abort.clicked.connect( self.cb_abort)
        self.abort.setToolTip( "Send AbortMacro to the MacroServer")

        self.stop = QtGui.QPushButton(self.tr("Stop"))
        hBox.addWidget( self.stop)
        self.stop.clicked.connect( self.cb_stop)
        self.stop.setToolTip( "Send StopMacro to the MacroServer")

        self.stopAllMoves = QtGui.QPushButton(self.tr("StopAllMoves"))
        hBox.addWidget( self.stopAllMoves)
        self.stopAllMoves.clicked.connect( self.cb_stopAllMoves)

        self.requestStop = QtGui.QPushButton(self.tr("RequestStop"))
        hBox.addWidget( self.requestStop)
        self.requestStop.setToolTip( "Set RequestStop == True, optionally sensed by Macros")
        self.requestStop.clicked.connect( self.cb_requestStop)

        hBox.addStretch()            

        self.layout_frame_v.addLayout( hBox)

    def updateMotorWidgets( self): 
        
        if self.nMotor == 0: 
            return 

        for i in range( self.nMotor): 
            self.motPosLabels[ i].setText( "%g" % self.motProxies[i].position) 
            if self.motProxies[i].state() == PyTango.DevState.MOVING:
                self.motPosLabels[ i].setStyleSheet( "background-color:%s;" % defs._BLUE_MOVING)
            elif self.motProxies[i].state() == PyTango.DevState.ON:
                self.motPosLabels[ i].setStyleSheet( "background-color:%s;" % defs._GREEN_OK)
            else:
                self.motPosLabels[ i].setStyleSheet( "background-color:%s;" % defs._RED_ALARM)


    def addScanFrame( self): 
        '''
        Prev | All | Checked | Next
        '''

        frame = QtGui.QFrame()
        frame.setFrameShape( QtGui.QFrame.Box)
        self.layout_v.addWidget( frame)
        self.layout_frame_v = QtGui.QVBoxLayout()
        frame.setLayout( self.layout_frame_v)
        #
        # the lineEdit line
        #
        #hBox = QtGui.QHBoxLayout()
        #self.lineEdit = QtGui.QLineEdit()
        #hBox.addWidget( self.lineEdit)
        #self.layout_frame_v.addLayout( hBox)
        #QtCore.QObject.connect( self.lineEdit, 
        #                        QtCore.SIGNAL("returnPressed()"),self.cb_lineEdit)
        #
        # prev, all, checked, next
        #
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

        self.checked = QtGui.QPushButton(self.tr("Checked"))
        hBox.addWidget( self.checked)
        self.checked.clicked.connect( self.displayChecked)
        self.checked.setToolTip( "Display checked scans.")
        self.checked.setShortcut( "Alt+c")

        self.next = QtGui.QPushButton(self.tr("&Next"))
        hBox.addWidget( self.next)
        self.next.clicked.connect( self.cb_next)
        self.next.setShortcut( "Alt+n")

        hBox.addStretch()            
        self.layout_frame_v.addLayout( hBox)

    def cb_abort( self): 
        '''
        execute AbortMacro on Door
        '''
        if self.proxyDoor is None:
            try:
                self.proxyDoor = PyTango.DeviceProxy( HasyUtils.getDoorNames()[0])
            except Exception, e: 
                print "pySpectraGui.cb_abort: failed to create proxy to door", HasyUtils.getDoorNames()[0]
                return 
            self.proxyDoor = PyTango.DeviceProxy( HasyUtils.getDoorNames()[0])
        self.proxyDoor.AbortMacro()
            
    def cb_stop( self): 
        '''
        execute StopMacro on Door
        '''
        if self.proxyDoor is None:
            try:
                self.proxyDoor = PyTango.DeviceProxy( HasyUtils.getDoorNames()[0])
            except Exception, e: 
                print "pySpectraGui.cb_stop: failed to create proxy to door", HasyUtils.getDoorNames()[0]
                return 
        if self.proxyDoor.State() != PyTango.DevState.ON:        
            self.proxyDoor.StopMacro()

    def cb_stopAllMoves( self): 
        HasyUtils.stopAllMoves()

    def cb_requestStop( self): 
        HasyUtils.setEnv( "RequestStop", True)
        self.logWidget.append( "RequestStop == True")
        

    def displayChecked( self): 
        pysp.cls()
        pysp.display( self.getCheckedNameList())

    def newPathSelected( self, pathName): 
        '''
        can be called with a dir name or a file name
        '''
        pathNameTokens = pathName.split( '.')
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
        elif pathNameTokens[-1] in defs.dataFormats:
            pysp.cls()
            pysp.delete()
            try: 
                pysp.read( pathName)
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

        self.updateMotorWidgets()

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
            fileNameTokens = file.split( '.')
            if fileNameTokens[-1] in defs.dataFormats:
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
            fileNameTokens = file.split( '.')
            if fileNameTokens[-1] in defs.dataFormats:
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

        self.miscMenu = self.menuBar.addMenu('&Misc')

        self.editAction = QtGui.QAction('Edit', self)        
        self.editAction.triggered.connect( self.cb_edit)
        self.miscMenu.addAction( self.editAction)

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
        self.scanListsMenu = self.menuBar.addMenu('&TestData')

        self.sl1Action = QtGui.QAction('1 Scan', self)        
        self.sl1Action.triggered.connect( scanList1)
        self.scanListsMenu.addAction( self.sl1Action)

        self.sl2Action = QtGui.QAction('2 Scans', self)        
        self.sl2Action.triggered.connect( scanList2)
        self.scanListsMenu.addAction( self.sl2Action)

        self.sl3Action = QtGui.QAction('5 Scans', self)        
        self.sl3Action.triggered.connect( scanList3)
        self.scanListsMenu.addAction( self.sl3Action)

        self.sl4Action = QtGui.QAction('10 Scans', self)        
        self.sl4Action.triggered.connect( scanList4)
        self.scanListsMenu.addAction( self.sl4Action)

        self.sl5Action = QtGui.QAction('22 Scans', self)        
        self.sl5Action.triggered.connect( scanList5)
        self.scanListsMenu.addAction( self.sl5Action)

        self.sl6Action = QtGui.QAction('56 Scans', self)        
        self.sl6Action.triggered.connect( scanList6)
        self.scanListsMenu.addAction( self.sl6Action)

        self.sl7Action = QtGui.QAction('Gauss Scan', self)        
        self.sl7Action.triggered.connect( scanList7)
        self.scanListsMenu.addAction( self.sl7Action)

        self.sl8Action = QtGui.QAction('Overlay', self)        
        self.sl8Action.triggered.connect( scanList8)
        self.scanListsMenu.addAction( self.sl8Action)

        self.sl9Action = QtGui.QAction('Overlay, log', self)        
        self.sl9Action.triggered.connect( scanList9)
        self.scanListsMenu.addAction( self.sl9Action)

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

        #
        # cls, delete
        #
        self.clsBtn = QtGui.QPushButton(self.tr("&Cls")) 
        self.statusBar.addWidget( self.clsBtn) 
        self.clsBtn.clicked.connect( self.cb_cls)
        self.clsBtn.setShortcut( "Alt+c")

        self.deleteBtn = QtGui.QPushButton(self.tr("&Delete")) 
        self.statusBar.addWidget( self.deleteBtn) 
        self.deleteBtn.clicked.connect( self.cb_delete)
        self.deleteBtn.setToolTip( "Delete checked scans")
        self.deleteBtn.setShortcut( "Alt+d")

        if __builtin__.__dict__[ 'graphicsLib'] == 'matplotlib':
            self.pdfBtn = QtGui.QPushButton(self.tr("&PDF")) 
            self.statusBar.addWidget( self.pdfBtn) 
            self.pdfBtn.clicked.connect( self.cb_pdf)
            self.pdfBtn.setShortcut( "Alt+p")
            self.pdfBtn.setToolTip( "Create PDF file")

        self.clearLog = QtGui.QPushButton(self.tr("&ClearLog")) 
        self.statusBar.addPermanentWidget( self.clearLog) # 'permanent' to shift it right
        self.clearLog.clicked.connect( self.cb_clearLog)
        self.clearLog.setToolTip( "Clear log widget")
        self.clearLog.setShortcut( "Alt+c")

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( sys.exit)
        self.exit.setShortcut( "Alt+x")

    def cb_clearLog( self): 
        self.logWidget.clear()

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
                nameList.append( str( item.text()))
        return nameList

    def cb_delete( self): 
        '''
        delete the scans, internally
        '''
        lst = self.getCheckedNameList()
        if len( lst) == 0:
            self.logWidget.append(  "cb_Delete: no scans checked")
            return 
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

    def cb_edit( self):
        item = self.filesListWidget.currentItem()
        if item is None:
            self.logWidget.append( "cb_edit: select a file name")
            return 
        fName = os.getcwd() + "/" + item.text()
        editor = os.getenv( "EDITOR")
        if editor is None: 
            editor = 'emacs'
        os.system( "%s %s&" % (editor, fName))
        
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

    def cb_writeFile( self):
        pysp.write()

    def cb_matplotlib( self):
        self.mplWidget = MplWidget( self.logWidget)
        self.mplWidget.show()
        pysp.mpl_graphics.display( self.getCheckedNameList())

    def cb_helpWidget(self):
        QtGui.QMessageBox.about(self, self.tr("Help Widget"), self.tr(
                "<h3> PySpectraGui</h3>"
                "The Python Spectra Gui"
                "<ul>"
                "<li> some remarks</li>"
                "</ul>"
                ))
def scanList1( self):
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "Ein Titel")
    pysp.setComment( "Ein Kommentar")
    t1 = pysp.Scan( name = "t1", color = 'blue', yLabel = 'sin')
    t1.y = np.sin( t1.x)
    pysp.display()

def scanList2( self):
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "Ein Titel")
    pysp.setComment( "Ein Kommentar")
    t1 = pysp.Scan( name = "t1", color = 'blue', yLabel = 'sin')
    t1.y = np.sin( t1.x)
    t2 = pysp.Scan( "t2", yLabel = 'cos')
    t2.y = np.cos( t2.x)
    pysp.display()

def scanList3( self):
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

def scanList4( self):
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "Ein Titel")
    pysp.setComment( "Ein Kommentar")
    for i in range( 10): 
        t = pysp.Scan( name = "t%d" % i, color = 'blue', yLabel = 'rand')
        t.y = np.random.random_sample( (len( t.x), ))
    pysp.display()

def scanList5( self):
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "22 Scans")
    #pysp.setComment( "Ein Kommentar")
    for i in range( 22): 
        t = pysp.Scan( name = "t%d" % i, color = 'blue', yLabel = 'rand')
        t.y = np.random.random_sample( (len( t.x), ))
    pysp.display()

def scanList6( self):
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "56 Scans")
    #pysp.setComment( "Ein Kommentar")
    for i in range( 56): 
        t = pysp.Scan( name = "t%d" % i, color = 'blue', yLabel = 'rand')
        t.y = np.random.random_sample( (len( t.x), ))
    pysp.display()

def scanList7( self):
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

def scanList8( self):
    '''
    overlay
    '''
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "2 Overlay Scans")
    g = pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, color = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma * np.sqrt(2 * np.pi)) * \
          np.exp( - (g.y - mu)**2 / (2 * sigma**2))
    t1 = pysp.Scan( name = "sinus", color = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = np.sin( t1.x)
    pysp.overlay( "sinus", "gauss")
    pysp.display()

def scanList9( self):
    '''
    overlay with log
    '''
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "2 Overlay Scans")
    g1 = pysp.Scan( name = "gauss", xMin = -5., xMax = 5., yLog = True, nPts = 101, color = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma * np.sqrt(2 * np.pi)) * \
          np.exp( - (g1.y - mu)**2 / (2 * sigma**2))
    g2 = pysp.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0, 
                    yMax = 1, nPts = 101, color = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma * np.sqrt(2 * np.pi)) * \
          np.exp( - (g2.y - mu)**2 / (2 * sigma**2))

    pysp.overlay( "gauss2", "gauss")
    pysp.display()
 
