# coding: utf-8

import olpy
import dbpy
import time
import datetime
import numpy as np

class TagDiscriminator():
    """
    Class for discrimination of tags.
    """
    def __init__(self, bl, chan, cycle, offset, field):
        self.bl = bl
        self.chan = chan
        self.cycle = cycle
        self.offset = offset
        self.field = field
        
    def analizePattern(self):
        """
        make a pattern of tags.
        """
        now = datetime.datetime.now()
        print("[{}]: Analyze pattern".format(now))
        numOfTags = 12
        run = dbpy.read_runnumber_newest(self.bl)
        run -= 0
        hiTag, startTag = dbpy.read_start_tagnumber(self.bl, run)
        #print(newestTag)
        tagList = dbpy.read_taglist(self.bl, hiTag, startTag, startTag + numOfTags - 1)
        #print(tagList)
        status = dbpy.read_syncdatalist_float(self.field, hiTag, tagList)
        status = np.array(status)
        #print(status)
        self.offset = tagList[np.nonzero(status)[0][0]]
        self.startTag = startTag
    
    def discriminate(self, tagList):
        return (tagList-self.offset) % self.cycle

class GetDataClass(object):
    """Class for getting data."""

    def __init__(self, detId='OPAL-234363', chan=0, bl=1, cycle=6, limNumImg=35):
        """Initialization"""
        self.repRate = 60
        self.tagRepRate = 60
        self.waitSec = 1
        self.limNumImg = limNumImg
        self.chan = 0
        self.cycle = 6
        self.bl = 1
        self.detId = detId

        self.read = olpy.StorageReader(self.detId)
        self.buf = olpy.StorageBuffer(self.read)
        self.disc = TagDiscriminator(self.bl, self.chan, self.cycle, None, 
                                     "xfel_bl_1_shutter_1_open_valid/status")
        self.startTag = -1
        self.endTag = -1
        self.isReset = False
        self.currentRun = -1

    def getData(self):
        """get data from the detector with Id `detId`. """
        st = time.time()
        currentRun = dbpy.read_runnumber_newest(self.bl)

        #tag discriminator setup
        # success_dbpy = False
        if self.endTag == -1 or self.currentRun != currentRun:
            runstatus = dbpy.read_runstatus(self.bl, currentRun)
            if runstatus == 2: # Analyse patterns after the latest Run start running.
                self.currentRun = currentRun
                self.disc.analizePattern()
        self.startTag = self.disc.startTag

        #initialize parameters
        image = [None for col in range(self.disc.cycle)]
        numOfImg = np.zeros(self.disc.cycle)

        #Acquire the current newest tag and image
        newestTag = self.read.collect(self.buf, olpy.NEWESTTAG)
        
        col = self.disc.discriminate(newestTag)
        if image[col] is None:
            image[col] = self.buf.read_det_data(self.chan)
        else:
            image[col] += self.buf.read_det_data(self.chan)
        numOfImg[col] += 1
        
        #repeat acquiring images backward
        for i in range(1, self.limNumImg + 1):
            #try to get image
            tag = newestTag - int(self.tagRepRate/self.repRate)*i
            if tag == self.endTag or tag < self.startTag:
                break

            try:
                self.read.collect(self.buf, tag)
            except Exception as ex:
                print(tag, ":", ex)
                continue

            col = self.disc.discriminate(tag)
            if image[col] is None:
                image[col] = self.buf.read_det_data(self.chan)
            else:
                image[col] += self.buf.read_det_data(self.chan)
            numOfImg[col] += 1

        self.endTag = newestTag

        run = dbpy.read_runnumber_newest(self.bl)
        runstatus = dbpy.read_runstatus(self.bl, run)
        if runstatus == 0: # (-1=not yet exist, 0=Stopped(ready to read), 1=Paused, 2=Running)
            pass
        elif runstatus != 2:
            self.startTag = -1
            self.endTag = -1
        else:
            pass
        
        # if elapsed < self.waitSec:
        #     time.sleep(self.waitSec - elapsed)
        return image, numOfImg, currentRun, self.startTag, self.endTag

if __name__ == "main":
    pass
    # getData()