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

        ### Some buttons.
        button_test = QPushButton()
        button_test.setText("Test")
        QObject.connect(button_test, SIGNAL("clicked()"), self.pushButton)
        grid.addWidget(button_test, 0, 0, 1, 1)
        
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.resize(800, 800)
        
        # self.grid = QGridLayout(self.w)
        # self.grid.setSpacing(10)

        self.pw2 = pg.PlotItem()
        self.iw = pg.ImageItem()

        self.p1 = self.glw.addPlot()
        self.p1.setMaximumWidth(200)
        p1 = self.glw.addPlot()
        p1.addItem(self.iw)
        self.glw.nextRow()
        self.p2 = self.glw.addPlot(col=1)
        self.p2.setMaximumHeight(200)
        try:
            _x = np.arange(0, 100) * 0.1*np.pi
            self.p2.plot(_x, np.sin(_x))
        except Exception as ex:
            print(ex)
        self.iw.setImage(np.random.randint(0, 100, (100, 100)))
        grid.addWidget(self.glw, 1, 0)
        
        self.data = None
    
    def show(self):
        self.exec_()
    
    def pushButton(self):
        pass