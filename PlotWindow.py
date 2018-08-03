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
import importlib
spam_spec = importlib.util.find_spec("PyQt4")
found = spam_spec is not None
if found is True:
    from PyQt4.QtGui import QGridLayout, QDialog, QPushButton, QLabel, QGroupBox, QCheckBox, QHBoxLayout
    from PyQt4.QtGui import QWidget
    from PyQt4.QtCore import pyqtSlot, Qt
else:
    spam_spec = importlib.util.find_spec("PyQt5")
    found = spam_spec is not None
    if found is True:
        from PyQt5.QtWidgets import QGridLayout, QDialog, QPushButton, QLabel, QGroupBox, QCheckBox, QHBoxLayout
        from PyQt5.QtWidgets import QWidget
        from PyQt5.QtCore import pyqtSlot, Qt
    else:
        raise ModuleNotFoundError("No module named either 'PyQt4' or 'PyQt5'")
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
pg.setConfigOptions(imageAxisOrder='row-major')

# from .core.deorator import footprint

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

    
    def initInnerParameters(self):
        """
        Initialize the inner parameters.
        """
        self.is_closed = False
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.updateImage)
        self._is_emulate = True
        self.data = None
        self._init_window_width = 600 # [pixel]
        self._init_window_height = 600 # [pixel]
        self._subplot_size = 100 # [pixel]
        self._font_size_groupbox_title = 11 # [pixel]
        self._update_interval = 1000
        self._plot_count = 0
    
    
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
        grid.addWidget(widget_coor_value, 1, 0)
        grid.addWidget(self.glw, 2, 0)

    
    def initPlotArea(self):
        """
        Initialize the plot area.
        """
        # Construct the graphic layout.
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.resize(self._init_window_width, self._init_window_height)

        # Plot area for x-projection.
        self._is_px = self.kwargs.get("px", True)
        if self._is_px:
            self.px = self.glw.addPlot()
            self.px.setMaximumWidth(self._subplot_size)

        # Plot area for the image.
        self.iw_tickBottom = {0:-50, 50:0, 100:50}
        self.iw_axBottom = pg.AxisItem(orientation="bottom")
        self.iw_axBottom.setTicks([self.iw_tickBottom.items()])
        self.iw_axBottom.setLabel("Value1")

        self.iw_tickLeft = {0:0, 50:50, 100:100}
        self.iw_axLeft = pg.AxisItem(orientation="left")
        self.iw_axLeft.setTicks([self.iw_tickLeft.items()])
        self.iw_axLeft.setLabel("Value2")
        self.p1 = self.glw.addPlot(
            axisItems={"bottom":self.iw_axBottom, "left":self.iw_axLeft}
        )
        self.p1.setAspectLocked(True)
        self.iw = pg.ImageItem()
        self.p1.addItem(self.iw)

        def mouseMoved(pos):
            try:
                coor = self.iw.mapFromScene(pos)
                x, y = int(coor.x()), int(coor.y())
                if self.iw.image is not None:
                    img = self.iw.image
                    if 0 <= x <= img.shape[1] and 0 <= y <= img.shape[0]:
                        self.label_coor_value.setText("({0}, {1}, {2:.2e})".format(x, y, img[y, x]))
            except Exception as ex:
                print(ex)
        
        self.iw.scene().sigMouseMoved.connect(mouseMoved)

        # Contrast/color control
        self.hist = pg.HistogramLUTItem()
        self.hist.setImageItem(self.iw)
        self.hist.setMaximumWidth(self._subplot_size*1.5)
        self.glw.addItem(self.hist)

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


    
    @pyqtSlot()
    def pushButton(self):
        """
        Button function.
        """
        try:
            if not self._timer.isActive():
                self._timer.setInterval(self._update_interval)
                self._timer.start()
                self.bp.setText("Stop plotting")
            else:
                self._timer.stop()
                self._plot_count = 0
                self.bp.setText("Start plotting")
        except Exception as ex:
            print(ex)

    # 
    @pyqtSlot()
    def updateImage(self):
        """
        Update the image and the other plots.
        """
        try:
            if self._is_emulate:
                self.data = np.random.normal(100, 10, (100, 100))
            if self.data is not None:
                self.iw_tickLeft = {
                    0:self._plot_count*100, 
                    50:self._plot_count*100+50, 
                    100:self._plot_count*100+100
                }
                self.iw_axLeft.setTicks([self.iw_tickLeft.items()])
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
        self._plot_count += 1

    
    def closeEvent(self, event):
        self.is_closed = True
        if self._timer.isActive():
            print("Stop the active timer.")
            self._timer.stop()
        self.data = None

def main():
    app = QtGui.QApplication([])
    mw = PlotWindow()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    main()