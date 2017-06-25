# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 00:42:08 2017

@author: Surpris
"""

import sys
import inspect
import os
import json
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
        self.resize(800, 800)
        grid = QGridLayout(self)
        grid.setSpacing(10)

        ## Some buttons.
        button_test = QPushButton()
        button_test.setText("Test")
        QObject.connect(button_test, SIGNAL("clicked()"), self.pushButton)
        grid.addWidget(button_test, 0, 0, 1, 1)
        
        ## Construct the graphic layout.
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.resize(800, 800)

        # Plot area for the image.
        p1 = self.glw.addPlot()
        self.iw = pg.ImageItem()
        p1.addItem(self.iw)

        # Plot area for x-projection.
        self.px = self.glw.addPlot()
        self.px.setMaximumWidth(250)

        self.glw.nextRow()

        # Plot area for y-projection.
        self.py = self.glw.addPlot()
        self.py.setMaximumHeight(250)

        # Plot area for histogram.
        self.ph = self.glw.addPlot()
        self.ph.setMaximumHeight(250)
        self.ph.setMaximumWidth(250)

        grid.addWidget(self.glw, 1, 0)
        
        self.data = None
    
    def show(self):
        self.exec_()
    
    def pushButton(self):
        self.updateImage()

    def updateImage(self):
        data = np.random.randint(0, 100, (100, 100))
        self.iw.setImage(data)
        self.px.plot(data.sum(axis=1), clear=True)
        self.py.plot(data.sum(axis=0), clear=True)
        hist, xbins = np.histogram(data.flatten())
        dxbins = xbins[1] - xbins[0]
        self.ph.plot(xbins[:-1] + dxbins/2.0, hist, clear=True)