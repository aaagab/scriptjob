#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from . import notify
from .custom_windows import CustomCheckBoxList
from .session import State

from ..gpkgs.guitools import Windows, XlibHelpers
from ..gpkgs.bwins import CheckBoxListOptions, Monitors, CheckBoxItem

def close(
    state:State,
    to_close_group_names:list[str]|None=None,
    close_all:bool=False,
):
    if to_close_group_names is None:
        to_close_group_names=[]
    dy_timestamps:dict[float,str]=dict()
    for group in state.groups:
        dy_timestamps[group.timestamp]=group.name

    items:list[CheckBoxItem]=[]
    prompt_group_names:list[str]=[]
    existing_group_names:list[str]=[]
    for timestamp in sorted(dy_timestamps):
        name=dy_timestamps[timestamp]
        items.append(CheckBoxItem(label=name, value=name, checked=False))
        existing_group_names.append(name)

    if len(items) == 0:
        notify.warning("There is no group to select.")
        sys.exit(1)

    if len(to_close_group_names) == 0:
        if close_all is True:
            to_close_group_names=existing_group_names
        else:
            options=CheckBoxListOptions(
                monitor=Monitors().get_primary_monitor(),
                items=items,
                prompt_text="Select Group(s) to close: ",
                title="Scriptjob Group Close",
            )

            groups_last_win_hex_ids:list[str]=[]
            for name in existing_group_names:
                group=[g for g in state.groups if g.name == name][0]
                window=[w for w in group.windows if w.ref == group.last_window_ref][0]
                groups_last_win_hex_ids.append(window.hex_id)

            output=CustomCheckBoxList(options, groups_last_win_hex_ids).loop().output

            if output is None:
                notify.warning("Scriptjob close canceled.")
                sys.exit(1)

                
            to_close_group_names=[i for i in output.labels]
            if len(to_close_group_names) == 0:
                notify.warning("Scriptjob close canceled.")
                sys.exit(1)
    else:
        to_close_group_names=list(set(to_close_group_names))
        for to_close_group_name in to_close_group_names:
            if not to_close_group_name in existing_group_names:
                notify.warning("There is no group to close with name '{}'.".format(to_close_group_name))
                sys.exit(1)

    non_selected_group_names=set(existing_group_names) - set(to_close_group_names)

    to_keep_win_hex_ids=set()
    for name in non_selected_group_names:
        group=[g for g in state.groups if g.name == name][0]
        for window in group.windows:
            if window.hex_id is not None:
                to_keep_win_hex_ids.add(window.hex_id)

    for win_hex_id in state.focus.windows:
        to_keep_win_hex_ids.add(win_hex_id)

    for name in sorted([g.name for g in state.groups]):
        if name in to_close_group_names:
            group=[g for g in state.groups if g.name == name][0]
            for window in group.windows:
                if window.hex_id not in to_keep_win_hex_ids:
                    XlibHelpers().close(hex_id=window.hex_id)

            state.groups.remove(group)
            existing_group_names.remove(name)
            prompt_group_names.append(name)


    if len(existing_group_names) > 0:
        state.active_group=existing_group_names[-1]
    else:
        state.active_group=None
    
    notify.success("Scriptjob group(s) {} closed.".format(prompt_group_names))
