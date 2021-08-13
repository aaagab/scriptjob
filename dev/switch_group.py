#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from .custom_windows import Windows_list
from . import notify

from ..gpkgs.guitools import Regular_windows

def switch_group(
    dy_state,
    active_monitor,
    active_window_hex_id,
    direction,
    group_name=None,
):
    dy_timestamps=dict()
    for name in dy_state["groups"]:
        dy_group=dy_state["groups"][name]
        dy_timestamps[dy_group["timestamp"]]=name

    group_names=[]
    for timestamp in sorted(dy_timestamps):
        group_names.append(dy_timestamps[timestamp])

    if len(group_names) == 0:
        notify.warning("There is no group to select.", obj_monitor=active_monitor)
        sys.exit(1)

    selected_name=None
    if group_name is None:
        if direction is None:
            groups_last_win_hex_ids=[]
            for name in group_names:
                win_ref=dy_state["groups"][name]["last_window_ref"]
                groups_last_win_hex_ids.append(dy_state["groups"][name]["windows"][win_ref]["hex_id"])

            window_list=Windows_list(dict(
                monitor=active_monitor,
                items=group_names, 
                prompt_text="Select a Group:", 
                checked=group_names.index(dy_state["active_group"]),
                title="ScriptJob"), groups_last_win_hex_ids)
                
            window_list.btn_done.pack_forget()
            window_list.focus_buttons.remove(window_list.btn_done)
            group_index=window_list.loop().output

            if group_index == "_aborted":
                notify.warning("switch_group canceled.", obj_monitor=active_monitor)
                sys.exit(1)
            else:
                selected_name=group_names[group_index]
        else:
            if len(group_names) == 1:
                selected_name=group_name
            else:
                group_name=dy_state["active_group"]
                group_index=group_names.index(group_name)
                if direction == "next":
                    is_last=(group_index == len(group_names) -1)
                    if is_last is True:
                        selected_name=group_names[0]
                    else:
                        selected_name=group_names[group_index+1]
                elif direction == "previous":
                    is_first=(group_index == group_names[0])
                    if is_first is True:
                        selected_name=group_names[-1]
                    else:
                        selected_name=group_names[group_index-1]
    else:
        if group_name in group_names:
            selected_name=group_name
        else:
            notify.error("Group '{}' does not exist in {}.".format(group_name, sorted(group_names)), obj_monitor=active_monitor)
            sys.exit(1)

    dy_group=dy_state["groups"][selected_name]
    dy_timestamp=dict()
    last_win_ref=dy_group["last_window_ref"]
    last_hex_id=None
    for win_ref in dy_group["windows"]:
        dy_win=dy_group["windows"][win_ref]
        if win_ref == last_win_ref:
            last_hex_id=dy_win["hex_id"]
        else:
            dy_timestamp[dy_win["timestamp"]]=dy_win["hex_id"]

    for timestamp in sorted(dy_timestamp):
        Regular_windows.focus(dy_timestamp[timestamp])

    Regular_windows.focus(last_hex_id)

    dy_state["active_group"]=selected_name
    dy_state["last_window_id"]=active_window_hex_id
