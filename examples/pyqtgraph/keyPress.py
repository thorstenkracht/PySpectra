#!/usr/bin/env python
import sys
from PyQt4 import QtGui, QtCore

class QCustomWidget (QtGui.QWidget):
    def __init__ (self, parent = None):
        super(QCustomWidget, self).__init__(parent)
        myQLayout = QtGui.QVBoxLayout()
        self.my1QPushButton = QtGui.QPushButton('Test 1', self)
        self.my2QPushButton = QtGui.QPushButton('Test 2', self)
        self.setChildrenFocusPolicy(QtCore.Qt.NoFocus)
        myQLayout.addWidget(self.my1QPushButton)
        myQLayout.addWidget(self.my2QPushButton)
        self.setLayout(myQLayout)

    def setChildrenFocusPolicy (self, policy):
        def recursiveSetChildFocusPolicy (parentQWidget):
            for childQWidget in parentQWidget.findChildren(QtGui.QWidget):
                childQWidget.setFocusPolicy(policy)
                recursiveSetChildFocusPolicy(childQWidget)
        recursiveSetChildFocusPolicy(self)

    def keyPressEvent (self, eventQKeyEvent):
        print eventQKeyEvent.key()
        messageQMessageBox = QtGui.QMessageBox(QtGui.QMessageBox.Question, 'Question', 'Hello Main', QtGui.QMessageBox.Yes)
        messageQMessageBox.exec_()
        QtGui.QWidget.keyPressEvent(self, eventQKeyEvent)

appQApplication = QtGui.QApplication(sys.argv)
windowQCustomWidget = QCustomWidget()
windowQCustomWidget.setFixedSize(640, 480)
windowQCustomWidget.show()
sys.exit(appQApplication.exec_())
