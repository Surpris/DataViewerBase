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
from PyQt4.QtGui import QMainWindow, QGridLayout, QMenu, QWidget
from PyQt4.QtGui import QPushButton, QMessageBox, QGroupBox, QDialog, QVBoxLayout, QHBoxLayout
from PyQt4.QtCore import pyqtSlot, QThread, QTimer
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

sys.path.append("../")
from gui import PlotWindow
from core.Worker import *
from core.decorator import footprint

class DataViewerBase(QMainWindow):
    """
    Base GUI class for viewing data / images.
    This class was made in the purpose of viewing VMI images.
    """
    # _name = DataViewerBase().__class__.__name__

    def __init__(self):
        """
        Initialization.
        """
        super().__init__()
        print("Initialize this application...")
        self.initInnerParameters()
        self.initGui()
        self.initGetDataProcess()
        self.initCheckWindowProcess()
    
    @footprint
    def initInnerParameters(self):
        """
        Initialize the inner parameters.
        """
        self._windows = []
        self.sig = None
        self.bg = None
        self._timer = QTimer()
        
        self._is_run = False
        self._currentDir = os.path.dirname(__file__)
        self._emulate = True
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
            if config.get("emulate") is not None:
                if isinstance(config.get("emulate"), bool):
                    self._emulate = config["emulate"]
    
    @footprint
    def initGui(self):
        """
        Initialize the GUI.
        """
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.initMainWidget()
        self.setMenuBar()

        self.setWindowTitle("VMI Viewer")
        self.resize(1280, 600)

        ### RunInfo.
        group_runinfo = QGroupBox(self)
        group_runinfo.setTitle("RunInfo")
        group_runinfo.resize(400, 100)
        grid_runinfo = QGridLayout(group_runinfo)

        ### Function buttons.
        group_func = QGroupBox(self)
        group_func.setTitle("Functions")
        group_func.resize(400, 100)
        box_func = QHBoxLayout(group_func)
        box_func.setSpacing(10)

        # Start/Stop main process button.
        self.brun = QPushButton(group_func)
        self.brun.setText("Start")
        font = self.brun.font()
        font.setPointSize(16)
        self.brun.setFont(font)
        self.brun.resize(400, 50)
        self.brun.clicked.connect(self.runMainProcess)

        # New window button. 
        bwindow = QPushButton(group_func)
        bwindow.setText("Window")
        font = bwindow.font()
        font.setPointSize(16)
        bwindow.setFont(font)
        bwindow.resize(400, 50)
        bwindow.clicked.connect(self.showWindow)
        
        # Construct the layout of RunInfo groupbox.
        box_func.addWidget(self.brun)
        box_func.addWidget(bwindow)

        ### Plotting area.
        self.pw1 = PlotWindow(self, px=False, py=False, ph=False)
        self.pw1.bp.setEnabled(False)
        self.pw2 = PlotWindow(self, px=False, py=False, ph=False)
        self.pw2.bp.setEnabled(False)
        self.pw3 = PlotWindow(self, px=False, py=False, ph=False)
        self.pw3.bp.setEnabled(False)

        ### Construct the layout.
        self.grid.addWidget(group_runinfo, 0, 0)
        self.grid.addWidget(group_func, 0, 1)
        self.grid.addWidget(self.pw1, 1, 0, 2, 1)
        self.grid.addWidget(self.pw2, 1, 1, 2, 1)
        self.grid.addWidget(self.pw3, 1, 2, 2, 1)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
    
    @footprint
    def initMainWidget(self):
        """
        Initialize the main widget and the grid.
        """
        self.main_widget = QWidget(self)
        self.grid = QGridLayout(self.main_widget)
        self.grid.setSpacing(10)

    @footprint
    def setMenuBar(self):
        """
        Set the contents of the menu bar
        """
        ## File
        file_menu = QMenu('&File', self)

        # Open
        # file_menu.addAction('&Open', self.openFile,
        #         QtCore.Qt.CTRL + QtCore.Qt.Key_O)

        # Config
        file_menu.addAction('&Config', self.setConfig,
                QtCore.Qt.CTRL + QtCore.Qt.Key_C)
        # Quit
        file_menu.addAction('&Quit', self.quitApp,
                QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        
        self.menuBar().addMenu(file_menu)

        ## Help
        help_menu = QMenu('&Help', self)
        help_menu.addAction('Help', self.showHelp)
        help_menu.addAction('About...', self.showAbout)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(help_menu)

######################## Menu bar ########################

    @footprint
    def openFile(self):
        """
        Show a file dialog and select a file
        """
        pass

    @footprint
    def setConfig(self):
        """
        Set configuration of this application.
        """
        pass

    @footprint
    def quitApp(self):
        """
        Quit this application.
        """
        self.close()
    
    @footprint
    def showHelp(self):
        """
        Show a pop-up dialog showing how to use this application.
        """
        pass

    @footprint
    def showAbout(self):
        """
        Show a pop-up dialog describing this application.
        """
        pass

######################## Widgets' functions ########################

    @footprint
    @pyqtSlot()
    def showWindow(self):
        window = PlotWindow(self, "win{0:02d}".format(len(self._windows)+1))
        window.show()
        window.raise_()
        window.activateWindow()
        self._windows.append(window)
    
    @pyqtSlot()
    def runMainProcess(self):
        if not self._is_run:
            self._worker_getData = Worker(name="RunWorker")
            self._worker_getData.sleep_interval = 1900
            self._worker_getData.do_something.connect(self.mainProcess)
            self._worker_getData.finished.connect(self.finishWorker)
            self._worker_getData.start()
            self.brun.setText("Stop")
            self._is_run = True
        else:
            self._worker_getData.stop()
            # self._worker_getData.quit()
            self._worker_getData.wait()
            self.brun.setText("Start")
            self._is_run = False
    
    @pyqtSlot()
    def mainProcess(self):
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        if self._emulate:
            self.updateEmulateData()
        else:
            pass
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

######################## GetDataProcess ########################
    
    @footprint
    def initGetDataProcess(self):
        self._timer_getData = QTimer()
        self._thread_getData = QThread()
        self._worker_getData = GetDataWorker()

######################## CheckWindowProcess ########################

    @footprint
    def initCheckWindowProcess(self):
        """
        Initialize checkWindow process.
        """
        self._timer_checkWindow = QTimer()
        self._timer_checkWindow.setInterval(1000)
        self._timer_checkWindow.timeout.connect(self.checkWindow)
        self._timer_checkWindow.start()
    
    @footprint
    @pyqtSlot()
    def checkWindow(self):
        """
        Check whether windows are active.
        """
        print(len(self._windows))
        N = len(self._windows)*1
        for ii in range(N):
            if self._windows[N-ii-1].is_closed:
                del self._windows[N-ii-1]

    @footprint
    @pyqtSlot()
    def finishWorker(self):
        pass

######################## Closing processes ########################

    @footprint
    def closeEvent(self, event):
        if self._thread_getData.isRunning():
            string = "Some threads are still running.\n"
            string += "Please wait for their finishing."
            confirmObject = QMessageBox.warning(self, "Closing is ignored.",
                string, QMessageBox.Ok)
            event.ignore()
            return
        if self._closing_dialog:
            confirmObject = QMessageBox.question(self, "Closing...",
                "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No)
            if confirmObject == QMessageBox.Yes:
                self.makeConfig()
                with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as ff:
                    json.dump(self.config, ff)
                if self._timer_checkWindow.isActive():
                    print("Stop checkWindow timer...")
                    self._timer_checkWindow.stop()
                    print("checkWindow timer stopped.")
                event.accept()
            else:
                event.ignore()
        else:
            self.makeConfig()
            with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as ff:
                json.dump(self.config, ff)
            if self._timer_checkWindow.isActive():
                print("Stop checkWindow timer...")
                self._timer_checkWindow.stop()
                print("checkWindow timer stopped.")
    
    @footprint
    def makeConfig(self):
        """
        Make a config dict object to save the latest configration in.
        """
        self.config = {"online":self._online, "closing_dialog":self._closing_dialog, 
                       "currentDir":self._currentDir, "emulate":self._emulate}


 ######################## Emulation functions ########################

    @footprint
    def emulateData(self):
        """
        Emulate data.
        TODO: modify so that this function works on a worker.
        """
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self.updateEmulateData)
        self._timer.start()
    
    def updateEmulateData(self):
        self.sig = np.random.normal(100, 10, (100, 100))
        self.bg = np.random.normal(100, 10, (100, 100))
        self.pw1.data = self.sig
        self.pw1.updateImage()
        self.pw2.data = self.bg
        self.pw2.updateImage()
        self.pw3.data = self.sig - self.bg
        self.pw3.updateImage()
        for window in self._windows:
            window.data = self.sig

def main():
    app = QtGui.QApplication([])
    mw = DataViewerBase()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    main()