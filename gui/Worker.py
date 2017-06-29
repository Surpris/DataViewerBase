# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 18:29:00 2017

@author: Surpris
"""

import sys
import datetime
from PyQt4.QtCore import QThread, QMutex, QMutexLocker, pyqtSignal, QObject

class Worker(QThread):
    do_something = pyqtSignal()

    def __init__(self, name = "", parent = None):
        super().__init__(parent)
        self.sleep_interval = 900
        self.mutex = QMutex()
        self.name = name
        self.isStopped = False
        
    def run(self):
        while not self.isStopped:
        # while True:
            self.mutex.lock()
            self.do_something.emit()
            self.mutex.unlock()
            self.msleep(self.sleep_interval)
        self.finished.emit()
        print(self.name + " finished.")

    def stop(self):
        with QMutexLocker(self.mutex):
            self.isStopped = True

class Worker2(QObject):
    do_something = pyqtSignal()

    def __init__(self, name = "", parent = None):
        super().__init__(parent)
        self.sleep_interval = 900
        self.mutex = QMutex()
        self.name = name
        self.isStopped = False