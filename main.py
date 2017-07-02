# -*- coding: utf-8 -*-

from gui import DataViewerBase
from pyqtgraph.Qt import QtGui

def main():
    app = QtGui.QApplication([])
    mw = DataViewerBase()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    main()