#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-beta-1547130928
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint
import time

from tkinter import *

from modules.bwins.bwins import Input_box, Radio_button_list
from modules.guitools.guitools import Monitors, Windows, Regular_windows
from modules.json_config.json_config import Json_config
from dev.windows_list import Windows_list
from dev.set_previous import set_previous
from dev.actions import *
from dev.helpers import generate_group_name, message
import copy

def get_selected_windows(discarded_windows):
    selected_windows=[]
    all_windows=Regular_windows().windows
    for window in all_windows:
        if not window["hex_id"] in [discarded_window["hex_id"] for discarded_window in discarded_windows]:
            selected_windows.append(window)

    return selected_windows

def add_group(scriptjob_conf):
    data=scriptjob_conf.data
    start_hex_id=Windows.get_active_hex_id()
    obj_monitor=Monitors().get_active()

    input_box=Input_box(dict(monitor=obj_monitor, title=Json_config().data["app_name"], prompt_text="Input Group Name: ", default_text=generate_group_name("scriptjob", scriptjob_conf)))
    group_name=generate_group_name(input_box.loop().output, scriptjob_conf)
    
    if group_name == "_aborted":
        message("warning", "Scriptjob 'add' cancelled", obj_monitor)
        sys.exit(1)

    obj_group=dict(name=group_name)


    discarded_windows=[]
    actions=Actions()

    while True:
        selected_windows=get_selected_windows(discarded_windows)
        selected_windows_hex_ids=[window["hex_id"] for window in selected_windows]

        windows_names=["{}: {}".format(window["exe_name"],window["name"])[:50] for window in selected_windows]
    
        if not windows_names:
            if obj_group["windows"]:            
                message("warning", "There is no more windows to process", obj_monitor)
            else:
                message("warning", "There is no windows to process", obj_monitor)
            break
    
        win_index=Windows_list(dict(
            items=windows_names, 
            prompt_text="Choose a window:", 
            monitor=obj_monitor, 
            checked=len(windows_names)-1, 
            title="Group: {}".format(group_name)), selected_windows_hex_ids).loop().output

        if win_index == "_aborted":
            message("warning", "Scriptjob 'add' cancelled", obj_monitor)
            sys.exit(1)

        if win_index == "_done":
            break
            
        selected_window=selected_windows[win_index]

        if not "windows" in obj_group:
            obj_group["windows"]=[]
        
        obj_group["windows"].append(dict(
            hex_id=selected_window["hex_id"],
            actions=[]
        ))

        discarded_windows.append(selected_windows[win_index])
        del selected_windows[win_index]

        arr_actions=[]

        action_selected=False
        while True:
            action_labels=[obj_action.label for obj_action in actions.obj_actions]
            no_action="No action"
            if action_selected:
                no_action="No more actions"
            action_labels.append(no_action)
            action_list=Windows_list(dict(
                items=action_labels,
                checked=0, 
                monitor=obj_monitor, 
                prompt_text="Add an action for window '{}':".format(selected_window["name"]), 
                title="Group: {}".format(group_name)
                ))
            
            action_list.btn_cancel.configure(text="Go Back")
            action_list.btn_done.pack_forget()
            action_list.focus_buttons.remove(action_list.btn_done)
            action_index=action_list.loop().output

            if action_index == "_aborted":
                if not action_selected:
                    del discarded_windows[-1]
                    del obj_group["windows"][-1]
                break

            if action_index == action_labels.index(no_action):
                break

            selected_obj_action=actions.obj_actions[action_index]

            parameters=actions.implement(selected_obj_action, obj_monitor, group_name, selected_window["hex_id"])
            if parameters is None:
                continue
            
            dict_action=dict(
                name=selected_obj_action.name,
                parameters=parameters
            )

            arr_actions.append(dict_action)
            action_selected=True

        if action_selected:
            obj_group["windows"][-1].update(
                actions=arr_actions
            )
           
    if "windows" in obj_group:
        if obj_group["windows"]:
            group_names=[group["name"] for group in data["groups"]]
            if group_names:
                set_previous(scriptjob_conf, "active_group", start_hex_id)

            Regular_windows.focus(obj_group["windows"][0]["hex_id"])
            obj_group["previous_window"]=obj_group["windows"][0]["hex_id"]

            data["groups"].append(obj_group)
            data["active_group"]=group_name
            # scriptjob_conf.set_file_with_data(data)

            set_previous(scriptjob_conf, "global", start_hex_id)
            message("success", "scriptjob group '{}' added.".format(group_name), obj_monitor)

            # scriptjob_conf.set_file_with_data(data)
