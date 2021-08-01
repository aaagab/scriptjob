#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys
import time

from . import notify
from .windows_list import Windows_list

from ..gpkgs.guitools import Regular_windows, Keyboard

class Action(object):
    def __init__(self, 
        name, 
        label, 
        parameters,
    ):
        self.name=name
        self.label=label
        self.parameters=parameters

    def print(self):
        pprint(vars(self))

    def execute_terminal(self, src_hex_id, dst_hex_id):
        src_kbd=Keyboard(int(src_hex_id, 16))
        src_kbd.key("Ctrl+s")
        time.sleep(.05)
        Regular_windows.focus(dst_hex_id)
        dst_kbd=Keyboard(int(dst_hex_id, 16))
        dst_kbd.key("Up")
        time.sleep(.05)
        dst_kbd.key("Return")

    def active_group_previous_window(self, window_hex_id):
        Regular_windows.focus(window_hex_id)

    def refresh_browser(self, src_hex_id, dst_hex_id):
        src_kbd=Keyboard(int(src_hex_id, 16))
        src_kbd.key("Ctrl+s")
        Regular_windows.focus(dst_hex_id)
        time.sleep(.01)
        dst_kbd=Keyboard(int(dst_hex_id, 16))
        dst_kbd.key("F5")

class Actions(object):
    def __init__(self,
        dy_actions,
    ):
        self.dy_actions=dy_actions
        self.obj_actions=[]
        self.set_actions()
        self.monitor=""

    def set_actions(self):
        for dy_action in self.dy_actions:
            name=dy_action["name"]
            label=dy_action["label"]
            parameters=dy_action["parameters"]
            self.obj_actions.append(Action(name, label, parameters))

    def implement(self, obj_action, obj_monitor, group_name, selected_window_hex_id, quick_params=[]):

        parameters=[]

        for parameter in obj_action.parameters:
            win_index=""
            parameter_windows=self.get_parameter_windows(parameter, obj_monitor)
            parameter_windows_hex_ids=[window["hex_id"] for window in parameter_windows]

            if parameter_windows:
                windows_names=["{}: {}".format(window["exe_name"],window["name"])[:50] for window in parameter_windows]

                if parameter["type"] == "window_hex_id":
                    if quick_params:
                        win_hex_id=quick_params.pop(0)
                        parameters.append(win_hex_id)
                    else:
                        while win_index == "":
                            win_list=Windows_list(dict(
                                items=windows_names, 
                                prompt_text="Action: '{}'\n{}".format(obj_action.label, parameter["prompt"]), 
                                monitor=obj_monitor, 
                                title="Group: {}".format(group_name)), parameter_windows_hex_ids)

                            win_list.btn_cancel.configure(text="Go Back")
                            win_list.btn_done.pack_forget()
                            win_list.focus_buttons.remove(win_list.btn_done)
                            win_index=win_list.loop().output

                            if win_index == "_aborted":
                                return None

                        parameters.append(parameter_windows[win_index]["hex_id"])
                elif parameter["type"] == "active_window":
                    parameters.append(selected_window_hex_id)
                elif parameter["type"] == "previous_window_hex_id":
                    parameters.append("")

        return parameters

    def get_parameter_windows(self, parameter, obj_monitor):
        all_windows=Regular_windows().windows
        parameter_windows=[]
        exe_name_found=False
        if "exe_names" in parameter:
                if parameter["exe_names"]:
                    exe_name_found=True

        for window in all_windows:
            if exe_name_found:
                if window["exe_name"] in parameter["exe_names"]:
                    parameter_windows.append(window)
            else:
                parameter_windows.append(window)

        if not parameter_windows:
            msg_error="In actions, implement, filter_windows: there is no parameter_windows with exe_name '{}'".format(parameter["exe_names"])
            notify.warning(msg_error, obj_monitor)
            parameter_windows=None

        return parameter_windows
