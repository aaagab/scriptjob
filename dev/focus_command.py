#!/usr/bin/env python3
import os
import sys
from pprint import pprint

from .helpers import message, generate_group_name
from .set_previous import set_previous

from ..gpkgs.bwins import Prompt_boolean
from ..gpkgs.guitools import Monitors, Window_open, Window, Windows

# def focus_command(dy_settings, dy_state):
def focus_command(default_applications, dy_state, command):
    active_hex_id=Windows.get_active_hex_id()
    obj_monitor=Monitors().get_active()

    if not command in default_applications:
        defaults="', '".join([alias for alias in default_applications])
        message("error", "'{}' command alias not found".format(command), obj_monitor)
        message("error", "Choose commad alias in ['{}']".format(defaults), obj_monitor)
        sys.exit(1)

    if not dy_state["focus"][command]:
        launch_window=Window_open(default_applications[command])
        while not launch_window.has_window():
            user_continue=Prompt_boolean(dict(monitor=obj_monitor, title="Scriptjob focus command", prompt_text="Can't open a window with cmd\n'{}'\nDo you want to retry?".format(default_applications[command]))).loop().output
            if not user_continue:
                message("Scriptjob command 'focus command' aborted.", "error", obj_monitor)
                sys.exit(1)
        
        window=launch_window.window
        dy_state["focus"][command]=window.hex_id
        if window.hex_id != active_hex_id:
            set_previous(dy_state, "global", active_hex_id)
        window.focus()

    else:
        window=Window(dy_state["focus"][command])
        if active_hex_id == window.hex_id:
            Window(dy_state["previous_window"]).focus() 
        else:
            if window.hex_id != active_hex_id:
                set_previous(dy_state, "global", active_hex_id)
            window.focus()
