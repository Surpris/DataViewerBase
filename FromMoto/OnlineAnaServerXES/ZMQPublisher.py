from PyQt4 import Qt, QtCore
import numpy as np
import zmq
import sys, signal

class ZMQPublisher(object):
    def __init__(self, port):
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://*:{}".format(port))

    def SendArray(self, A, name="", flags=0, copy=True, track=False):
        """send a numpy array with metadata"""
        md = dict(dtype = str(A.dtype), shape = A.shape,)
        self.socket.send(name.encode(), flags|zmq.SNDMORE)
        self.socket.send_json(md, flags|zmq.SNDMORE)
        self.socket.send(A, flags, copy=copy, track=track)
        
### -----------Test------------###
class DataSender:
    def __init__(self):
        self.zpub = ZMQPublisher(5555)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.SendData)

    def Start(self):
        self.timer.start(1000)

    def SendData(self):
        data = np.random.normal(size=(10000,50)).sum(axis=1)
        data += 5 * np.sin(np.linspace(0, 10, data.shape[0]))
        print(".")
        self.zpub.SendArray(data, "Signal1")

        data = np.random.normal(size=(10000,50)).sum(axis=1)
        data += 5 * np.sin(np.linspace(0, 5, data.shape[0]))
        self.zpub.SendArray(data, "Signal2")

def SIGINTHandler(*args):
    """Handler for the SIGINT signal."""
    print("Quit publish.")
    Qt.QApplication.quit()

if __name__ == "__main__":
    # start application
    app = Qt.QCoreApplication([])
    ds = DataSender()
    ds.Start()
    print("Publishing....")
    signal.signal(signal.SIGINT, SIGINTHandler)
    sys.exit(app.exec_())
