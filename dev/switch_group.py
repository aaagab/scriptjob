#!/usr/bin/env python3
import os
import sys

from .windows_list import Windows_list
from .set_previous import set_previous
from .helpers import message, generate_group_name

from ..gpkgs.guitools import Regular_windows, Windows, Monitors

def switch_group(dy_state, action, group_name=None):
    active_monitor=Monitors().get_active()

    group_names=[group["name"] for group in dy_state["groups"]]
    group_index=""
    if not group_names:
        message("warning", "There is no group to select", active_monitor)
        sys.exit(1)
    
    active_group_index=group_names.index(dy_state["active_group"])
    start_hex_id=Windows.get_active_hex_id()


    process_switch_group=False
    
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
        if group_name is None:
            groups_previous_window_hex_ids=[group["previous_window"] for group in dy_state["groups"]]
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
            group_index=group_names.index(group_name)

    if dy_state["active_group"] != group_names[group_index]:
        set_previous(dy_state, "active_group", start_hex_id)
        # dy_state["groups"]

        dy_state["active_group"]=group_names[group_index]

        set_previous(dy_state, "global", start_hex_id)
        active_group_hex_ids=[win["hex_id"] for win in dy_state["groups"][group_index]["windows"]]
        focus_all_group_windows(active_group_hex_ids)
        Regular_windows.focus(dy_state["groups"][group_index]["previous_window"])
    else:
        active_group_hex_ids=[win["hex_id"] for win in dy_state["groups"][active_group_index]["windows"]]
        focus_all_group_windows(active_group_hex_ids)
        if start_hex_id in active_group_hex_ids:
            Regular_windows.focus(start_hex_id)
        else:
            Regular_windows.focus(dy_state["groups"][active_group_index]["previous_window"])
            set_previous(dy_state, "global", start_hex_id)

    message("success", "Active_Group: {}".format(dy_state["active_group"]), active_monitor)

def focus_all_group_windows(windows_hex_ids):
    for window_hex_id in windows_hex_ids:
        Regular_windows.focus(window_hex_id)
