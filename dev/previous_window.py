#!/usr/bin/env python3
import os
import sys

from .set_previous import set_previous
from .helpers import message

from ..gpkgs.guitools import Windows, Window, Regular_windows, Monitors

def previous_window(dy_state, previous_type):
    obj_monitor=Monitors().get_active()
    start_hex_id=Windows.get_active_hex_id()
    if previous_type == "global":
        if data["previous_window"] != start_hex_id:
            Regular_windows.focus(data["previous_window"])
            set_previous(dy_state, "global", start_hex_id)
        else:
            pass
    elif previous_type == "active_group":
        group_names=[group["name"] for group in data["groups"]]

        if not group_names:
            message("warning", "There is no group for previous_window", obj_monitor)
            sys.exit(1)

        active_group_index=group_names.index(data["active_group"])
        active_group=data["groups"][active_group_index]
        active_group_hex_ids=[win["hex_id"] for win in active_group["windows"]]

        if start_hex_id in active_group_hex_ids:
            if start_hex_id != active_group["previous_window"]:
                Regular_windows.focus(active_group["previous_window"])
                set_previous(dy_state, "active_group", start_hex_id)
            else:
                pass
        else:
            Regular_windows.focus(active_group["previous_window"])
