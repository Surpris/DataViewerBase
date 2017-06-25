# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 23:22:08 2017

@author: Surpris
"""

import sys
import inspect
import os
import json
import datetime
from PyQt4.QtGui import QMainWindow, QGridLayout, QMenu, QDialog, QPushButton, QMessageBox, QWidget
from PyQt4.QtCore import QObject, SIGNAL, pyqtSlot
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from PlotWindow import PlotWindow
from Worker import Worker

class DataViewerBase(QMainWindow):
    """
    Base GUI class for viewing data / images.
    This class was made in the purpose of viewing VMI images.
    """
    def __init__(self):
        """
        Initialization.
        """
        super().__init__()
        print("Initialize this application...")
        self.initInnerParameters()
        self.initGui()
        self.setupCheckingWorker()
    
    def initInnerParameters(self):
        """
        Initialize the inner parameters.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        try:
            self._windows = []
            self._currentDir = os.path.dirname(__file__)
            self._online = False
            self._closing_dialog = True
            if os.path.exists(os.path.join(os.path.dirname(__file__), "config.json")):
                with open(os.path.join(os.path.dirname(__file__), "config.json"),'r') as ff:
                    config = json.load(ff)
                if config.get("currentDir") is not None:
                    if isinstance(config.get("currentDir"), str):
                        if os.path.exists(config.get("currentDir")):
                            self._currentDir = config["currentDir"]
                if config.get("online") is not None:
                    if isinstance(config.get("online"), bool):
                        self._online = config["online"]
                if config.get("closing_dialog") is not None:
                    if isinstance(config.get("closing_dialog"), bool):
                        self._closing_dialog = config["closing_dialog"]
        except Exception as ex:
            print(ex)
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
    
    def initGui(self):
        """
        Initialize the GUI.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.initMainWidget()
        self.setMenuBar()

        self.setWindowTitle("VMI Viewer")
        self.resize(1200, 600)

        ### Some buttons.
        button_test = QPushButton()
        button_test.setText("Test")
        button_test.clicked.connect(self.pushButton)
        # QObject.connect(button_test, SIGNAL("clicked()"), self.pushButton)

        ### Plotting area.
        self.pw1 = PlotWindow(self)
        self.pw2 = PlotWindow(self)
        self.pw3 = PlotWindow(self)

        ### Construct the layout.
        self.grid.addWidget(button_test, 0, 0)
        self.grid.addWidget(self.pw1, 1, 0, 2, 1)
        self.grid.addWidget(self.pw2, 1, 1, 2, 1)
        self.grid.addWidget(self.pw3, 1, 2, 2, 1)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
    
    def initMainWidget(self):
        """
        Initialize the main widget and the grid.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        self.main_widget = QWidget(self)
        self.grid = QGridLayout(self.main_widget)
        self.grid.setSpacing(10)
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

    def setMenuBar(self):
        """
        Set the contents of the menu bar
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        ## File
        file_menu = QMenu('&File', self)

        # Open
        file_menu.addAction('&Open', self.openFile,
                QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.menuBar().addMenu(file_menu)
        # Quit
        file_menu.addAction('&Quit', self.quitApp,
                QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        ## Help
        help_menu = QMenu('&Help', self)
        help_menu.addAction('Help', self.showHelp)
        help_menu.addAction('About...', self.showAbout)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(help_menu)
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
    
    def openFile(self):
        """
        Show a file dialog and select a file
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        pass
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

    def quitApp(self):
        """
        Quit this application.
        """
        self.close()
    
    def closeEvent(self, event):
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        if self._closing_dialog:
            confirmObject = QMessageBox.question(self, "Closing...",
                "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No)
            if confirmObject == QMessageBox.Yes:
                config = self.makeConfig()
                with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as ff:
                    json.dump(config, ff)
                self._worker.stop()
                event.accept()
            else:
                event.ignore()
        else:
            config = self.makeConfig()
            with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as ff:
                json.dump(config, ff)
            self._worker.stop()
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
    
    def makeConfig(self):
        """
        Make a config dict object to save the latest configration in.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        config = {"online":self._online, "closing_dialog":self._closing_dialog, 
                "currentDir":self._currentDir}
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        return config
    
    def setupCheckingWorker(self):
        self._worker = Worker()
        self._worker.do_something.connect(self.checkWindow)
        self._worker.finished.connect(self.finishCheckWindow)
        self._worker.start()

    def showHelp(self):
        """
        Show a pop-up dialog showing how to use this application.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        pass
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
    
    def showAbout(self):
        """
        Show a pop-up dialog describing this application.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        pass
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

    @pyqtSlot()
    def pushButton(self):
        window = PlotWindow(self, "win{0:02d}".format(len(self._windows)+1))
        window.show()
        window.raise_()
        window.activateWindow()
        self._windows.append(window)
        print(len(self._windows))
    
    @pyqtSlot()
    def checkWindow(self):
        """
        Check whether windows are active.
        """
        print(len(self._windows))
        for window in self._windows:
            pass
    
    @pyqtSlot()
    def finishCheckWindow(self):
        self._worker.wait()

def main():
    app = QtGui.QApplication([])
    mw = DataViewerBase()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    main()