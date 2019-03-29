#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.3.0
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint
from dev.actions import Actions
from modules.guitools.guitools import Windows, Window, Regular_windows, Monitors
from modules.notification.notification import set_notification
from dev.helpers import message
from dev.set_previous import set_previous

def execute(dy_app, scriptjob_conf):
    data=scriptjob_conf.data

    group_names=[group["name"] for group in data["groups"]]
    obj_monitor=Monitors().get_active()

    if not group_names:
        message("warning", "There is no group to select for execute", obj_monitor)
        sys.exit(1)

    active_group_index=group_names.index(data["active_group"])
    active_group=data["groups"][active_group_index]

    obj_actions=Actions(dy_app).obj_actions
    start_hex_id=Windows.get_active_hex_id()


    active_group_wins_hex_id=[window["hex_id"] for window in active_group["windows"]]
    if start_hex_id in active_group_wins_hex_id:
        for window in active_group["windows"]:
            if window["hex_id"] == start_hex_id:
                for action in window["actions"]:
                    action_index=[act.name for act in obj_actions].index(action["name"])
                    obj_action=obj_actions[action_index]

                    if not os.access(obj_action.filenpa, os.X_OK):
                        os.chmod(obj_action.filenpa, 0o755)
                    
                    os.system("{} {}".format(
                        obj_action.filenpa,
                        " ".join(action["parameters"])))
                break
    else:
        Regular_windows.focus(active_group["previous_window"])

    set_previous(scriptjob_conf, "active_group", start_hex_id)
    set_previous(scriptjob_conf, "global", start_hex_id)
    # scriptjob_conf.set_file_with_data()
