# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 00:42:08 2017

@author: Surpris
"""

import sys
import inspect
import os
import json
import time
import datetime
import numpy as np
from PyQt4.QtGui import QGridLayout, QDialog, QPushButton, QLabel, QGroupBox, QCheckBox
from PyQt4.QtCore import pyqtSlot
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
pg.setConfigOptions(imageAxisOrder='row-major')

sys.path.append("../")
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
        self._subplot_size = 100
        self._font_size_groupbox_title = 12
    
    @footprint
    def initGui(self):
        """
        Initialize the GUI.
        """
        self.resize(600, 600)
        grid = QGridLayout(self)
        grid.setSpacing(10)

        ### Functions.
        group_func = QGroupBox(self)
        # group_func.setTitle("Functions")
        font = group_func.font()
        font.setPointSize(self._font_size_groupbox_title)
        group_func.setFont(font)
        group_func.resize(400, 100)
        grid.addWidget(group_func, 0, 0)

        grid_func = QGridLayout(group_func)
        grid_func.setSpacing(10)

        # Some buttons.
        self._is_bp = self.kwargs.get("bp", True)
        if self._is_bp:
            self.bp = QPushButton(group_func)
            self.bp.setText("Start plotting")
            self.bp.clicked.connect(self.pushButton)
            grid_func.addWidget(self.bp, 0, 0, 1, 1)

        # Some options.
        label_logscale = QLabel(group_func)
        label_logscale.setText("Log")
        grid_func.addWidget(label_logscale, 0, 1)

        self.checkbox_logscale = QCheckBox(group_func)
        grid_func.addWidget(self.checkbox_logscale, 0, 2)

        ### Plotting area.
        self.initPlotArea()
        grid.addWidget(self.glw, 1, 0)

    @footprint
    def initPlotArea(self):
        """
        Initialize the plot area.
        """
        # Construct the graphic layout.
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.resize(600, 600)

        # Plot area for x-projection.
        self._is_px = self.kwargs.get("px", True)
        if self._is_px:
            self.px = self.glw.addPlot()
            self.px.setMaximumWidth(self._subplot_size)

        # Plot area for the image.
        p1 = self.glw.addPlot()
        self.iw = pg.ImageItem()
        p1.addItem(self.iw)

        def mouseMoved(pos):
            try:
                # pos = event.pos()
                print("Image position:", self.iw.mapFromScene(pos))
            except Exception as ex:
                print(ex)
        
        self.iw.scene().sigMouseMoved.connect(mouseMoved)

        # Contrast/color control
        hist = pg.HistogramLUTItem()
        hist.setImageItem(self.iw)
        hist.setMaximumWidth(self._subplot_size)
        self.glw.addItem(hist)

        # Plot area for histogram.
        self._is_ph = self.kwargs.get("ph", True)
        self._is_py = self.kwargs.get("py", True)
        if self._is_ph or self._is_py:
            self.glw.nextRow()
        if self._is_ph:
            self.ph = self.glw.addPlot()
            self.ph.setMaximumHeight(self._subplot_size)
            self.ph.setMaximumWidth(self._subplot_size)
        
        # Plot area for y-projection.
        if self._is_py:
            self.py = self.glw.addPlot()
            self.py.setMaximumHeight(self._subplot_size)


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