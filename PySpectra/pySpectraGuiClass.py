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
import PySpectra.dMgt.GQE as gqe
import mtpltlb.graphics as mpl_graphics # to create postscript

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

win = None
ACTIVITY_SYMBOLS = ['|', '/', '-', '\\', '|', '/', '-', '\\'] 
updateTime = 0.5

HISTORY_MAX = 100

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
    def __init__( self, parent, newItemSelected, name, logWidget): 
        QtGui.QListWidget.__init__(self)
        self.parent = parent
        self.newItemSelected = newItemSelected
        self.name = name
        self.logWidget = logWidget
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
            scan = pysp.getScan( item.text())
            if scan.textOnly: 
                self.logWidget.append( "%s is textOnly" % item.text())
                return 
            self.scanAttributes = ScanAttributes( self.parent, item.text())
        return 

class QLineEditTK( QtGui.QLineEdit): 
    '''
    '''
    def __init__( self, parent): 
        QtGui.QListWidget.__init__(self)
        self.parent = parent
        self.history = []
        self.historyIndex = 0

    def storeHistory( self, text): 
        if len( self.history) >= HISTORY_MAX: 
            self.history = self.history[1:]
        self.history.append( str(text))
        self.historyIndex = len( self.history) - 1
        #print "store", self.historyIndex, repr( self.history)
        return 

    def getPrevious( self): 
        if self.historyIndex < 0:
            return ""
        self.historyIndex -= 1
        return self.history[ self.historyIndex + 1] 
        
    def getNext( self): 
        if len( self.history) == 0:
            return ""
        self.historyIndex += 1

        if self.historyIndex < len( self.history): 
            return self.history[ self.historyIndex] 

        self.historyIndex -= 1
        return ""

    def keyPressEvent (self, eventQKeyEvent):
        key = eventQKeyEvent.key()

        if key == QtCore.Qt.Key_Down:
            text = self.getNext()
            self.clear()
            self.insert( text)
            #print "key down", key
        elif key == QtCore.Qt.Key_Up:
            text = self.getPrevious()
            self.clear()
            self.insert( text)
            #print "key up", key
        elif key == QtCore.Qt.Key_Return:
            self.storeHistory( self.text())
            #print "key return", key
        else: 
            #print "else: key", key
            pass

        return QtGui.QLineEdit.keyPressEvent(self, eventQKeyEvent)
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
        self.layout_grid = QtGui.QGridLayout()
        w.setLayout( self.layout_grid)
        self.setCentralWidget( w)
        #
        # name
        #
        row = 0
        self.nameLabel = QtGui.QLabel( "Name:")
        self.layout_grid.addWidget( self.nameLabel, row, 0)
        self.nameValue = QtGui.QLabel( self.name)
        self.layout_grid.addWidget( self.nameValue, row, 1)
        #
        # length
        #
        row += 1
        self.lengthLabel = QtGui.QLabel( "Length:")
        self.layout_grid.addWidget( self.lengthLabel, row, 0)
        self.lengthValue = QtGui.QLabel( "%d" % len(self.scan.x))
        self.layout_grid.addWidget( self.lengthValue, row, 1)
        #
        # xMin
        #
        row += 1
        self.xMinLabel = QtGui.QLabel( "xMin:")
        self.layout_grid.addWidget( self.xMinLabel, row, 0)
        self.xMinValue = QtGui.QLabel( "%g" % (self.scan.xMin))
        self.layout_grid.addWidget( self.xMinValue, row, 1)
        self.xMinLineEdit = QtGui.QLineEdit()
        self.xMinLineEdit.setMaximumWidth( 70)
        self.layout_grid.addWidget( self.xMinLineEdit, row, 2)
        #
        # xMax
        #
        self.xMaxLabel = QtGui.QLabel( "xMax:")
        self.layout_grid.addWidget( self.xMaxLabel, row, 3)
        self.xMaxValue = QtGui.QLabel( "%g" % (self.scan.xMax))
        self.layout_grid.addWidget( self.xMaxValue, row, 4)
        self.xMaxLineEdit = QtGui.QLineEdit()
        self.xMaxLineEdit.setMaximumWidth( 70)
        self.layout_grid.addWidget( self.xMaxLineEdit, row, 5)
        #
        # yMin
        #
        row += 1
        self.yMinLabel = QtGui.QLabel( "yMin:")
        self.layout_grid.addWidget( self.yMinLabel, row, 0)
        if self.scan.yMin is None:
            self.yMinValue = QtGui.QLabel( "None")
        else:
            self.yMinValue = QtGui.QLabel( "%g" % (self.scan.yMin))
        self.layout_grid.addWidget( self.yMinValue, row, 1)
        self.yMinLineEdit = QtGui.QLineEdit()
        self.yMinLineEdit.setMaximumWidth( 70)
        self.layout_grid.addWidget( self.yMinLineEdit, row, 2)
        #
        # yMax
        #
        self.yMaxLabel = QtGui.QLabel( "yMax:")
        self.layout_grid.addWidget( self.yMaxLabel, row, 3)
        if self.scan.yMax is None:
            self.yMaxValue = QtGui.QLabel( "None")
        else:
            self.yMaxValue = QtGui.QLabel( "%g" % (self.scan.yMax))
        self.layout_grid.addWidget( self.yMaxValue, row, 4)
        self.yMaxLineEdit = QtGui.QLineEdit()
        self.yMaxLineEdit.setMaximumWidth( 70)
        self.layout_grid.addWidget( self.yMaxLineEdit, row, 5)
        #
        # autorangeX
        #
        row += 1
        self.autorangeXLabel = QtGui.QLabel( "autorangeX:")
        self.layout_grid.addWidget( self.autorangeXLabel, row, 0)
        self.autorangeXCheckBox = QtGui.QCheckBox()
        self.autorangeXCheckBox.setChecked( self.scan.autorangeX)
        self.layout_grid.addWidget( self.autorangeXCheckBox, row, 1)
        self.autorangeXCheckBox.stateChanged.connect( self.cb_autorangeXChanged)
        #
        # autorangeY
        #
        self.autorangeYLabel = QtGui.QLabel( "autorangeY:")
        self.layout_grid.addWidget( self.autorangeYLabel, row, 3)
        self.autorangeYCheckBox = QtGui.QCheckBox()
        self.autorangeYCheckBox.setChecked( self.scan.autorangeY)
        self.layout_grid.addWidget( self.autorangeYCheckBox, row, 4)
        self.autorangeYCheckBox.stateChanged.connect( self.cb_autorangeYChanged)
        #
        # xLog
        #
        row += 1
        self.xLogLabel = QtGui.QLabel( "xLog:")
        self.layout_grid.addWidget( self.xLogLabel, row, 0)
        self.xLogCheckBox = QtGui.QCheckBox()
        self.xLogCheckBox.setChecked( self.scan.xLog)
        self.layout_grid.addWidget( self.xLogCheckBox, row, 1)
        self.xLogCheckBox.stateChanged.connect( self.cb_xLogChanged)
        #
        # yLog
        #
        self.yLogLabel = QtGui.QLabel( "yLog:")
        self.layout_grid.addWidget( self.yLogLabel, row, 3)
        self.yLogCheckBox = QtGui.QCheckBox()
        self.yLogCheckBox.setChecked( self.scan.yLog)
        self.layout_grid.addWidget( self.yLogCheckBox, row, 4)
        self.yLogCheckBox.stateChanged.connect( self.cb_yLogChanged)
        #
        # doty
        #
        row += 1
        self.dotyLabel = QtGui.QLabel( "DOTY")
        self.layout_grid.addWidget( self.dotyLabel, row, 0)
        self.w_dotyCheckBox = QtGui.QCheckBox()
        self.w_dotyCheckBox.setChecked( self.scan.doty)
        self.w_dotyCheckBox.setToolTip( "x-axis is day-of-the-year")
        self.layout_grid.addWidget( self.w_dotyCheckBox, row, 1) 
        self.w_dotyCheckBox.stateChanged.connect( self.cb_dotyChanged)
        #
        # GridX
        #
        row += 1
        self.gridXLabel = QtGui.QLabel( "GridX")
        self.layout_grid.addWidget( self.gridXLabel, row, 0)
        self.w_gridXCheckBox = QtGui.QCheckBox()
        self.w_gridXCheckBox.setChecked( self.scan.showGridX)
        self.layout_grid.addWidget( self.w_gridXCheckBox, row, 1) 
        self.w_gridXCheckBox.stateChanged.connect( self.cb_gridXChanged)
        #
        # GridY
        #
        self.gridYLabel = QtGui.QLabel( "GridY")
        self.layout_grid.addWidget( self.gridYLabel, row, 3)
        self.w_gridYCheckBox = QtGui.QCheckBox()
        self.w_gridYCheckBox.setChecked( self.scan.showGridY)
        self.layout_grid.addWidget( self.w_gridYCheckBox, row, 4) 
        self.w_gridYCheckBox.stateChanged.connect( self.cb_gridYChanged)
        #
        # lineColor
        #
        row += 1
        self.lineColorLabel = QtGui.QLabel( "LineColor")
        self.layout_grid.addWidget( self.lineColorLabel, row, 0)
        self.w_lineColorComboBox = QtGui.QComboBox()
        for lineColor in defs._lineColorArr:
            self.w_lineColorComboBox.addItem( lineColor)
        self.w_lineColorComboBox.setCurrentIndex( defs._lineColorDct[ self.scan.lineColor.upper()])
        self.w_lineColorComboBox.currentIndexChanged.connect( self.cb_lineColor)
        self.layout_grid.addWidget( self.w_lineColorComboBox, row, 1) 
        #
        # lineStyle
        #
        self.lineStyleLabel = QtGui.QLabel( "LineStyle")
        self.layout_grid.addWidget( self.lineStyleLabel, row, 2)
        self.w_lineStyleComboBox = QtGui.QComboBox()
        for lineStyle in defs._lineStyleArr:
            self.w_lineStyleComboBox.addItem( lineStyle)
        self.w_lineStyleComboBox.setCurrentIndex( defs._lineStyleDct[ self.scan.lineStyle.upper()])
        self.w_lineStyleComboBox.currentIndexChanged.connect( self.cb_lineStyle)
        self.layout_grid.addWidget( self.w_lineStyleComboBox, row, 3) 
        #
        # lineWidth
        #
        self.lineWidthLabel = QtGui.QLabel( "LineWidth")
        self.layout_grid.addWidget( self.lineWidthLabel, row, 4)
        self.w_lineWidthComboBox = QtGui.QComboBox()
        if str( self.scan.lineWidth) not in defs._lineWidthDct.keys():
            self.scan.lineWidth = 1.0
        for lineWidth in defs._lineWidthArr:
            self.w_lineWidthComboBox.addItem( lineWidth)
        self.w_lineWidthComboBox.setCurrentIndex( defs._lineWidthDct[ str( self.scan.lineWidth)])
        self.w_lineWidthComboBox.currentIndexChanged.connect( self.cb_lineWidth)
        self.layout_grid.addWidget( self.w_lineWidthComboBox, row, 5) 

        #
        # symbolColor
        #
        row += 1
        self.symbolColorLabel = QtGui.QLabel( "SymbolColor")
        self.layout_grid.addWidget( self.symbolColorLabel, row, 0)
        self.w_symbolColorComboBox = QtGui.QComboBox()
        if str( self.scan.symbolColor).upper() not in defs._lineColorDct.keys():
            self.scan.symbolColor = 'black'
        for symbolColor in defs._lineColorArr:
            self.w_symbolColorComboBox.addItem( symbolColor)
        self.w_symbolColorComboBox.setCurrentIndex( 
            defs._lineColorDct[ str( self.scan.symbolColor).upper()])
        self.w_symbolColorComboBox.currentIndexChanged.connect( self.cb_symbolColor)
        self.layout_grid.addWidget( self.w_symbolColorComboBox, row, 1) 
        #
        # symbol
        #
        self.symbolLabel = QtGui.QLabel( "Symbol")
        self.layout_grid.addWidget( self.symbolLabel, row, 2)
        self.w_symbolComboBox = QtGui.QComboBox()
        if str( self.scan.symbol) not in defs._symbolArr:
            self.scan.symbol = 'o'
        for symbol in defs._symbolArr:
            self.w_symbolComboBox.addItem( defs._symbolDctFullName[ str( symbol)])
        self.w_symbolComboBox.setCurrentIndex( defs._symbolDct[ str( self.scan.symbol)])
        self.w_symbolComboBox.currentIndexChanged.connect( self.cb_symbol)
        self.layout_grid.addWidget( self.w_symbolComboBox, row, 3) 
        #
        # symbolSize
        #
        self.symbolSizeLabel = QtGui.QLabel( "SymbolSize")
        self.layout_grid.addWidget( self.symbolSizeLabel, row, 4)
        self.w_symbolSizeComboBox = QtGui.QComboBox()
        if str( self.scan.symbolSize) not in defs._symbolSizeDct.keys():
            self.scan.symbolSize = 5
        for symbolSize in defs._symbolSizeArr:
            self.w_symbolSizeComboBox.addItem( symbolSize)
        self.w_symbolSizeComboBox.setCurrentIndex( 
            defs._symbolSizeDct[ str( self.scan.symbolSize)])
        self.w_symbolSizeComboBox.currentIndexChanged.connect( self.cb_symbolSize)
        self.layout_grid.addWidget( self.w_symbolSizeComboBox, row, 5) 
        #
        # overlay
        #
        row += 1
        self.overlayLabel = QtGui.QLabel( "Overlay")
        self.layout_grid.addWidget( self.overlayLabel, row, 0)
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
        self.layout_grid.addWidget( self.w_overlayComboBox, row, 1) 

    #
    # the menu bar
    #
    def prepareMenuBar( self): 

        self.fileMenu = self.menuBar.addMenu('&File')

        self.exitAction = QtGui.QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        #self.exitAction.triggered.connect( sys.exit)
        self.exitAction.triggered.connect( self.close)
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

        line = str(self.yMinLineEdit.text()).strip()
        if len(line) > 0: 
            if line.upper() == 'NONE':
                self.scan.yMin = None
                self.yMinValue.setText( "None")
            else:
                self.scan.yMin = float( line.strip())
                self.yMinValue.setText( "%g" % self.scan.yMin)
            self.yMinLineEdit.clear()

        line = str(self.yMaxLineEdit.text()).strip()
        if len(line) > 0: 
            if line.upper() == 'NONE':
                self.scan.yMax = None
                self.yMaxValue.setText( "None")
            else:
                self.scan.yMax = float( line.strip())
                self.yMaxValue.setText( "%g" % self.scan.yMax)
            self.yMaxLineEdit.clear()
        pysp.cls()
        pysp.display()
        
    def cb_lineColor( self): 
        temp = self.w_lineColorComboBox.currentText()
        self.scan.lineColor = str( temp)
        pysp.cls()
        pysp.display()
        return

    def cb_lineStyle( self): 
        temp = self.w_lineStyleComboBox.currentText()
        self.scan.lineStyle = str( temp)
        if self.scan.lineStyle == 'None': 
            self.scan.lineStyle = None
        pysp.cls()
        pysp.display()
        return

    def cb_lineWidth( self): 
        temp = self.w_lineWidthComboBox.currentText()
        self.scan.lineWidth = float( temp)
        pysp.cls()
        pysp.display()
        return

    def cb_symbolSize( self): 
        temp = self.w_symbolSizeComboBox.currentText()
        self.scan.symbolSize = int( temp)
        pysp.cls()
        pysp.display()
        return

    def cb_symbolColor( self): 
        temp = self.w_symbolColorComboBox.currentText()
        self.scan.symbolColor = str( temp)
        pysp.cls()
        pysp.display()
        return

    def cb_symbol( self): 
        temp = self.w_symbolComboBox.currentText()
        for k, v in defs._symbolDctFullName.items():
            if v == temp:
                temp = k
        self.scan.symbol = str( temp)
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
                "<h3> ScanAttributes Widget </h3>"
                "<ul>"
                "<li> Lines/markers are disabled by selecting the color NONE</li>"
                "<li> yMin/yMax are reset to None by entering 'None' into the LineEdit widgets.</li>"
                "<li> 'DOTY' is day-of-the-year, the x-axis ticks are date/time</li>"
                "<li> 'Overlay' selects the target scan, meaning that the current scan is displayed in the viewport of the target scan.</li>"
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
        mpl_graphics.cls()

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
        
        mpl_graphics._initGraphic( self.figure, self.canvas)

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
        self.exitAction.triggered.connect( self.close)
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
        mpl_graphics.cls()
        mpl_graphics.display()

    def cb_pdf( self): 
        fileName = mpl_graphics.createPDF()
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
    def __init__( self, files = None, parent = None, 
                  calledFromSardanaMonitor = False, 
                  flagExitOnClose = False):
        #print "pySpectraGui.__init__"
        super( pySpectraGui, self).__init__( parent)
        #
        # called from SardanaMonitor? If so, do not show motor list
        #
        self.calledFromSardanaMonitor = calledFromSardanaMonitor
        #
        # exitOnClose: there are applications that want to exit, if the Gui is closed
        #
        self.flagExitOnClose = flagExitOnClose
        
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
        self.mplWidget = None
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
        # create the logWidget here because it is need a few lines below
        #
        self.logWidget = QtGui.QTextEdit()

        #
        # the files ListWidget
        #
        vBox = QtGui.QVBoxLayout()
        self.dirNameLabel = QtGui.QLabel( "dirName")
        vBox.addWidget( self.dirNameLabel)
        self.scrollAreaFiles = QtGui.QScrollArea()
        vBox.addWidget( self.scrollAreaFiles)
        self.filesListWidget = QListWidgetTK( self, self.newPathSelected, "filesListWidget", self.logWidget)
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
        self.scansListWidget = QListWidgetTK( self, self.newScanSelected, "scansListWidget", self.logWidget)
        self.scrollAreaScans.setWidget( self.scansListWidget)
        hBox.addLayout( vBox)

        self.layout_v.addLayout( hBox)
        #
        # the log widget, has been created a few lines up
        #
        #self.logWidget = QtGui.QTextEdit()
        self.logWidget.setMaximumHeight( 100)
        self.logWidget.setReadOnly( 1)
        self.layout_v.addWidget( self.logWidget)
        #
        #
        #
        #self.a = {'text': ''}
        #self.console = EmbedIPython(testing=123, a=self.a)
        #self.layout_v.addWidget( self.console)
        #
        # motors and Macroserver
        #
        if self.calledFromSardanaMonitor: 
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
        hBox = QtGui.QHBoxLayout()

        self.lineEdit = QLineEditTK( self)
        hBox.addWidget( self.lineEdit)
        self.layout_frame_v.addLayout( hBox)
        QtCore.QObject.connect( self.lineEdit, 
                                QtCore.SIGNAL("returnPressed()"),self.cb_lineEdit)
        self.lineEdit.hide()
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
        elif pathNameTokens[-1] in defs._dataFormats:
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
            if fileNameTokens[-1] in defs._dataFormats:
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
            if fileNameTokens[-1] in defs._dataFormats:
                for pat in patternList:
                    if HasyUtils.match( file, pat): 
                        argout.append( file)
        return argout

    def cb_all( self): 
        pysp.cls()
        pysp.display()

    def cb_prev( self): 
        scan = gqe._prevScan()
        index = gqe._getIndex( scan.name)
        pysp.cls()
        pysp.display( [ scan.name])
        self.scansListWidget.setCurrentRow( index)

    def cb_next( self): 
        scan = gqe._nextScan()
        index = gqe._getIndex( scan.name)
        pysp.cls()
        pysp.display( [ scan.name])
        self.scansListWidget.setCurrentRow( index)

    def cb_lineEdit( self): 
        #+++pysp.ipython.ifc.command( str(self.lineEdit.text()))
        try: 
            exec str( self.lineEdit.text())
        except Exception, e:
            self.logWidget.append( "command: %s" % str( self.lineEdit.text()))
            self.logWidget.append( "caused the exception\n %s" % repr( e))
            
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

        self.createPDFAction = QtGui.QAction('Create PDF', self)        
        self.createPDFAction.setStatusTip('Create a PDF file')
        self.createPDFAction.triggered.connect( self.cb_createPDF)
        self.fileMenu.addAction( self.createPDFAction)

        self.createPDFPrintAction = QtGui.QAction('Create PDF and print', self)        
        self.createPDFPrintAction.setStatusTip('Create a PDF file and send it to PRINTER')
        self.createPDFPrintAction.triggered.connect( self.cb_createPDFPrint)
        self.fileMenu.addAction( self.createPDFPrintAction)

        if __builtin__.__dict__[ 'graphicsLib'] != 'matplotlib':
            self.matplotlibAction = QtGui.QAction('matplotlib', self)        
            self.matplotlibAction.setStatusTip('Launch matplotlib to create ps or pdf output')
            self.matplotlibAction.triggered.connect( self.cb_matplotlib)
            self.fileMenu.addAction( self.matplotlibAction)

        self.miscMenu = self.menuBar.addMenu('Misc')

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

        self.sl1Action = QtGui.QAction('1 Scan with texts', self)        
        self.sl1Action.triggered.connect( pysp.testCreate1)
        self.scanListsMenu.addAction( self.sl1Action)

        self.sl10Action = QtGui.QAction('2 overlaid Scans, Doty', self)        
        self.sl10Action.triggered.connect( pysp.testCreate2OverlayDoty)
        self.scanListsMenu.addAction( self.sl10Action)

        self.sl11Action = QtGui.QAction('2 overlaid Scans', self)        
        self.sl11Action.triggered.connect( pysp.testCreate2Overlay)
        self.scanListsMenu.addAction( self.sl11Action)

        self.sl2Action = QtGui.QAction('3 Scans, with textbox', self)        
        self.sl2Action.triggered.connect( pysp.testCreate3)
        self.scanListsMenu.addAction( self.sl2Action)

        self.sl3Action = QtGui.QAction('5 Scans', self)        
        self.sl3Action.triggered.connect( pysp.testCreate5)
        self.scanListsMenu.addAction( self.sl3Action)

        self.sl4Action = QtGui.QAction('10 Scans', self)        
        self.sl4Action.triggered.connect( pysp.testCreate10)
        self.scanListsMenu.addAction( self.sl4Action)

        self.sl5Action = QtGui.QAction('22 Scans', self)        
        self.sl5Action.triggered.connect( pysp.testCreate22)
        self.scanListsMenu.addAction( self.sl5Action)

        self.sl6Action = QtGui.QAction('56 Scans', self)        
        self.sl6Action.triggered.connect( pysp.testCreate56)
        self.scanListsMenu.addAction( self.sl6Action)

        self.sl7Action = QtGui.QAction('Gauss Scan', self)        
        self.sl7Action.triggered.connect( pysp.testCreateGauss)
        self.scanListsMenu.addAction( self.sl7Action)

        self.sl8Action = QtGui.QAction('Overlay', self)        
        self.sl8Action.triggered.connect( pysp.testCreateOverlaid)
        self.scanListsMenu.addAction( self.sl8Action)

        self.sl9Action = QtGui.QAction('Overlay, log', self)        
        self.sl9Action.triggered.connect( pysp.testCreateOverlaidWithLog)
        self.scanListsMenu.addAction( self.sl9Action)

        self.exitAction = QtGui.QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect( self.cb_close)
        self.fileMenu.addAction( self.exitAction)


        self.debugMenu = self.menuBar.addMenu('&Debug')

        self.execAction = QtGui.QAction('Python command line', self)        
        self.execAction.triggered.connect( self.cb_exec)
        self.debugMenu.addAction( self.execAction)

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

        self.showBtn = QtGui.QPushButton(self.tr("&Show")) 
        self.statusBar.addWidget( self.showBtn) 
        self.showBtn.clicked.connect( self.cb_show)
        self.showBtn.setToolTip( "Print info about the scans")
        self.showBtn.setShortcut( "Alt+s")

        if __builtin__.__dict__[ 'graphicsLib'] != 'matplotlib':
            self.matplotlibBtn = QtGui.QPushButton(self.tr("&Matplotlib")) 
            self.statusBar.addWidget( self.matplotlibBtn) 
            self.matplotlibBtn.clicked.connect( self.cb_matplotlib)
            self.matplotlibBtn.setToolTip( "Print info about the scans")
            self.matplotlibBtn.setShortcut( "Alt+m")

        #if __builtin__.__dict__[ 'graphicsLib'] == 'matplotlib':
        #    self.pdfBtn = QtGui.QPushButton(self.tr("&PDF")) 
        #    self.statusBar.addWidget( self.pdfBtn) 
        #    self.pdfBtn.clicked.connect( self.cb_pdf)
        #    self.pdfBtn.setShortcut( "Alt+p")
        #    self.pdfBtn.setToolTip( "Create PDF file")

        self.clearLog = QtGui.QPushButton(self.tr("&ClearLog")) 
        self.statusBar.addPermanentWidget( self.clearLog) # 'permanent' to shift it right
        self.clearLog.clicked.connect( self.cb_clearLog)
        self.clearLog.setToolTip( "Clear log widget")
        self.clearLog.setShortcut( "Alt+c")

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( self.cb_close)
        self.exit.setShortcut( "Alt+x")

    def cb_createPDF( self): 
        fName = pysp.createPDF()
        print "Created %s" % fName

    def cb_createPDFPrint( self): 
        pysp.createPDF( flagPrint = True)

    def cb_close( self): 
        pysp.close()
        if self.mplWidget is not None:
            self.mplWidget.close()
            self.mplWidget = None
        self.close()
        if self.flagExitOnClose:
            sys.exit( 0)

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

    def cb_show( self): 
        pysp.show()

    def cb_pdf( self): 
        fileName = mpl_graphics.createPDF()
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
        
    def cb_exec( self): 
        if self.lineEdit.isHidden(): 
            self.lineEdit.show()
        else:
            self.lineEdit.hide()
            

    def cb_derivative( self):
        displayList = gqe._getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append(  "cb_derivative: expecting 1 displayed scan")
            return 
        pysp.derivative( displayList[0].name)

    def cb_antiderivative( self):
        displayList = gqe._getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append(  "cb_antiderivative: expecting 1 displayed scan")
            return 
        pysp.antiderivative( displayList[0].name)

    def cb_y2my( self):
        displayList = gqe._getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append(  "cb_y2my: expecting 1 displayed scan")
            return 
        pysp.yToMinusY( displayList[0].name)

    def cb_ssa( self):
        displayList = gqe._getDisplayList()
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
        mpl_graphics.display( self.getCheckedNameList())

    def cb_helpWidget(self):
        QtGui.QMessageBox.about(self, self.tr("Help Widget"), self.tr(
                "<h3> PySpectraGui</h3>"
                "The Python Spectra Gui"
                "<ul>"
                "<li> some remarks</li>"
                "</ul>"
                ))
 
