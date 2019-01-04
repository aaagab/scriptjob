#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-beta-1546629922
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint

from modules.notification.notification import set_notification
import modules.message.message as msg
from modules.guitools.guitools import Windows, Window, Regular_windows
from dev.actions import Actions

def get_window_name(existing_windows, hex_id):
    win_index=[w["hex_id"] for w in existing_windows].index(hex_id)
    win_name=[w["name"] for w in existing_windows][win_index]

    return win_name

def update_groups(scriptjob_conf):
    obj_actions=Actions().obj_actions
    existing_windows=Regular_windows().windows
    active_window_hex_id=Windows.get_active_hex_id()

    data=scriptjob_conf.data
    windows_hex_ids_to_remove=[]
    groups_indexes_to_remove=[]
    
    if not "active_group" in data:
        data["active_group"]=""

    if not "previous_window" in data:
        data["previous_window"]=""
       
    if not "groups" in data or not data["groups"]:
        if "active_group" in data:
            data["active_group"]=""

        if not "groups" in data:
            data["groups"]=[]
    else:
        tmp_groups=[]
        for group in data["groups"]:
            tmp_group={}
            for w, window in enumerate(group["windows"]):
                if window["hex_id"] in windows_hex_ids_to_remove:
                    continue
                elif not Windows.exists(window["hex_id"]):
                    windows_hex_ids_to_remove.append(window["hex_id"])
                    continue
                else:
                    
                    if not "name" in tmp_group:
                        tmp_group.update(
                            name=group["name"],
                            windows=[dict(
                                    hex_id=window["hex_id"],
                                    name=get_window_name(existing_windows, window["hex_id"]),
                                    actions=[]
                                )]
                        )

                    else:
                        tmp_group["windows"].append(dict(
                                    hex_id=window["hex_id"],
                                    name=get_window_name(existing_windows, window["hex_id"]),
                                    actions=[]
                                )
                            )

                actions_win_hex_ids=set()
                for a, action in enumerate(window["actions"]):
                    index_action=[act.name for act in obj_actions].index(action["name"])
                    current_action=obj_actions[index_action]
                    for p, parameter in enumerate(action["parameters"]):
                        if current_action.parameters[p]["type"] == "window_hex_id":
                            if parameter in windows_hex_ids_to_remove:
                                continue
                            elif not Windows.exists(parameter):
                                windows_hex_ids_to_remove.append(parameter)
                                continue
                            else:
                                actions_win_hex_ids.add(parameter)
                                if not tmp_group["windows"][-1]["actions"]:
                                    tmp_group["windows"][-1]["actions"].append(dict(
                                        name=action["name"],
                                        parameters=[parameter]
                                    ))
                                else:
                                    tmp_group["windows"][-1]["actions"][-1][parameters].append(parameter)

            if "windows" in tmp_group and tmp_group["windows"]:
                tmp_group_hex_ids=[win["hex_id"] for win in tmp_group["windows"]]
                if actions_win_hex_ids:
                    for action_win_hex_id in actions_win_hex_ids:
                        if action_win_hex_id not in tmp_group_hex_ids:
                            tmp_group["windows"].append(dict(
                                    hex_id=action_win_hex_id,
                                    name=get_window_name(existing_windows, action_win_hex_id),
                                    actions=[]
                                )
                            )

                if "previous_window" in tmp_group:
                    if not Windows.exists(tmp_group["previous_window"]):
                        tmp_group["previous_window"]=tmp_group["windows"][0]["hex_id"]
                else:
                    tmp_group["previous_window"]=tmp_group["windows"][0]["hex_id"]
                
                tmp_groups.append(tmp_group)
                
        data["groups"]=tmp_groups

        
    if data["groups"]:
        group_names=[group["name"] for group in data["groups"]]
        if data["active_group"]:
            if data["active_group"] not in group_names:
                data["active_group"]= data["groups"][-1]["name"]
        else:
            data["active_group"]= data["groups"][-1]["name"]
    else:
        data["active_group"]=""

    if data["previous_window"]:
        if not Windows.exists(data["previous_window"]):
            data["previous_window"]=active_window_hex_id
    else:
        data["previous_window"]=active_window_hex_id
    
    scriptjob_conf.set_file_with_data()
