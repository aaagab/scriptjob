#!/usr/bin/env python3
import os
import sys
from pprint import pprint

from . import notify
from .helpers import generate_group_name
from .set_previous import set_previous

from ..gpkgs.bwins import Prompt_boolean
from ..gpkgs.guitools import Window_open, Window

def focus_command(
    default_applications,
    dy_state,
    active_monitor,
    active_window_hex_id,
    obj_monitors,
    command,
):
    if not command in default_applications:
        defaults="', '".join([alias for alias in default_applications])
        notify.error("'{}' command alias not found".format(command), active_monitor)
        notify.error("Choose commad alias in ['{}']".format(defaults), active_monitor)
        sys.exit(1)

    if not dy_state["focus"][command]:
        launch_window=Window_open(default_applications[command], obj_monitors=obj_monitors)
        while not launch_window.has_window():
            user_continue=Prompt_boolean(dict(monitor=active_monitor, title="Scriptjob focus command", prompt_text="Can't open a window with cmd\n'{}'\nDo you want to retry?".format(default_applications[command]))).loop().output
            if not user_continue:
                notify.error("Scriptjob command 'focus command' aborted.", active_monitor)
                sys.exit(1)
        
        window=launch_window.window
        dy_state["focus"][command]=window.hex_id
        if window.hex_id != active_window_hex_id:
            set_previous(dy_state, "global", active_window_hex_id)
        window.focus()

    else:
        window=Window(dy_state["focus"][command], obj_monitors=obj_monitors)
        if active_window_hex_id == window.hex_id:
            Window(dy_state["previous_window"], obj_monitors=obj_monitors).focus() 
        else:
            if window.hex_id != active_window_hex_id:
                set_previous(dy_state, "global", active_window_hex_id)
            window.focus()
