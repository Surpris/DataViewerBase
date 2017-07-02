# -*- coding: utf-8 -*
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import time
import inspect
import os
import numpy as np
sys.path.append("../")
from gui.Worker import GetDataWorker, Worker, Worker_Sample

class MyForm(QMainWindow):
    quit_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mutex = QMutex()
        self.timer1 = QTimer()
        self.timer1.setInterval(1000)
        self.stopTimer = False
        self.data = np.array([1, 2, 3])
        self.button = QPushButton('Start thread')
        self.button.clicked.connect(self.on_click)

        self.button2 = QPushButton('Click2')
        self.button2.clicked.connect(self.on_click2)

        self.label1 = QLabel(self)
        self.label1.setText("")

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.button2)
        layout.addWidget(self.label1)

        main_frame = QWidget()
        main_frame.setLayout(layout)
        self.resize(400, 200)

        self.setCentralWidget(main_frame)
        self.thread1 = QThread()
        self.isThread1Finished = False
        self.timer1.timeout.connect(self.startThread)
        # self.worker1 = Worker()
        self.worker1 = GetDataWorker()
        # self.worker1 = Worker_Sample()
        self.thread1.started.connect(self.worker1.process)
        # self.thread1.started.connect(lambda: self.worker1.process())
        self.worker1.finished.connect(self.thread1.quit)
        self.thread1.finished.connect(self.stopTimer1)
        self.worker1.do_something.connect(self.test)
        self.worker1.sendData.connect(self.test2)
        
        # self.quit_signal.connect(self.worker1.stop)
        self.worker1.moveToThread(self.thread1)
        print("__init__:",os.getpid(), QThread.currentThread(), QThread.currentThreadId())
    
    @pyqtSlot()
    def startThread(self):
        if not self.thread1.isRunning():
            print("start thread by timer.")
            self.thread1.start()
    
    @pyqtSlot()
    def stopTimer1(self):
        if self.stopTimer:
            self.timer1.stop()
            print("timer stopped.")
            self.stopTimer = False
            self.button.setEnabled(True)
            self.button.setText("Start thread")

    @pyqtSlot(object)
    def test(self, obj):
        print(">> test():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        print("ttest: wait for thread's finished.")
        self.label1.setText("")
        print("Received object:", obj)
        print("<< test():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
    
    @pyqtSlot(object)
    def test2(self, obj):
        print(">> test2():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        print("Object received during worker processing:", obj)
        if isinstance(obj, str):
            self.label1.setText(self.label1.text() + obj)
        print("<< test2():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())

    @pyqtSlot()
    def on_click(self):
        print(">> onclick():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        if not self.timer1.isActive():
            self.timer1.start()
            self.button.setText("Stop")
            print("thread starts.")
        else:
            print("onclick: wait for thread's finishing")
            self.button.setEnabled(False)
            self.stopTimer = True
        print("<< onclick():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
    
    @pyqtSlot()
    def on_click2(self):
        print(">> onclick2():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        print("G")
        print("<< onclick2():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
    
    def closeEvent(self, event):
        print(">>" + self.__class__.__name__ + "." + inspect.currentframe().f_code.co_name + "()")
        if self.thread1.isRunning():
            string = "Some threads are still running.\n"
            string += "Please wait for their finishing."
            confirmObject = QMessageBox.warning(self, "Closing is ignored.",
                string, QMessageBox.Ok)
            event.ignore()
            return
        else:
            confirmObject = QMessageBox.question(self, "Closing...",
                "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No)
            if confirmObject == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
                return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyForm()
    main_window.show()
    app.exec_()