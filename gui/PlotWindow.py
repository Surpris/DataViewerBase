# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 00:42:08 2017

@author: Surpris
"""

from PyQt4.QtGui import QMainWindow, QGridLayout, QDialog, QPushButton, QWidget
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
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.resize(800, 800)
        
        # self.grid = QGridLayout(self.w)
        # self.grid.setSpacing(10)

        self.pw1 = pg.PlotWidget()
        self.pw2 = pg.PlotWidget()
        self.iw = pg.ImageItem()

        self.p1 = self.glw.addPlot()
        self.p1.addItem(self.iw)
        grid.addWidget(self.glw, 0, 0)
        
        # self.grid.addWidget(self.pw1, 0, 0, 3, 1)
        # self.grid.addWidget(self.pw2, 3, 1, 1, 3)
        # self.grid.addWidget(self.iw , 0, 1, 3, 3)
        self.data = None
    
    def show(self):
        self.exec_()