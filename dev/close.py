#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from . import notify
from .custom_windows import Custom_check_box_list

from ..gpkgs.guitools import Regular_windows

def close(
    dy_state,
    active_monitor,
    obj_monitors,
    to_close_group_names=[],
    close_all=False,
):
    dy_timestamps=dict()
    for name in dy_state["groups"]:
        dy_group=dy_state["groups"][name]
        dy_timestamps[dy_group["timestamp"]]=name

    existing_group_names=[]
    prompt_group_names=[]
    for timestamp in sorted(dy_timestamps):
        existing_group_names.append(dy_timestamps[timestamp])
        prompt_group_names.append(dy_timestamps[timestamp])

    if len(existing_group_names) == 0:
        notify.warning("There is no group to select.", obj_monitor=active_monitor)
        sys.exit(1)

    if len(to_close_group_names) == 0:
        if close_all is True:
            to_close_group_names=existing_group_names
        else:
            options=dict(
                monitor=active_monitor,
                items=existing_group_names,
                values=existing_group_names,
                prompt_text="Select Group(s) to close: ",
                title="Scriptjob Group Close",
                checked=[False] * len(existing_group_names)
            )

            groups_last_win_hex_ids=[]
            for name in existing_group_names:
                win_ref=dy_state["groups"][name]["last_window_ref"]
                groups_last_win_hex_ids.append(dy_state["groups"][name]["windows"][win_ref]["hex_id"])


            to_close_group_names=Custom_check_box_list(options, groups_last_win_hex_ids).loop().output

            if to_close_group_names == "_aborted":
                notify.warning("Scriptjob close canceled.", obj_monitor=active_monitor)
                sys.exit(1)
            
            if len(to_close_group_names) == 0:
                notify.warning("Scriptjob close canceled.", obj_monitor=active_monitor)
                sys.exit(1)
    else:
        to_close_group_names=set(to_close_group_names)
        for to_close_group_name in to_close_group_names:
            if not to_close_group_name in existing_group_names:
                notify.warning("There is no group to close with name '{}'.".format(to_close_group_name), obj_monitor=active_monitor)
                sys.exit(1)

    non_selected_group_names=set(existing_group_names) - set(to_close_group_names)

    to_keep_win_hex_ids=set()
    for name in non_selected_group_names:
        dy_group=dy_state["groups"][name]
        for ref_num in dy_group["windows"]:
            to_keep_win_hex_ids.add(dy_group["windows"][ref_num]["hex_id"])

    for win_hex_id in dy_state["focus"]["windows"]:
        to_keep_win_hex_ids.add(win_hex_id)

    for name in sorted(dy_state["groups"]):
        if name in to_close_group_names:
            dy_group=dy_state["groups"][name]
            for ref_num in dy_group["windows"]:
                win_hex_id=dy_group["windows"][ref_num]["hex_id"]
                if win_hex_id not in to_keep_win_hex_ids:
                    Regular_windows.close(win_hex_id)
            del dy_state["groups"][name]
            existing_group_names.remove(name)

    if len(existing_group_names) > 0:
        dy_state["active_group"]=existing_group_names[-1]
    else:
        dy_state["active_group"]=None
    
    notify.success("Scriptjob group(s) {} closed.".format(prompt_group_names), obj_monitor=active_monitor)
