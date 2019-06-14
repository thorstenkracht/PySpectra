#!/usr/bin/env python
#
import sys, os, argparse, math, PyTango, time
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import HasyUtils
sys.path.append( "/home/kracht/Misc/pySpectra")
import PySpectra as pysp

class pyqtWidget():
    def __init__( self): 
        xMin = 0
        xMax = 50
        xDelta = 0.1
        x = np.arange( xMin, xMax, xDelta)
        t = np.tan(x)
        self.win = pg.GraphicsWindow( title="Scan the Tango Function")
        self.win.clear()

        self.win.addLabel( "A figure containing a plots", row = 1, col = 1)
        tan = self.win.addPlot( row=2, col=1)
        tan.showGrid( x = True, y = True)
        tan.setTitle( title = "The tan() Function")
        tan.setLabel( 'left', 'tan')
        tan.setLabel( 'bottom', 'phase')
        tan.enableAutoRange( x = False, y = True)
        #tan.setXRange( xMin - 0.25, xMax + 0.25)
        tan.setXRange( xMin, xMax, padding=0)
        
        tan.clear()
        tan.plot( x, t, pen=( 0, 0, 255))
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
        # size
        self.setGeometry( geo.width() - 680, 30, 650, 500)

        # background/foreground have to be set before the channels are defined
        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')

        # used by cb_postscript
        self.lastFileWritten = None

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

        self.pyqt = pyqtWidget()
        self.layout_v.addWidget( self.pyqt.win)

        self.lineEdit = QtGui.QLineEdit()
        self.layout_v.addWidget( self.lineEdit)

        QtCore.QObject.connect(self.lineEdit, QtCore.SIGNAL("returnPressed()"),self.cb_lineEdit)

    def cb_lineEdit( self): 
        pysp.command( str(self.lineEdit.text()))
        self.lineEdit.clear()
    #
    # the menu bar
    #
    def prepareMenuBar( self): 

        self.fileMenu = self.menuBar.addMenu('&File')

        self.writeFileAction = QtGui.QAction('Write .fio file', self)        
        self.writeFileAction.setStatusTip('Write .fio file')
        self.writeFileAction.triggered.connect( self.cb_writeFile)
        self.fileMenu.addAction( self.writeFileAction)

        self.exitAction = QtGui.QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect( sys.exit)
        self.fileMenu.addAction( self.exitAction)

        #
        # the help menubar
        #
        self.menuBarHelp = QtGui.QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarHelp, QtCore.Qt.TopRightCorner)

        self.helpMenu = self.menuBarHelp.addMenu('Help')
        self.helpWidget = self.helpMenu.addAction(self.tr("Widget"))
        self.helpWidget.triggered.connect( self.cb_helpWidget)
    #
    # the status bar
    #
    def prepareStatusBar( self): 

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( sys.exit)
        self.exit.setShortcut( "Alt+x")

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

    args = parseCLI()
    sys.argv = []
    if os.getenv( "DISPLAY") != ':0':
        QtGui.QApplication.setStyle( 'Cleanlooks')

    app = QtGui.QApplication(sys.argv)

    o = pySpectraGui()
    o.show()

    try:
        sys.exit( app.exec_())
    except Exception, e:
        print repr( e)

if __name__ == "__main__":
    main()
    

