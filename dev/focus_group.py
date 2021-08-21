#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from . import notify
from .custom_windows import Window_Prompt, Custom_check_box_list

from ..gpkgs.guitools import Regular_windows

def focus_group(
    dy_state,
    active_monitor,
    active_window_hex_id,
    obj_monitors,
    dy_existing_regular_windows,
    dy_desktop_windows,
    command,
):
    wins=dy_state["focus"]["windows"]
    if command != "add":
        if len(wins) == 0:
            notify.warning("Focus group has no windows. Add a window first with --focus-group --add.", obj_monitor=active_monitor, exit=1)

    if command in ["last", "next", "previous"]:
        last_window_id=dy_state["focus"]["last_window_id"]
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
            Regular_windows().focus(selected_id)
            if selected_id in wins:
                dy_state["focus"]["last_window_id"]=selected_id
    elif command == "add":
        window=Window_Prompt(options=dict(
            desktop_win_hex_ids=sorted(dy_desktop_windows),
            monitor=active_monitor,
            obj_monitors=obj_monitors,
            prompt_text="Choose a window to add to focus group.",
        )).loop().output

        if window is "_aborted":
            notify.warning("--focus-group --add canceled.", obj_monitor=active_monitor, exit=1)

        if window.hex_id in wins:
            notify.warning("window '{}' is already part of focus group.".format(window.name), obj_monitor=active_monitor, exit=1)

        wins.append(window.hex_id)
        dy_state["focus"]["last_window_id"]=window.hex_id
        notify.success("window '{}' selected.".format(window.name), obj_monitor=active_monitor)
        
        window.focus()

    elif command == "delete":
        win_names=[]
        for hex_id in wins:
            win_names.append(dy_existing_regular_windows[hex_id])

        options=dict(
            monitor=active_monitor,
            items=win_names,
            values=wins,
            prompt_text="Select window(s) to close: ",
            title="Scriptjob Focus group delete",
            checked=[False] * len(wins),
        )

        output=Custom_check_box_list(options, wins).loop().output

        if output == "_aborted" or len(output) == 0:
            notify.warning("Scriptjob close canceled.", obj_monitor=active_monitor)
            sys.exit(1)

        groups_hex_ids=[]
        for name in dy_state["groups"]:
            dy_group=dy_state["groups"][name]
            for win_ref in dy_group["windows"]:
                groups_hex_ids.append(dy_group["windows"][win_ref]["hex_id"])

        for hex_id in output:
            if hex_id not in groups_hex_ids:
                Regular_windows.close(hex_id)
            wins.remove(hex_id)

        if dy_state["focus"]["last_window_id"] is None:
            if len(wins) > 0:
                dy_state["focus"]["last_window_id"]=wins[-1]
        else:
            if dy_state["focus"]["last_window_id"] not in wins:
                if len(wins) > 0:
                    dy_state["focus"]["last_window_id"]=wins[-1]
                else:
                    dy_state["focus"]["last_window_id"]=None
    elif command == "toggle":
        focus_last_window_id=dy_state["focus"]["last_window_id"]
        groups_last_window_id=dy_state["last_window_id"]

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
            Regular_windows().focus(groups_last_window_id)
        else:
            Regular_windows().focus(focus_last_window_id)
            if active_window_hex_id not in dy_state["focus"]["windows"]:
                dy_state["last_window_id"]=active_window_hex_id
                dy_group=dy_state["groups"][dy_state["active_group"]]
                dy_group_ids={ dy_group["windows"][ref]["hex_id"]: ref  for ref in dy_group["windows"] }
                if active_window_hex_id in dy_group_ids:
                    dy_group["last_window_ref"]=dy_group_ids[active_window_hex_id]

        #     # go back to last active_window            


        # focus_last_window_id=None
        # if dy_state["active_group"] is not None:
        #     # {key: value for (key, value) in iterable}
        #     dy_group=dy_state["groups"][dy_state["active_group"]]

        #     pprint(dy_group_ids)

        #     sys.exit()
        #     if active_window_hex_id in dy_group_ids:
        #         dy_group["last_window_ref"]=dy_group_ids[active_window_hex_id]
        #     else:
        #         pass
        # # else:
        #     # focus_last_window_id=dy_state["focus"]["last_window_id"]
        # # pprint(dy_state)
        # # sys.exit()
        # # if active_window_hex_id
        # groups_last_window_id=dy_state["last_window_id"]
        # if active_window_hex_id == focus_last_window_id:
        #     Regular_windows().focus(groups_last_window_id)
        # elif active_window_hex_id == groups_last_window_id:
        #     Regular_windows().focus(focus_last_window_id)
        # else:        
        #     Regular_windows().focus(focus_last_window_id)
