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
import json
from PyQt4.QtCore import QThread, QMutex, QMutexLocker, pyqtSignal, QObject, pyqtSlot
from .ZeroMQ import ZeroMQListener

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
        self.stopWorking = False
        self.sleepInterval = 1

    @pyqtSlot()
    def process(self):
        """
        This function is to be connected with a pyqtSignal object on another thread.
        """
        # print(">> process():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        # self.stopWorking = False
        # while not self.stopWorking:
        st = time.time()
        try:
            with QMutexLocker(self.mutex):
                self._process()
        except Exception as ex:
            print(ex)
                # self.stopWorking = True
        self.do_something.emit(self.data)
        elapsed = time.time() - st
        print("Elapsed time of process:{0:.4f} sec.".format(elapsed))
        # if elapsed < self.sleepInterval:
        #     time.sleep(self.sleepInterval - elapsed)
        self.finished.emit()

    @pyqtSlot(object)
    def process2(self, obj):
        """
        This function stops the thread calling this object.
        """
        print(">> process():", os.getpid(), QThread.currentThread(), QThread.currentThreadId())
        self.stopWorking = False
        while not self.stopWorking:
            try:
                with QMutexLocker(self.mutex):
                    self._process()
            except Exception as ex:
                print(ex)
                self.stopWorking = True
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
    def __init__(self, name = "", parent = None):
        super().__init__(name=name, parent=parent)

    def _process(self):
        self.data = np.random.uniform(0.0, 10., (1000, 2000))
        # self.stopWorking = True

class GetDataWorker2(Worker):
    def __init__(self, name = "", parent = None):
        super().__init__(name=name, parent=parent)

    def _process(self):
        try:
            run_number = np.random.randint(0, 2000)
            tag_start = np.random.randint(0, 1000000)
            tag_end = tag_start + np.random.randint(0, 100)
            nbr_of_sig = int((tag_end - tag_start + 1)/3)
            nbr_of_bg = (tag_end - tag_start + 1) - nbr_of_sig
            bg = np.random.uniform(0.0, 10., (1000, 2000))
            sig = np.random.uniform(0.0, 10., (1000, 2000))
            self.data = dict(tag_start=tag_start, tag_end=tag_end, run_number=run_number,
                         nbr_of_sig=nbr_of_sig, nbr_of_bg=nbr_of_bg, bg=bg, sig=sig)
        except Exception as e:
            print(e)
            self.data = None

class GetDataWorker3(Worker):
    def __init__(self, name = "", parent = None, fpath_port_config = None):
        if fpath_port_config is None:
            raise ValueError("fpath_port_config should be given.")
        super().__init__(name=name, parent=parent)
        with open(fpath_port_config, 'r') as ff:
            config = json.load(ff)
        self.types = [key for key in config["port"].keys()]
        self.ports = config["port"]
        self.listeners = dict()
        self.interval = config["interval"]
        for _type in self.types:
            self.listeners[_type] = ZeroMQListener(self.ports[_type])

    def _process(self):
        try:
            print("process()")
            for listener in self.listeners.values():
                listener.Shot()
            run_number = np.random.randint(0, 2000)
            tag_start = np.random.randint(0, 1000000)
            tag_end = tag_start + np.random.randint(0, 100)
            nbr_of_sig = int((tag_end - tag_start + 1)/3)
            nbr_of_bg = (tag_end - tag_start + 1) - nbr_of_sig
            self.data = dict(tag_start=tag_start, tag_end=tag_end, run_number=run_number,
                         nbr_of_sig=nbr_of_sig, nbr_of_bg=nbr_of_bg)
            for listener in self.listeners.values():
                self.data[listener.name.decode()] = listener.data
        except Exception as e:
            print(e)
            self.data = None

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
