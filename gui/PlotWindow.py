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
from PyQt4.QtCore import QObject, SIGNAL
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
pg.setConfigOptions(imageAxisOrder='row-major')

class PlotWindow(QDialog):
    """
    Class for some plots.
    """
    def __init__(self, parent=None):
        """
        Initialization.
        """
        super().__init__(parent)
        print("Initialize this plot window...")
        self.initInnerParameters()
        self.initGui()
    
    def show(self):
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        self.exec_()
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

    def initInnerParameters(self):
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        self._is_plot_started = False
        self.data = None
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
    
    def initGui(self):
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        self.resize(800, 800)
        self.grid = QGridLayout(self)
        self.grid.setSpacing(10)

        ## Some buttons.
        self.bp = QPushButton()
        self.bp.setText("Start plotting")
        QObject.connect(self.bp, SIGNAL("clicked()"), self.pushButton)
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
        self.glw.resize(800, 800)

        # Plot area for x-projection.
        self.px = self.glw.addPlot()
        self.px.setMaximumWidth(250)

        # Plot area for the image.
        p1 = self.glw.addPlot()
        self.iw = pg.ImageItem()
        p1.addItem(self.iw)

        # Contrast/color control
        hist = pg.HistogramLUTItem()
        hist.setImageItem(self.iw)
        hist.setMaximumWidth(100)
        self.glw.addItem(hist)
        self.glw.nextRow()

        # Plot area for histogram.
        self.ph = self.glw.addPlot()
        self.ph.setMaximumHeight(250)
        self.ph.setMaximumWidth(250)
        
        # Plot area for y-projection.
        self.py = self.glw.addPlot()
        self.py.setMaximumHeight(250)

        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")

    def pushButton(self):
        """
        Button function.
        """
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        try:
            if not self._is_plot_started:
                
                self.timer = QtCore.QTimer()
                self.timer.setInterval(1000)
                self.timer.timeout.connect(self.updateImage)
                self.timer.start()
                self._is_plot_started = True
                self.bp.setText("Stop plotting")
            else:
                self.timer.stop()
                self._is_plot_started = False
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
            data = np.random.normal(100, 10, (100, 100))
            self.iw.setImage(data)
            self.px.plot(data.mean(axis=1), np.arange(data.shape[0]), clear=True)
            self.py.plot(np.arange(data.shape[1]), data.mean(axis=0), clear=True)
            hist, xbins = np.histogram(data.flatten())
            dxbins = xbins[1] - xbins[0]
            self.ph.plot(xbins + dxbins/2.0, hist, clear=True,
                         stepMode=True, fillLevel=0,brush=(0,0,255,150))
        except Exception as ex:
            print(ex)
        
        print("<<" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")