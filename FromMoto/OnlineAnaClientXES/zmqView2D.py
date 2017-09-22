#encoding: UTF-8
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import zmq
import sys
import argparse

def RecvArray(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""
    name = socket.recv()
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buf = memoryview(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape']), name

class ZeroMQListener(QtCore.QObject):
    """ZMQ listener"""
    # SIGNAL recieved data
    sigGetData = QtCore.pyqtSignal(bytes)

    def __init__(self, port, subFilter = ""):
        #
        QtCore.QObject.__init__(self)

        # Socket to talk to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)

        print ("Collecting updates from zmq server")
        self.socket.connect("tcp://xu-bl3-anapc02:{}".format(port))
        #self.socket.connect("tcp://localhost:5555")
 
        self.socket.setsockopt(zmq.SUBSCRIBE, subFilter.encode())
        self.running = True

    def Close(self):
        self.socket.close()

    def Loop(self):
        while self.running:
            self.data, self.name = RecvArray(self.socket)
            self.sigGetData.emit(self.name)

class MainWindow(QtGui.QWidget):
    """Main window"""
    def __init__(self, port, name, parent=None,):
        QtGui.QWidget.__init__(self, parent)
        self.resize(400, 600)
        self.setWindowTitle("GraphName:{0} Port:{1}".format(name, port))

        ## Create some widgets to be placed inside
        self.runCheck = QtGui.QCheckBox('Running')
        # Image view objects
        self.imv = pg.ImageView(view=pg.PlotItem())

        ## Create a grid layout to manage the widgets size and position
        layout = QtGui.QGridLayout()
        self.setLayout(layout)

        ## Add widgets to the layout in their proper positions
        layout.addWidget(self.runCheck, 0, 0)
        layout.addWidget(self.imv, 1, 0)

        ## zmq worker
        self.thread = QtCore.QThread()
        self.zeromqListener = ZeroMQListener(port, name)
        self.zeromqListener.moveToThread(self.thread)

        self.thread.started.connect(self.zeromqListener.Loop)
        self.zeromqListener.sigGetData.connect(self.SignalReceived)

        QtCore.QTimer.singleShot(0, self.thread.start)

    @QtCore.pyqtSlot(bytes)
    def SignalReceived(self, name):
        self.UpdatePlot(self.zeromqListener.data, name)

    def closeEvent(self, event):
        self.zeromqListener.running = False
        #self.zeromqListener.Close()
        self.thread.terminate()
        self.thread.wait(1000)

    def UpdatePlot(self, data, name):
        if self.runCheck.isChecked():
            self.imv.setImage(data)

def main(arg):
    ## Always start by initializing Qt (only once per application)
    app = QtGui.QApplication(sys.argv)
    app.setStyle('cleanlooks')
    mainWin = MainWindow(arg.port, arg.name)
    mainWin.show()
    ## Start the Qt event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Online Analysis XES")
    parser.add_argument('-port', action='store', dest='port', type=int, required=True)
    parser.add_argument('-name', action='store', dest='name', type=str, required=True)
    argmnt = parser.parse_args()
    main(argmnt)