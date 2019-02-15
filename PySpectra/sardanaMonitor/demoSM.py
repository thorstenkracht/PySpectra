#!/usr/bin/env python
'''
'''
import sys
#from PyQt4 import QtGui, QtCore
from taurus.external.qt import QtGui 
from taurus.external.qt import QtCore
from taurus.qt.qtgui.application import TaurusApplication 
import taurus
import numpy as np
import HasyUtils
import time

class demoSM( QtGui.QMainWindow):
    '''
    the main class of the SardanaMotorMenu application
    '''
    def __init__( self, parent = None):
        super( demoSM, self).__init__( parent)

        self.setWindowTitle( "demoSM")

        self.setCentralWidget( QtGui.QLabel( "Demo"))

        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar( self.statusBar)
        self.prepareStatusBar()

    #
    # the status bar
    #
    def prepareStatusBar( self): 

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( sys.exit)
        self.exit.setShortcut( "Alt+x")

def main():




    app = TaurusApplication( [])

    import demoDoor

    door = taurus.Device( HasyUtils.getLocalDoorNames()[0])

    o = demoSM()
    o.show()

    sys.exit( app.exec_())

if __name__ == "__main__":
    main()
    

