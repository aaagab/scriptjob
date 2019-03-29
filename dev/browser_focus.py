#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.3.0
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint
from dev.helpers import message
from dev.set_previous import set_previous

from modules.guitools.guitools import Window, Monitors
from modules.bwins.bwins import Prompt_boolean
from modules.guitools.guitools import Monitors, Window_open, Window, Windows


def browser_focus(dy_app, scriptjob_conf):
    active_hex_id=Windows.get_active_hex_id()
    data=scriptjob_conf.data
    obj_monitor=Monitors().get_active()
    if not data["browser_window"]:
        cmd="firefox"
        launch_window=Window_open(cmd)
        while not launch_window.has_window():
            user_continue=Prompt_boolean(dict(monitor=obj_monitor, title="Scriptjob browser focus", prompt_text="Can't open a window with cmd\n'{}'\nDo you want to retry?".format(cmd))).loop().output
            if not user_continue:
                message("Scriptjob command 'browser focus' aborted.", "error", obj_monitor)
                sys.exit(1)
        
        window=launch_window.window
        data["browser_window"]=window.hex_id
        window.focus()
        set_previous(scriptjob_conf, "global", active_hex_id)

    else:
        window=Window(data["browser_window"])
        if active_hex_id == window.hex_id:
            Window(data["previous_window"]).focus() 
        else:
            window.focus()
            set_previous(scriptjob_conf, "global", active_hex_id)
