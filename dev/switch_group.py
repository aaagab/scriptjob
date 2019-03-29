#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.2.0
# name: scriptjob
# license: MIT

import os, sys

from dev.windows_list import Windows_list
from dev.set_previous import set_previous
from dev.helpers import message
from modules.guitools.guitools import Regular_windows, Windows, Monitors

def switch_group(scriptjob_conf, action="", group_name=""):
    data=scriptjob_conf.data
    active_monitor=Monitors().get_active()

    group_names=[group["name"] for group in data["groups"]]
    group_index=""
    if not group_names:
        message("warning", "There is no group to select", active_monitor)
        sys.exit(1)
    
    active_group_index=group_names.index(data["active_group"])
    start_hex_id=Windows.get_active_hex_id()


    process_switch_group=False
    if not action:
        groups_previous_window_hex_ids=[group["previous_window"] for group in data["groups"]]
        window_list=Windows_list(dict(
            monitor=active_monitor,
            items=group_names, 
            prompt_text="Select a Group:", 
            checked=active_group_index,
            title="ScriptJob"), groups_previous_window_hex_ids)
            
        window_list.btn_done.pack_forget()
        window_list.focus_buttons.remove(window_list.btn_done)
        group_index=window_list.loop().output

        if group_index == "_aborted":
            message("warning", "Scriptjob switch_group cancelled.", active_monitor)
            sys.exit(1)
    
    else:
        if action == "next":
            if active_group_index == len(group_names) -1:
                group_index=0
            else:
                group_index=active_group_index+1
        elif action == "previous":
            if active_group_index == 0:
                group_index=len(group_names) - 1
            else:
                group_index=active_group_index-1
        elif action == "group":
            if not group_name:
                message("error", "Group Name needs to be given when group is selected.", active_monitor)
                sys.exit(1)

            group_index=group_names.index(group_name)
        else:
            if not group_name:
                message("error", "Unknow action '{}'".format(action), active_monitor)
                sys.exit(1)

    if data["active_group"] != group_names[group_index]:
        set_previous(scriptjob_conf, "active_group", start_hex_id)
        # data["groups"]

        data["active_group"]=group_names[group_index]
        scriptjob_conf.set_file_with_data()

        set_previous(scriptjob_conf, "global", start_hex_id)
        active_group_hex_ids=[win["hex_id"] for win in data["groups"][group_index]["windows"]]
        focus_all_group_windows(active_group_hex_ids)
        Regular_windows.focus(data["groups"][group_index]["previous_window"])
    else:
        active_group_hex_ids=[win["hex_id"] for win in data["groups"][active_group_index]["windows"]]
        focus_all_group_windows(active_group_hex_ids)
        if start_hex_id in active_group_hex_ids:
            Regular_windows.focus(start_hex_id)
        else:
            Regular_windows.focus(data["groups"][active_group_index]["previous_window"])
            set_previous(scriptjob_conf, "global", start_hex_id)

    # scriptjob_conf.set_file_with_data()

    message("success", "Active_Group: {}".format(data["active_group"]), active_monitor)

def focus_all_group_windows(windows_hex_ids):
    for window_hex_id in windows_hex_ids:
        Regular_windows.focus(window_hex_id)
