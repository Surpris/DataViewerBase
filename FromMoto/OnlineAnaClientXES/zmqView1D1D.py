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
    sigGetData = QtCore.pyqtSignal(int)

    def __init__(self, port, subFilter = ""):
        #
        QtCore.QObject.__init__(self)
        # Socket to talk to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.port = port
        #print ("Collecting updates from zmq server")
        self.socket.connect("tcp://xu-bl3-anapc02:{}".format(self.port))
        #self.socket.connect("tcp://localhost:5555")
        self.socket.setsockopt(zmq.SUBSCRIBE, subFilter.encode())
        self.running = True

    def Close(self):
        self.socket.close()

    def Loop(self):
        while self.running:
            self.data, self.name = RecvArray(self.socket)
            self.sigGetData.emit(self.port)

class MainWindow(QtGui.QWidget):
    """Main window"""
    def __init__(self, port1, port2, name, parent=None,):
        QtGui.QWidget.__init__(self, parent)
        self.resize(800, 600)
        self.setWindowTitle("GraphName:{0} Port:{1}and{2}".format(name, port1, port2))
        ## port
        self.port1 = port1
        self.port2 = port2
        ## Create some widgets to be placed inside
        self.runCheck = QtGui.QCheckBox('Running')
        # Plot objects
        pg.setConfigOptions(antialias=False)
        pg.setConfigOption('background', (255, 255, 255))
        self.plt = pg.PlotWidget()
        self.plt.showGrid(x=True, y=True)

        ## Create a grid layout to manage the widgets size and position
        layout = QtGui.QGridLayout()
        self.setLayout(layout)

        ## Add widgets to the layout in their proper positions
        layout.addWidget(self.runCheck, 0, 0)
        layout.addWidget(self.plt, 1, 0)

        ## zmq worker
        self.thread1 = QtCore.QThread()
        self.thread2 = QtCore.QThread()
        self.zeromqListener1 = ZeroMQListener(port1, name)
        self.zeromqListener2 = ZeroMQListener(port2, name)
        self.zeromqListener1.moveToThread(self.thread1)
        self.zeromqListener2.moveToThread(self.thread2)

        self.thread1.started.connect(self.zeromqListener1.Loop)
        self.thread2.started.connect(self.zeromqListener2.Loop)
        self.zeromqListener1.sigGetData.connect(self.UpdatePlot)
        self.zeromqListener2.sigGetData.connect(self.UpdatePlot)

        QtCore.QTimer.singleShot(0, self.thread1.start)
        QtCore.QTimer.singleShot(0, self.thread2.start)

    @QtCore.pyqtSlot(int)
    def UpdatePlot(self, port):
        if self.runCheck.isChecked():
            self.plt.plot(self.zeromqListener1.data, pen='r', clear=True)
            self.plt.plot(self.zeromqListener2.data, pen='b')
            
    def closeEvent(self, event):
        self.zeromqListener1.running = False
        self.zeromqListener2.running = False
        #self.zeromqListener.Close()
        self.thread1.terminate()
        self.thread2.terminate()
        self.thread1.wait(1000)
        self.thread2.wait(100)
        
##### main #####
def main(arg):
    app = QtGui.QApplication(sys.argv)
    app.setStyle('cleanlooks')
    mainWin = MainWindow(arg.port1, arg.port2, arg.name)
    mainWin.show()
    ## Start the Qt event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Online Analysis XES")
    parser.add_argument('-port1', action='store', dest='port1', type=int, required=True)
    parser.add_argument('-port2', action='store', dest='port2', type=int, required=True)
    parser.add_argument('-name', action='store', dest='name', type=str, required=True)
    argmnt = parser.parse_args()
    main(argmnt)