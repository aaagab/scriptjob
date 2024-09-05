#!/usr/bin/env python3
from pprint import pprint
from typing import Any, cast
import re
import os
import sys
import time

from . import notify
from .get_dy_group import execute_regexes

from .session import State, Group, Window

from ..gpkgs.guitools import Windows, Keyboard, Mouse, XlibHelpers


def get_window_hex_id(group:Group, active_win_hex_id:str, value:str, group_win_hex_ids:list[str]|None=None):
    if group_win_hex_ids is None:
        group_win_hex_ids=get_group_win_hex_ids(group)

    if value == "last":
        win_ref=group.last_window_ref
        window:Window
        try:
            window=[w for w in group.windows if w.ref == win_ref][0]
        except IndexError:
            raise NotImplementedError()

        if len(group_win_hex_ids) <= 1:
            return None
        else:
            if active_win_hex_id == window.hex_id:
                win_index=group_win_hex_ids.index(active_win_hex_id)
                is_first=(win_index == group_win_hex_ids[0])
                if is_first is True:
                    return group_win_hex_ids[-1]
                else:
                    return group_win_hex_ids[win_index-1]
            else:
                return window.hex_id
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
        try:
            return [w.hex_id for w in group.windows if w.ref == int(value)][0]
        except IndexError:
            raise NotImplementedError()

def get_group_win_hex_ids(group:Group):
    dy_timestamp:dict[float, str]=dict()
    for w in group.windows:
        dy_timestamp[w.timestamp]=w.hex_id

    group_win_hex_ids:list[str]=[]
    for timestamp in sorted(dy_timestamp):
        group_win_hex_ids.append(dy_timestamp[timestamp])

    return group_win_hex_ids

def execute(
    state:State, 
    active_window_hex_id:str,
    shortcuts:list[str]|None=None,
    window_ref:int|None=None,
    group_name:str|None=None,
):    
    if shortcuts is None:
        shortcuts=[]
    group_names=[g.name for g in state.groups]
    if len(group_names) == 0:
        notify.warning("There is no group to select for execute")
        sys.exit(1)

    group:Group|None=None
    if group_name is None:
        try:
            group=[g for g in state.groups if g.name == state.active_group][0]
        except IndexError:
            raise NotImplementedError()
    else:
        try:
            group=[g for g in state.groups if g.name == group_name][0]
        except IndexError:
            notify.error("At command execute group name '{}' not found.".format(group_name))
            sys.exit(1)

    window:Window|None=None
    if window_ref is None:
        for win in group.windows:
            if active_window_hex_id == win.hex_id:
                window=win
                window_ref=window.ref
                break
    else:
        try:
            window=[w for w in group.windows if w.ref == window_ref][0]
        except IndexError:
            notify.error("At command execute for group name '{}' window '{}' not found.".format(group_name, window_ref))
            sys.exit(1)

    if window is None:
        win_ref=group.last_window_ref
        hex_id:str
        try:
            hex_id=[w.hex_id for w in group.windows if w.ref == win_ref][0]
        except IndexError:
            raise NotImplementedError()
        XlibHelpers().focus_window(hex_id=hex_id)
    else:
        group_win_hex_ids=get_group_win_hex_ids(group)
        for shortcut in shortcuts:
            cmds=[]
            try:
                cmds=[e.commands for e in window.execute if e.shortcut == shortcut][0]
            except IndexError:
                notify.error("At command execute for group name '{}' at window '{}' command '{}' not found".format(group_name, window_ref, shortcut))
                sys.exit(1)

            for cmd in cmds:
                for reg_txt in execute_regexes():
                    reg=re.match(reg_txt, cmd)
                    if reg:
                        dy_cmd=reg.groupdict()
                        if dy_cmd["cmd"] in ["click", "focus", "send-keys"]:
                            win_hex_id=get_window_hex_id(
                                group,
                                active_window_hex_id,
                                dy_cmd["value"],
                                group_win_hex_ids,
                            )
                            if win_hex_id is not None:
                                if dy_cmd["cmd"] == "focus":
                                    if win_hex_id != active_window_hex_id:
                                        Windows.get_window(hex_id=win_hex_id).focus()

                                elif dy_cmd["cmd"] == "send-keys":
                                    Keyboard(int(win_hex_id, 16)).key(dy_cmd["keys"])
                                elif dy_cmd["cmd"] == "click":
                                    Mouse(int(win_hex_id, 16)).click(int(dy_cmd["keys"]))
                        elif dy_cmd["cmd"] == "sleep":
                            time.sleep(float(dy_cmd["value"]))
                        break

        state.last_window_id=window.hex_id
        group.last_window_ref=window_ref