# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 23:22:08 2017

@author: Surpris
"""

import sys
import os
import json
import datetime
from PyQt4.QtGui import QMainWindow, QGridLayout, QMenu, QDialog, QPushButton, QMessageBox, QWidget
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

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
        self.initInnerParameters()
        self.initGui()
    
    def initInnerParameters(self):
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
        print(self._currentDir)
    
    def initGui(self):
        """
        Initialize the GUI.
        """
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.initMainWidget()
        self.setMenuBar()

        self.setWindowTitle("VMI Viewer")
        self.resize(1200, 600)
    
    def initMainWidget(self):
        """
            Initialize the main widget and the grid
        """
        self.main_widget = QWidget(self)
        self.grid = QGridLayout(self.main_widget)
        self.grid.setSpacing(10)

    def setMenuBar(self):
        """
        Set the contents of the menu bar
        """
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
    
    def openFile(self):
        """
        Show a file dialog and select a file
        """
        pass

    def quitApp(self):
        """
        Quit this application.
        """
        self.close()
    
    def closeEvent(self, event):
        if self._closing_dialog:
            confirmObject = QMessageBox.question(self, "Closing...",
                "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No)
            if confirmObject == QMessageBox.Yes:
                config = self.makeConfig()
                with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as ff:
                    json.dump(config, ff)
                event.accept()
            else:
                event.ignore()
        else:
            config = self.makeConfig()
            with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as ff:
                json.dump(config, ff)
    
    def makeConfig(self):
        return {"online":self._online, "closing_dialog":self._closing_dialog, 
                "currentDir":self._currentDir}
    
    def showHelp(self):
        """
        Show a pop-up dialog showing how to use this application.
        """
        pass
    
    def showAbout(self):
        """
        Show a pop-up dialog describing this application.
        """
        pass

def main():
    app = QtGui.QApplication([])
    mw = DataViewerBase()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    main()