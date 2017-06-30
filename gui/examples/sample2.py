# -*- coding: utf-8 -*
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import time
import os

class Worker2(QObject):
    do_something = pyqtSignal()

    def __init__(self, name = "", parent = None):
        super().__init__(parent)
        self.mutex = QMutex()
        self.name = name
        self._timer = QTimer()
        self.string = "A"
    
    @pyqtSlot()
    def doWork(self):
        if not self._timer.isActive():
            self._timer.setInterval(1000)
            self._timer.timeout.connect(self.addA)
            print("timer")
            self._timer.start()
            print(">> doWork():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        else:
            self._timer.stop()
            print("<< doWork():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
            self.do_something.emit()
    
    def addA(self):
        print("addA():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        print(self.string)
        self.string += "A"

class MyForm(QMainWindow):
    def __init__(self, parent=None):
        super(MyForm, self).__init__(parent)
        self.button = QPushButton('Click')
        # エラーが発生する
        # button.clicked.connect(self.on_click("Hello world"))
        # lambdaを使う
        self.string = "A"
        self.button.clicked.connect(self.on_click)

        layout = QHBoxLayout()
        layout.addWidget(self.button)

        main_frame = QWidget()
        main_frame.setLayout(layout)

        self.setCentralWidget(main_frame)

        self.thread1 = QThread()
        self.worker1 = Worker2()
        self.thread1.started.connect(self.worker1.doWork)
        self.worker1.do_something.connect(self.test)
        self.worker1.moveToThread(self.thread1)
        self.mutex = QMutex()
        print("__init__:",os.getpid(), QThread.currentThread(), QThread.currentThreadId())

    @pyqtSlot()
    def test(self):
        print("test:", os.getpid(), QThread.currentThread(), QThread.currentThreadId())

    @pyqtSlot()
    def on_click(self):
        print("onclick:", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        if not self.thread1.isRunning():
            print("start.")
            self.thread1.start()
        else:
            print("quit.")
            self.thread1.quit()
            print("wait.")
            self.thread1.wait(10)
            print("finished.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyForm()
    main_window.show()
    app.exec_()