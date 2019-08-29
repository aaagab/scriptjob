#!/usr/bin/env python3
from pprint import pprint
from dev.windows_list import Windows_list
from modules.json_config.json_config import Json_config
from modules.notification.notification import set_notification
from modules.guitools.guitools import Regular_windows
import modules.message.message as msg
import sys, os

class Action(object):
    def __init__(self, name):
        self.name=name
        self.label=""

    def print(self):
        pprint(vars(self))

class Actions(object):
    def __init__(self, dy_app):
        self.direpa_actions=dy_app["direpa_actions"]
        self.filenpa_actions_json=os.path.join(self.direpa_actions, dy_app["filen_actions_json"])
        self.actions_data=Json_config(self.filenpa_actions_json).data
        self.obj_actions=[]
        self.set_actions()
        self.monitor=""

    def set_action(self, name, filenpa_action):
        action_index=[action["name"] for action in self.actions_data["actions"]].index(name)
        dict_action=self.actions_data["actions"][action_index]
        action=Action(name)
        action.label=dict_action["label"]
        action.filenpa=filenpa_action
        action.parameters=dict_action["parameters"]
        self.obj_actions.append(action)

    def set_actions(self):
        for elem in os.listdir(self.direpa_actions):
            path_elem=os.path.join(self.direpa_actions, elem)
            if os.path.isfile(path_elem):
                if path_elem != self.filenpa_actions_json:
                    self.set_action(elem, path_elem)

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
            set_notification(msg_error, "warning", obj_monitor)
            msg.warning(msg_error)
            parameter_windows=None

        return parameter_windows
