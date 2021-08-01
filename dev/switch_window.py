#!/usr/bin/env python3
import os
import sys
from pprint import pprint

from .set_previous import set_previous
from . import notify
from .helpers import generate_group_name

from ..gpkgs.guitools import Regular_windows

def switch_window(
    dy_state,
    active_monitor,
    active_window_hex_id,
    direction,
):
    group_names=[group["name"] for group in dy_state["groups"]]

    if not group_names:
        notify.warning("There is no group to select", active_monitor)
        sys.exit(1)
    
    if direction in ["previous", "next"]:
        active_group_index=group_names.index(dy_state["active_group"])
        active_group=dy_state["groups"][active_group_index]
        windows_hex_ids=[window["hex_id"] for window in active_group["windows"]]
        
        if active_window_hex_id in windows_hex_ids:
            current_index=windows_hex_ids.index(active_window_hex_id)
            selected_hex_id=""
            if direction == "previous":
                if current_index == 0:
                    selected_hex_id=windows_hex_ids[-1]
                else:
                    selected_hex_id=windows_hex_ids[current_index - 1]
            elif direction == "next":
                if current_index == len(windows_hex_ids) - 1:
                    selected_hex_id=windows_hex_ids[0]
                else:
                    selected_hex_id=windows_hex_ids[current_index + 1]

            Regular_windows.focus(selected_hex_id)
            set_previous(dy_state, "active_group", active_window_hex_id)
            # dy_state.set_file_with_data()
        else:
            Regular_windows.focus(active_group["previous_window"])

        set_previous(dy_state, "global", active_window_hex_id)
    else:
        notify.error("switch_window wrong entry '{}'".format(direction), active_monitor)
        sys.exit(1)
