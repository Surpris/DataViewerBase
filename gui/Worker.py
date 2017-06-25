# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 18:29:00 2017

@author: Surpris
"""

import sys
from PyQt4.QtCore import QThread, QMutex, QMutexLocker, pyqtSignal

class Worker(QThread):
    do_something = pyqtSignal()

    def __init__(self, name = "", parent = None):
        super().__init__(parent)
        self.mutex = QMutex()
        self.name = name
        self.isStopped = False
        
    def run(self):
        while not self.isStopped:
            self.mutex.lock()
            self.msleep(1000)
            self.mutex.unlock()
            self.do_something.emit()
        self.finished.emit()

    def stop(self):
        with QMutexLocker(self.mutex):
            self.isStopped = True