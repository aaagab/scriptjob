#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from .custom_windows import WindowsList
from . import notify

from .session import State

from ..gpkgs.guitools import XlibHelpers
from ..gpkgs.bwins import Monitors, RadioButtonListOptions, RadioButtonItem

def switch_group(
    state:State,
    active_window_hex_id:str,
    direction:str,
    group_name:str|None=None,
):
    dy_timestamps:dict[float,str]=dict()
    for group in state.groups:
        dy_timestamps[group.timestamp]=group.name

    items:list[RadioButtonItem]=[]
    group_names:list[str]=[]
    for timestamp in sorted(dy_timestamps):
        name=dy_timestamps[timestamp]
        items.append(RadioButtonItem(label=name))
        group_names.append(name)

    if len(items) == 0:
        notify.warning("There is no group to select.")
        sys.exit(1)

    selected_name=None
    if group_name is None:
        if direction is None:
            groups_last_win_hex_ids:list[str]=[]
            for item in items:
                group=[g for g in state.groups if g.name == item.label][0]
                win_ref=group.last_window_ref
                groups_last_win_hex_ids.append([w for w in group.windows if w.ref == win_ref][0].hex_id)

            window_list=WindowsList(
                RadioButtonListOptions(
                    monitor=Monitors().get_primary_monitor(),
                    items=items, 
                    prompt_text="Select a Group:", 
                    checked=[i.label for i in items].index(state.active_group),
                    title="ScriptJob",
                ),
                windows_hex_ids=groups_last_win_hex_ids,
            )
                
            output=window_list.loop().output
            if output is None:
                notify.warning("switch_group canceled.")
                sys.exit(1)
            else:
                selected_name=group_names[output.index]
        else:
            if len(group_names) == 1:
                selected_name=group_name
            else:
                group_name=state.active_group
                if group_name is None:
                    raise NotImplementedError()
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
            notify.error("Group '{}' does not exist in {}.".format(group_name, sorted(group_names)))
            sys.exit(1)

    group=[g for g in state.groups if g.name == selected_name][0]
    dy_timestamp:dict[float, str]=dict()
    last_win_ref=group.last_window_ref
    last_hex_id:str|None=None
    for window in group.windows:
        if window.ref == last_win_ref:
            last_hex_id=window.hex_id
        else:
            dy_timestamp[window.timestamp]=window.hex_id


    xlib=XlibHelpers()
    for timestamp in sorted(dy_timestamp):
        xlib.focus_window(hex_id=dy_timestamp[timestamp])

    if last_hex_id is None:
        raise NotImplementedError()
    xlib.focus_window(hex_id=last_hex_id)
    state.active_group=selected_name
    state.last_window_id=active_window_hex_id
