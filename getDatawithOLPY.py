# -*- coding: utf-8 -*-

"""
Created on Thu Jul 14 21:40 2017

@author: Surpris
"""
import argparse
import signal
import sys
import time
import datetime
import numpy as np
import zmq
import os
import json

from core.ZeroMQ import ZMQPublisher
from core.OnlineSimulator import GetDataClass

description = """
    get real-time images from buffer using olpy.
"""

with open(os.path.join(os.path.dirname(__file__), "config_getdata.json"), 'r') as ff:
    config = json.load(ff)
types = [key for key in config["port"].keys()]
ports = config["port"]
publishers = dict()
interval = config["interval"]
for _type in types:
    publishers[_type] = ZMQPublisher(ports[_type])

process_timeout = config["timeout"] # [sec]

# GetDataClass related.
detId = config["GetDataClass"]["detId"]
chan = config["GetDataClass"]["channel"]
bl = config["GetDataClass"]["bl"]
limNumImg = config["GetDataClass"]["limNumImg"]


def emulate():
    """emulate data"""
    output = dict()
    for _type in types:
        output[_type] = np.random.uniform(100., 10., (1000, 2000))
    return output

def main(arg):
    """main process"""
    if arg.emulate is not None and arg.emulate:
        func = emulate
    else:
        getDataClass = GetDataClass(detId=detId, chan=chan, bl=bl, limNumImg=limNumImg)
        func = getDataClass.getData

    datetime_fmt = "%Y-%m-%d %H:%M:%S"
    publisher_info = ZMQPublisher(config["port_pub"])
    datetime_start = datetime.datetime.now()
    print("start datetime:", datetime_start)
    # numOfImg_total = np.zeros(6)
    while True:
        try:
            st = time.time()
            now = datetime.datetime.now()
            delta = now - datetime_start
            if delta.total_seconds() > process_timeout:
                print("Emulation timeout.")
                break
            if arg.emulate is not None and arg.emulate:
                dataset = func()
                # currentRun = np.random.randint(0, 2000)
                # tag_start = np.random.randint(0, 1000000)
                # tag_end = tag_start + np.random.randint(0, 100)
                # nbr_of_sig = int((tag_end - tag_start + 1)/3)
                # nbr_of_bg = (tag_end - tag_start + 1) - nbr_of_sig
            else:
                _data, numOfImg, currentRun, startTag, endTag = func()
                # numOfImg_total += numOfImg
                # print(numOfImg_total, currentRun, startTag, endTag)
                dataset = {"sig_wl":_data[0]+_data[2],
                           "sig_wol":_data[1]+_data[3],
                           "bg_wl":_data[4], "bg_wol":_data[5]}
            for _type in types:
                publishers[_type].SendArray(dataset[_type], _type)
            publisher_info.sendString(now.strftime(datetime_fmt), 
                                          datetime_start.strftime(datetime_fmt))
            elapsed = time.time()-st
            print(now, "publish succeeded. Elapsed time: {0:.4f} sec.".format(elapsed))
            # for data in dataset.values():
            #     print(data.flatten())
            if interval - elapsed > 0:
                time.sleep(interval - elapsed)
        except KeyboardInterrupt:
            print("Keyboard interruption.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-emulate', action='store', dest='emulate', type=bool, required=False)
    argmnt = parser.parse_args()
    main(argmnt)
