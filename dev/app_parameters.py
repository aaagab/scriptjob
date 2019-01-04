#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-beta-1546641342
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint
import time

def get_title(window):
    if window["exe"] == "konsole":
        return window["name"].replace(" \u2014 Konsole", "")

def set_cmds_after_open(window_data, window):
    if window_data["exe"] == "dolphin":
        if window_data["hex_id"] == "create":
            if window_data["paths"]:
                del window_data["paths"][0]

        for path in window_data["paths"]:
            time.sleep(.3)
            window.kbd.key("Escape Menu Down Down Down Return")
            window.kbd.key("Control+l")
            window.kbd.type(path)
            window.kbd.key("Return")
            time.sleep(.3)
