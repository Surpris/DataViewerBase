# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 18:29:00 2017

@author: Surpris
"""

import sys
import os
import datetime
import numpy as np
import time
from PyQt4.QtCore import QThread, QMutex, QMutexLocker, pyqtSignal, QObject, pyqtSlot

class WorkerThread(QThread):
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

class Worker(QObject):
    do_something = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, name = "", parent = None):
        super().__init__(parent)
        self.mutex = QMutex()
        self.name = name
        self.data = None
        self.StopWorking = False
    
    @pyqtSlot()
    def process(self):
        """
        This function is to be connected with a pyqtSignal object on another thread.
        """
        print(">> process():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        self.StopWorking = False
        while not self.StopWorking:
            try:
                with QMutexLocker(self.mutex):
                    self._process()
            except Exception as ex:
                print(ex)
                self.StopWorking = True
        self.do_something.emit(self.data)
        self.finished.emit()
    
    @pyqtSlot(object)
    def process2(self, obj):
        """
        This function stops the thread calling this object.
        """
        print(">> process():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        self.StopWorking = False
        while not self.StopWorking:
            try:
                with QMutexLocker(self.mutex):
                    self._process()
            except Exception as ex:
                print(ex)
                self.StopWorking = True
        self.do_something.emit(self.data)
        self.finished.emit()
    
    def _process(self):
        """
        Something to do should descriibed in this function.
        """
        print("sleep")
        time.sleep(10)
        self.data = "Test"
        self.isStopped = True

class GetDataWorker(Worker):
    sendData = pyqtSignal(object)

    def __init__(self, name = "", parent = None):
        super().__init__(name=name, parent=parent)
        self.count = 0

    def _process(self):
        # print(">> _process():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        self.count += 1
        self.sendData.emit("B")
        print(self.count)
        time.sleep(1)
        if self.count == 10:
            self.StopWorking = True
            self.data = "FFF"
            self.count = 0

class Worker_Sample(QObject):
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
    def process(self):
        print(">> process():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        self.isInterrupted = False
        count = 0
        while not self.isInterrupted:
            if count == 10:
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
        print("<< process():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        self.do_something.emit(self.data)
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