# -*- coding: utf-8 -*
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys

class Worker2(QObject):
    do_something = pyqtSignal()

    def __init__(self, name = "", parent = None):
        super().__init__(parent)
        self.mutex = QMutex()
    
    @pyqtSlot()
    def doWork(self):
        self.do_something.emit()

class MyForm(QMainWindow):
    def __init__(self, parent=None):
        super(MyForm, self).__init__(parent)
        button = QPushButton('Click')
        # エラーが発生する
        # button.clicked.connect(self.on_click("Hello world"))
        # lambdaを使う
        self.string = "A"
        button.clicked.connect(lambda: self.on_click(self.string))

        layout = QHBoxLayout()
        layout.addWidget(button)

        main_frame = QWidget()
        main_frame.setLayout(layout)

        self.setCentralWidget(main_frame)

    def on_click(self, string):
        print(string)
        self.string += "A"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyForm()
    main_window.show()
    app.exec_()