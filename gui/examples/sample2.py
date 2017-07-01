# -*- coding: utf-8 -*
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import time
import os
import numpy as np

class Worker2(QObject):
    do_something = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, name = "", parent = None):
        super().__init__(parent)
        self.mutex = QMutex()
        self.name = name
        self.data = np.array([1,2,3])
        self.string = ""
        self.isInterrupted = False
    
    @pyqtSlot()
    def doWork(self):
        print(">> doWork():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        self.isInterrupted = False
        count = 0
        while not self.isInterrupted:
            if count == 100:
                self.isInterrupted = True
                continue
            try:
                with QMutexLocker(self.mutex):
                    self.addA()
                    self.addOne()
                time.sleep(1)
                count += 1
            except Exception as ex:
                print(ex)
                self.isInterrupted = True
        print("<< doWork():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        self.do_something.emit(self.data)
        self.finished.emit()
    
    @pyqtSlot(str)
    def doWork2(self, string):
        self.string = string
        print(">> doWork():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        self.isInterrupted = False
        count = 0
        while not self.isInterrupted:
            if count == 5:
                self.isInterrupted = True
                continue
            try:
                with QMutexLocker(self.mutex):
                    self.addA()
                time.sleep(1)
                count += 1
            except Exception as ex:
                print(ex)
                self.isInterrupted = True
        print("<< doWork():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        self.do_something.emit()
        self.finished.emit()

    def addA(self):
        self.string += "A"
        print(self.string)

    def addOne(self):
        if isinstance(self.data, np.ndarray):
            self.data[0] += 1
            print(self.data)
    
    @pyqtSlot()
    def stop(self):
        with QMutexLocker(self.mutex):
            self.isInterrupted = True
        print(self.isInterrupted)

class MyForm(QMainWindow):
    quit_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mutex = QMutex()
        self.string = ""
        self.data = np.array([1, 2, 3])
        self.button = QPushButton('Click')
        self.button.clicked.connect(self.on_click)

        layout = QHBoxLayout()
        layout.addWidget(self.button)

        main_frame = QWidget()
        main_frame.setLayout(layout)

        self.setCentralWidget(main_frame)
        self.thread1 = QThread()
        self.worker1 = Worker2()
        self.thread1.started.connect(self.worker1.doWork)
        # self.thread1.started.connect(lambda: self.worker1.doWork())
        self.worker1.finished.connect(self.thread1.quit)
        self.worker1.do_something.connect(self.test)
        
        self.quit_signal.connect(self.worker1.stop)
        self.worker1.moveToThread(self.thread1)
        print("__init__:",os.getpid(), QThread.currentThread(), QThread.currentThreadId())

    @pyqtSlot(object)
    def test(self, obj):
        print(">> test():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        print("wait for thread's finished.")
        try:
            self.thread1.wait(10)
            print("thread finished.")
        except Exception as ex:
            print(ex)
        self.button.setEnabled(True)
        print("Received object:", obj)
        # with QMutexLocker(self.mutex):
        #     self.string = ""
        print("<< test():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())

    @pyqtSlot()
    def on_click(self):
        print(">> onclick():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        print(self.data)
        print("thread starts.")
        self.thread1.start()
        self.button.setEnabled(False)
        print("<< onclick():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyForm()
    main_window.show()
    app.exec_()