import sys
sys.path.append('/xdaq/users/bl3user/uedalab/onlineAPI/SaclaOnlineAPI')
import saclaOL
import numpy as np

class OLSaclaDetector(object):
    """ """
    def __init__(self, ccdName, roiX, roiY, selectTag="all"):
        """ """
        self.ccd = saclaOL.OnlineDetData(ccdName.encode())
        self.ccd.Connect()

        self.previousTag = 0
        self.roiX = roiX
        self.roiY = roiY
        self.ROI = (roiX[0], roiX[1], roiY[0], roiY[1])
        #self.ROI = (roiY[0], roiY[1], roiX[0], roiX[1])
        self.tags = np.zeros(30)
        #self.images = np.zeros((30, self.roiY[1] - self.roiY[0], self.roiX[1] - self.roiX[0]))
        self.images = np.zeros((30, self.roiX[1] - self.roiX[0], self.roiY[1] - self.roiY[0]))
        self.frameCounter = 0
        self.selectTag = selectTag
        self.previousTag = 0
        self.GetCurrentTag()
        print("ROI=", roiX[0], roiX[1], roiY[0], roiY[1])

    def GetCurrentTag(self):
        self.previousTag = self.ccd.ReadTagNumber() + 2
        return self.previousTag

    def GetImeges(self):
        bufLastTAG = self.ccd.ReadTagNumber()
        if bufLastTAG - self.previousTag > 58:
            tagFrom = bufLastTAG - 60 + 2
        else:
            tagFrom = self.previousTag
            
        self.previousTag = bufLastTAG + 2
        offset = 0
        # make and select tag list
        tagList = np.arange(tagFrom + offset , bufLastTAG + 2 + offset, 2)
        #print(list(tagList))
        if self.selectTag == "on":
            tagList = tagList[tagList % 4 == 0]
            #tagList = tagList[tagList % 8 == 0] # off
        elif self.selectTag == "off":
            tagList = tagList[tagList % 4 == 2]
            #tagList = tagList[tagList % 8 == 4] # On
        if len(tagList) == 0:
            return self.tags[0:0], self.images[0:0,:,:]
        # -----Main loop-----
        self.frameCounter = 0
        for tag in tagList:
            try:
                detData, retTag = self.ccd.ReadDetDataROI(tag, self.ROI)
            except:
                print("miss")
                continue
            #print(self.frameCounter)                
            self.tags[self.frameCounter] = retTag
            self.images[self.frameCounter,:,:] = detData.T
            self.frameCounter += 1
        #print(self.frameCounter, end=":")
        return self.tags[0:self.frameCounter], self.images[0:self.frameCounter,:,:]

if __name__ == "__main__":
    olDet = OLSaclaDetector("MPCCD-1N0-M01-002", (230, 430), (400, 600))
    print(olDet.GetCurrentTag)
