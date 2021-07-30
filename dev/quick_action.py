#!/usr/bin/env python3
from pprint import pprint
import copy
import os
import sys
import time

from .set_previous import set_previous
from .helpers import generate_group_name, message
from .windows_list import Windows_list

from ..gpkgs.bwins import Input_box, Radio_button_list
from ..gpkgs.guitools import Monitors, Windows, Regular_windows, Window

def quick_action(
    app_name,
    actions,
    dy_state,
    action_name,
):
    if action_name not in ["terminal", "browser"]:
        message("error", "Unknown action '{}'".format(action_name), obj_monitor)
        sys.exit(1)
    else:
        obj_monitor=Monitors().get_active()
        start_hex_id=Windows.get_active_hex_id()
        
        input_box=Input_box(dict(monitor=obj_monitor, title=app_name, prompt_text="Input Group Name: ", default_text=generate_group_name(action_name, dy_state["groups"])))
        group_name=generate_group_name(input_box.loop().output, dy_state["groups"])

        if group_name == "_aborted":
            message("warning", "Scriptjob 'add' cancelled", obj_monitor)
            sys.exit(1)

        obj_group=dict(
            name=group_name,
            windows=[]
        )

        if action_name == "terminal":
            message("info", "Choose Editor Window", obj_monitor)
            hex_id_editor=Window().select().hex_id
            message("info", "Choose Terminal Window", obj_monitor)
            hex_id_terminal=Window().select().hex_id

            obj_group["windows"].append(
                get_group_window(obj_monitor, actions, group_name, "execute_terminal", hex_id_editor, [hex_id_terminal]))

            obj_group["windows"].append(
                get_group_window(obj_monitor, actions, group_name, "active_group_previous_window", hex_id_terminal, []))
        
        elif action_name == "browser":
            message("info", "Choose Editor Window", obj_monitor)
            hex_id_editor=Window().select().hex_id

            message("info", "Choose Browser Window", obj_monitor)
            hex_id_browser=Window().select().hex_id
        
            obj_group["windows"].append(
                get_group_window(obj_monitor, actions, group_name, "refresh_browser", hex_id_editor, [hex_id_browser]))

            obj_group["windows"].append(
                get_group_window(obj_monitor, actions, group_name, "active_group_previous_window", hex_id_browser, []))

        group_names=[group["name"] for group in dy_state["groups"]]
        if group_names:
            set_previous(dy_state, "active_group", start_hex_id)

        Regular_windows.focus(obj_group["windows"][0]["hex_id"])
        obj_group["previous_window"]=obj_group["windows"][0]["hex_id"]

        dy_state["groups"].append(obj_group)
        dy_state["active_group"]=group_name

        set_previous(dy_state, "global", start_hex_id)
        message("success", "scriptjob group '{}' added.".format(group_name), obj_monitor)

def get_group_window(obj_monitor, actions, group_name, action_name, main_hex_id, quick_params):
    index=[obj_action.name for obj_action in actions.obj_actions].index(action_name)
    selected_obj_action=actions.obj_actions[index]
    parameters=actions.implement(selected_obj_action, obj_monitor, group_name, main_hex_id, quick_params)
    return dict(
        hex_id=main_hex_id,
        actions=[dict(
            name=selected_obj_action.name,
            parameters=parameters
        )]
    )
