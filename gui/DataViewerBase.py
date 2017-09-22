# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 23:22:08 2017

@author: Surpris
"""

import sys
import inspect
import time
import os
import json
import datetime
from collections import OrderedDict
from PyQt4.QtGui import QMainWindow, QGridLayout, QMenu, QWidget, QLabel, QTextList, QLineEdit
from PyQt4.QtGui import QSpinBox, QDoubleSpinBox, QIcon
from PyQt4.QtGui import QPushButton, QMessageBox, QGroupBox, QDialog, QVBoxLayout, QHBoxLayout
from PyQt4.QtGui import QStyle, QPalette, QColor, QPixmap
from PyQt4.QtCore import pyqtSlot, QThread, QTimer, Qt, QMutex
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

    def __init__(self, filepath):
        """
        Initialization.
        """
        super().__init__()
        self.initInnerParameters(filepath)
        self.initGui()
        self.initGetDataProcess()
        self.initUpdateImageProcess()
        self.initCheckWindowProcess()
    
    @footprint
    def initInnerParameters(self, filepath):
        """
        Initialize the inner parameters.
        """
        self._mutex = QMutex()
        self._windows = []
        self.initData()
        self._isUpdatingImage = False
        self._font_size_button = 16 # [pixel]
        self._font_size_groupbox_title = 12 # [pixel]
        self._font_size_label = 11 # [pixel]
        self._font_bold_label = True
        self._init_window_width = 1600 # [pixel]
        self._init_window_height = 700 # [pixel]
        self._init_button_color = "#EBF5FB"
        self.main_bgcolor = "#FDF2E9"

        self._get_data_interval = 1 # [sec]
        self._get_data_worker_sleep_interval = self._get_data_interval - 0.1 # [sec]
        self._update_image_interval = 2 # [sec]
        self._get_update_delay = 1 # [sec]
        self._check_window_interval = 1 # [sec]

        self._currentDir = os.path.dirname(__file__)
        self._online = False
        self._closing_dialog = True

        if os.path.exists(os.path.join(os.path.dirname(__file__), "config.json")):
            self.loadConfig()
        if os.path.exists(filepath):
            self.loadConfigGetData(filepath)
        
    @footprint
    @pyqtSlot()
    def initData(self):
        """
        Initialize inner data.
        """
        self.dataset = {"sig_wl":None, "sig_wol":None, "bg_wl":None, "bg_wol":None}
        self.nbr_of_sig = 0
        self.nbr_of_bg = 0
        self.sig = None
        self.bg = None
        self.currentRun = -1
        self.startTag = -1
        self.endTag = -1
    
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
        if config.get("font_bold_label") is not None:
            if isinstance(config.get("font_bold_label"), bool):
                self._font_bold_label = config["font_bold_label"]
        self._config = config
    
    def loadConfigGetData(self, filepath):
        """
        Load a config file of getDatawithOLPY.
        """
        with open(filepath,'r') as ff:
            config_get_data = json.load(ff)
        self._get_data_interval = config_get_data["interval"] # [sec]
        self._get_data_worker_sleep_interval = self._get_data_interval - 0.1 # [sec]
        self._get_data_ports = config_get_data["port"]
        self._get_info_port = config_get_data["port_info"]
        self._config_get_data = config_get_data
    
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
        label_run.setAlignment(Qt.AlignRight)
        font = label_run.font()
        font.setPointSize(self._font_size_label)
        font.setBold(self._font_bold_label)
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
        label_tag.setAlignment(Qt.AlignRight)
        font = label_tag.font()
        font.setPointSize(self._font_size_label)
        font.setBold(self._font_bold_label)
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
        font.setBold(self._font_bold_label)
        label_tag_hyphen.setFont(font)

        self.label_tag_end = QLabel(self)
        self.label_tag_end.setText("None")
        font = self.label_tag_end.font()
        font.setBold(True)
        font.setPointSize(self._font_size_label)
        self.label_tag_end.setFont(font)

        # Sig / BG.
        label_sig = QLabel(self)
        label_sig.setText("# of Sig : ")
        label_sig.setAlignment(Qt.AlignRight)
        font = label_sig.font()
        font.setPointSize(self._font_size_label)
        font.setBold(self._font_bold_label)
        label_sig.setFont(font)

        self.label_nbr_of_sig = QLabel(self)
        self.label_nbr_of_sig.setText("None")
        font = self.label_nbr_of_sig.font()
        font.setBold(True)
        font.setPointSize(self._font_size_label)
        self.label_nbr_of_sig.setFont(font)

        label_bg = QLabel(self)
        label_bg.setText("# of BG : ")
        label_bg.setAlignment(Qt.AlignRight)
        font = label_bg.font()
        font.setPointSize(self._font_size_label)
        font.setBold(self._font_bold_label)
        label_bg.setFont(font)

        self.label_nbr_of_bg = QLabel(self)
        self.label_nbr_of_bg.setText("None")
        font = self.label_nbr_of_bg.font()
        font.setBold(True)
        font.setPointSize(self._font_size_label)
        self.label_nbr_of_bg.setFont(font)

        # Construct the layout.
        grid_runinfo.addWidget(label_run, 0, 0)
        grid_runinfo.addWidget(self.label_run_number, 0, 1, 1, 3)
        
        grid_runinfo.addWidget(label_tag, 1, 0)
        grid_runinfo.addWidget(self.label_tag_start, 1, 1)
        grid_runinfo.addWidget(label_tag_hyphen, 1, 2)
        grid_runinfo.addWidget(self.label_tag_end, 1, 3)

        grid_runinfo.addWidget(label_sig, 2, 0)
        grid_runinfo.addWidget(self.label_nbr_of_sig, 2, 1)
        grid_runinfo.addWidget(label_bg, 2, 2)
        grid_runinfo.addWidget(self.label_nbr_of_bg, 2, 3)

        ### Settings.
        # group_settings = QGroupBox(self)
        # group_settings.setTitle("Settings")
        # font = group_settings.font()
        # font.setPointSize(self._font_size_groupbox_title)
        # group_settings.setFont(font)
        # group_settings.resize(400, 100)
        # grid_settings = QGridLayout(group_settings)

        # # Update interval.
        # label_upd_rate = QLabel(self)
        # label_upd_rate.setText("Upd. image interval: ")
        # font = label_upd_rate.font()
        # font.setPointSize(self._font_size_label)
        # font.setBold(self._font_bold_label)
        # label_upd_rate.setFont(font)
        
        # self.spinbox_upd_img_interval = QDoubleSpinBox(self)
        # self.spinbox_upd_img_interval.setValue(self._get_data_interval)
        # self.spinbox_upd_img_interval.setFixedWidth(100)
        # self.spinbox_upd_img_interval.setAlignment(Qt.AlignRight)
        # font = self.spinbox_upd_img_interval.font()
        # font.setBold(True)
        # font.setPointSize(self._font_size_label)
        # self.spinbox_upd_img_interval.setFont(font)

        # label_upd_rate_unit = QLabel(self)
        # label_upd_rate_unit.setText("sec")
        # font = label_upd_rate_unit.font()
        # font.setPointSize(self._font_size_label)
        # font.setBold(self._font_bold_label)
        # label_upd_rate_unit.setFont(font)

        # Construct the layout.
        # grid_settings.addWidget(label_upd_rate, 0, 0, 1, 3)
        # grid_settings.addWidget(self.spinbox_upd_img_interval, 0, 3)
        # grid_settings.addWidget(label_upd_rate_unit, 0, 4)

        ### Function buttons.
        group_func = QGroupBox(self)
        group_func.setTitle("Function")
        font = group_func.font()
        font.setPointSize(self._font_size_groupbox_title)
        group_func.setFont(font)
        group_func.resize(400, 100)
        grid_func = QGridLayout(group_func)
        grid_func.setSpacing(10)

        # Start/Stop main process button.
        self.brun = QPushButton(group_func)
        self.brun.setText("Start")
        font = self.brun.font()
        font.setPointSize(self._font_size_button)
        self.brun.setFont(font)
        self.brun.resize(400, 50)
        self.brun.setStyleSheet("background-color:{};".format(self._init_button_color))
        self.brun.clicked.connect(self.runMainProcess)

        # Clear data button.
        bclear = QPushButton(group_func)
        bclear.setText("Clear")
        font = bclear.font()
        font.setPointSize(self._font_size_button)
        bclear.setFont(font)
        bclear.resize(400, 50)
        bclear.setStyleSheet("background-color:{};".format(self._init_button_color))
        bclear.clicked.connect(self.clearData)

        # Save images button.
        bsave = QPushButton(group_func)
        bsave.setText("Save")
        font = bsave.font()
        font.setPointSize(self._font_size_button)
        bsave.setFont(font)
        bsave.resize(400, 50)
        bsave.setStyleSheet("background-color:{};".format(self._init_button_color))
        bsave.clicked.connect(self.saveData)

        # New window button. 
        bwindow = QPushButton(group_func)
        bwindow.setText("Window")
        font = bwindow.font()
        font.setPointSize(self._font_size_button)
        bwindow.setFont(font)
        bwindow.resize(400, 50)
        bwindow.setStyleSheet("background-color:{};".format(self._init_button_color))
        bwindow.clicked.connect(self.showWindow)
        
        # Construct the layout of RunInfo groupbox.
        grid_func.addWidget(self.brun, 0, 0)
        grid_func.addWidget(bclear, 0, 1)
        grid_func.addWidget(bsave, 1, 0)
        grid_func.addWidget(bwindow, 1, 1)

        ### Plotting area.
        grp1 = QGroupBox(self)
        # grp1.setTitle("SIG WL")
        grp1.setTitle("SIG")
        font = grp1.font()
        font.setPointSize(self._font_size_groupbox_title)
        grp1.setFont(font)
        gp1 = QGridLayout(grp1)
        gp1.setSpacing(10)

        grp2 = QGroupBox(self)
        # grp2.setTitle("SIG WOL")
        grp2.setTitle("BG")
        font = grp2.font()
        font.setPointSize(self._font_size_groupbox_title)
        grp2.setFont(font)
        gp2 = QGridLayout(grp2)
        gp2.setSpacing(10)

        grp3 = QGroupBox(self)
        # grp3.setTitle("BG WL")
        grp3.setTitle("SIg - BG")
        font = grp3.font()
        font.setPointSize(self._font_size_groupbox_title)
        grp3.setFont(font)
        gp3 = QGridLayout(grp3)
        gp3.setSpacing(10)

        # grp4 = QGroupBox(self)
        # grp4.setTitle("BG WOL")
        # font = grp4.font()
        # font.setPointSize(self._font_size_groupbox_title)
        # grp4.setFont(font)
        # gp4 = QGridLayout(grp4)
        # gp4.setSpacing(10)

        kwargs = dict(px=False, py=False, ph=False, bp=False)
        self.pw1 = PlotWindow(self, **kwargs)
        self.pw2 = PlotWindow(self, **kwargs)
        self.pw3 = PlotWindow(self, **kwargs)
        # self.pw4 = PlotWindow(self, **kwargs)

        gp1.addWidget(self.pw1, 0, 0)
        gp2.addWidget(self.pw2, 0, 0)
        gp3.addWidget(self.pw3, 0, 0)
        # gp4.addWidget(self.pw4, 0, 0)

        ### Construct the layout.
        self.grid.addWidget(group_runinfo, 0, 0)
        # self.grid.addWidget(group_settings, 0, 1)
        self.grid.addWidget(group_func, 0, 1)
        self.grid.addWidget(grp1, 1, 0, 2, 1)
        self.grid.addWidget(grp2, 1, 1, 2, 1)
        self.grid.addWidget(grp3, 1, 2, 2, 1)
        # self.grid.addWidget(grp4, 1, 3, 2, 1)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
    
    @footprint
    def initMainWidget(self):
        """
        Initialize the main widget and the grid.
        """
        self.main_widget = QWidget(self)
        self.setStyleSheet("background-color:{};".format(self.main_bgcolor))
        self.grid = QGridLayout(self.main_widget)
        self.grid.setSpacing(10)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "python.png")))

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
        # help_menu = QMenu('&Help', self)
        # help_menu.addAction('Help', self.showHelp)
        # help_menu.addAction('About...', self.showAbout)
        self.menuBar().addSeparator()
        # self.menuBar().addMenu(help_menu)

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
            self.initData()
            for listener in self._worker_getData.listeners.values():
                listener.Connect()
            self._worker_getData.listener_info.Connect()
            # self._update_image_interval = self.spinbox_upd_img_interval.value()
            # self.spinbox_upd_img_interval.setEnabled(False)
            self._timer_getData.start()
            self.brun.setText("Stop")
            if not self._timer_updImage.isActive():
                time.sleep(self._get_update_delay)
                self._timer_updImage.start()
        else:
            self.brun.setEnabled(False)
            self.stopTimer = True
    
    @footprint
    @pyqtSlot()
    def saveData(self):
        now_save = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        saveDataDir = os.path.join(os.path.dirname(__file__), "data", "Run{}".format(str(self.currentRun)))
        
        # Data.
        if not os.path.exists(saveDataDir):
            os.makedirs(saveDataDir)
        for _types in self._get_data_ports.keys():
            np.save(os.path.join(saveDataDir, "data_{0}_{1}.npy".format(now, _types)), \
                    self.dataset[_types])
        
        # Image.
        saveScn = os.path.join(saveDataDir, "{}_screenshot.png".format(now))
        QPixmap.grabWindow(self.winId()).save(saveScn, 'png')

        # Status.
        status = {"save_datetime":now_save, "Run":self.label_run_number.text(), 
                  "StartTag":self.label_tag_start.text(), "CurrentTag":self.label_tag_end.text()}
        with open(os.path.join(saveDataDir, "{}_status.json".format(now)), "w") as ff:
            json.dump(status, ff)
    
    @footprint
    @pyqtSlot()
    def clearData(self):
        self.saveData()
        self.initData()

######################## GetDataProcess ########################
    
    @footprint
    def initGetDataProcess(self):
        self._timer_getData = QTimer()
        self._timer_getData.setInterval(int(self._get_data_interval*1000))
        self.stopTimer = False
        self._thread_getData = QThread()
        self._worker_getData = GetDataWorker3(port=self._get_data_ports, port_info=self._get_info_port)
        self._worker_getData.sleepInterval = self._get_data_worker_sleep_interval
        
        # Start.
        self._timer_getData.timeout.connect(self.startGettingDataThread)
        self._thread_getData.started.connect(self._worker_getData.process)
        self._worker_getData.do_something.connect(self.updateData)

        # Finish.
        self._worker_getData.finished.connect(self._thread_getData.quit)
        self._thread_getData.finished.connect(self.checkIsTimerStopped)

        # Move.
        self._worker_getData.moveToThread(self._thread_getData)
    
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
        if self._isUpdatingImage is False: # In case.
            if obj is not None:
                for key in self.dataset.keys():
                    if self.dataset.get(key) is None and obj.get(key) is not None:
                        self.dataset[key] = obj.get(key).copy()
                    elif obj.get(key) is not None:
                        self.dataset[key] += obj.get(key).copy()
                currentRun = obj.get("currentRun")
                self.label_run_number.setText(str(currentRun))
                if self.nbr_of_sig == 0:
                    self.label_tag_start.setText(str(obj.get("startTag")))
                self.label_tag_end.setText(str(obj.get("endTag")))

                self.nbr_of_sig += obj.get("nbr_sig_wl") + obj.get("nbr_sig_wol")
                self.nbr_of_bg += obj.get("nbr_bg_wl") + obj.get("nbr_bg_wol")
                self.label_nbr_of_sig.setText(str(self.nbr_of_sig))
                self.label_nbr_of_bg.setText(str(self.nbr_of_bg))
                if self.currentRun != -1 and currentRun != self.currentRun:
                    self.saveData()
                    self.initData()
                self.currentRun = currentRun

    @footprint
    @pyqtSlot()
    def checkIsTimerStopped(self):
        if self.stopTimer:
            self._timer_getData.stop()
            self._timer_updImage.stop()
            print("timer stopped.")
            for listener in self._worker_getData.listeners.values():
                listener.Close()
            self._worker_getData.listener_info.Close()
            self.stopTimer = False
            self.brun.setEnabled(True)
            self.brun.setText("Start")
            # self.spinbox_upd_img_interval.setEnabled(True)

######################## updateImageProcess ########################

    @footprint
    def initUpdateImageProcess(self):
        self._timer_updImage = QTimer()
        self._timer_updImage.setInterval(int(self._update_image_interval*1000))
        self._timer_updImage.timeout.connect(self.updateImage)
    
    @footprint
    def updateImage(self):
        self._isUpdatingImage = True
        try:
            with QMutexLocker(self._mutex):
                sig_wl = self.dataset.get("sig_wl", None)
                sig_wol = self.dataset.get("sig_wol", None)
                bg_wl = self.dataset.get("bg_wl", None)
                bg_wol = self.dataset.get("bg_wol", None)
                if self.sig is None or self.bg is None:
                    self.sig = sig_wl + sig_wol
                    self.bg = bg_wl + bg_wol
                else:
                    self.sig += sig_wl + sig_wol
                    self.bg += bg_wl + bg_wol
                # print(self.sig.dtype)
                # buff1 = self.sig / float(self.nbr_of_sig)
                self.pw1.data = self.sig / float(self.nbr_of_sig)
                # buff1 = self.bg / float(self.nbr_of_bg)
                self.pw2.data = self.bg / float(self.nbr_of_bg)
                self.pw3.data = self.pw1.data - self.pw2.data
                # self.pw4.data = bg_wol

                # if sig_wl is not None and sig_wol is not None:
                #     self.pw3.data = sig_wl - sig_wol
                for window in self._windows:
                    if not window.is_closed:
                        window.data = sig_wl
        except Exception as ex:
            print(ex)
        self._isUpdatingImage = False
        
        if self.sig is not None and self.bg is not None:
            self.pw1.updateImage()
            self.pw2.updateImage()
            self.pw3.updateImage()
        # self.pw4.updateImage()
    
######################## CheckWindowProcess ########################

    @footprint
    def initCheckWindowProcess(self):
        """
        Initialize checkWindow process.
        """
        self._timer_checkWindow = QTimer()
        self._timer_checkWindow.setInterval(int(self._check_window_interval*1000))
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
                self.stopAllTimers()
                self.saveData()
                event.accept()
            else:
                event.ignore()
        else:
            self.makeConfig()
            with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as ff:
                json.dump(self.config, ff, indent=4)
            self.saveData()
            self.stopAllTimers()

    @footprint
    def stopAllTimers(self):
        if self._timer_getData.isActive():
            self._timer_getData.stop()
        if self._timer_updImage.isActive():
            self._timer_updImage.stop()
        if self._timer_checkWindow.isActive():
            self._timer_checkWindow.stop()
    
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

def main():
    app = QtGui.QApplication([])
    mw = DataViewerBase()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    main()