# -*- coding: utf-8 -*-

from gui import DataViewerBase
from pyqtgraph.Qt import QtGui

def main(filepath):
    app = QtGui.QApplication([])
    mw = DataViewerBase(filepath)
    mw.show()
    app.exec_()

if __name__ == "__main__":
    filepath = "./config_getdata.json"
    main(filepath)