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

def emulate():
    """emulate data"""
    return np.random.uniform(100., 10., (2, 2))

def get_data_with_olpy():
    pass

def main(arg):
    """main process"""
    if arg.emulate is not None and arg.emulate:
        func = emulate
    else:
        # func = get_data_with_olpy
        raise NotImplementedError()

    with open(os.path.join(os.path.dirname(__file__), "config_getdata.json"),'r') as ff:
        config = json.load(ff)
    types = [key for key in config["port"].keys()]
    # types = ["sig_wl", "sig_wol", "bg_wl", "bg_wol"]
    ports = config["port"]
    publishers = dict()
    dataset = dict()
    interval = config["interval"]
    for ii, _type in enumerate(types):
        publishers[_type] = ZMQPublisher(ports[_type])

    datetime_fmt = "%Y-%m-%d %H:%M:%S"
    publisher_datetime = ZMQPublisher(config["port_pub"])
    datetime_start = datetime.datetime.now().strftime(datetime_fmt)
    print("start datetime:", datetime_start)
    while True:
        try:
            now = datetime.datetime.now().strftime(datetime_fmt)
            for _type in types:
                dataset[_type] = func()
                publishers[_type].SendArray(func(), _type)
            publisher_datetime.sendString(now, datetime_start)
            print(now, "publish succeeded. data:")
            for data in dataset.values():
                print(data.flatten())
            time.sleep(arg.interval)
        except KeyboardInterrupt as ex:
            print("Keyboard interruption.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-emulate', action='store', dest='emulate', type=bool, required=False)
    parser.add_argument('-interval', action='store', dest='interval', type=int, required=False)
    parser.add_argument('-port', action='store', dest='port', type=bool, required=True)
    argmnt = parser.parse_args()
    main(argmnt)
