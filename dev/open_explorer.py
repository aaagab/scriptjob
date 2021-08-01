#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import time

from . import notify
from .helpers import generate_group_name
from .set_previous import set_previous

from ..gpkgs.bwins import Prompt_boolean
from ..gpkgs.guitools import Window_open, Window

def open_explorer(
    default_applications,
    dy_state,
    active_monitor,
    active_window_hex_id,
    obj_monitors,
    filen_scriptjob_json,
):
    dy_active_group=""
    direpa_group=""
    for group in dy_state["groups"]:
        if group["name"] == dy_state["active_group"]:
            dy_active_group=group
            break
    
    if not dy_active_group:
        notify.error("There are no groups in '{}'".format(filen_scriptjob_json), active_monitor)
        sys.exit(1)

    if not "direpa_save_json" in dy_active_group:
        notify.error("There is no direpa_save_json in active group '{}' in '{}'".format(dy_state["active_group"], filen_scriptjob_json), active_monitor)
        sys.exit(1)
    else:
        direpa_group=dy_active_group["direpa_save_json"]

    if not dy_state["focus"]["explorer"]:
        launch_window=Window_open(default_applications["explorer"], obj_monitors=obj_monitors)
        while not launch_window.has_window():
            user_continue=Prompt_boolean(dict(monitor=active_monitor, title="Scriptjob open explorer", prompt_text="Can't open a window with cmd\n'{}'\nDo you want to wait?".format(default_applications["explorer"]))).loop().output
            if not user_continue:
                notify.error("Scriptjob command 'open explorer' aborted.", active_monitor)
                sys.exit(1)
        
        window=launch_window.window
        dy_state["focus"]["explorer"]=window.hex_id
        open_explorer_at_path(dy_state, active_window_hex_id, window, direpa_group)

    else:
        window=Window(dy_state["focus"]["explorer"], obj_monitors=obj_monitors)
        open_explorer_at_path(dy_state, active_window_hex_id, window, direpa_group)

def open_explorer_at_path(dy_state, active_window_hex_id, window, direpa_group):
    if window.hex_id != active_window_hex_id:
        set_previous(dy_state, "global", active_window_hex_id)
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
