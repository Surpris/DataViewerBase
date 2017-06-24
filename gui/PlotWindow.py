# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 00:42:08 2017

@author: Surpris
"""

from PyQt4.QtGui import QMainWindow, QGridLayout, QMenu, QDialog, QPushButton, QMessageBox, QWidget
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg

class PlotWindow():
    def __init__(self, parent=None):
        self.w = QDialog(parent)
        
    def show(self):
        self.w.exec_()