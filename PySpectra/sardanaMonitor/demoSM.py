#!/usr/bin/env python
'''
'''
import taurus
import sys

from taurus.external.qt import QtGui 
from taurus.external.qt import QtCore
from taurus.qt.qtgui.application import TaurusApplication 

DOOR_NAME = 'p09/door/haso107d1.01'

def main():

    app = QtGui.QApplication.instance()
    if app is None:
        #app = QtGui.QApplication(sys.argv)
        app = TaurusApplication( [])
        
    import demoDoor

    door = taurus.Device( DOOR_NAME)
    
    sys.exit( app.exec_())
        
if __name__ == "__main__":
    main()
    

