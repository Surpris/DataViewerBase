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

def emulate():
    """emulate data"""
    output = dict()
    for _type in types:
        output[_type] = np.random.uniform(100., 10., (1000, 2000))
    return output

def get_data_with_olpy():
    pass

def main(arg):
    """main process"""
    if arg.emulate is not None and arg.emulate:
        func = emulate
    else:
        # func = get_data_with_olpy
        raise NotImplementedError()

    datetime_fmt = "%Y-%m-%d %H:%M:%S"
    publisher_datetime = ZMQPublisher(config["port_pub"])
    datetime_start = datetime.datetime.now()
    print("start datetime:", datetime_start)
    while True:
        try:
            st = time.time()
            now = datetime.datetime.now()
            dataset = func()
            for _type in types:
                publishers[_type].SendArray(dataset[_type], _type)
            publisher_datetime.sendString(now.strftime(datetime_fmt), 
                                          datetime_start.strftime(datetime_fmt))
            print(now, "publish succeeded. Elapsed time: {0:.4f} sec.".format(time.time()-st))
            # for data in dataset.values():
            #     print(data.flatten())
            time.sleep(interval)
        except KeyboardInterrupt:
            print("Keyboard interruption.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-emulate', action='store', dest='emulate', type=bool, required=False)
    argmnt = parser.parse_args()
    main(argmnt)
