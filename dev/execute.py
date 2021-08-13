#!/usr/bin/env python3
from pprint import pprint
import re
import os
import sys
import time

from . import notify
from .get_dy_group import execute_regexes

from ..gpkgs.guitools import Regular_windows, Keyboard


def get_window_hex_id(dy_group, active_win_hex_id, value, group_win_hex_ids=None):
    if group_win_hex_ids is None:
        group_win_hex_ids=get_group_win_hex_ids(dy_group)

    if value == "last":
        win_ref=dy_group["last_window_ref"]
        dy_win=dy_group["windows"][win_ref]

        if len(group_win_hex_ids) <= 1:
            return None
        else:
            if active_win_hex_id == dy_win["hex_id"]:
                win_index=group_win_hex_ids.index(active_win_hex_id)
                is_first=(win_index == group_win_hex_ids[0])
                if is_first is True:
                    return group_win_hex_ids[-1]
                else:
                    return group_win_hex_ids[win_index-1]
            else:
                return dy_win["hex_id"]
    elif value in ["next", "previous"]:
        if len(group_win_hex_ids) <= 1:
            return None
        else:
            win_index=group_win_hex_ids.index(active_win_hex_id)
            if value == "next":
                is_last=(win_index == len(group_win_hex_ids) -1)
                if is_last is True:
                    return group_win_hex_ids[0]
                else:
                    return group_win_hex_ids[win_index+1]
            elif value == "previous":
                is_first=(win_index == group_win_hex_ids[0])
                if is_first is True:
                    return group_win_hex_ids[-1]
                else:
                    return group_win_hex_ids[win_index-1]
    else:
        # value equals win_ref as str
        return dy_group["windows"][value]["hex_id"]

def get_group_win_hex_ids(dy_group):
    dy_timestamp=dict()
    for index in dy_group["windows"]:
        dy_win=dy_group["windows"][index]
        dy_timestamp[dy_win["timestamp"]]=dy_win["hex_id"]

    group_win_hex_ids=[]
    for timestamp in sorted(dy_timestamp):
        group_win_hex_ids.append(dy_timestamp[timestamp])

    return group_win_hex_ids

def execute(dy_state, active_window_hex_id, active_monitor):
    group_names=sorted(dy_state["groups"])
    if len(group_names) == 0:
        notify.warning("There is no group to select for execute", obj_monitor=active_monitor)
        sys.exit(1)

    dy_group=dy_state["groups"][dy_state["active_group"]]

    group_win_hex_ids=get_group_win_hex_ids(dy_group)

    # active_window_hex_id="0x7c00007"
    # active_window_hex_id="0x620011c"
    if active_window_hex_id in group_win_hex_ids:
        for win_ref in dy_group["windows"]:
            dy_win=dy_group["windows"][win_ref]
            if dy_win["hex_id"] == active_window_hex_id:
                for cmd in dy_win["execute"]:
                    for reg_txt in execute_regexes():
                        reg=re.match(reg_txt, cmd)
                        if reg:
                            dy_cmd=reg.groupdict()
                            if dy_cmd["cmd"] in ["focus", "send-keys"]:
                                win_hex_id=get_window_hex_id(
                                    dy_group,
                                    active_window_hex_id,
                                    dy_cmd["value"],
                                    group_win_hex_ids,
                                )
                                if win_hex_id is not None:
                                    if dy_cmd["cmd"] == "focus":
                                        if win_hex_id != active_window_hex_id:
                                            Regular_windows.focus(win_hex_id)
                                    elif dy_cmd["cmd"] == "send-keys":
                                        Keyboard(int(win_hex_id, 16)).key(dy_cmd["keys"])
                            elif dy_cmd["cmd"] == "sleep":
                                time.sleep(float(dy_cmd["value"]))
                            
                            break
                break
    else:
        win_ref=dy_group["last_window_ref"]
        Regular_windows.focus(dy_group["windows"][win_ref]["hex_id"])

    dy_state["last_window_id"]=active_window_hex_id
    if active_window_hex_id in group_win_hex_ids:
        dy_state["groups"][dy_state["active_group"]]["last_window_ref"]