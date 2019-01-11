#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-beta-1547213809
# name: scriptjob
# license: MIT

import os, sys
from modules.guitools.guitools import Windows, Window, Regular_windows, Monitors
from dev.set_previous import set_previous
from dev.helpers import message

def previous_window(scriptjob_conf, previous_type):
    obj_monitor=Monitors().get_active()
    data=scriptjob_conf.data
    start_hex_id=Windows.get_active_hex_id()
    if previous_type == "global":
        if data["previous_window"] != start_hex_id:
            Regular_windows.focus(data["previous_window"])
            set_previous(scriptjob_conf, "global", start_hex_id)
            # scriptjob_conf.set_file_with_data()
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
                set_previous(scriptjob_conf, "active_group", start_hex_id)
                # scriptjob_conf.set_file_with_data()
            else:
                pass
        else:
            Regular_windows.focus(active_group["previous_window"])
