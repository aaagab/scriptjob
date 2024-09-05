#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from . import notify
from .session import State
from .custom_windows import WindowPrompt, CustomCheckBoxList, WindowPromptOptions

from ..gpkgs.guitools import XlibHelpers
from ..gpkgs.bwins import CheckBoxListOptions, Monitors, CheckBoxItem

def focus_group(
    state:State,
    active_window_hex_id:str,
    dy_existing_regular_windows:dict[str,str],
    desktop_win_hex_ids:list[str],
    command:str,
):
    xlib=XlibHelpers()
    wins=state.focus.windows
    if command != "add":
        if len(wins) == 0:
            notify.warning("Focus group has no windows. Add a window first with --focus-group --add.")
            sys.exit(1)

    if command in ["last", "next", "previous"]:
        last_window_id=state.focus.last_window_id
        if active_window_hex_id in wins:
            selected_id=None
            if command == "last":
                if active_window_hex_id != last_window_id:
                    selected_id=last_window_id
            elif command in ["next", "previous"]:
                win_index=wins.index(active_window_hex_id)
                if command == "next":
                    is_last=(win_index == len(wins) -1)
                    if is_last is True:
                        selected_id=wins[0]
                    else:
                        selected_id=wins[win_index+1]
                elif command == "previous":
                    is_first=(win_index == wins[0])
                    if is_first is True:
                        selected_id=wins[-1]
                    else:
                        selected_id=wins[win_index-1]
        else:
            selected_id=last_window_id

        if selected_id is not None:
            xlib.focus_window(hex_id=selected_id)
            if selected_id in wins:
                state.focus.last_window_id=selected_id
    elif command == "add":
        window=WindowPrompt(WindowPromptOptions(
            desktop_win_hex_ids=desktop_win_hex_ids,
            monitor=Monitors().get_primary_monitor(),
            prompt_text="Choose a window to add to focus group.",
        )).loop().output

        if window is None:
            notify.warning("--focus-group --add canceled.")
            sys.exit(1)

        if window.hex_id in wins:
            notify.warning("window '{}' is already part of focus group.".format(window.name))
            sys.exit(1)

        wins.append(window.hex_id)
        state.focus.last_window_id=window.hex_id
        notify.success("window '{}' selected.".format(window.name))
        
        window.focus()

    elif command == "delete":
        items:list[CheckBoxItem]=[]
        for hex_id in wins:
            items.append(CheckBoxItem(
                label=dy_existing_regular_windows[hex_id],
                value=hex_id,
                checked=False,
            ))

        options=CheckBoxListOptions(
            monitor=Monitors().get_primary_monitor(),
            items=items,
            prompt_text="Select window(s) to close: ",
            title="Scriptjob Focus group delete",
        )

        output=CustomCheckBoxList(options, wins).loop().output

        if output is None or len(output.indexes) == 0:
            notify.warning("Scriptjob close canceled.")
            sys.exit(1)

        groups_hex_ids:list[str]=[]
        for group in state.groups:
            for window in group.windows:
                if window.hex_id is not None:
                    groups_hex_ids.append(window.hex_id)

        for hex_id in output.values:
            if hex_id not in groups_hex_ids:
                xlib.close(hex_id=hex_id)
            wins.remove(hex_id)

        if state.focus.last_window_id is None:
            if len(wins) > 0:
                state.focus.last_window_id=wins[-1]
        else:
            if state.focus.last_window_id not in wins:
                if len(wins) > 0:
                    state.focus.last_window_id=wins[-1]
                else:
                    state.focus.last_window_id=None
    elif command == "toggle":
        focus_last_window_id=state.focus.last_window_id
        groups_last_window_id=state.last_window_id

        # if active window is last focus window id then
        #     I go to last window Id from dy_state.
        # else:
        #     I go to last focus window id
        #     if active window hex_id is not part of focus windows, then 
        #         it is set in dy_state.
        #         what about active group then when going to focus_window
        #         if active_window hex_id is part of active group:
        #             then active group last window_Ref is set with active_window ref

        if active_window_hex_id == focus_last_window_id:
            if groups_last_window_id is not None:
                xlib.focus_window(hex_id=groups_last_window_id)
        else:
            if focus_last_window_id is not None:
                xlib.focus_window(hex_id=focus_last_window_id)
            if active_window_hex_id not in state.focus.windows:
                state.last_window_id=active_window_hex_id
                group=[g for g in state.groups if g.name == state.active_group][0]
                dy_group_ids={ w.hex_id: w.ref for w in group.windows}
                if active_window_hex_id in dy_group_ids:
                    group.last_window_ref=dy_group_ids[active_window_hex_id]
