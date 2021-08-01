#!/usr/bin/env python3

from pprint import pprint
import json
import os
import sys

from ..gpkgs.guitools import Windows, Regular_windows

def get_window_name(existing_windows, hex_id):
    win_index=[w["hex_id"] for w in existing_windows].index(hex_id)
    win_name=[w["name"] for w in existing_windows][win_index]

    return win_name

def update_groups(
    active_window_hex_id,
    default_applications,
    dy_state,
    actions,
):
    existing_windows=Regular_windows().windows
    windows_hex_ids_to_remove=[]
    groups_indexes_to_remove=[]
    
    if not "active_group" in dy_state:
        dy_state["active_group"]=""

    if not "previous_window" in dy_state:
        dy_state["previous_window"]=""

    if not "focus" in dy_state:
        dy_state["focus"]={}

    for cmd_alias in default_applications:
        if not cmd_alias in dy_state["focus"]:
            dy_state["focus"][cmd_alias]=""

        if dy_state["focus"][cmd_alias]:
            if not Windows.exists(dy_state["focus"][cmd_alias]):
                dy_state["focus"][cmd_alias]=""
        
    if not "groups" in dy_state or not dy_state["groups"]:
        if "active_group" in dy_state:
            dy_state["active_group"]=""

        if not "groups" in dy_state:
            dy_state["groups"]=[]
    else:
        tmp_groups=[]
        for group in dy_state["groups"]:
            tmp_group={}
            for w, window in enumerate(group["windows"]):
                if window["hex_id"] in windows_hex_ids_to_remove:
                    continue
                elif not Windows.exists(window["hex_id"]):
                    windows_hex_ids_to_remove.append(window["hex_id"])
                    continue
                else:
                    if not "name" in tmp_group:
                        previous_window=""
                        if "previous_window" in group:
                            if Windows.exists(group["previous_window"]):
                                previous_window=group["previous_window"]
                            else:
                                previous_window=group["windows"][0]["hex_id"]
                        else:
                            previous_window=group["windows"][0]["hex_id"]

                        direpa_save_json=""
                        if "direpa_save_json" in group:
                            direpa_save_json=group["direpa_save_json"]

                        tmp_group.update(
                            name=group["name"],
                            previous_window=previous_window,
                            direpa_save_json=direpa_save_json,
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
                    index_action=[act.name for act in actions.obj_actions].index(action["name"])
                    current_action=actions.obj_actions[index_action]
                    tmp_group["windows"][-1]["actions"].append(dict(
                        name=action["name"],
                        parameters=[]
                    ))
                    for p, parameter in enumerate(action["parameters"]):
                        if current_action.parameters[p]["type"] in ["window_hex_id", "active_window"]:
                            if parameter in windows_hex_ids_to_remove:
                                continue
                            elif not Windows.exists(parameter):
                                windows_hex_ids_to_remove.append(parameter)
                                continue
                            else:
                                actions_win_hex_ids.add(parameter)
                                tmp_group["windows"][-1]["actions"][-1]["parameters"].append(parameter)
                        elif current_action.parameters[p]["type"] == "previous_window_hex_id":
                            tmp_group["windows"][-1]["actions"][-1]["parameters"].append(tmp_group["previous_window"])

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
                
                tmp_groups.append(tmp_group)
                
        dy_state["groups"]=tmp_groups

        
    if dy_state["groups"]:
        group_names=[group["name"] for group in dy_state["groups"]]
        if dy_state["active_group"]:
            if dy_state["active_group"] not in group_names:
                dy_state["active_group"]= dy_state["groups"][-1]["name"]
        else:
            dy_state["active_group"]= dy_state["groups"][-1]["name"]
    else:
        dy_state["active_group"]=""

    if dy_state["previous_window"]:
        if not Windows.exists(dy_state["previous_window"]):
            dy_state["previous_window"]=active_window_hex_id
    else:
        dy_state["previous_window"]=active_window_hex_id

    # with open(filenpa_scriptjob_json, "w") as f:
        # f.write(json.dumps(dy_state, sort_keys=True, indent=4))
