# -*- coding: utf-8 -*
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import time
import os
import numpy as np
sys.path.append("../")
from gui.Worker import GetDataWorker, Worker, Worker_Sample

class MyForm(QMainWindow):
    quit_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mutex = QMutex()
        self.string = ""
        self.data = np.array([1, 2, 3])
        self.button = QPushButton('Click')
        self.button.clicked.connect(self.on_click)

        self.button2 = QPushButton('Click2')
        self.button2.clicked.connect(self.on_click2)

        layout = QHBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.button2)

        main_frame = QWidget()
        main_frame.setLayout(layout)
        self.resize(400, 200)

        self.setCentralWidget(main_frame)
        self.thread1 = QThread()
        # self.worker1 = Worker()
        self.worker1 = GetDataWorker()
        # self.worker1 = Worker_Sample()
        self.thread1.started.connect(self.worker1.process)
        # self.thread1.started.connect(lambda: self.worker1.process())
        self.worker1.finished.connect(self.thread1.quit)
        self.worker1.do_something.connect(self.test)
        
        # self.quit_signal.connect(self.worker1.stop)
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
    
    @pyqtSlot()
    def on_click2(self):
        print(">> onclick2():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        print("G")
        print("<< onclick2():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyForm()
    main_window.show()
    app.exec_()