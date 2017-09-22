# -*- coding: utf-8 -*-

from PyQt4 import Qt, QtCore, QtGui
import numpy as np
import sys, signal
import argparse

import ZMQPublisher
import OLSaclaDetector

class MainAnalysis(QtGui.QWidget):
    """ Main analysis class """
    def __init__(self, ccd, pub):
        QtGui.QWidget.__init__(self)
        self.setGeometry(10,10,40,300)
        button = QtGui.QPushButton('Clear',self)
        button.setGeometry(5,60,80,40)
        self.Label = QtGui.QLabel()
        self.Label.setGeometry(20,20,40,40)
        self.connect(button,QtCore.SIGNAL('clicked()'),self.Clear) 
            
        self.ccd = ccd
        self.pub = pub
        # define timers
        self.analysisTimer = QtCore.QTimer()
        self.analysisTimer.timeout.connect(self.Analyze)
        self.publishTimer = QtCore.QTimer()
        self.publishTimer.timeout.connect(self.Publish)
        # initialize valiables
        self.threshold = 50
        
        self.InitAnaVals()
        
    def LoadBackGround(self, fileName=None):
        if fileName is None:
            self.bg = np.zeros_like(self.ccd.images[0, :, :])
            return

        print("Loading background...", end="")
        originalBG = np.load(fileName)
        originalBG = np.flipud(np.rot90(originalBG))
        self.bg = originalBG[self.ccd.roiX[0]:self.ccd.roiX[1], self.ccd.roiY[0]:self.ccd.roiY[1]]
        print(self.ccd.roiX[0],self.ccd.roiX[1], self.ccd.roiY[0],self.ccd.roiY[1])

    def InitAnaVals(self):
        self.imageCounter = 0
        self.imageRaw = np.zeros_like(self.ccd.images[0, :, :])
        self.imageSum = np.zeros_like(self.ccd.images[0, :, :])
        self.imageAve = np.zeros_like(self.ccd.images[0, :, :])
        self.imageAveBGSub = np.zeros_like(self.ccd.images[0, :, :])
        self.imageSumTh = np.zeros_like(self.ccd.images[0, :, :])
        self.imageAveTh = np.zeros_like(self.ccd.images[0, :, :])
        self.spectrum = np.zeros_like(self.ccd.images[0, 0, :])
        self.previousTag = self.ccd.GetCurrentTag() - 2
    
    def Start(self, anaInterval=500, pubInterval=2000):
        self.analysisTimer.start(anaInterval)
        self.publishTimer.start(pubInterval)

    def Analyze(self):
        self.tags, self.images = self.ccd.GetImeges()
        numberOfFrames = len(self.tags)
        if numberOfFrames == 0:
            return
        self.imageCounter += numberOfFrames
        #print(self.images.shape)
        # 2D stuff
        self.images -= self.bg
        self.imageRaw = self.images[0, :, :]
        self.imageSum += self.images.sum(axis=0)      
        self.imageAve = self.imageSum / self.imageCounter     
        # apply threshold
        #self.images -= self.bg
        self.images[self.images < self.threshold] = 0
        self.imageSumTh += self.images.sum(axis=0)      
        self.imageAveTh = self.imageSumTh / self.imageCounter    
        # 1D stuff
        
        self.spectrum = self.imageAveTh.mean(axis=0)
        
        # Check tag
#        if self.tags[0] - self.previousTag != 2: # or 4
#            print("Data is missed {0}:{1}:{2}".format(self.tags[0] - self.previousTag, self.tags[0], self.previousTag))
        
        self.previousTag = self.tags[-1]
        #print(".", end="")
        #sys.stdout.flush()
        
    def Publish(self):
        self.pub.SendArray(self.imageRaw, "ImageRaw")
        #self.pub.SendArray(self.imageAve, "ImageAve")
        self.pub.SendArray(self.imageAveTh, "ImageAveTh")
        self.pub.SendArray(self.spectrum, "Spectrum")
        #print(self.spectrum.sum(), end="")
        print(".", end="")
        sys.stdout.flush()
        
    def Clear(self):
        print("Reset analysis.")
        self.InitAnaVals()
        
    
#        if key == QtCore.Qt.Key_Q:
#            print("Quit application.")
#            Qt.QCoreApplication.quit()
        
def SIGINTHandler(*args):
    """Handler for the SIGINT signal."""
    print("Quit application.")
    Qt.QApplication.quit()

def main(arg):
    app = QtGui.QApplication([])

    #olDet = OLSaclaDetector.OLSaclaDetector("MPCCD-1-1-010", (230, 430), (400, 600))
    #olDet = OLSaclaDetector.OLSaclaDetector("MPCCD-2N0-1-004-1", (325, 340), (200, 600))
    olDet = OLSaclaDetector.OLSaclaDetector(arg.det, (arg.roi[0], arg.roi[1]), (arg.roi[2], arg.roi[3]), arg.uv)
    zpub = ZMQPublisher.ZMQPublisher(arg.port)
    
    mainAna = MainAnalysis(olDet, zpub)
    label = "DetID: {0}\nLaser: {1}\nPort: {2}".format(arg.det, arg.uv, arg.port)
    mainAna.Label = QtGui.QLabel(label, mainAna)
    main_window =QtGui.QMainWindow()
    main_window.setCentralWidget(mainAna)
    main_window.show()

    mainAna.LoadBackGround("/xdaq/users/bl3user/uedalab/BG/" + arg.bg)
    mainAna.Start(1000, 2000)
    signal.signal(signal.SIGINT, SIGINTHandler)
    sys.exit(app.exec_())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Online Analysis XES")
    parser.add_argument('-port', action='store', dest='port', type=int, required=True)
    parser.add_argument('-det', action='store', dest='det', type=str, required=True)
    parser.add_argument('-bg', action='store', dest='bg', type=str, required=True)
    parser.add_argument('-roi', nargs='+', dest='roi', required=True, type=int)
    parser.add_argument('-uv', action='store', dest='uv', type=str, default="all")
    
    argmnt = parser.parse_args()
    main(argmnt)

