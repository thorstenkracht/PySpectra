#!/usr/bin/env python
'''

This is the main PySpectra Gui class. It is used by pyspMonitor, pyspViewer. 
Both applications select the graphics library in their first code lines. 
'''

import sys, os, argparse, math, time
from PyQt4 import QtGui, QtCore
import numpy as np

import PySpectra 
import PySpectra.examples.exampleCode
import PySpectra.definitions as definitions
import PySpectra.calc as calc
import PySpectra.mtpltlb.graphics as mpl_graphics # for pdf output

from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

win = None
ACTIVITY_SYMBOLS = ['|', '/', '-', '\\', '|', '/', '-', '\\'] 

updateTime = 0.5
SLIDER_RESOLUTION = 256

HISTORY_MAX = 100


def make_cb_fsa_1( self, mode): 
    #
    # used from ScanAttributes()
    #
    def func(): 
        self.scan.fsa( mode = mode, logWidget = self.logWidget)
        PySpectra.cls()
        PySpectra.display( [ self.scan.name])
        return 
    return func

def make_cb_fsa_2( self, mode): 
    #
    # used from pySpectraGui()
    #
    def func(): 
        displayList = PySpectra.getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append( "cb_fsa_peak: expecting 1 displayed scan")
            return 
        scan = displayList[0]
        scan.fsa( mode = mode, logWidget = self.logWidget)

        PySpectra.cls()
        PySpectra.display( [scan.name])
        return 
    return func


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
            if self.parent.gqesListWidget.count() > 0:
                self.parent.gqesListWidget.setFocus()
                self.parent.gqesListWidget.setCurrentRow( 0)
        elif key == QtCore.Qt.Key_Down:
            pass
        elif key == QtCore.Qt.Key_Up:
            pass
        elif key == QtCore.Qt.Key_Return or key == 32:
            item = self.currentItem()
            #
            # the files list widget has no check boxes
            #
            if self.name == "gqesListWidget":
                if item.checkState() == QtCore.Qt.Checked:
                    item.setCheckState(QtCore.Qt.Unchecked)       
                else:
                    item.setCheckState(QtCore.Qt.Checked)       
            self.newItemSelected( str(item.text()))
            return 
        else: 
            print( "keyPressEvent, key %s" % repr(key))

        return QtGui.QListWidget.keyPressEvent(self, eventQKeyEvent)

    def cb_doubleClicked( self, item): 
        '''
        double click: reads a file
        '''

        if self.name == "filesListWidget":
            self.newItemSelected( str( item.text()))
        return 

    def mouseReleaseEvent( self, event): 
        '''
        left-MB:  change checkState of a scan
                  does not give the correct item, if 
                  the user clicked on the checkbox 
                  instead of the name
        right-MB: opens the attributesWidget
        '''
        if self.name == "filesListWidget":
            return 

        #
        # the following line is necessary because a click on  
        # a checkbox does not make the item the currentItem.
        # So we use the mouse position to find the currentItem
        #
        self.setCurrentItem( self.itemAt( event.pos()))
        if event.button() == QtCore.Qt.LeftButton:
            item = self.currentItem()
            if item is None: 
                print( "mouseReleaseEvent: click on the name")
                return 
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)       
            else:
                item.setCheckState(QtCore.Qt.Checked)       
            if item is not None:
                self.parent.displayChecked()
        if event.button() == QtCore.Qt.RightButton:
            item = self.currentItem()
            gqe = PySpectra.getGqe( item.text())
            if type( gqe) == PySpectra.Scan:
                if gqe.textOnly: 
                    self.logWidget.append( "%s is textOnly" % item.text())
                    return 
                self.scanAttributes = ScanAttributes( self.parent, item.text(), self.logWidget)
            elif type( gqe) == PySpectra.Image:
                self.imageAttributes = ImageAttributes( self.parent, item.text(), self.logWidget)
        return 
#
#
#
class PyQtConfig( QtGui.QMainWindow):
    def __init__( self, parent = None):
        super( PyQtConfig, self).__init__( parent)
        self.parent = parent

        self.setWindowTitle( "PyQtConfig")
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
        self.layout_grid.addWidget( QtGui.QLabel( "Margins:"), row, 0)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Left:"), row, 1)
        self.marginLeft = QtGui.QLabel( "%g" % definitions.marginLeft)
        self.layout_grid.addWidget( self.marginLeft, row, 2)
        self.marginLeftLineEdit = QtGui.QLineEdit()
        self.marginLeftLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.marginLeftLineEdit, row, 3)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Top:"), row, 1)
        self.marginTop = QtGui.QLabel( "%g" % definitions.marginTop)
        self.layout_grid.addWidget( self.marginTop, row, 2)
        self.marginTopLineEdit = QtGui.QLineEdit()
        self.marginTopLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.marginTopLineEdit, row, 3)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Right:"), row, 1)
        self.marginRight = QtGui.QLabel( "%g" % definitions.marginRight)
        self.layout_grid.addWidget( self.marginRight, row, 2)
        self.marginRightLineEdit = QtGui.QLineEdit()
        self.marginRightLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.marginRightLineEdit, row, 3)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Bottom:"), row, 1)
        self.marginBottom = QtGui.QLabel( "%g" % definitions.marginBottom)
        self.layout_grid.addWidget( self.marginBottom, row, 2)
        self.marginBottomLineEdit = QtGui.QLineEdit()
        self.marginBottomLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.marginBottomLineEdit, row, 3)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Spacing:"), row, 0)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Horizontal:"), row, 1)
        self.spacingHorizontal = QtGui.QLabel( "%g" % definitions.spacingHorizontal)
        self.layout_grid.addWidget( self.spacingHorizontal, row, 2)
        self.spacingHorizontalLineEdit = QtGui.QLineEdit()
        self.spacingHorizontalLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.spacingHorizontalLineEdit, row, 3)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Vertical:"), row, 1)
        self.spacingVertical = QtGui.QLabel( "%g" % definitions.spacingVertical)
        self.layout_grid.addWidget( self.spacingVertical, row, 2)
        self.spacingVerticalLineEdit = QtGui.QLineEdit()
        self.spacingVerticalLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.spacingVerticalLineEdit, row, 3)

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

        self.helpWidgetAction = self.helpMenu.addAction(self.tr("Widget"))
        self.helpWidgetAction.triggered.connect( self.cb_helpWidget)

        self.activityIndex = 0
        self.activity = self.menuBarActivity.addMenu( "_")

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
                
    def cb_apply( self):
        line = str(self.marginLeftLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.marginLeft = float( line.strip())
            self.marginLeft.setText( "%g" % definitions.marginLeft)
            self.marginLeftLineEdit.clear()
        line = str(self.marginTopLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.marginTop = float( line.strip())
            self.marginTop.setText( "%g" % definitions.marginTop)
            self.marginTopLineEdit.clear()
        line = str(self.marginRightLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.marginRight = float( line.strip())
            self.marginRight.setText( "%g" % definitions.marginRight)
            self.marginRightLineEdit.clear()
        line = str(self.marginBottomLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.marginBottom = float( line.strip())
            self.marginBottom.setText( "%g" % definitions.marginBottom)
            self.marginBottomLineEdit.clear()

        line = str(self.spacingHorizontalLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.spacingHorizontal = float( line.strip())
            self.spacingHorizontal.setText( "%g" % definitions.spacingHorizontal)
            self.spacingHorizontalLineEdit.clear()
        line = str(self.spacingVerticalLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.spacingVertical = float( line.strip())
            self.spacingVertical.setText( "%g" % definitions.spacingVertical)
            self.spacingVerticalLineEdit.clear()

        PySpectra.configGraphics()
        PySpectra.cls()
        PySpectra.display()
        
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
        PySpectra.cls()
        PySpectra.display()#

    def cb_helpWidget(self):
        QtGui.QMessageBox.about(self, self.tr("Help Widget"), self.tr(
                "<h3> PyQt Configuration </h3>"
                "<ul>"
                "<li> Margins (left, top, etc.): the margins around the plots</li>"
                "<li> Spacing (hor., vert.): the spacing between the plots </li>"
                "</ul>"
                ))

#
#
class Config( QtGui.QMainWindow):
    def __init__( self, parent = None):
        super( Config, self).__init__( parent)
        self.parent = parent

        self.setWindowTitle( "Config")
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
        self.layout_grid.addWidget( QtGui.QLabel( "Font sizes:"), row, 0)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Normal:"), row, 1)
        self.fontNormal = QtGui.QLabel( "%d" % definitions.FONT_SIZE_NORMAL)
        self.layout_grid.addWidget( self.fontNormal, row, 2)
        self.fontNormalLineEdit = QtGui.QLineEdit()
        self.fontNormalLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.fontNormalLineEdit, row, 3)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Small:"), row, 1)
        self.fontSmall = QtGui.QLabel( "%d" % definitions.FONT_SIZE_SMALL)
        self.layout_grid.addWidget( self.fontSmall, row, 2)
        self.fontSmallLineEdit = QtGui.QLineEdit()
        self.fontSmallLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.fontSmallLineEdit, row, 3)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "VerySmall:"), row, 1)
        self.fontVerySmall = QtGui.QLabel( "%d" % definitions.FONT_SIZE_VERY_SMALL)
        self.layout_grid.addWidget( self.fontVerySmall, row, 2)
        self.fontVerySmallLineEdit = QtGui.QLineEdit()
        self.fontVerySmallLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.fontVerySmallLineEdit, row, 3)

        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Tick sizes:"), row, 0)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Normal:"), row, 1)
        self.tickFontNormal = QtGui.QLabel( "%d" % definitions.TICK_FONT_SIZE_NORMAL)
        self.layout_grid.addWidget( self.tickFontNormal, row, 2)
        self.tickFontNormalLineEdit = QtGui.QLineEdit()
        self.tickFontNormalLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.tickFontNormalLineEdit, row, 3)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "Small:"), row, 1)
        self.tickFontSmall = QtGui.QLabel( "%d" % definitions.TICK_FONT_SIZE_SMALL)
        self.layout_grid.addWidget( self.tickFontSmall, row, 2)
        self.tickFontSmallLineEdit = QtGui.QLineEdit()
        self.tickFontSmallLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.tickFontSmallLineEdit, row, 3)
        row += 1
        self.layout_grid.addWidget( QtGui.QLabel( "VerySmall:"), row, 1)
        self.tickFontVerySmall = QtGui.QLabel( "%d" % definitions.TICK_FONT_SIZE_VERY_SMALL)
        self.layout_grid.addWidget( self.tickFontVerySmall, row, 2)
        self.tickFontVerySmallLineEdit = QtGui.QLineEdit()
        self.tickFontVerySmallLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.tickFontVerySmallLineEdit, row, 3)

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
        self.activity = self.menuBarActivity.addMenu( "_")

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

    def cb_apply( self):
        line = str(self.fontNormalLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.FONT_SIZE_NORMAL = int( line.strip())
            self.fontNormal.setText( "%d" % definitions.FONT_SIZE_NORMAL)
            self.fontNormalLineEdit.clear()
        line = str(self.fontSmallLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.FONT_SIZE_SMALL = int( line.strip())
            self.fontSmall.setText( "%d" % definitions.FONT_SIZE_SMALL)
            self.fontSmallLineEdit.clear()
        line = str(self.fontVerySmallLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.FONT_SIZE_VERY_SMALL = int( line.strip())
            self.fontVerySmall.setText( "%d" % definitions.FONT_SIZE_VERY_SMALL)
            self.fontVerySmallLineEdit.clear()

        line = str(self.tickFontNormalLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.TICK_FONT_SIZE_NORMAL = int( line.strip())
            self.tickFontNormal.setText( "%d" % definitions.TICK_FONT_SIZE_NORMAL)
            self.tickFontNormalLineEdit.clear()
        line = str(self.tickFontSmallLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.TICK_FONT_SIZE_SMALL = int( line.strip())
            self.tickFontSmall.setText( "%d" % definitions.TICK_FONT_SIZE_SMALL)
            self.tickFontSmallLineEdit.clear()
        line = str(self.tickFontVerySmallLineEdit.text())
        if len(line.strip()) > 0: 
            definitions.TICK_FONT_SIZE_VERY_SMALL = int( line.strip())
            self.tickFontVerySmall.setText( "%d" % definitions.TICK_FONT_SIZE_VERY_SMALL)
            self.tickFontVerySmallLineEdit.clear()

        PySpectra.cls()
        PySpectra.display()
        
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
        PySpectra.cls()
        PySpectra.display()

    def cb_helpWidget(self):
        QtGui.QMessageBox.about(self, self.tr("Help Widget"), self.tr(
                "<h3> PyQt Configuration </h3>"
                "<ul>"
                "<li> 'Font sizes': normal/small/verySmall, these font sizes are used for texts, if several plots, many plots or very many plots are displayed.</li>"
                "<li> 'Tick sizes': normal/small/verySmall, these sizes are used for tick labels, if several plots, many plots or very many plots are displayed.</li>"
                "</ul>"
                ))
#
#
#
class ScanAttributes( QtGui.QMainWindow):

    objectCounter = 0
    def __init__( self, parent = None, name = None, logWidget = None):
        super( ScanAttributes, self).__init__( parent)
        ScanAttributes.objectCounter += 1
        self.parent = parent

        if name is None:
            raise ValueError( "pyspFio.ScanAttributes: name not specified")
        self.name = name
        self.logWidget = logWidget
        self.scan = PySpectra.getGqe( self.name)
        self.scan.attributeWidget = self
        self.scan.flagDisplayVLines = False
        PySpectra.cls()
        PySpectra.display( [self.name])
        #self.setWindowTitle( "ScanAttributes")
        self.setWindowTitle( name)

        self.prepareWidgets()

        self.menuBar = QtGui.QMenuBar()
        self.setMenuBar( self.menuBar)
        self.prepareMenuBar()
        #
        # we cannot set the geometry because we can have multiple 
        #
        if ScanAttributes.objectCounter == 1: 
            geoWin = self.geometry()
            geo = QtGui.QDesktopWidget().screenGeometry(-1)
            self.setGeometry( geo.width() - 710, 600, geoWin.width(), geoWin.height())

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
        
    def __del__( self): 
        print( "the destructor")
        return 

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
        # xLabel
        #
        self.xLabel = QtGui.QLabel( "xLabel:")
        self.layout_grid.addWidget( self.xLabel, row, 2)
        self.xValue = QtGui.QLabel( self.scan.xLabel)
        self.layout_grid.addWidget( self.xValue, row, 3)
        #
        # mouse
        #
        #self.mouseLabel = QtGui.QLabel( "Mouse")
        #self.mouseLabel.setAlignment( QtCore.Qt.AlignRight)
        #self.layout_grid.addWidget( self.mouseLabel, row, 3)
        self.mouseLabelX = QtGui.QLabel( "")
        self.mouseLabelX.setMinimumWidth( 90)
        self.layout_grid.addWidget( self.mouseLabelX, row, 4)
        self.mouseLabelY = QtGui.QLabel( "")
        self.mouseLabelY.setMinimumWidth( 90)
        self.layout_grid.addWidget( self.mouseLabelY, row, 5)
        self.scan.cb_mouseLabel = self.cb_mouseLabel
        #
        # length
        #
        row += 1
        self.lengthLabel = QtGui.QLabel( "Length:")
        self.layout_grid.addWidget( self.lengthLabel, row, 0)
        self.lengthValue = QtGui.QLabel( "%d" % len(self.scan.x))
        self.layout_grid.addWidget( self.lengthValue, row, 1)
        #
        # currentIndex
        #
        self.currentIndexLabel = QtGui.QLabel( "Current/LastIndex:")
        self.currentIndexLabel.setToolTip( "CurrentIndex refers to the last valid x-, y-values (Np == CurrentIndex + 1)")
        self.layout_grid.addWidget( self.currentIndexLabel, row, 2)
        self.currentIndexValue = QtGui.QLabel( "%d/%d" % (self.scan.currentIndex, self.scan.lastIndex))
        self.layout_grid.addWidget( self.currentIndexValue, row, 3)
        #
        # sum
        #
        self.sumLabel = QtGui.QLabel( "Sum:")
        self.sumLabel.setToolTip( "Sum of the y-values")
        self.layout_grid.addWidget( self.sumLabel, row, 4)
        self.sumValue = QtGui.QLabel( "%g" % (self.scan.getTotalCounts()))
        self.layout_grid.addWidget( self.sumValue, row, 5)
        #
        # xMin
        #
        row += 1
        self.xMinLabel = QtGui.QLabel( "xMin:")
        self.layout_grid.addWidget( self.xMinLabel, row, 0)
        self.xMinValue = QtGui.QLabel( "%g" % (self.scan.xMin))
        self.layout_grid.addWidget( self.xMinValue, row, 1)
        self.xMinLineEdit = QtGui.QLineEdit()
        self.xMinLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.xMinLineEdit, row, 2)
        #
        # xMax
        #
        self.xMaxLabel = QtGui.QLabel( "xMax:")
        self.layout_grid.addWidget( self.xMaxLabel, row, 3)
        self.xMaxValue = QtGui.QLabel( "%g" % (self.scan.xMax))
        self.layout_grid.addWidget( self.xMaxValue, row, 4)
        self.xMaxLineEdit = QtGui.QLineEdit()
        self.xMaxLineEdit.setMinimumWidth( 50)
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
        self.yMinLineEdit.setMinimumWidth( 50)
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
        self.yMaxLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.yMaxLineEdit, row, 5)
        #
        # autoscaleX
        #
        row += 1
        self.autoscaleXLabel = QtGui.QLabel( "autoscaleX:")
        self.layout_grid.addWidget( self.autoscaleXLabel, row, 0)
        self.autoscaleXCheckBox = QtGui.QCheckBox()
        self.autoscaleXCheckBox.setChecked( self.scan.autoscaleX)
        self.layout_grid.addWidget( self.autoscaleXCheckBox, row, 1)
        self.autoscaleXCheckBox.stateChanged.connect( self.cb_autoscaleXChanged)
        #
        # autoscaleY
        #
        self.autoscaleYLabel = QtGui.QLabel( "autoscaleY:")
        self.layout_grid.addWidget( self.autoscaleYLabel, row, 3)
        self.autoscaleYCheckBox = QtGui.QCheckBox()
        self.autoscaleYCheckBox.setChecked( self.scan.autoscaleY)
        self.layout_grid.addWidget( self.autoscaleYCheckBox, row, 4)
        self.autoscaleYCheckBox.stateChanged.connect( self.cb_autoscaleYChanged)
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
        # at
        #
        self.atLabel = QtGui.QLabel( "at:")
        self.layout_grid.addWidget( self.atLabel, row, 3)
        self.atValue = QtGui.QLabel( "%s" % (str(self.scan.at)))
        self.layout_grid.addWidget( self.atValue, row, 4)
        self.atLineEdit = QtGui.QLineEdit()
        self.atLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.atLineEdit, row, 5)
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
        for lineColor in definitions.colorArr:
            self.w_lineColorComboBox.addItem( lineColor)
        self.w_lineColorComboBox.setCurrentIndex( definitions.colorDct[ self.scan.lineColor.upper()])
        self.w_lineColorComboBox.currentIndexChanged.connect( self.cb_lineColor)
        self.layout_grid.addWidget( self.w_lineColorComboBox, row, 1) 
        #
        # lineStyle
        #
        self.lineStyleLabel = QtGui.QLabel( "LineStyle")
        self.layout_grid.addWidget( self.lineStyleLabel, row, 2)
        self.w_lineStyleComboBox = QtGui.QComboBox()
        for lineStyle in definitions.lineStyleArr:
            self.w_lineStyleComboBox.addItem( lineStyle)
        self.w_lineStyleComboBox.setCurrentIndex( definitions.lineStyleDct[ self.scan.lineStyle.upper()])
        self.w_lineStyleComboBox.currentIndexChanged.connect( self.cb_lineStyle)
        self.layout_grid.addWidget( self.w_lineStyleComboBox, row, 3) 
        #
        # lineWidth
        #
        self.lineWidthLabel = QtGui.QLabel( "LineWidth")
        self.layout_grid.addWidget( self.lineWidthLabel, row, 4)
        self.w_lineWidthComboBox = QtGui.QComboBox()
        if str( self.scan.lineWidth) not in list( definitions.lineWidthDct.keys()):
            self.scan.lineWidth = 1.0
        for lineWidth in definitions.lineWidthArr:
            self.w_lineWidthComboBox.addItem( lineWidth)
        self.w_lineWidthComboBox.setCurrentIndex( definitions.lineWidthDct[ str( self.scan.lineWidth)])
        self.w_lineWidthComboBox.currentIndexChanged.connect( self.cb_lineWidth)
        self.layout_grid.addWidget( self.w_lineWidthComboBox, row, 5) 

        #
        # symbolColor
        #
        row += 1
        self.symbolColorLabel = QtGui.QLabel( "SymbolColor")
        self.layout_grid.addWidget( self.symbolColorLabel, row, 0)
        self.w_symbolColorComboBox = QtGui.QComboBox()
        if str( self.scan.symbolColor).upper() not in list(definitions.colorDct.keys()):
            self.scan.symbolColor = 'black'
        for symbolColor in definitions.colorArr:
            self.w_symbolColorComboBox.addItem( symbolColor)
        self.w_symbolColorComboBox.setCurrentIndex( 
            definitions.colorDct[ str( self.scan.symbolColor).upper()])
        self.w_symbolColorComboBox.currentIndexChanged.connect( self.cb_symbolColor)
        self.layout_grid.addWidget( self.w_symbolColorComboBox, row, 1) 
        #
        # symbol
        #
        self.symbolLabel = QtGui.QLabel( "Symbol")
        self.layout_grid.addWidget( self.symbolLabel, row, 2)
        self.w_symbolComboBox = QtGui.QComboBox()
        if str( self.scan.symbol) not in definitions.symbolArr:
            self.scan.symbol = 'o'
        for symbol in definitions.symbolArr:
            self.w_symbolComboBox.addItem( definitions.symbolDctFullName[ str( symbol)])
        self.w_symbolComboBox.setCurrentIndex( definitions.symbolDct[ str( self.scan.symbol)])
        self.w_symbolComboBox.currentIndexChanged.connect( self.cb_symbol)
        self.layout_grid.addWidget( self.w_symbolComboBox, row, 3) 
        #
        # symbolSize
        #
        self.symbolSizeLabel = QtGui.QLabel( "SymbolSize")
        self.layout_grid.addWidget( self.symbolSizeLabel, row, 4)
        self.w_symbolSizeComboBox = QtGui.QComboBox()
        if str( self.scan.symbolSize) not in list( definitions.symbolSizeDct.keys()):
            self.scan.symbolSize = 5
        for symbolSize in definitions.symbolSizeArr:
            self.w_symbolSizeComboBox.addItem( symbolSize)
        self.w_symbolSizeComboBox.setCurrentIndex( 
            definitions.symbolSizeDct[ str( self.scan.symbolSize)])
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
        for scan in PySpectra.getGqeList(): 
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
        # useTargetWindow
        #
        self.useTargetWindowLabel = QtGui.QLabel( "UseTargetWindow")
        self.useTargetWindowLabel.setToolTip( "Use the yMin, yMax of target scan")
        self.layout_grid.addWidget( self.useTargetWindowLabel, row, 2)
        self.w_useTargetWindowCheckBox = QtGui.QCheckBox()
        self.w_useTargetWindowCheckBox.setChecked( self.scan.useTargetWindow)
        self.layout_grid.addWidget( self.w_useTargetWindowCheckBox, row, 3) 
        self.w_useTargetWindowCheckBox.stateChanged.connect( self.cb_useTargetWindowChanged)

    #
    # the menu bar
    #
    def prepareMenuBar( self): 

        self.fileMenu = self.menuBar.addMenu('&File')

        self.showTextsAction = QtGui.QAction('ShowTexts', self)        
        self.showTextsAction.setStatusTip('Show the texts belonging to this GQE')
        self.showTextsAction.triggered.connect( self.cb_showTexts)
        self.fileMenu.addAction( self.showTextsAction)

        self.exitAction = QtGui.QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        #self.exitAction.triggered.connect( sys.exit)
        self.exitAction.triggered.connect( self.cb_close)
        self.fileMenu.addAction( self.exitAction)


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

        for mode in definitions.fsaModes:
            qa = QtGui.QAction('FSA(%s)' % mode, self)        
            qa.triggered.connect( make_cb_fsa_1( self, mode))
            self.utilsMenu.addAction( qa)

        self.detailsAction = QtGui.QAction('Details', self)        
        self.detailsAction.triggered.connect( self.cb_details)
        self.utilsMenu.addAction( self.detailsAction)


        #
        # the activity menubar: help and activity
        #
        self.menuBarActivity = QtGui.QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarActivity, QtCore.Qt.TopRightCorner)

        #
        # Help menu (bottom part)
        #
        self.helpMenu = self.menuBarActivity.addMenu('Help')

        self.helpScanAttributesAction = self.helpMenu.addAction(self.tr("Scan Attributes"))
        self.helpScanAttributesAction.triggered.connect( self.cb_helpScanAttributes)

        self.helpSymbolsAction = self.helpMenu.addAction(self.tr("Symbols"))
        self.helpSymbolsAction.triggered.connect( self.cb_helpSymbols)

        self.activityIndex = 0
        self.activity = self.menuBarActivity.addMenu( "_")

    #
    # the status bar
    #
    def prepareStatusBar( self): 

        self.back = QtGui.QPushButton(self.tr("&Back")) 
        self.statusBar.addPermanentWidget( self.back) # 'permanent' to shift it right
        self.back.setToolTip( "Select previous GQE")
        self.back.clicked.connect( self.cb_back)
        self.back.setShortcut( "Alt+b")

        self.next = QtGui.QPushButton(self.tr("&Next")) 
        self.statusBar.addPermanentWidget( self.next) # 'permanent' to shift it right
        self.next.setToolTip( "Select next GQE")
        self.next.clicked.connect( self.cb_next)
        self.next.setShortcut( "Alt+n")

        self.vlines = QtGui.QPushButton(self.tr("VLines")) 
        self.vlines.setToolTip( "Display vertical lines, used by SSA")
        self.statusBar.addPermanentWidget( self.vlines) # 'permanent' to shift it right
        self.vlines.clicked.connect( self.cb_vlines)
        self.vlines.setShortcut( "Alt+v")
       
        #self.showScan = QtGui.QPushButton(self.tr("Show")) 
        #self.showScan.setToolTip( "Prints a list i, x, y")
        #self.statusBar.addPermanentWidget( self.showScan) # 'permanent' to shift it right
        #self.showScan.clicked.connect( self.cb_showScan)

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
        self.exit.clicked.connect( self.cb_close)
        self.exit.setShortcut( "Alt+x")


    def cb_next( self): 
        nextScan = PySpectra.nextScan( self.name)
        index = PySpectra.getIndex( nextScan.name)
        self.name = nextScan.name
        self.scan = nextScan
        PySpectra.cls()
        PySpectra.display( [ self.name])
        self.parent.gqesListWidget.setCurrentRow( index)
        return 

    def cb_back( self): 
        prevScan = PySpectra.prevScan( self.name)
        index = PySpectra.getIndex( prevScan.name)
        self.name = prevScan.name
        self.scan = prevScan
        PySpectra.cls()
        PySpectra.display( [ self.name])
        self.parent.gqesListWidget.setCurrentRow( index)

    def cb_mouseLabel( self, x, y): 
        self.mouseLabelX.setText( "x: %g" % (x))
        self.mouseLabelY.setText( "y: %g" % (y))

    def cb_vlines( self): 
        if self.scan.flagDisplayVLines: 
            self.scan.flagDisplayVLines = False
        else:
            self.scan.flagDisplayVLines = True
        PySpectra.cls()
        PySpectra.display( [self.scan.name])

    def cb_derivative( self):
        calc.derivative( self.scan.name)

    def cb_antiderivative( self):
        calc.antiderivative( self.scan.name)

    def cb_y2my( self):
        calc.yToMinusY( self.scan.name)

    def cb_showTexts( self): 
        if len( self.scan.textList) == 0:
            self.logWidget.append( "%s has no texts" % self.scan.name)
            return 
        self.logWidget.append( "Texts of %s" % self.scan.name)
        for t in self.scan.textList:
            self.logWidget.append( "  '%s' at %g %g" % (t.text, t.x, t.y))
        return 
            
    def cb_close( self): 
        ScanAttributes.objectCounter -= 1
        self.close()
        return
        
    def cb_autoscaleXChanged( self): 
        self.scan.autoscaleX = self.autoscaleXCheckBox.isChecked()
        PySpectra.cls()
        PySpectra.display( [self.name])

    def cb_autoscaleYChanged( self): 
        self.scan.autoscaleY = self.autoscaleYCheckBox.isChecked()
        PySpectra.cls()
        PySpectra.display( [self.name])

    def cb_xLogChanged( self): 
        self.scan.xLog = self.xLogCheckBox.isChecked()
        PySpectra.cls()
        PySpectra.display( [self.name])

    def cb_yLogChanged( self): 
        self.scan.yLog = self.yLogCheckBox.isChecked()
        PySpectra.cls()
        PySpectra.display( [self.name])

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

        line = str(self.atLineEdit.text())
        if len(line.strip()) > 0: 
            line = line.strip()
            if line == 'None':
                self.scan.at = None
            else:
                lstStr = line[1:-1].split( ',')
                if len( lstStr) == 3:
                    self.scan.at = [int( i) for i in lstStr]
                else: 
                    self.scan.at = [1, 1, 1]
                    self.atValue.setText( "[%d, %d, %d]" % (self.scan.at[0], self.scan.at[1], self.scan.at[2]))
        self.atLineEdit.clear()
        PySpectra.cls()
        PySpectra.display( self.parent.getCheckedNameList())
        
    def cb_lineColor( self): 
        temp = self.w_lineColorComboBox.currentText()
        self.scan.lineColor = str( temp)
        PySpectra.cls()
        PySpectra.display( [ self.name])
        return

    def cb_lineStyle( self): 
        temp = self.w_lineStyleComboBox.currentText()
        self.scan.lineStyle = str( temp)
        if self.scan.lineStyle == 'None': 
            self.scan.lineStyle = None
        PySpectra.cls()
        PySpectra.display( [ self.name])
        return

    def cb_lineWidth( self): 
        temp = self.w_lineWidthComboBox.currentText()
        self.scan.lineWidth = float( temp)
        PySpectra.cls()
        PySpectra.display( [ self.name])
        return

    def cb_symbolSize( self): 
        temp = self.w_symbolSizeComboBox.currentText()
        self.scan.symbolSize = int( temp)
        PySpectra.cls()
        PySpectra.display( [ self.name])
        return

    def cb_symbolColor( self): 
        temp = self.w_symbolColorComboBox.currentText()
        self.scan.symbolColor = str( temp)
        PySpectra.cls()
        PySpectra.display( [ self.name])
        return

    def cb_symbol( self): 
        temp = self.w_symbolComboBox.currentText()
        for k, v in list( definitions.symbolDctFullName.items()):
            if v == temp:
                temp = k
        self.scan.symbol = str( temp)
        PySpectra.cls()
        PySpectra.display( [ self.name])
        return

    def cb_overlay( self): 
        temp = str( self.w_overlayComboBox.currentText())
        if temp.lower() == 'none': 
            temp = None
        self.scan.overlay = temp
        PySpectra.cls()
        PySpectra.display( [ self.name])
        return
        
    def cb_refreshAttr( self):

        if self.isMinimized(): 
            return
        
        self.activityIndex += 1
        if self.activityIndex > (len( ACTIVITY_SYMBOLS) - 1):
            self.activityIndex = 0
        self.activity.setTitle( ACTIVITY_SYMBOLS[ self.activityIndex])
        self.updateTimer.stop()

        self.nameValue.setText( self.name)
        if self.scan.xLabel is not None: 
            self.xValue.setText( self.scan.xLabel)
        self.lengthValue.setText( "%d" % len( self.scan.x))
        self.currentIndexValue.setText( "%d/%d" % (self.scan.currentIndex, self.scan.lastIndex))
        self.sumValue.setText( "%g" % (self.scan.getTotalCounts()))
        self.xMinValue.setText( "%g" % self.scan.xMin)
        self.xMaxValue.setText( "%g" % self.scan.xMax)
        if self.scan.yMin is None:
            self.yMinValue.setText( "None")
        else:
            self.yMinValue.setText( "%g" % self.scan.yMin)
        if self.scan.yMax is None:
            self.yMaxValue.setText( "None")
        else:
            self.yMaxValue.setText( "%g" % self.scan.yMax)

        self.autoscaleXCheckBox.setChecked( self.scan.autoscaleX)
        self.autoscaleYCheckBox.setChecked( self.scan.autoscaleY)

        self.xLogCheckBox.setChecked( self.scan.xLog)
        self.yLogCheckBox.setChecked( self.scan.yLog)

        self.w_dotyCheckBox.setChecked( self.scan.doty)

        self.w_lineStyleComboBox.setCurrentIndex( definitions.lineStyleDct[ self.scan.lineStyle.upper()])
        self.w_lineWidthComboBox.setCurrentIndex( definitions.lineWidthDct[ str( self.scan.lineWidth)])

        self.w_symbolColorComboBox.setCurrentIndex( 
            definitions.colorDct[ str( self.scan.symbolColor).upper()])
        self.w_symbolComboBox.setCurrentIndex( definitions.symbolDct[ str( self.scan.symbol)])
        self.w_symbolSizeComboBox.setCurrentIndex( 
            definitions.symbolSizeDct[ str( self.scan.symbolSize)])

        self.atValue.setText( "%s" % (str(self.scan.at)))

        #self.w_gridXCheckBox.setCheckState( self.scan.showGridX) 
        #self.w_gridYCheckBox.setCheckState( self.scan.showGridY) 
        self.updateTimer.start( int( updateTime*1000))

    def cb_ssa( self): 
        self.scan.ssa( self.parent.logWidget)
        PySpectra.cls()
        PySpectra.display( [ self.scan.name])

    def cb_details( self): 
        print( "\n %s " % self.scan.name)
        print( "arrowCurrent %s" % repr( self.scan.arrowCurrent))
        print( "labelArrowCurrent %s" % repr( self.scan.labelArrowCurrent))
        print( "arrowSetPoint %s" % repr( self.scan.arrowSetPoint))
        print( "infLineMouseX %s" % repr( self.scan.infLineMouseX))
        print( "infLineMouseY %s" % repr( self.scan.infLineMouseY))
        print( "infLineLeft %s" % repr( self.scan.infLineLeft))
        print( "infLineRight %s" % repr( self.scan.infLineRight))
        return 

    def cb_showScan( self): 
        print( "showScan: %s " % self.scan.name)
        for i in range( 0, self.scan.currentIndex + 1): 
            print( "%5d %15g %15g " % ( i, self.scan.x[i], self.scan.y[i]))
        if self.scan.motorNameList is not None and len( self.scan.motorNameList) > 0:
            print( "\nmotorNameList: %s" % repr( self.scan.motorNameList) )
        return 

    def cb_display( self): 
        PySpectra.cls()
        PySpectra.display()

    def cb_helpScanAttributes(self):
        QtGui.QMessageBox.about(self, self.tr("Help Scan Attributes"), self.tr(
                "<h3> Scan Attributes </h3>"
                "<ul>"
                "<li> Lines/markers are disabled by selecting the color NONE</li>"
                "<li> yMin/yMax are reset to None by entering 'None' into the LineEdit widgets.</li>"
                "<li> 'DOTY' is day-of-the-year, the x-axis ticks are date/time</li>"
                "<li> 'Overlay' selects the target scan, meaning that the current scan is displayed in the viewport of the target scan.</li>"
                "<li> 'at' makes sense for matplotlib only.</li>"
                "</ul>"
                ))

    def cb_helpSymbols(self):
        QtGui.QMessageBox.about(self, self.tr("Help Symbols"), self.tr(
                "<h3> Symbols </h3>"
                "<ul>"
                "<li> '+' plus</li>"
                "<li> 's' square</li>"
                "<li> 'd' diamond</li>"
                "<li> 'o' circle</li>"
                "</ul>"
                ))

    def cb_dotyChanged( self):
        self.scan.doty = self.w_dotyCheckBox.isChecked()
        PySpectra.cls()
        PySpectra.display( [ self.scan.name])
        return 

    def cb_useTargetWindowChanged( self):
        self.scan.useTargetWindow = self.w_useTargetWindowCheckBox.isChecked()
        PySpectra.cls()
        PySpectra.display( [ self.scan.name])
        return 

    def cb_gridXChanged( self):
        self.scan.showGridX = self.w_gridXCheckBox.isChecked()
        PySpectra.cls()
        PySpectra.display( [ self.scan.name])
        return 

    def cb_gridYChanged( self):
        self.scan.showGridY = self.w_gridYCheckBox.isChecked()
        PySpectra.cls()
        PySpectra.display( self.parent.getCheckedNameList())
        return 
#
#
#
class ImageAttributes( QtGui.QMainWindow):

    objectCounter = 0
    def __init__( self, parent = None, name = None, logWidget = None):
        super( ImageAttributes, self).__init__( parent)
        ImageAttributes.objectCounter += 1
        self.parent = parent

        if name is None:
            raise ValueError( "pyspFio.ImageAttributes: name not specified")
        self.name = name
        self.logWidget = logWidget
        self.image = PySpectra.getGqe( self.name)
        self.image.attributeWidget = self

        PySpectra.cls()
        PySpectra.display( [self.name])
        #self.setWindowTitle( "ImageAttributes")
        self.setWindowTitle( name)

        self.deltaXYLabel = None
        self.prepareWidgets()

        self.menuBar = QtGui.QMenuBar()
        self.setMenuBar( self.menuBar)
        self.prepareMenuBar()
        #
        # we cannot set the geometry because we can have multiple 
        #
        if ImageAttributes.objectCounter == 1: 
            geoWin = self.geometry()
            geo = QtGui.QDesktopWidget().screenGeometry(-1)
            self.setGeometry( geo.width() - 710, 600, geoWin.width(), geoWin.height())

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
        
    def __del__( self): 
        print( "the destructor")
        return 

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
        # mouse
        #
        self.mouseLabelX = QtGui.QLabel( "")
        self.mouseLabelX.setMinimumWidth( 90)
        self.layout_grid.addWidget( self.mouseLabelX, row, 3)
        self.mouseLabelY = QtGui.QLabel( "")
        self.mouseLabelY.setMinimumWidth( 90)
        self.layout_grid.addWidget( self.mouseLabelY, row, 4)
        self.mouseLabelValue = QtGui.QLabel( "")
        self.mouseLabelValue.setMinimumWidth( 90)
        self.layout_grid.addWidget( self.mouseLabelValue, row, 5)
        self.image.cb_mouseLabel = self.cb_mouseLabel
        #
        # xLabel
        #
        row += 1
        self.xLabel = QtGui.QLabel( "xLabel:")
        self.layout_grid.addWidget( self.xLabel, row, 0)
        self.xValue = QtGui.QLabel( self.image.xLabel)
        self.layout_grid.addWidget( self.xValue, row, 1)
        #
        # yLabel
        #
        self.yLabel = QtGui.QLabel( "yLabel:")
        self.layout_grid.addWidget( self.yLabel, row, 3)
        self.yValue = QtGui.QLabel( self.image.yLabel)
        self.layout_grid.addWidget( self.yValue, row, 4)
        #
        # shape
        #
        row += 1
        self.shapeLabel = QtGui.QLabel( "Shape:")
        self.layout_grid.addWidget( self.shapeLabel, row, 0)
        self.shapeValue = QtGui.QLabel( "%s" % repr( self.image.data.shape))
        self.layout_grid.addWidget( self.shapeValue, row, 1)
        #
        # xMin
        #
        row += 1
        self.xMinLabel = QtGui.QLabel( "xMin:")
        self.layout_grid.addWidget( self.xMinLabel, row, 0)
        self.xMinValue = QtGui.QLabel( "%g" % (self.image.xMin))
        self.layout_grid.addWidget( self.xMinValue, row, 1)
        self.xMinLineEdit = QtGui.QLineEdit()
        self.xMinLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.xMinLineEdit, row, 2)
        #
        # xMax
        #
        self.xMaxLabel = QtGui.QLabel( "xMax:")
        self.layout_grid.addWidget( self.xMaxLabel, row, 3)
        self.xMaxValue = QtGui.QLabel( "%g" % (self.image.xMax))
        self.layout_grid.addWidget( self.xMaxValue, row, 4)
        self.xMaxLineEdit = QtGui.QLineEdit()
        self.xMaxLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.xMaxLineEdit, row, 5)
        #
        # yMin
        #
        row += 1
        self.yMinLabel = QtGui.QLabel( "yMin:")
        self.layout_grid.addWidget( self.yMinLabel, row, 0)
        if self.image.yMin is None:
            self.yMinValue = QtGui.QLabel( "None")
        else:
            self.yMinValue = QtGui.QLabel( "%g" % (self.image.yMin))
        self.layout_grid.addWidget( self.yMinValue, row, 1)
        self.yMinLineEdit = QtGui.QLineEdit()
        self.yMinLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.yMinLineEdit, row, 2)
        #
        # yMax
        #
        self.yMaxLabel = QtGui.QLabel( "yMax:")
        self.layout_grid.addWidget( self.yMaxLabel, row, 3)
        if self.image.yMax is None:
            self.yMaxValue = QtGui.QLabel( "None")
        else:
            self.yMaxValue = QtGui.QLabel( "%g" % (self.image.yMax))
        self.layout_grid.addWidget( self.yMaxValue, row, 4)
        self.yMaxLineEdit = QtGui.QLineEdit()
        self.yMaxLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.yMaxLineEdit, row, 5)
        #
        # Log
        #
        row += 1
        self.logLabel = QtGui.QLabel( "log:")
        self.layout_grid.addWidget( self.logLabel, row, 0)
        self.logCheckBox = QtGui.QCheckBox()
        self.logCheckBox.setToolTip( "log base e")
        self.logCheckBox.setChecked( self.image.log)
        self.layout_grid.addWidget( self.logCheckBox, row, 1)
        self.logCheckBox.stateChanged.connect( self.cb_logChanged)
        #
        # at
        #
        self.atLabel = QtGui.QLabel( "at:")
        self.layout_grid.addWidget( self.atLabel, row, 3)
        self.atValue = QtGui.QLabel( "%s" % (str(self.image.at)))
        self.layout_grid.addWidget( self.atValue, row, 4)
        self.atLineEdit = QtGui.QLineEdit()
        self.atLineEdit.setMinimumWidth( 50)
        self.layout_grid.addWidget( self.atLineEdit, row, 5)
        #
        # flagAxes
        #
        row += 1
        self.flagAxesLabel = QtGui.QLabel( "flagAxes:")
        self.flagAxesLabel.setStatusTip('MB-1 flagAxess')
        self.layout_grid.addWidget( self.flagAxesLabel, row, 0)
        self.flagAxesCheckBox = QtGui.QCheckBox()
        self.flagAxesCheckBox.setChecked( self.image.flagAxes)
        self.layout_grid.addWidget( self.flagAxesCheckBox, row, 1)
        self.flagAxesCheckBox.stateChanged.connect( self.cb_flagAxesChanged)

        self.moduloLabel = QtGui.QLabel( "Modulo")
        self.layout_grid.addWidget( self.moduloLabel, row, 3)
        self.w_moduloComboBox = QtGui.QComboBox()
        self.w_moduloComboBox.setToolTip( "-1: disable modulo")
        for modulo in definitions.moduloList:
            self.w_moduloComboBox.addItem( "%d" % modulo)
        self.w_moduloComboBox.setCurrentIndex( 
            definitions.moduloList.index( self.image.modulo))
        self.w_moduloComboBox.currentIndexChanged.connect( self.cb_modulo)
        self.layout_grid.addWidget( self.w_moduloComboBox, row, 4) 
        #
        # cmap, color map
        #
        row += 1
        self.colorMapLabel = QtGui.QLabel( "ColorMaps")
        self.layout_grid.addWidget( self.colorMapLabel, row, 0)
        self.w_colorMapComboBox = QtGui.QComboBox()
        self.w_colorMapComboBox.setToolTip( "Chose a color map")
        for colorMap in definitions.colorMaps:
            self.w_colorMapComboBox.addItem( colorMap)
        self.w_colorMapComboBox.currentIndexChanged.connect( self.cb_colorMap)
        ind = definitions.colorMaps.index(self.image.colorMap)
        self.w_colorMapComboBox.setCurrentIndex( ind)
        self.layout_grid.addWidget( self.w_colorMapComboBox, row, 1) 

        if str(self.name).upper().find( "MANDELBROT") != -1:
            #
            # maxIter
            #
            row += 1
            self.maxIterLabel = QtGui.QLabel( "MaxIter")
            self.layout_grid.addWidget( self.maxIterLabel, row, 0)
            self.w_maxIterComboBox = QtGui.QComboBox()
            self.w_maxIterComboBox.setToolTip( "-1: disable maxIter")
            for maxIter in definitions.maxIterList:
                self.w_maxIterComboBox.addItem( "%d" % maxIter)
            self.w_maxIterComboBox.setCurrentIndex( 
                definitions.maxIterList.index( self.image.maxIter))
            self.w_maxIterComboBox.currentIndexChanged.connect( self.cb_maxIter)
            self.layout_grid.addWidget( self.w_maxIterComboBox, row, 1) 
            #
            # progress
            #
            self.layout_grid.addWidget( QtGui.QLabel( "Progress:"), row, 2)
            self.progressLabel = QtGui.QLabel( "")
            self.layout_grid.addWidget( self.progressLabel, row, 3)
            self.image.cbZoomMbProgress = self.cb_zoomMbProgress

            #
            # deltaXY, fille from GQE.zoomMB
            #
            row += 1
            self.layout_grid.addWidget( QtGui.QLabel( "Delta"), row, 0)
            self.deltaXYLabel = QtGui.QLabel( "")
            self.layout_grid.addWidget( self.deltaXYLabel, row, 1)
            self.deltaXYLabel.setToolTip( "Resolution, max - min")

            #
            # zoom factor
            #
            self.zoomFactor = QtGui.QLabel( "ZoomFactor")
            self.layout_grid.addWidget( self.zoomFactor, row, 2)
            self.w_zoomFactorComboBox = QtGui.QComboBox()
            self.w_zoomFactorComboBox.setToolTip( "The zoom-in/out factor applied with every click.")
            for zoomFactor in definitions.zoomFactorList:
                self.w_zoomFactorComboBox.addItem( "%g" % zoomFactor)
            self.w_zoomFactorComboBox.setCurrentIndex( 
                definitions.zoomFactorList.index( self.image.zoomFactor))
            self.w_zoomFactorComboBox.currentIndexChanged.connect( self.cb_zoomFactor)
            self.layout_grid.addWidget( self.w_zoomFactorComboBox, row, 3) 


            row += 1

            self.w_indexRotate = QtGui.QSlider()
            self.w_indexRotate.valueChanged.connect( self.cb_indexRotateValueChanged)
            self.w_indexRotate.setMinimum( 0)
            self.w_indexRotate.setMaximum( int(SLIDER_RESOLUTION))
            self.w_indexRotate.setOrientation( 1) # 1 horizontal, 2 vertical
            self.layout_grid.addWidget( self.w_indexRotate, row, 0, 1, 6)

            row += 1
            self.w_indexRotateLabel = QtGui.QLabel( "indexRotate")
            self.layout_grid.addWidget( self.w_indexRotateLabel, row, 1)
            self.w_indexRotatePosition = QtGui.QLabel()
            self.layout_grid.addWidget( self.w_indexRotatePosition, row, 2, 1, 2)

        else:
            self.w_indexRotatePosition = None

    #
    # the menu bar
    #
    def prepareMenuBar( self): 

        self.fileMenu = self.menuBar.addMenu('&File')

        self.showTextsAction = QtGui.QAction('ShowTexts', self)        
        self.showTextsAction.setStatusTip('Show the texts belonging to this GQE')
        self.showTextsAction.triggered.connect( self.cb_showTexts)
        self.fileMenu.addAction( self.showTextsAction)

        self.exitAction = QtGui.QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        #self.exitAction.triggered.connect( sys.exit)
        self.exitAction.triggered.connect( self.cb_close)
        self.fileMenu.addAction( self.exitAction)


        self.utilsMenu = self.menuBar.addMenu('&Utils')

        self.derivativeAction = QtGui.QAction('Derivative', self)        
        #self.derivativeAction.triggered.connect( self.cb_derivative)
        self.utilsMenu.addAction( self.derivativeAction)

        #
        # the activity menubar: help and activity
        #
        self.menuBarActivity = QtGui.QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarActivity, QtCore.Qt.TopRightCorner)

        #
        # Help menu (bottom part)
        #
        self.helpMenu = self.menuBarActivity.addMenu('Help')

        self.helpImageAttributesAction = self.helpMenu.addAction(self.tr("Image Attributes"))
        self.helpImageAttributesAction.triggered.connect( self.cb_helpImageAttributes)

        if str(self.name).upper().find( "MANDELBROT") != -1:
            self.helpMandelbrotAttributesAction = self.helpMenu.addAction(self.tr("Mandelbrot Attributes"))
            self.helpMandelbrotAttributesAction.triggered.connect( self.cb_helpMandelbrotAttributes)

        self.activityIndex = 0
        self.activity = self.menuBarActivity.addMenu( "_")

    #
    # the status bar
    #
    def prepareStatusBar( self): 

        if str(self.name).upper().find( "MANDELBROT") != -1:

            self.zoomOut = QtGui.QPushButton(self.tr("Zoom out")) 
            self.zoomOut.setToolTip( "Increase the limits")
            self.statusBar.addPermanentWidget( self.zoomOut) # 'permanent' to shift it right
            self.zoomOut.clicked.connect( self.cb_zoomOut)

            self.reset = QtGui.QPushButton(self.tr("Reset")) 
            self.reset.setToolTip( "Reset the limits to max.")
            self.statusBar.addPermanentWidget( self.reset) # 'permanent' to shift it right
            self.reset.clicked.connect( self.cb_reset)
        else:
            self.back = QtGui.QPushButton(self.tr("&Back")) 
            self.statusBar.addPermanentWidget( self.back) # 'permanent' to shift it right
            self.back.clicked.connect( self.cb_back)
            self.back.setShortcut( "Alt+b")

            self.next = QtGui.QPushButton(self.tr("&Next")) 
            self.statusBar.addPermanentWidget( self.next) # 'permanent' to shift it right
            self.next.clicked.connect( self.cb_next)
            self.next.setShortcut( "Alt+n")

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
        self.exit.clicked.connect( self.cb_close)
        self.exit.setShortcut( "Alt+x")

    def cb_mouseLabel( self, x, y, val): 
        self.mouseLabelX.setText( "x: %g" % (x))
        self.mouseLabelY.setText( "y: %g" % (y))
        self.mouseLabelValue.setText( "val: %g" % (val))


    def cb_modulo( self): 
        temp = self.w_moduloComboBox.currentText()
        self.image.modulo = int( temp)
        PySpectra.cls()
        PySpectra.display( [ self.name])
        return

    def cb_maxIter( self): 
        temp = self.w_maxIterComboBox.currentText()
        self.image.maxIter = int( temp)
        self.image.zoomMb()
        PySpectra.cls()
        PySpectra.display( [ self.name])
        return

    def cb_zoomFactor( self): 
        temp = self.w_zoomFactorComboBox.currentText()
        self.image.zoomFactor = float( temp)
        return

    def cb_zoomMbProgress( self, line): 
        '''
        called from image.zoomMb() to display the progress
        '''
        self.progressLabel.setText( "%s" % line)
        return 

    def cb_colorMap( self): 
        temp = self.w_colorMapComboBox.currentText()
        self.image.colorMap = str( temp)
        #PySpectra.cls()
        PySpectra.display( [ self.name])
        return

    def cb_next( self): 
        nextImage = PySpectra.nextImage( self.name)
        index = PySpectra.getIndex( nextImage.name)
        self.name = nextImage.name
        self.image = nextImage
        PySpectra.cls()
        PySpectra.display( [ self.name])
        self.parent.gqesListWidget.setCurrentRow( index)
        return 

    def cb_back( self): 
        prevImage = PySpectra.prevImage( self.name)
        index = PySpectra.getIndex( prevImage.name)
        self.name = prevImage.name
        self.image = prevImage
        PySpectra.cls()
        PySpectra.display( [ self.name])
        self.parent.gqesListWidget.setCurrentRow( index)


    def cb_reset( self): 
        self.image.xMin = -2
        self.image.xMax = 0.5
        self.image.yMin = -1.25
        self.image.yMax = 1.25
        self.image.maxIter = 512
        self.image.modulo = 512
        self.image.indexRotate = 0
        self.image.zoomMb()

        return 

    def cb_zoomOut( self): 
        delta = self.image.xMax - self.image.xMin
        cx = (self.image.xMax + self.image.xMin)/2.
        cy = (self.image.yMax + self.image.yMin)/2.

        self.image.xMin = cx - 2.*delta
        self.image.xMax = cx + 2.*delta
        self.image.yMin = cy - 2.*delta
        self.image.yMax = cy + 2.*delta
        if self.image.xMin < -2: 
            self.image.xMin = -2
        if self.image.xMax > 1: 
            self.image.xMax = 1
        if self.image.yMin < -1.5: 
            self.image.yMin = -1.5
        if self.image.yMax > 1.5: 
            self.image.yMax = 1.5
        self.image.maxIter = 512
        self.image.modulo = -1
        self.image.indexRotate = 0
        self.image.zoomMb()

        return 

    def cb_indexRotateValueChanged( self, value): 
        self.image.indexRotate = value
        PySpectra.display( [ self.name])
        self.w_indexRotatePosition.setText( "%d" % value)
        return 

    def cb_showTexts( self): 
        if len( self.scan.textList) == 0:
            self.logWidget.append( "%s has no texts" % self.scan.name)
            return 
        self.logWidget.append( "Texts of %s" % self.scan.name)
        for t in self.scan.textList:
            self.logWidget.append( "  '%s' at %g %g" % (t.text, t.x, t.y))
        return 
            
    def cb_close( self): 
        ScanAttributes.objectCounter -= 1
        self.close()
        return

    def cb_logChanged( self): 
        self.image.log = self.logCheckBox.isChecked()
        PySpectra.cls()
        PySpectra.display( [self.name])

    def cb_flagAxesChanged( self): 
        self.image.flagAxes = self.flagAxesCheckBox.isChecked()

    def cb_apply( self):
        line = str(self.xMinLineEdit.text())
        if len(line.strip()) > 0: 
            self.image.xMin = float( line.strip())
            self.xMinValue.setText( "%g" % self.image.xMin)
            self.xMinLineEdit.clear()

        line = str(self.xMaxLineEdit.text())
        if len(line.strip()) > 0: 
            self.image.xMax = float( line.strip())
            self.xMaxValue.setText( "%g" % self.image.xMax)
            self.xMaxLineEdit.clear()

        line = str(self.yMinLineEdit.text()).strip()
        if len(line) > 0: 
            if line.upper() == 'NONE':
                self.image.yMin = None
                self.yMinValue.setText( "None")
            else:
                self.image.yMin = float( line.strip())
                self.yMinValue.setText( "%g" % self.image.yMin)
            self.yMinLineEdit.clear()

        line = str(self.yMaxLineEdit.text()).strip()
        if len(line) > 0: 
            if line.upper() == 'NONE':
                self.image.yMax = None
                self.yMaxValue.setText( "None")
            else:
                self.image.yMax = float( line.strip())
                self.yMaxValue.setText( "%g" % self.image.yMax)
            self.yMaxLineEdit.clear()

        line = str(self.atLineEdit.text())
        if len(line.strip()) > 0: 
            line = line.strip()
            if line == 'None':
                self.image.at = None
            else:
                lstStr = line[1:-1].split( ',')
                if len( lstStr) == 3:
                    self.image.at = [int( i) for i in lstStr]
                else: 
                    self.image.at = [1, 1, 1]
                    self.atValue.setText( "[%d, %d, %d]" % (self.image.at[0], self.image.at[1], self.image.at[2]))
        self.atLineEdit.clear()

        if str(self.name).upper().find( "MANDELBROT") != -1:
            line = str(self.maxIterLineEdit.text()).strip()
            if len(line) > 0: 
                self.image.maxIter = int( line.strip())
                self.maxIterValue.setText( "%d" % self.image.maxIter)
                self.maxIterLineEdit.clear()
                self.image.zoom()

        PySpectra.cls()
        PySpectra.display( self.parent.getCheckedNameList())
        
    def cb_refreshAttr( self):

        if self.isMinimized(): 
            return
        
        self.activityIndex += 1
        if self.activityIndex > (len( ACTIVITY_SYMBOLS) - 1):
            self.activityIndex = 0
        self.activity.setTitle( ACTIVITY_SYMBOLS[ self.activityIndex])
        self.updateTimer.stop()

        self.nameValue.setText( self.name)
        if self.image.xLabel is not None:
            self.xValue.setText( self.image.xLabel)
        if self.image.yLabel is not None:
            self.yValue.setText( self.image.yLabel)
        self.shapeValue.setText( "%s" % repr( self.image.data.shape))
        self.xMinValue.setText( "%g" % self.image.xMin)
        self.xMaxValue.setText( "%g" % self.image.xMax)
        if self.image.yMin is None:
            self.yMinValue.setText( "None")
        else:
            self.yMinValue.setText( "%g" % self.image.yMin)
        if self.image.yMax is None:
            self.yMaxValue.setText( "None")
        else:
            self.yMaxValue.setText( "%g" % self.image.yMax)

        if str(self.name).upper().find( "MANDELBROT") != -1:
            self.w_maxIterComboBox.setCurrentIndex( 
                definitions.maxIterList.index( self.image.maxIter))

        self.w_moduloComboBox.setCurrentIndex( 
            definitions.moduloList.index( self.image.modulo))
        self.logCheckBox.setChecked( self.image.log)

        self.atValue.setText( "%s" % (str(self.image.at)))

        if self.w_indexRotatePosition is not None:
            self.w_indexRotatePosition.setText( "%d" % self.image.indexRotate)

        if self.deltaXYLabel is not None:
            self.deltaXYLabel.setText( "%.2e" % (self.image.xMax - self.image.xMin))

        self.updateTimer.start( int( updateTime*1000))

    def cb_display( self): 
        PySpectra.cls()
        PySpectra.display()

    def cb_helpImageAttributes(self):
        QtGui.QMessageBox.about(self, self.tr("Help Image Attributes"), self.tr(
                "<h3> Image Attributes </h3>"
                "<ul>"
                "<li> n.n.</li>"
                "</ul>"
                ))

    def cb_helpMandelbrotAttributes(self):
        QtGui.QMessageBox.about(self, self.tr("Help Mandelbrot Attributes"), self.tr(
                "<h3> Mandelbrot Attributes </h3>"
                "<ul>"
                "<li> Mandelbrot: MB-1: zoom, MB-2: shift</li>"
                "</ul>"
                ))

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
        PySpectra.cls()
        mpl_graphics.cls()
        mpl_graphics.display()

    def cb_pdf( self): 
        fileName = mpl_graphics.createPDF()
        if fileName:
            self.logWidget.append( "created %s/%s" % (os.getenv( "PWD"), fileName))
            os.system( "evince %s &" % fileName)
        else:
            self.logWidget.append( "failed to create PDF file")
#
# ===
#
class pySpectraGui( QtGui.QMainWindow):
    '''
    '''
    def __init__( self, files = None, parent = None, 
                  calledFromSardanaMonitor = False, 
                  flagExitOnClose = False):
        #
        # for PCs without Tango
        #
        self.flagTango = False
        try: 
            import PyTango
        except: 
            self.flagTango = False

        import HasyUtils
        #print( "pySpectraGui.__init__")
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

        self.gqeList = None
        self.scanAttributes = None
        if self.flagTango: 
            doors = HasyUtils.getDoorNames()
            if doors is not None and len( doors) > 0:
                self.proxyDoor = PyTango.DeviceProxy( doors[0]) 
            else: 
                self.proxyDoor = None
        self.nMotor = 0
        
        self.useMatplotlib = True 
        try:
            if os.environ["PYSP_USE_MATPLOTLIB"] == "True":
                self.useMatplotlib = True
        except: 
            pass

        #
        # 'files' come from the command line. If nothing is supplied
        # files == []
        #
        self.files = None
        if files is not None and len( files) > 0:
            self.files = self.getMatchingFiles( files)
            for f in self.files:
                PySpectra.read( f)
            PySpectra.display()

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
        #
        #if self.useMatplotlib: 
        #    self.mplWidget = MplWidget( self.logWidget)        
        #    self.mplWidget.show()
        #
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

        self.pyQtConfigWidget = None
        self.configWidget = None
        #
        # MacroServer info
        #
        self.msInfo = None
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
        self.gqesListWidget = QListWidgetTK( self, self.newScanSelected, "gqesListWidget", self.logWidget)
        self.scrollAreaScans.setWidget( self.gqesListWidget)
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
        self.motorNameButtons = []
        self.motPosLabels = []
        names = [ 'mot1', 'mot2', 'mot3']
        for i in range( len( names)):
            w = QtGui.QPushButton( names[i])
            self.motorNameButtons.append( w)
            hBox.addWidget( w)
            w.hide()

            w = QtGui.QLabel( "pos")
            w.setMinimumWidth( 60)

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

        hBox.addWidget( QtGui.QLabel( "Door:"))

        self.msInfo = QtGui.QLabel( "")
        self.msInfo.setMinimumWidth( 70)
        self.msInfo.setAlignment( QtCore.Qt.AlignCenter)

        hBox.addWidget( self.msInfo)

        self.abort = QtGui.QPushButton(self.tr("Abort"))
        hBox.addWidget( self.abort)
        self.abort.clicked.connect( self.cb_abort)
        self.abort.setToolTip( "Execute AbortMacro on Door")

        self.stop = QtGui.QPushButton(self.tr("Stop"))
        hBox.addWidget( self.stop)
        self.stop.clicked.connect( self.cb_stop)
        self.stop.setToolTip( "Send StopMacro to the MacroServer")

        self.stopAllMoves = QtGui.QPushButton(self.tr("StopAllMoves"))
        hBox.addWidget( self.stopAllMoves)
        self.stopAllMoves.clicked.connect( self.cb_stopAllMoves)
        self.stopAllMoves.setToolTip( "Execute StopMacro on every Door, if the state is not ON\nStop all Pool motors (names from Pool motorList)\nStop all Tango server motors (names from Tango DB)")

        self.requestStop = QtGui.QPushButton(self.tr("RequestStop"))
        hBox.addWidget( self.requestStop)
        self.requestStop.setToolTip( "Set RequestStop == True, optionally sensed by Macros")
        self.requestStop.clicked.connect( self.cb_requestStop)

        hBox.addStretch()            

        self.layout_frame_v.addLayout( hBox)


    def getMsInfo( self): 
        macroStatusLst = self.proxyDoor.status().split( "\n")

        if macroStatusLst[0] == 'The device is in ON state.':
            argout = "Idle"
            return argout
        try:
            a = ""
            for elm in macroStatusLst[2:]:
                lst = elm.split("\t")
                lst1 = lst[1].split( " ")
                a = a + lst1[0] + '->'
        except: 
            a = "unknown ->" 
        #
        # cut the trailing '->'
        #
        argout = a[:-2]
        return argout

    def updateMotorWidgets( self): 

        if not self.flagTango: 
            return 

        import PyTango

        if self.msInfo is not None: 
            if self.proxyDoor.state() == PyTango.DevState.MOVING:
                self.msInfo.setStyleSheet( "background-color:%s;" % definitions.BLUE_MOVING)
            elif self.proxyDoor.state() == PyTango.DevState.RUNNING:
                self.msInfo.setStyleSheet( "background-color:%s;" % definitions.BLUE_MOVING)
            elif self.proxyDoor.state() == PyTango.DevState.ON:
                self.msInfo.setStyleSheet( "background-color:%s;" % definitions.GREEN_OK)
            else:
                self.msInfo.setStyleSheet( "background-color:%s;" % definitions.RED_ALARM)
            
            self.msInfo.setText( self.getMsInfo())

        if self.nMotor == 0: 
            return 

        for i in range( self.nMotor): 
            self.motPosLabels[ i].setText( "%g" % self.motProxies[i].position) 
            if self.motProxies[i].state() == PyTango.DevState.MOVING:
                self.motPosLabels[ i].setStyleSheet( "background-color:%s;" % definitions.BLUE_MOVING)
            elif self.motProxies[i].state() == PyTango.DevState.ON:
                self.motPosLabels[ i].setStyleSheet( "background-color:%s;" % definitions.GREEN_OK)
            else:
                self.motPosLabels[ i].setStyleSheet( "background-color:%s;" % definitions.RED_ALARM)

        return 

    def addScanFrame( self): 
        '''
        Back | All | Checked | Next
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

        #
        # back, all, checked, next
        #
        hBox = QtGui.QHBoxLayout()
        hBox.addStretch()            

        self.back = QtGui.QPushButton(self.tr("&Back"))
        hBox.addWidget( self.back)
        self.back.clicked.connect( self.cb_back)
        self.back.setShortcut( "Alt+b")

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

        if not self.flagTango: 
            return 

        import HasyUtils
        import PyTango
        if self.proxyDoor is None:
            try:
                self.proxyDoor = PyTango.DeviceProxy( HasyUtils.getDoorNames()[0])
            except Exception as e : 
                print( "pySpectraGui.cb_abort: failed to create proxy to door %s" % HasyUtils.getDoorNames()[0])
                return 
            self.proxyDoor = PyTango.DeviceProxy( HasyUtils.getDoorNames()[0])
        self.proxyDoor.AbortMacro()
            
    def cb_stop( self): 
        '''
        execute StopMacro on Door
        '''
        if not self.flagTango: 
            return 
        import HasyUtils
        import PyTango
        if self.proxyDoor is None:
            try:
                self.proxyDoor = PyTango.DeviceProxy( HasyUtils.getDoorNames()[0])
            except Exception as e : 
                print( "pySpectraGui.cb_stop: failed to create proxy to door %s " % HasyUtils.getDoorNames()[0])
                return 
        if self.proxyDoor.State() != PyTango.DevState.ON:        
            self.proxyDoor.StopMacro()

    def cb_stopAllMoves( self): 
        import HasyUtils
        HasyUtils.stopAllMoves()

    def cb_requestStop( self): 
        import HasyUtils
        HasyUtils.setEnv( "RequestStop", True)
        self.logWidget.append( "RequestStop == True")
        return 

    def displayChecked( self): 
        PySpectra.cls()
        PySpectra.display( self.getCheckedNameList())

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
        elif pathNameTokens[-1] in definitions.dataFormats:
            PySpectra.cls()
            PySpectra.delete()
            try: 
                PySpectra.read( pathName, flagMCA = self.mcaAction.isChecked())
            except Exception as e :
                print( "pySpectraGui.newPathSelected: trouble reading %s" % pathName)
                print( repr( e))
                return 

            PySpectra.setTitle( pathName)
            PySpectra.display()
            self.updateScansList()
        else:
            if self is not None:
                self.logWidget.append(  "newItemSelected: bad pathName %s" % pathName)
        return 

    def newScanSelected( self, scanName): 
        '''
        called with the name of a scan
        '''
        PySpectra.cls()
        self.displayChecked()
        # PySpectra.display( [scanName])

        return 

    def cb_refreshPySpectraGui( self):

        if self.isMinimized(): 
            return
        
        self.activityIndex += 1
        if self.activityIndex > (len( ACTIVITY_SYMBOLS) - 1):
            self.activityIndex = 0
        self.activity.setTitle( ACTIVITY_SYMBOLS[ self.activityIndex])

        #self.updateTimerPySpectraGui.stop()        
        
        self.updateScansList()

        self.updateMotorWidgets()

        if len( self.getCheckedNameList()) != 1: 
            return 

        #gqe = PySpectra.getGqe( self.getCheckedNameList()[0])
        #gqe.updateArrowCurrent()
        
        #self.updateTimerPySpectraGui.start( int( updateTime*1000))
        return 
   
    def updateScansList( self):
        #
        # the scan layout is updated, if
        #   - nothing has been created before self.gqeList == None
        #   - the current gqeList and the displayed gqeList are different
        #

        gqeList = PySpectra.getGqeList()[:]
        #
        # see, if one of the GQEs has an arrowCurrent. 
        # if so, update it because the motor might have been 
        # moved somehow
        # 
        for gqe in gqeList: 
            if type( gqe) != PySpectra.Scan:            
                continue
            if gqe.arrowCurrent is None: 
                continue
            gqe.updateArrowCurrent()

        flagUpdate = False
        if self.gqeList is None:
            flagUpdate = True
        else:
            if len( gqeList) != len( self.gqeList):
                flagUpdate = True
            else:
                for i in range( len( gqeList)):
                    if gqeList[i] != self.gqeList[i]:
                        flagUpdate = True
                        break

        if not flagUpdate: 
            self.updateTimerPySpectraGui.start( int( updateTime*1000))
            return 
        #
        # so we have to make an update, clear the gqeListWidget first
        #
        if self.gqesListWidget.count() > 0:
            self.gqesListWidget.clear()
       
        self.gqeList = gqeList[:]

        if len( self.gqeList) == 0:
            return 
            
        #
        # fill the gqesListWidget
        #
        if len( self.gqeList) > 0:
            if type( self.gqeList[0]) == PySpectra.Scan:
                if self.gqeList[0].fileName is not None:
                    self.fileNameLabel.setText( self.gqeList[0].fileName)

        for scan in self.gqeList:
            item = QtGui.QListWidgetItem( scan.name)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)       
            self.gqesListWidget.addItem( item)

    def updateFilesList( self):
        '''
        the file list in the scrolling area
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
            if fileNameTokens[-1] in definitions.dataFormats:
                self.filesListWidget.addItem( file)
            elif file.startswith( "."):
                continue
            elif self.files is None and os.path.isdir( file):
                self.filesListWidget.addItem( file)
        #print( "updateFilesList DONE")
        #self.scrollAreaFiles.setFocusPolicy( QtCore.Qt.StrongFocus)

    def getMatchingFiles( self, patternList):
        '''
        patternList is specified on the command line
        '''
        argout = []
        import HasyUtils
        for file in os.listdir( "."):
            fileNameTokens = file.split( '.')
            if fileNameTokens[-1] in definitions.dataFormats:
                for pat in patternList:
                    if HasyUtils.match( file, pat): 
                        argout.append( file)
        return argout

    def cb_all( self): 
        PySpectra.cls()
        PySpectra.display()

    def cb_back( self): 
        scan = PySpectra.prevScan()
        index = PySpectra.getIndex( scan.name)
        PySpectra.cls()
        PySpectra.display( [ scan.name])
        self.gqesListWidget.setCurrentRow( index)

    def cb_next( self): 
        scan = PySpectra.nextScan()
        index = PySpectra.getIndex( scan.name)
        PySpectra.cls()
        PySpectra.display( [ scan.name])
        self.gqesListWidget.setCurrentRow( index)

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

        self.editAction = QtGui.QAction('Edit', self)        
        self.editAction.triggered.connect( self.cb_edit)
        self.fileMenu.addAction( self.editAction)

        self.deleteFileAction = QtGui.QAction('Delete file', self)        
        self.deleteFileAction.setStatusTip('Permanently delete the selected file')
        self.deleteFileAction.triggered.connect( self.cb_deleteFile)
        self.fileMenu.addAction( self.deleteFileAction)

        self.createPDFAction = QtGui.QAction('Hardcopy DINA4', self)        
        self.createPDFAction.setStatusTip('Create a PDF file, DINA4')
        self.createPDFAction.triggered.connect( self.cb_createPdfA4)
        self.fileMenu.addAction( self.createPDFAction)

        self.createPDF6Action = QtGui.QAction('Hardcopy DINA6', self)        
        self.createPDF6Action.setStatusTip('Create a PDF file, DINA6')
        self.createPDF6Action.triggered.connect( self.cb_createPdfA6)
        self.fileMenu.addAction( self.createPDF6Action)

        self.evinceAction = QtGui.QAction('evince pyspOutput.pdf', self)        
        self.evinceAction.triggered.connect( self.cb_launchEvince)
        self.fileMenu.addAction( self.evinceAction)

        if self.useMatplotlib: 
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

        for mode in definitions.fsaModes:
            qa = QtGui.QAction('FSA(%s)' % mode, self)        
            qa.triggered.connect( make_cb_fsa_2( self, mode))
            self.utilsMenu.addAction( qa)

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

        self.mcaAction = QtGui.QAction('MCA File', self, checkable = True)        
        self.mcaAction.setStatusTip('The input files contain MCA data (no x-position column)')
        self.mcaAction.triggered.connect( self.cb_mca)
        self.optionsMenu.addAction( self.mcaAction)


        self.exitAction = QtGui.QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect( self.cb_close)
        self.fileMenu.addAction( self.exitAction)


        self.configMenu = self.menuBar.addMenu('&Config')

        self.pyqtConfigAction = QtGui.QAction('PyQtConfig', self)        
        self.pyqtConfigAction.triggered.connect( self.cb_pyqtConfig)
        self.configMenu.addAction( self.pyqtConfigAction)

        self.configAction = QtGui.QAction('Config', self)        
        self.configAction.triggered.connect( self.cb_config)
        self.configMenu.addAction( self.configAction)


        self.dina4Action = QtGui.QAction('DINA4', self)        
        self.dina4Action.triggered.connect( lambda : PySpectra.setWsViewport( 'dina4'))
        self.configMenu.addAction( self.dina4Action)

        self.dina4sAction = QtGui.QAction('DINA4S', self)        
        self.dina4sAction.triggered.connect( lambda : PySpectra.setWsViewport( 'dina4s'))
        self.configMenu.addAction( self.dina4sAction)

        self.dina5Action = QtGui.QAction('DINA5', self)        
        self.dina5Action.triggered.connect( lambda : PySpectra.setWsViewport( 'dina5'))
        self.configMenu.addAction( self.dina5Action)

        self.dina5sAction = QtGui.QAction('DINA5S', self)        
        self.dina5sAction.triggered.connect( lambda : PySpectra.setWsViewport( 'dina5s'))
        self.configMenu.addAction( self.dina5sAction)

        self.dina6Action = QtGui.QAction('DINA6', self)        
        self.dina6Action.triggered.connect( lambda : PySpectra.setWsViewport( 'dina6'))
        self.configMenu.addAction( self.dina6Action)

        self.dina6sAction = QtGui.QAction('DINA6S', self)        
        self.dina6sAction.triggered.connect( lambda : PySpectra.setWsViewport( 'dina6s'))
        self.configMenu.addAction( self.dina6sAction)


        #
        # the activity menubar: help and activity
        #
        self.menuBarActivity = QtGui.QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarActivity, QtCore.Qt.TopRightCorner)

        #
        # examples
        #
        self.examplesMenu = self.menuBarActivity.addMenu('&Examples')

        # /home/kracht/Misc/pySpectra/PySpectra/examples/exampleCode.py
        for funcName in dir( PySpectra.examples.exampleCode):
            if funcName.find( 'example') != 0: 
                continue
            action = QtGui.QAction( funcName[7:], self)        
            action.triggered.connect( self.make_example( funcName))
            self.examplesMenu.addAction( action)

        action = QtGui.QAction( "View code", self)        
        action.triggered.connect( self.cb_displayExampleCode)
        self.examplesMenu.addAction( action)
        #
        # Help menu (bottom part)
        #
        self.helpMenu = self.menuBarActivity.addMenu('Help')
        self.widgetAction = self.helpMenu.addAction(self.tr("PySpectra"))
        self.widgetAction.triggered.connect( self.cb_helpPySpectra)

        self.scanNameAction = self.helpMenu.addAction(self.tr("ScanName widget"))
        self.scanNameAction.triggered.connect( self.cb_helpScanName)

        self.activityIndex = 0
        self.activity = self.menuBarActivity.addMenu( "_")
    #
    # the status bar
    #
    def prepareStatusBar( self): 

        #
        # cls
        #
        self.clsBtn = QtGui.QPushButton(self.tr("&Cls")) 
        self.statusBar.addWidget( self.clsBtn) 
        self.clsBtn.clicked.connect( self.cb_cls)
        self.clsBtn.setToolTip( "Clear the graphics window")
        self.clsBtn.setShortcut( "Alt+c")
        #
        # display
        #
        self.displayBtn = QtGui.QPushButton(self.tr("Display")) 
        self.statusBar.addWidget( self.displayBtn) 
        self.displayBtn.clicked.connect( self.cb_display)
        self.displayBtn.setToolTip( "Display")
        #
        # delete
        #
        self.deleteBtn = QtGui.QPushButton(self.tr("&Delete")) 
        self.statusBar.addWidget( self.deleteBtn) 
        self.deleteBtn.clicked.connect( self.cb_delete)
        self.deleteBtn.setToolTip( "Delete checked scans")
        self.deleteBtn.setShortcut( "Alt+d")

        if self.useMatplotlib:
            self.matplotlibBtn = QtGui.QPushButton(self.tr("&Matplotlib")) 
            self.statusBar.addWidget( self.matplotlibBtn) 
            self.matplotlibBtn.clicked.connect( self.cb_matplotlib)
            self.matplotlibBtn.setToolTip( "Use matplotlib for display")
            self.matplotlibBtn.setShortcut( "Alt+m")


        self.refreshFiles = QtGui.QPushButton(self.tr("&Refresh")) 
        self.statusBar.addPermanentWidget( self.refreshFiles) # 'permanent' to shift it right
        self.refreshFiles.clicked.connect( self.cb_refreshFiles)
        self.refreshFiles.setToolTip( "Refresh files widget")
        self.refreshFiles.setShortcut( "Alt+r")

        self.clearLog = QtGui.QPushButton(self.tr("&ClearLog")) 
        self.statusBar.addPermanentWidget( self.clearLog) # 'permanent' to shift it right
        self.clearLog.clicked.connect( self.cb_clearLog)
        self.clearLog.setToolTip( "Clear log widget")
        self.clearLog.setShortcut( "Alt+c")

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( self.cb_close)
        self.exit.setShortcut( "Alt+x")

    def make_example( self, funcName): 
        def func(): 
            f = getattr( PySpectra.examples.exampleCode, funcName)
            if callable( f):
                f()
            else: 
                print( "pySpectraGuiClass.make_example: problem with %s" % funcName)
            return 
        return func
        
    def cb_pyqtConfig( self):
        self.pyQtConfigWidget = PyQtConfig()
        self.pyQtConfigWidget.show()
        
    def cb_config( self):
        self.configWidget = Config()
        self.configWidget.show()
        
    def cb_displayExampleCode( self): 
        fName = PySpectra.examples.exampleCode.__file__
        #
        # '/usr/lib/python2.7/dist-packages/PySpectra/examples/exampleCode.pyc'
        # -- don't look at .pyc files
        #
        if fName[ -1] == 'c':
            fName = fName[:-1]
            
        editor = os.getenv( "EDITOR")
        if editor is None: 
            editor = 'emacs'
        self.logWidget.append( "Opening %s" % fName)
        os.system( "%s %s&" % (editor, fName))

    def _printHelper( self, frmt): 
        import HasyUtils

        lst = PySpectra.getGqeList()
        if len( lst) == 0:
            QtGui.QMessageBox.about(self, 'Info Box', "No Scans to print")
            return
            
        prnt = os.getenv( "PRINTER")
        if prnt is None: 
            QtGui.QMessageBox.about(self, 'Info Box', "No shell environment variable PRINTER.") 
            return
        fName = PySpectra.createPDF(format = frmt, flagPrint = False)
        self.logWidget.append( HasyUtils.getDateTime())
        self.logWidget.append("Created %s (%s)" % (fName, frmt))

        msg = "Send %s to %s" % ( fName, prnt)
        reply = QtGui.QMessageBox.question(self, 'YesNo', msg, 
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            if os.system( "/usr/bin/lpr -P %s %s" % (prnt, fName)):
                self.logWidget.append( "failed to print %s on %s" % (fName, prnt))
            self.logWidget.append(" printed on %s" % (prnt))
        
    def cb_createPdfA4( self): 
        self._printHelper( "DINA4")
        
    def cb_createPdfA6( self): 
        self._printHelper( "DINA6")

    def cb_display( self): 
        PySpectra.cls()
        PySpectra.display()
        
    def cb_launchEvince( self):
        sts = os.system( "evince pyspOutput.pdf &")

    def cb_createPDFPrint( self): 
        prnt = os.getenv( "PRINTER")
        if prnt is None: 
            QtGui.QMessageBox.about(self, 'Info Box', "No shell environment variable PRINTER.") 
            return

        fName = PySpectra.createPDF( printer = prnt, flagPrint = True)
        self.logWidget.append( "Created %s, printed on %s" % (fName, prnt))

    def cb_close( self): 
        PySpectra.close()
        if self.mplWidget is not None:
            self.mplWidget.close()
            self.mplWidget = None
        if self.pyQtConfigWidget is not None:
            self.pyQtConfigWidget.close()
            self.pyQtConfigWidget = None
        if self.configWidget is not None:
            self.configWidget.close()
            self.configWidget = None
        self.close()
        if self.flagExitOnClose:
            sys.exit( 0)

    def cb_clearLog( self): 
        self.logWidget.clear()

    def cb_refreshFiles( self): 
        '''
        the files list is not refreshed automatically
          - otherwise we cannot select a file for edit.
          - the directory may contain may files
        '''
        self.updateFilesList()

    def cb_cls( self):
        '''
        clear screen
        '''
        PySpectra.cls()
        
    def getCheckedNameList( self): 
        '''
        get the list of selected names
        '''
        nameList = []
        for row in range( self.gqesListWidget.count()):
            item = self.gqesListWidget.item( row)
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
        PySpectra.delete( lst)
        PySpectra.cls()
        PySpectra.display()
        return 

    def cb_pdf( self): 
        fileName = mpl_graphics.createPDF()
        if fileName:
            self.logWidget.append( "created %s" % fileName)
            os.system( "evince %s &" % fileName)
        else:
            self.logWidget.append( "failed to create PDF file")
        
    def cb_doty( self):
        lst = PySpectra.getGqeList()
        if self.dotyAction.isChecked():
            for elm in lst:
                elm.doty = True
        else:
            for elm in lst:
                elm.doty = False
        PySpectra.cls()
        PySpectra.display()

    def cb_grid( self): 
        lst = PySpectra.getGqeList()
        if self.gridAction.isChecked():
            for scan in lst:
                scan.showGridX = True
                scan.showGridY = True
        else:
            for scan in lst:
                scan.showGridX = False
                scan.showGridY = False
        PySpectra.cls()
        PySpectra.display()

    def cb_mca( self): 
        self.mcaAction.isChecked() 

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

    def cb_deleteFile( self):
        item = self.filesListWidget.currentItem()
        if item is None:
            self.logWidget.append( "cb_deleteFile: select a file name")
            return 
        fName = os.getcwd() + "/" + item.text()
        msg = "Permanently delete %s" % ( fName)
        reply = QtGui.QMessageBox.question(self, 'YesNo', msg, 
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            os.remove( fName)
            self.updateFilesList()
        return 
        
    def cb_derivative( self):
        displayList = PySpectra.getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append(  "cb_derivative: expecting 1 displayed scan")
            return 
        calc.derivative( displayList[0].name)

    def cb_antiderivative( self):
        displayList = PySpectra.getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append(  "cb_antiderivative: expecting 1 displayed scan")
            return 
        calc.antiderivative( displayList[0].name)

    def cb_y2my( self):
        displayList = PySpectra.getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append(  "cb_y2my: expecting 1 displayed scan")
            return 
        calc.yToMinusY( displayList[0].name)

    def cb_ssa( self):
        displayList = PySpectra.getDisplayList()
        if len( displayList) != 1:
            self.logWidget.append( "cb_ssa: expecting 1 displayed scan")
            return 
        scan = displayList[0]
        scan.ssa( self.logWidget)

        PySpectra.cls()
        PySpectra.display( [scan.name])


    def cb_writeFile( self):
        if len( self.getCheckedNameList()) > 0: 
            fName = PySpectra.write( self.getCheckedNameList())
        else:
            fName = PySpectra.write()
        if fName is None: 
            self.logWidget.append( "Failed to create .fio file")
        else:
            self.logWidget.append( "created %s" % fName)
            

    def cb_matplotlib( self):
        #
        # clear things before we enter matplotlib
        #
        PySpectra.cls()
        self.mplWidget = MplWidget( self.logWidget)
        self.mplWidget.show()
        mpl_graphics.display( self.getCheckedNameList())

    def cb_helpPySpectra(self):
        QtGui.QMessageBox.about(self, self.tr("Help Widget"), self.tr(
                "<h3> PySpectra displays 1D and 2D data</h3>"
                "<br> Documentation:"
                "<br>"
                "<br> import PySpectra"
                "<br> PySpectra?"
                ))

    def cb_helpScanName(self):
        QtGui.QMessageBox.about(self, self.tr("Help ScanName"), self.tr(
                "<h3> The ScanName widget</h3>"
                "<ul>"
                "<li> if no Scan (aka GQE) is checked, all are displayed</li>"
                "<li> the MB3-click opens an attributes widget</li>"
                "</ul>"
                ))


