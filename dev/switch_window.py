#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-beta-1546641342
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint

from modules.guitools.guitools import Windows, Window, Regular_windows
from dev.set_previous import set_previous
from dev.helpers import message

def switch_window(scriptjob_conf, direction):
    data=scriptjob_conf.data

    group_names=[group["name"] for group in data["groups"]]

    if not group_names:
        message("warning", "There is no group to select")
        sys.exit(1)
    
    if direction in ["previous", "next"]:
        active_group_index=group_names.index(data["active_group"])
        active_group=data["groups"][active_group_index]
        windows_hex_ids=[window["hex_id"] for window in active_group["windows"]]
        start_hex_id=Windows.get_active_hex_id()
        
        if start_hex_id in windows_hex_ids:
            current_index=windows_hex_ids.index(start_hex_id)
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
            set_previous(scriptjob_conf, "active_group", start_hex_id)
            # scriptjob_conf.set_file_with_data()
        else:
            Regular_windows.focus(active_group["previous_window"])

        set_previous(scriptjob_conf, "global", start_hex_id)
    else:
        message("error", "switch_window wrong entry '{}'".format(direction))
        sys.exit(1)
