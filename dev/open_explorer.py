#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.0.0
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint
from dev.helpers import message
from dev.set_previous import set_previous

from modules.guitools.guitools import Window, Monitors
from modules.bwins.bwins import Prompt_boolean
from modules.guitools.guitools import Monitors, Window_open, Window, Windows
import time

def open_explorer(dy_app, scriptjob_conf):
    active_hex_id=Windows.get_active_hex_id()
    data=scriptjob_conf.data
    obj_monitor=Monitors().get_active()

    dy_active_group=""
    direpa_group=""
    for group in data["groups"]:
        if group["name"] == data["active_group"]:
            dy_active_group=group
            break
    
    if not dy_active_group:
        message("user_error", "There are no groups in '{}'".format(data["filen_scriptjob_json"]), obj_monitor)
        sys.exit(1)

    if not "direpa_save_json" in dy_active_group:
        message("user_error", "There is no direpa_save_json in active group '{}' in '{}'".format(data["active_group"], data["filen_scriptjob_json"]), obj_monitor)
        sys.exit(1)
    else:
        direpa_group=dy_active_group["direpa_save_json"]

    if not data["focus"]["explorer"]:
        launch_window=Window_open(dy_app["default"]["explorer"])
        while not launch_window.has_window():
            user_continue=Prompt_boolean(dict(monitor=obj_monitor, title="Scriptjob open explorer", prompt_text="Can't open a window with cmd\n'{}'\nDo you want to retry?".format(dy_app["default"]["explorer"]))).loop().output
            if not user_continue:
                message("Scriptjob command 'open explorer' aborted.", "error", obj_monitor)
                sys.exit(1)
        
        window=launch_window.window
        data["focus"]["explorer"]=window.hex_id
        open_explorer_at_path(scriptjob_conf, active_hex_id, window, direpa_group)

    else:
        window=Window(data["focus"]["explorer"])
        open_explorer_at_path(scriptjob_conf, active_hex_id, window, direpa_group)

def open_explorer_at_path(scriptjob_conf, active_hex_id, window, direpa_group):
    if window.hex_id != active_hex_id:
        set_previous(scriptjob_conf, "global", active_hex_id)
    window.focus()

    time.sleep(.3)
    # window.kbd.key("Escape Menu Down Down Down Return")
    window.kbd.key("Control+Shift+n")
    window.kbd.key("Control+l")
    window.kbd.type(direpa_group)
    window.kbd.key("Return")
    # time.sleep(.3)
    window.kbd.key("Shift+Tab")
    # time.sleep(.3)
    window.kbd.key("Shift+Tab")
    # time.sleep(.3)
    window.kbd.key("Shift+Tab")

    # time.sleep(.3)
    # window.kbd.key("Tab")

    time.sleep(.3)
