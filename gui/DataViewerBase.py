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
from collections import OrderedDict
from PyQt4.QtGui import QMainWindow, QGridLayout, QMenu, QWidget, QLabel, QTextList, QLineEdit
from PyQt4.QtGui import QPushButton, QMessageBox, QGroupBox, QDialog, QVBoxLayout, QHBoxLayout
from PyQt4.QtGui import QStyle, QPalette, QColor
from PyQt4.QtCore import pyqtSlot, QThread, QTimer, Qt
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
        self._font_size_button = 16
        self._font_size_groupbox_title = 12
        self._font_size_label = 11
        self._init_window_width = 1400
        self._init_window_height = 700
        
        self._is_run = False
        self._currentDir = os.path.dirname(__file__)
        self._emulate = True
        self._online = False
        self._closing_dialog = True

        if os.path.exists(os.path.join(os.path.dirname(__file__), "config.json")):
            self.loadConfig()
    
    @footprint
    def loadConfig(self):
        """
        Load a config file.
        """
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
        if config.get("font_size_button") is not None:
            if isinstance(config.get("font_size_button"), int):
                self._font_size_button = config["font_size_button"]
        if config.get("font_size_groupbox_title") is not None:
            if isinstance(config.get("font_size_groupbox_title"), int):
                self._font_size_groupbox_title = config["font_size_groupbox_title"]
        if config.get("font_size_label") is not None:
            if isinstance(config.get("font_size_label"), int):
                self._font_size_label = config["font_size_label"]
    
    @footprint
    def initGui(self):
        """
        Initialize the GUI.
        """
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.initMainWidget()
        self.setMenuBar()

        self.setWindowTitle("VMI Viewer")
        self.resize(self._init_window_width, self._init_window_height)

        ### RunInfo.
        group_runinfo = QGroupBox(self)
        group_runinfo.setTitle("RunInfo")
        font = group_runinfo.font()
        font.setPointSize(self._font_size_groupbox_title)
        group_runinfo.setFont(font)
        group_runinfo.resize(400, 100)
        grid_runinfo = QGridLayout(group_runinfo)
        
        # Run No.
        label_run = QLabel(self)
        label_run.setText("Run No. : ")
        font = label_run.font()
        font.setPointSize(self._font_size_label)
        label_run.setFont(font)
        
        self.label_run_number = QLabel(self)
        self.label_run_number.setText("Unknown")
        pal = QPalette()
        pal.setColor(QPalette.Foreground, QColor("#0B5345"))
        self.label_run_number.setPalette(pal)
        font = self.label_run_number.font()
        font.setBold(True)
        font.setPointSize(self._font_size_label)
        self.label_run_number.setFont(font)

        # Tag No.
        label_tag = QLabel(self)
        label_tag.setText("Tag No. : ")
        font = label_tag.font()
        font.setPointSize(self._font_size_label)
        label_tag.setFont(font)

        self.label_tag_start = QLabel(self)
        self.label_tag_start.setText("None")
        font = self.label_tag_start.font()
        font.setBold(True)
        font.setPointSize(self._font_size_label)
        self.label_tag_start.setFont(font)

        label_tag_hyphen = QLabel(self)
        label_tag_hyphen.setText(" - ")
        label_tag_hyphen.setFixedWidth(30)
        font = label_tag_hyphen.font()
        font.setPointSize(self._font_size_label)
        label_tag_hyphen.setFont(font)

        self.label_tag_end = QLabel(self)
        self.label_tag_end.setText("None")
        font = self.label_tag_end.font()
        font.setBold(True)
        font.setPointSize(self._font_size_label)
        self.label_tag_end.setFont(font)

        # Sig / BG.
        label_sig = QLabel(self)
        label_sig.setText("Sig # : ")
        font = label_sig.font()
        font.setPointSize(self._font_size_label)
        label_sig.setFont(font)

        self.label_sig_number = QLabel(self)
        self.label_sig_number.setText("None")
        font = self.label_sig_number.font()
        font.setBold(True)
        font.setPointSize(self._font_size_label)
        self.label_sig_number.setFont(font)

        label_bg = QLabel(self)
        label_bg.setText("BG # : ")
        font = label_bg.font()
        font.setPointSize(self._font_size_label)
        label_bg.setFont(font)

        self.label_bg_number = QLabel(self)
        self.label_bg_number.setText("None")
        font = self.label_bg_number.font()
        font.setBold(True)
        font.setPointSize(self._font_size_label)
        self.label_bg_number.setFont(font)

        # Construct the layout.
        grid_runinfo.addWidget(label_run, 0, 0)
        grid_runinfo.addWidget(self.label_run_number, 0, 1, 1, 3)
        
        grid_runinfo.addWidget(label_tag, 1, 0)
        grid_runinfo.addWidget(self.label_tag_start, 1, 1)
        grid_runinfo.addWidget(label_tag_hyphen, 1, 2)
        grid_runinfo.addWidget(self.label_tag_end, 1, 3)

        grid_runinfo.addWidget(label_sig, 2, 0)
        grid_runinfo.addWidget(self.label_sig_number, 2, 1)
        grid_runinfo.addWidget(label_bg, 2, 2)
        grid_runinfo.addWidget(self.label_bg_number, 2, 3)

        ### Settings.
        group_settings = QGroupBox(self)
        group_settings.setTitle("Settings")
        font = group_settings.font()
        font.setPointSize(self._font_size_groupbox_title)
        group_settings.setFont(font)
        group_settings.resize(400, 100)
        grid_settings = QGridLayout(group_settings)

        # Update interval.
        label_upd_rate = QLabel(self)
        label_upd_rate.setText("Upd. interval: ")
        font = label_upd_rate.font()
        font.setPointSize(self._font_size_label)
        label_upd_rate.setFont(font)
        
        self.textbox_upd_rate = QLineEdit(self)
        self.textbox_upd_rate.setText("1")
        self.textbox_upd_rate.setFixedWidth(60)
        self.textbox_upd_rate.setAlignment(Qt.AlignRight)
        font = self.textbox_upd_rate.font()
        font.setBold(True)
        font.setPointSize(self._font_size_label)
        self.textbox_upd_rate.setFont(font)

        label_upd_rate_unit = QLabel(self)
        label_upd_rate_unit.setText("sec")
        font = label_upd_rate_unit.font()
        font.setPointSize(self._font_size_label)
        label_upd_rate_unit.setFont(font)

        # Construct the layout.
        grid_settings.addWidget(label_upd_rate, 0, 0, 1, 3)
        grid_settings.addWidget(self.textbox_upd_rate, 0, 3)
        grid_settings.addWidget(label_upd_rate_unit, 0, 4)

        ### Function buttons.
        group_func = QGroupBox(self)
        group_func.setTitle("Setting")
        font = group_func.font()
        font.setPointSize(self._font_size_groupbox_title)
        group_func.setFont(font)
        group_func.resize(400, 100)
        box_func = QHBoxLayout(group_func)
        box_func.setSpacing(10)

        # Start/Stop main process button.
        self.brun = QPushButton(group_func)
        self.brun.setText("Start")
        font = self.brun.font()
        font.setPointSize(self._font_size_button)
        self.brun.setFont(font)
        self.brun.resize(400, 50)
        self.brun.clicked.connect(self.runMainProcess)

        # New window button. 
        bwindow = QPushButton(group_func)
        bwindow.setText("Window")
        font = bwindow.font()
        font.setPointSize(self._font_size_button)
        bwindow.setFont(font)
        bwindow.resize(400, 50)
        bwindow.clicked.connect(self.showWindow)
        
        # Construct the layout of RunInfo groupbox.
        box_func.addWidget(self.brun)
        box_func.addWidget(bwindow)

        ### Plotting area.
        kwargs = dict(px=False, py=False, ph=False, bp=False)
        self.pw1 = PlotWindow(self, **kwargs)
        self.pw2 = PlotWindow(self, **kwargs)
        self.pw3 = PlotWindow(self, **kwargs)

        ### Construct the layout.
        self.grid.addWidget(group_runinfo, 0, 0)
        self.grid.addWidget(group_settings, 0, 1)
        self.grid.addWidget(group_func, 0, 2)
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
    
    @footprint
    @pyqtSlot()
    def runMainProcess(self):
        if not self._timer_getData.isActive():
            self._timer_getData.start()
            self.brun.setText("Stop")
        else:
            self.brun.setEnabled(False)
            self.stopTimer = True
    
    # @pyqtSlot()
    # def mainProcess(self):
    #     if self._emulate:
    #         self.updateEmulateData()
    #     else:
    #         pass

######################## GetDataProcess ########################
    
    @footprint
    def initGetDataProcess(self):
        self._timer_getData = QTimer()
        self._timer_getData.setInterval(1000)
        self.stopTimer = False
        self._thread_getData = QThread()
        self._worker_getData = GetDataWorker()
        
        # Start.
        self._timer_getData.timeout.connect(self.startGettingDataThread)
        self._thread_getData.started.connect(self._worker_getData.process)
        self._worker_getData.sendData.connect(self.updateData)

        # Finish.
        self._worker_getData.finished.connect(self._thread_getData.quit)
        self._thread_getData.finished.connect(self.checkTimerGettingData)
    
    @footprint
    @pyqtSlot()
    def startGettingDataThread(self):
        if not self._thread_getData.isRunning():
            print("start thread by timer.")
            self._thread_getData.start()
        else:
            print("Thread is running.")
    
    @footprint
    @pyqtSlot(object)
    def updateData(self, obj):
        if self._emulate:
            self.updateEmulateData()
        else:
            self.sig = obj.copy()
            self.bg = obj.copy()
        self.updateImage()
    
    @footprint
    def updateImage(self):
        self.pw1.data = self.sig
        self.pw1.updateImage()
        self.pw2.data = self.bg
        self.pw2.updateImage()
        self.pw3.data = self.sig - self.bg
        self.pw3.updateImage()
        for window in self._windows:
            window.data = self.sig

    @footprint
    @pyqtSlot()
    def checkTimerGettingData(self):
        if self.stopTimer:
            self._timer_getData.stop()
            print("timer stopped.")
            self.stopTimer = False
            self.brun.setEnabled(True)
            self.brun.setText("Start")

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
    
    # @footprint
    @pyqtSlot()
    def checkWindow(self):
        """
        Check whether windows are active.
        """
        # print(len(self._windows))
        N = len(self._windows)*1
        for ii in range(N):
            if self._windows[N-ii-1].is_closed:
                del self._windows[N-ii-1]

    # @footprint
    # @pyqtSlot()
    # def finishWorker(self):
    #     pass

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
                json.dump(self.config, ff, indent=4)
            if self._timer_checkWindow.isActive():
                print("Stop checkWindow timer...")
                self._timer_checkWindow.stop()
                print("checkWindow timer stopped.")
    
    @footprint
    def makeConfig(self):
        """
        Make a config dict object to save the latest configration in.
        """
        self.config = OrderedDict([
            ("online", self._online), 
            ("closing_dialog", self._closing_dialog), 
            ("currentDir", self._currentDir), 
            ("emulate", self._emulate), 
            ("font_size_button", self._font_size_button),
            ("font_size_label", self._font_size_label),
            ("font_size_groupbox_title", self._font_size_groupbox_title)])


 ######################## Emulation functions ########################

    # @footprint
    # def emulateData(self):
    #     """
    #     Emulate data.
    #     TODO: modify so that this function works on a worker.
    #     """
    #     self._timer.setInterval(2000)
    #     self._timer.timeout.connect(self.updateEmulateData)
    #     self._timer.start()
    
    @footprint
    def updateEmulateData(self):
        self.sig = np.random.normal(100, 10, (100, 100))
        self.bg = np.random.normal(100, 10, (100, 100))

def main():
    app = QtGui.QApplication([])
    mw = DataViewerBase()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    main()