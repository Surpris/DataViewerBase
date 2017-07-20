# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 15:02:08 2017

@author: Surpris
"""

import sys
import inspect
import os
import json
import time
import datetime
import numpy as np
from PyQt4.QtGui import QGridLayout, QDialog, QPushButton, QLabel, QGroupBox, QCheckBox, QHBoxLayout
from PyQt4.QtGui import QWidget, QDoubleSpinBox
from PyQt4.QtCore import pyqtSlot, Qt
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
pg.setConfigOptions(imageAxisOrder='row-major')

sys.path.append("../")
import anatools as ans
from core.decorator import footprint

class PlotWindow(QDialog):
    """
    Class for some plots.
    """

    def __init__(self, parent=None, name = "", **kwargs):
        """
        Initialization.
        """
        super().__init__(parent)
        self.setParent(parent)
        print("Initialize this plot window...")
        self.name = name
        self.kwargs = kwargs
        self.initInnerParameters()
        self.initGui()

    @footprint
    def initInnerParameters(self):
        """
        Initialize the inner parameters.
        """
        self.is_closed = False
        self._timer = QtCore.QTimer()
        self._is_emulate = False
        self.data = None
        self._init_window_width = 600 # [pixel]
        self._init_window_height = 600 # [pixel]
        self._subplot_size = 100 # [pixel]
        self._font_size_groupbox_title = 11 # [pixel]
    
    @footprint
    def initGui(self):
        """
        Initialize the GUI.
        """
        self.resize(self._init_window_width, self._init_window_height)
        grid = QGridLayout(self)
        grid.setSpacing(10)

        ### Functions.
        group_func = QGroupBox(self)
        font = group_func.font()
        font.setPointSize(self._font_size_groupbox_title)
        group_func.setFont(font)
        group_func.resize(400, 100)
        grid_func = QGridLayout(group_func)
        grid_func.setSpacing(10)

        # Some buttons.
        self._is_bp = self.kwargs.get("bp", True)
        if self._is_bp:
            self.bp = QPushButton(group_func)
            self.bp.setText("Start plotting")
            self.bp.clicked.connect(self.pushButton)
            
        # Some options.
        label_logscale = QLabel(group_func)
        label_logscale.setText("Log")
        
        self.checkbox_logscale = QCheckBox(group_func)

        # Construct.
        if self._is_bp:
            grid_func.addWidget(self.bp, 0, 0, 1, 1)
        grid_func.addWidget(label_logscale, 0, 1)
        grid_func.addWidget(self.checkbox_logscale, 0, 2)
        
        ### Coordinate and Value of the mouse pointer.
        widget_coor_value = QWidget(self)
        widget_coor_value.resize(self._init_window_width, 30)
        grid_coor_value = QGridLayout(widget_coor_value)
        grid_coor_value.setSpacing(10)

        label_coor_value = QLabel(self)
        label_coor_value.setText("Coor, Value:")
        label_coor_value.setAlignment(Qt.AlignRight)
        # label_coor_value.setFixedWidth(120)
        font = label_coor_value.font()
        font.setPointSize(self._font_size_groupbox_title)
        font.setBold(True)
        label_coor_value.setFont(font)

        self.label_coor_value = QLabel(self)
        # self.label_coor_value.setFixedSize(200, 30)
        self.label_coor_value.setText("")
        font = self.label_coor_value.font()
        font.setPointSize(self._font_size_groupbox_title)
        font.setBold(True)
        self.label_coor_value.setFont(font)

        # Construct.
        grid_coor_value.addWidget(label_coor_value, 0, 0)
        grid_coor_value.addWidget(self.label_coor_value, 0, 1, 1, 3)

        
        ### Plotting area.
        self.initPlotArea()

        ### Construct the layout.
        grid.addWidget(group_func, 0, 0)
        grid.addWidget(self.glw, 1, 0)
        grid.addWidget(widget_coor_value, 1, 0)

    @footprint
    def initPlotArea(self):
        """
        Initialize the plot area.
        """
        # Construct the graphic layout.
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.resize(self._init_window_width, self._init_window_height)

        # Plot area.
        self.plotArea = self.glw.addPlot()

        # # Plot area for the image.
        # p1 = self.glw.addPlot()
        # p1.setAspectLocked(True)
        # self.iw = pg.ImageItem()
        # p1.addItem(self.iw)

        def mouseMoved(pos):
            try:
                coor = self.plotArea.mapFromScene(pos)
                x, y = int(coor.x()), int(coor.y())
                if self.iw.image is not None:
                    img = self.iw.image
                    if 0 <= x <= img.shape[1] and 0 <= y <= img.shape[0]:
                        self.label_coor_value.setText("({0}, {1}, {2:.2e})".format(x, y, img[y, x]))
            except Exception as ex:
                print(ex)
        
        self.plotArea.scene().sigMouseMoved.connect(mouseMoved)

    @footprint
    @pyqtSlot()
    def pushButton(self):
        """
        Button function.
        """
        try:
            if not self._timer.isActive():
                self._timer.setInterval(1000)
                self._timer.timeout.connect(self.updateImage)
                self._timer.start()
                self.bp.setText("Stop plotting")
            else:
                self._timer.stop()
                self.bp.setText("Start plotting")
        except Exception as ex:
            print(ex)

    # @footprint
    @pyqtSlot()
    def updateImage(self):
        """
        Update the image and the other plots.
        """
        try:
            if self.data is not None:
                if self._is_emulate:
                    self.data = np.random.normal(100, 10, (100, 100))
                self.iw.setImage(self.data)
                # self.hist.vb.setLimits(yMin=self.data.min(), yMax=self.data.max())
                if self.checkbox_logscale.isChecked:
                    # if self.data.min() < 0:
                    #     self.hist.vb.setLimits(yMin=0.1, yMax=self.data.max())
                    self.hist.plot.setLogMode(False,True)
                if self._is_px:
                    self.px.plot(self.data.mean(axis=1), np.arange(self.data.shape[0]), clear=True)
                if self._is_py:
                    self.py.plot(np.arange(self.data.shape[1]), self.data.mean(axis=0), clear=True)
                if self._is_ph:
                    hist, xbins = np.histogram(self.data.flatten())
                    dxbins = xbins[1] - xbins[0]
                    self.ph.plot(xbins + dxbins/2.0, hist, clear=True,
                                stepMode=True, fillLevel=0,brush=(0,0,255,150))
        except Exception as ex:
            print(ex)

    @footprint
    def closeEvent(self, event):
        self.is_closed = True
        if self._timer.isActive():
            print("Stop the active timer.")
            self._timer.stop()
        self.data = None