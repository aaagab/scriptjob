#!/usr/bin/env python3
from pprint import pprint
import copy
import os
import sys
import time

from . import notify
from .helpers import generate_group_name
from .set_previous import set_previous
from .windows_list import Windows_list

from ..gpkgs.bwins import Input_box, Radio_button_list
from ..gpkgs.guitools import Regular_windows

def get_selected_windows(discarded_windows):
    selected_windows=[]
    all_windows=Regular_windows().windows
    for window in all_windows:
        if not window["hex_id"] in [discarded_window["hex_id"] for discarded_window in discarded_windows]:
            selected_windows.append(window)

    return selected_windows

def add_group(
    app_name,
    actions,
    dy_state,
    active_monitor,
    active_window_hex_id,
):
    dy_state=dy_state

    input_box=Input_box(dict(monitor=active_monitor, title=app_name, prompt_text="Input Group Name: ", default_text=generate_group_name("scriptjob", dy_state["groups"])))
    group_name=generate_group_name(input_box.loop().output, dy_state["groups"])
    
    if group_name == "_aborted":
        notify.warning("Scriptjob 'add' cancelled", active_monitor)
        sys.exit(1)

    obj_group=dict(name=group_name)
    discarded_windows=[]

    while True:
        selected_windows=get_selected_windows(discarded_windows)
        selected_windows_hex_ids=[window["hex_id"] for window in selected_windows]

        windows_names=["{}: {}".format(window["exe_name"],window["name"])[:50] for window in selected_windows]
    
        if not windows_names:
            if obj_group["windows"]:            
                notify.warning("There is no more windows to process", active_monitor)
            else:
                notify.warning("There is no windows to process", active_monitor)
            break
    
        win_index=Windows_list(dict(
            items=windows_names, 
            prompt_text="Choose a window:", 
            monitor=active_monitor, 
            checked=len(windows_names)-1, 
            title="Group: {}".format(group_name)), selected_windows_hex_ids).loop().output

        if win_index == "_aborted":
            notify.warning("Scriptjob 'add' cancelled", active_monitor)
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
                monitor=active_monitor, 
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

            parameters=actions.implement(selected_obj_action, active_monitor, group_name, selected_window["hex_id"])
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
            group_names=[group["name"] for group in dy_state["groups"]]
            if group_names:
                set_previous(dy_state, "active_group", active_window_hex_id)

            Regular_windows.focus(obj_group["windows"][0]["hex_id"])
            obj_group["previous_window"]=obj_group["windows"][0]["hex_id"]

            dy_state["groups"].append(obj_group)
            dy_state["active_group"]=group_name

            set_previous(dy_state, "global", active_window_hex_id)
            notify.success("scriptjob group '{}' added.".format(group_name), active_monitor)

