#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from .helpers import message, generate_group_name
from .set_previous import set_previous

from ..gpkgs.guitools import Windows, Window, Regular_windows, Monitors

def execute(obj_actions, dy_state):

    group_names=[group["name"] for group in dy_state["groups"]]
    obj_monitor=Monitors().get_active()

    if not group_names:
        message("warning", "There is no group to select for execute", obj_monitor)
        sys.exit(1)

    active_group_index=group_names.index(dy_state["active_group"])
    active_group=dy_state["groups"][active_group_index]

    start_hex_id=Windows.get_active_hex_id()

    active_group_wins_hex_id=[window["hex_id"] for window in active_group["windows"]]
    if start_hex_id in active_group_wins_hex_id:
        for window in active_group["windows"]:
            if window["hex_id"] == start_hex_id:
                for action in window["actions"]:
                    action_index=[act.name for act in obj_actions].index(action["name"])
                    obj_action=obj_actions[action_index]
                    getattr(obj_action, obj_action.name)(*action["parameters"])
                break
    else:
        Regular_windows.focus(active_group["previous_window"])

    set_previous(dy_state, "active_group", start_hex_id)
    set_previous(dy_state, "global", start_hex_id)
    # scriptjob_conf.set_file_with_data()
