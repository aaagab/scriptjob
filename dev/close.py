#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from .custom_check_box_list import Custom_check_box_list
from .helpers import message
from .update_groups import update_groups

from ..gpkgs.guitools import Window, Monitors
from ..gpkgs.bwins import Check_box_list

def close(
    default_applications,
    dy_state,
    actions,
    to_close_group_names=[],
):
    obj_monitor=Monitors().get_active()
    existing_group_names=[group["name"] for group in dy_state["groups"]]

    if to_close_group_names:
        if to_close_group_names[0] == "all" and "all" not in existing_group_names:
            for cmd_alias in dy_state["focus"]:
                if dy_state["focus"][cmd_alias]:
                    Window(dy_state["focus"][cmd_alias]).close()

    if not existing_group_names:
        message("warning", "There is no group to close", obj_monitor)
        sys.exit(1)

    if to_close_group_names:
        if to_close_group_names[0] == "all" and "all" not in existing_group_names:
            to_close_group_names=existing_group_names
        else:
            to_close_group_names=set(to_close_group_names)
            for to_close_group_name in to_close_group_names:
                if not to_close_group_name in existing_group_names:
                    message("warning", "There is no group with name '{}' to close".format(to_close_group_name), obj_monitor)
                    sys.exit(1)
    else:
        options=dict(
            monitor=obj_monitor,
            items=existing_group_names,
            values=existing_group_names,
            prompt_text="Select Group(s) to close: ",
            title="Scriptjob Group Close",
            checked=[False] * len(existing_group_names)
        )
        groups_first_window_hex_ids=[group["windows"][0]["hex_id"] for group in dy_state["groups"]]
        to_close_group_names=Custom_check_box_list(options, groups_first_window_hex_ids).loop().output

        if not isinstance(to_close_group_names, list):
            if to_close_group_names == "_aborted":
                message("warning", "Scriptjob close cancelled", obj_monitor)
                sys.exit(1)
        
        if not to_close_group_names:
            message("warning", "Scriptjob close cancelled", obj_monitor)
            sys.exit(1)

    other_groups_windows=[]
    selected_group_windows=[]

    tmp_groups=[]
    for group in dy_state["groups"]:
        if group["name"] not in to_close_group_names :
            tmp_groups.append(group)
        for window in group["windows"]:
            if group["name"] in to_close_group_names :
                selected_group_windows.append(window["hex_id"])
            else:
                other_groups_windows.append(window["hex_id"])
            for a, action in enumerate(window["actions"]):
                index_action=[act.name for act in actions.obj_actions].index(action["name"])
                current_action=actions.obj_actions[index_action]
                for p, parameter in enumerate(action["parameters"]):
                    if current_action.parameters[p]["type"] == "window_hex_id":
                        if group["name"] in to_close_group_names :
                            selected_group_windows.append(parameter)
                        else:
                            other_groups_windows.append(parameter)

    windows_hex_id_to_close=set(selected_group_windows) - set(other_groups_windows)

    for hex_id in windows_hex_id_to_close:
        focus_hex_ids=[dy_state["focus"][cmd_alias] for cmd_alias in dy_state["focus"]]
        if focus_hex_ids:
            if hex_id not in focus_hex_ids:
                Window(hex_id).close()
        else:
            Window(hex_id).close()

    dy_state["groups"]=tmp_groups

    update_groups(default_applications, dy_state, actions)
    
    message("success", "Scriptjob group(s) ['{}'] closed.".format("', '".join(to_close_group_names)), obj_monitor)
