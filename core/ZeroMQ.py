# -*- coding: utf-8 -*-

"""
Created on Thu Jul 14 15:53 2017

@original author: Koji Motomura (SACLA staff)
@author: Surpris
"""

from PyQt4 import QtCore
import numpy as np
import zmq
import sys, signal
import time
import argparse

class ZMQPublisher(object):
    """
    Publisher class using ZeroMQ.
    """
    def __init__(self, port):
        """
        Initialization of this class.
        """
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://*:{}".format(port))

    def SendArray(self, A, name="", flags=0, copy=True, track=False):
        """
        send a numpy array with metadata
        """
        md = dict(dtype = str(A.dtype), shape = A.shape,)
        self.socket.send(name.encode(), flags|zmq.SNDMORE)
        self.socket.send_json(md, flags|zmq.SNDMORE)
        self.socket.send(A, flags, copy=copy, track=track)

class ZeroMQListener(QtCore.QObject):
    """
    ZMQ listener.
    """
    # SIGNAL recieved data
    sigGetData = QtCore.pyqtSignal(bytes)

    def __init__(self, port, subFilter = ""):
        #
        QtCore.QObject.__init__(self)

        # Socket to talk to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)

        print ("Collecting updates from zmq server")
        # self.socket.connect("tcp://xu-bl3-anapc02:{}".format(port))
        self.socket.connect("tcp://localhost:{}".format(port))
 
        self.socket.setsockopt(zmq.SUBSCRIBE, subFilter.encode())
        self.running = True

    def Close(self):
        self.socket.close()

    def Loop(self):
        while self.running:
            self.data, self.name = RecvArray(self.socket)
            self.sigGetData.emit(self.name)
    
    @QtCore.pyqtSlot()
    def Shot(self):
        try:
            self.data, self.name = RecvArray(self.socket)
            # self.sigGetData.emit(self.name)
        except Exception as ex:
            print(ex)
            self.sigGetData.emit(self.name)

def RecvArray(socket, flags=0, copy=True, track=False):
    """
    Receive a numpy array.
    """
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    success = False
    if poller.poll(1000): # 10s timeout in milliseconds
        name = socket.recv()
        md = socket.recv_json(flags=flags)
        msg = socket.recv(flags=flags, copy=copy, track=track)
        success = True
    else:
        print("Timeout processing auth request")
    if success:
        buf = memoryview(msg)
        A = np.frombuffer(buf, dtype=md['dtype'])
        return A.reshape(md['shape']), name
    else:
        A = np.zeros((2, 2), dtype=int)
        name = b""
        return A, name

def main(arg):
    """main process"""
    port = 3333
    if arg.type.lower() in ["pub", "publisher"]:
        publisher = ZMQPublisher(port)
        count = 0
        A = np.array([[0, 1], [2, 3]])
        while True:
            try:
                buff = A + count
                publisher.SendArray(buff, str(count))
                print(count, ":", buff.flatten())
                count += 1
                time.sleep(arg.interval)
            except KeyboardInterrupt as ex:
                print("Keyboard interruption.")
                break
    elif arg.type.lower() in ["lis", "listener"]:
        listener = ZeroMQListener(port)
        while True:
            try:
                listener.Shot()
                print(listener.name.decode(), ",", listener.data.flatten())
            except Exception as ex:
                print(ex)
            time.sleep(arg.interval)
    else:
        raise ValueError

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test of publisher and listener using ZeroMQ")
    parser.add_argument('-type', action='store', dest='type', type=str, required=True)
    parser.add_argument('-interval', action='store', dest='interval', type=int, required=True)
    argmnt = parser.parse_args()
    main(argmnt)