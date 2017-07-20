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
from core.GetDataClass import GetDataClass

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
port_info = config["port_info"]

process_timeout = config["timeout"] # [sec]

# GetDataClass related.
detId = config["GetDataClass"]["detId"]
chan = config["GetDataClass"]["channel"]
bl = config["GetDataClass"]["bl"]
limNumImg = config["GetDataClass"]["limNumImg"]
cycle = config["GetDataClass"]["cycle"]
signal_flag = config["signal_flag"]

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
        getDataClass = GetDataClass(detId=detId, chan=chan, bl=bl, cycle=cycle, limNumImg=limNumImg)
        func = getDataClass.getData

    datetime_fmt = "%Y-%m-%d %H:%M:%S"
    publisher_info = ZMQPublisher(port_info)
    datetime_start = datetime.datetime.now()
    print("start datetime:", datetime_start)
    numOfImg_total = np.zeros(6)
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
                for _type in types:
                    publishers[_type].SendArray(dataset[_type], _type)

                currentRun = np.random.randint(0, 2000)
                startTag = np.random.randint(0, 1000000)
                endTag = startTag + np.random.randint(0, 100)
                nbr_of_sig = int((endTag - startTag + 1)/3)
                nbr_of_bg = (endTag - startTag + 1) - nbr_of_sig
                info = [currentRun, startTag, endTag, nbr_of_sig, nbr_of_sig, nbr_of_bg, nbr_of_bg]
                publisher_info.SendArray(info, now.strftime(datetime_fmt))
            else:
                try:
                    data, numOfImg, currentRun, startTag, endTag = func()
                    numOfImg_total += numOfImg
                    print(numOfImg_total, currentRun, startTag, endTag)
                    for _type in types:
                        # buff = None
                        if _type == "sig_wl":
                            buff = data[0] + data[2]
                        elif _type == "sig_wol":
                            buff = data[1] + data[3]
                        elif _type == "bg_wl":
                            buff = data[4]
                        else:
                            buff = data[5]
                        # for ind in signal_flag[_type]:
                        #     print(_type, ind)
                        #     if isinstance(ind, int):
                        #         buff = data[ind].copy()
                        #     else:
                        #         for ii in ind:
                        #             if buff is None:
                        #                 buff = data[ii].copy()
                        #             else:
                        #                 buff += data[ii]
                        publishers[_type].SendArray(buff, _type)
                    
                    info = [currentRun, startTag, endTag]
                    for _type in ["sig_wl", "sig_wol", "bg_wl", "bg_wol"]:
                        ind = signal_flag[_type]
                        num = 0
                        if isinstance(ind, int):
                            num = numOfImg[ind]
                        else:
                            for ii in ind:
                                num += numOfImg[ii]
                        info.append(num)

                    publisher_info.SendArray(np.array(info, dtype=int), now.strftime(datetime_fmt))
                    elapsed = time.time() - st
                    print("[{0}]: publish succeeded. Elapsed time: {1:.4f} sec.".format(now, elapsed))
                except Exception as ex:
                    elapsed = time.time() - st
                    print(ex)
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
