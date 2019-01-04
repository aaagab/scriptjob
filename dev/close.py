#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-beta-1546629922
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint
from modules.notification.notification import set_notification
import modules.message.message as msg
from modules.guitools.guitools import Window
from dev.actions import Actions
from dev.update_groups import update_groups
from dev.helpers import message
from modules.bwins.bwins import Check_box_list
from dev.custom_check_box_list import Custom_check_box_list

def close(scriptjob_conf, to_close_group_names=[]):

    data=scriptjob_conf.data

    existing_group_names=[group["name"] for group in data["groups"]]

    if not existing_group_names:
        message("warning", "There is no group to close")
        sys.exit(1)

    if to_close_group_names:
        to_close_group_names=set(to_close_group_names)
        for to_close_group_name in to_close_group_names:
            if not to_close_group_name in existing_group_names:
                message("warning", "There is no group with name '{}' to close".format(to_close_group_name))
                sys.exit(1)
    else:
        options=dict(
            items=existing_group_names,
            values=existing_group_names,
            prompt_text="Select Group(s) to close: ",
            title="Scriptjob Group Close",
            checked=[False] * len(existing_group_names)
        )
        groups_first_window_hex_ids=[group["windows"][0]["hex_id"] for group in data["groups"]]
        to_close_group_names=Custom_check_box_list(options, groups_first_window_hex_ids).loop().output

        if not isinstance(to_close_group_names, list):
            if to_close_group_names == "_aborted":
                message("warning", "Scriptjob close cancelled")
                sys.exit(1)
        
        if not to_close_group_names:
            message("warning", "Scriptjob close cancelled")
            sys.exit(1)

    obj_actions=Actions().obj_actions

    other_groups_windows=[]
    selected_group_windows=[]

    tmp_groups=[]
    for group in data["groups"]:
        if group["name"] not in to_close_group_names :
            tmp_groups.append(group)
        for window in group["windows"]:
            if group["name"] in to_close_group_names :
                selected_group_windows.append(window["hex_id"])
            else:
                other_groups_windows.append(window["hex_id"])
            for a, action in enumerate(window["actions"]):
                index_action=[act.name for act in obj_actions].index(action["name"])
                current_action=obj_actions[index_action]
                for p, parameter in enumerate(action["parameters"]):
                    if current_action.parameters[p]["type"] == "window_hex_id":
                        if group["name"] in to_close_group_names :
                            selected_group_windows.append(parameter)
                        else:
                            other_groups_windows.append(parameter)

    windows_hex_id_to_close=set(selected_group_windows) - set(other_groups_windows)

    for hex_id in windows_hex_id_to_close:
        Window(hex_id).close()

    data["groups"]=tmp_groups

    update_groups(scriptjob_conf)
    
    message("success", "Scriptjob group(s) ['{}'] closed.".format("', '".join(to_close_group_names)))
