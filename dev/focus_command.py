#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.0.0
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint
from dev.helpers import message
from dev.set_previous import set_previous

from modules.guitools.guitools import Window, Monitors
from modules.bwins.bwins import Prompt_boolean
from modules.guitools.guitools import Monitors, Window_open, Window, Windows

def focus_command(dy_app, scriptjob_conf):
    active_hex_id=Windows.get_active_hex_id()
    data=scriptjob_conf.data
    obj_monitor=Monitors().get_active()

    cmd_alias=dy_app["args"]["focus_command"][0]

    if not cmd_alias in dy_app["default"]:
        defaults="', '".join([alias for alias in dy_app["default"]])
        message("user_error", "'{}' command alias not found".format(cmd_alias), obj_monitor)
        message("user_error", "Choose commad alias in ['{}']".format(defaults), obj_monitor)
        sys.exit(1)

    if not data["focus"][cmd_alias]:
        launch_window=Window_open(dy_app["default"][cmd_alias])
        while not launch_window.has_window():
            user_continue=Prompt_boolean(dict(monitor=obj_monitor, title="Scriptjob focus command", prompt_text="Can't open a window with cmd\n'{}'\nDo you want to retry?".format(dy_app["default"][cmd_alias]))).loop().output
            if not user_continue:
                message("Scriptjob command 'focus command' aborted.", "error", obj_monitor)
                sys.exit(1)
        
        window=launch_window.window
        data["focus"][cmd_alias]=window.hex_id
        if window.hex_id != active_hex_id:
            set_previous(scriptjob_conf, "global", active_hex_id)
        window.focus()

    else:
        window=Window(data["focus"][cmd_alias])
        if active_hex_id == window.hex_id:
            Window(data["previous_window"]).focus() 
        else:
            if window.hex_id != active_hex_id:
                set_previous(scriptjob_conf, "global", active_hex_id)
            window.focus()
