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
from PyQt4.QtGui import QMainWindow, QGridLayout, QDialog, QPushButton, QWidget, QMenu
from PyQt4.QtCore import pyqtSlot
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
pg.setConfigOptions(imageAxisOrder='row-major')

class PlotWindow(QDialog):
    """
    Class for some plots.
    """
    def __init__(self, parent=None, name = ""):
        """
        Initialization.
        """
        super().__init__(parent)
        self.setParent(parent)
        print("Initialize this plot window...")
        self.name = name
        self.initInnerParameters()
        self.initGui()

    def initInnerParameters(self):
        """
        Initialize the inner parameters.
        """
        print(">>" + self.name + "()" + self.__class__.__name__ \
              + "." + inspect.currentframe().f_code.co_name + "()")
        self.is_closed = False
        self._timer = QtCore.QTimer()
        self._is_emulate = False
        self.data = None
        self._subplot_size = 100
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
    
    def initGui(self):
        """
        Initialize the GUI.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        self.resize(600, 600)
        self.grid = QGridLayout(self)
        self.grid.setSpacing(10)

        ## Some buttons.
        self.bp = QPushButton()
        self.bp.setText("Start plotting")
        self.bp.clicked.connect(self.pushButton)
        self.grid.addWidget(self.bp, 0, 0, 1, 1)

        ## Plotting area.
        self.initPlotArea()
        self.grid.addWidget(self.glw, 1, 0)

        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

    def initPlotArea(self):
        """
        Initialize the plot area.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

        # Construct the graphic layout.
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.resize(600, 600)

        # Plot area for x-projection.
        self.px = self.glw.addPlot()
        self.px.setMaximumWidth(self._subplot_size)

        # Plot area for the image.
        p1 = self.glw.addPlot()
        self.iw = pg.ImageItem()
        p1.addItem(self.iw)

        # Contrast/color control
        hist = pg.HistogramLUTItem()
        hist.setImageItem(self.iw)
        hist.setMaximumWidth(self._subplot_size)
        self.glw.addItem(hist)
        self.glw.nextRow()

        # Plot area for histogram.
        self.ph = self.glw.addPlot()
        self.ph.setMaximumHeight(self._subplot_size)
        self.ph.setMaximumWidth(self._subplot_size)
        
        # Plot area for y-projection.
        self.py = self.glw.addPlot()
        self.py.setMaximumHeight(self._subplot_size)

        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

    @pyqtSlot()
    def pushButton(self):
        """
        Button function.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
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
        
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

    def updateImage(self):
        """
        Update the image and the other plots.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        try:
            if self.data is not None:
                if self._is_emulate:
                    self.data = np.random.normal(100, 10, (100, 100))
                self.iw.setImage(self.data)
                self.px.plot(self.data.mean(axis=1), np.arange(self.data.shape[0]), clear=True)
                self.py.plot(np.arange(self.data.shape[1]), self.data.mean(axis=0), clear=True)
                hist, xbins = np.histogram(self.data.flatten())
                dxbins = xbins[1] - xbins[0]
                self.ph.plot(xbins + dxbins/2.0, hist, clear=True,
                            stepMode=True, fillLevel=0,brush=(0,0,255,150))
        except Exception as ex:
            print(ex)
        
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

    def closeEvent(self, event):
        self.is_closed = True
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        if self._timer.isActive():
            print("Stop the active timer.")
            self._timer.stop()
        self.data = None
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")