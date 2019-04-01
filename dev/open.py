#!/usr/bin/env python3
# author: Gabriel Auger
# version: 2.0.0
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint
import re
import subprocess
import shlex
import time
import copy
import tempfile
import getpass

from modules.guitools.guitools import Window, Windows, Regular_windows, Monitors, Window_open
from modules.bwins.bwins import Prompt_boolean
from modules.json_config.json_config import Json_config
from modules.timeout.timeout import Timeout
from dev.windows_list import Windows_list
import dev.app_parameters as app_params
from dev.helpers import message, generate_group_name
from dev.set_previous import set_previous

def has_prop(prop, obj):
    if prop in obj and obj[prop]:
        return True
    else:
        return False

def open_json(dy_app, scriptjob_conf, filenpa_save_json="", group_names=[]):
    if not filenpa_save_json:
        direpa_current=os.getcwd()
        filen_scriptjob_json=dy_app["filen_scriptjob_json"]
        name, ext=os.path.splitext(filen_scriptjob_json)
        filen_save_json="{}_save{}".format(name, ext)
        filenpa_save_json=os.path.join(direpa_current, filen_save_json)
    
    obj_monitor=Monitors().get_active()


    if not os.path.exists(filenpa_save_json):
        message("error", "open: '{}' not found.".format(filenpa_save_json), obj_monitor)
        sys.exit(1)

    filenpa_save_json=os.path.abspath(filenpa_save_json)
    open_conf=Json_config(filenpa_save_json)
    data_open=open_conf.data
    start_hex_id=Windows.get_active_hex_id()

    if not has_prop("windows", data_open):
        message("error", "open: no windows in '{}'.".format(filenpa_save_json), obj_monitor)
        sys.exit(1)

    if not has_prop("groups", data_open):
        message("error", "open: no groups in '{}'.".format(filenpa_save_json), obj_monitor)
        sys.exit(1)

    in_file_group_names=[group["name"] for group in data_open["groups"]]

    if not in_file_group_names:
        message("error", "There is no group to open", obj_monitor)
        sys.exit(1)

    if group_names:
        tmp_groups=[]
        tmp_windows_ids=[]
        group_names=set(group_names)
        for group_name in group_names:
            if not group_name in in_file_group_names:
                message("error", "There is no group with name '{}' to open".format(group_name), obj_monitor)
                sys.exit(1)

        for group in data_open["groups"]:
            if group["name"] in group_names:
                tmp_groups.append(group)
                for window in group["windows"]:
                    tmp_windows_ids.append(window["id"])
                    for action in window["actions"]:
                        for parameter in action["parameters"]:
                            param_win_id=re.match(r"^win_id:(.*)$", parameter)
                            if param_win_id:
                                if param_win_id.group(1) not in tmp_windows_ids:
                                    tmp_windows_ids.append(param_win_id.group(1))

        tmp_windows=[]
        for window in data_open["windows"]:
            if window["id"] in tmp_windows_ids:
                tmp_windows.append(window)

        data_open["groups"]=tmp_groups
        data_open["windows"]=tmp_windows

    shared_windows_hex_ids=[]
    existing_windows=Regular_windows()

    for window in data_open["windows"]:
        has_selected_shared_window=False
        
        existing_related_windows=copy.deepcopy([win for win in existing_windows.windows if win["exe_name"] == window["exe"]])
        related_app_data=[exe for exe in dy_app["exes"] if exe["name"] == window["exe"]]
        related_app_data=related_app_data[0] if related_app_data else {}

        if has_prop("shared", related_app_data):
            for hex_id in shared_windows_hex_ids:
                existing_hex_ids=[win for win in existing_related_windows]
                if hex_id in existing_hex_ids:
                    del existing_related_windows[existing_hex_ids.index(hex_id)]

            if existing_related_windows:
                existing_related_windows_names=["{}: {}".format(w["exe_name"],w["name"])[:50] for w in existing_related_windows]

                no_action="None - Create a New Window"
                existing_related_windows_names.append(no_action)

                existing_related_windows_hex_ids=[win["hex_id"] for win in existing_related_windows]
                win_list=Windows_list(dict(
                    items=existing_related_windows_names, 
                    prompt_text="Choose a shared window for '{}' and group(s) '{}'".format(
                        window["exe"],
                        ", ".join(window["groups"])+"':"
                        ), 
                    monitor=obj_monitor, 
                    checked=len(existing_related_windows_names)-1, 
                    title="Scriptjob Open"), existing_related_windows_hex_ids)

                win_list.btn_done.pack_forget()
                win_list.focus_buttons.remove(win_list.btn_done)
                win_index=win_list.loop().output

                if win_index == "_aborted":
                    message("warning", "Scriptjob 'open' cancelled", obj_monitor)
                    sys.exit(1)

                if win_index != len(existing_related_windows_names)-1:
                    has_selected_shared_window=True
                    selected_hex_id=existing_related_windows[win_index]["hex_id"]
                    shared_windows_hex_ids.append(selected_hex_id)
                    window["hex_id"]=selected_hex_id
                    set_commands(window, True, related_app_data)
                    continue
                else:
                    # create a new window
                    pass

        if not has_selected_shared_window:
            window["hex_id"]="create"
            set_commands(window, False, related_app_data)

    windows_hex_ids=launch_windows(data_open["windows"], obj_monitor)
    insert_scriptjob_groups_data(windows_hex_ids, data_open, scriptjob_conf, start_hex_id, obj_monitor, filenpa_save_json)

def get_window_index(data_open, win_id):
    for w, window in enumerate(data_open["windows"]):
        if window["id"] == win_id:
            return w

def insert_scriptjob_groups_data(windows_hex_ids, data_open, scriptjob_conf, start_hex_id, obj_monitor, filenpa_save_json):
    scriptjob_data=scriptjob_conf.data
    for group in data_open["groups"]:
        group["name"]=generate_group_name(group["name"], scriptjob_conf)
        group["direpa_save_json"]=os.path.dirname(filenpa_save_json)
        for window in group["windows"]:
            window_index=get_window_index(data_open, window["id"])
            window["hex_id"]=windows_hex_ids[window_index]
            del window["id"]
            for action in window["actions"]:
                for p, parameter in enumerate(action["parameters"]):
                    param_win_id=re.match(r"^win_id:(.*)$", parameter)
                    if param_win_id:
                        window_index=get_window_index(data_open, param_win_id.group(1))
                        parameter=windows_hex_ids[window_index]
                        action["parameters"][p]=windows_hex_ids[window_index]
        scriptjob_data["groups"].append(group)

    if has_prop("active_group", data_open):
        scriptjob_data["active_group"]=data_open["active_group"]
    else:
        scriptjob_data["active_group"]=data_open["groups"][0]["name"]

    # scriptjob_conf.set_file_with_data()

    active_group=[group for group in scriptjob_data["groups"] if group["name"] == scriptjob_data["active_group"]][0]
    Window(active_group["windows"][0]["hex_id"]).focus()
    
    set_previous(scriptjob_conf, "active_group", active_group["windows"][0]["hex_id"])
    set_previous(scriptjob_conf, "global", start_hex_id)

    # scriptjob_conf.set_file_with_data()

    message(
        "success", 
        "Scriptjob group(s) ['{}'] opened.".format("', '".join([group["name"] for group in data_open["groups"]])
        ),
        obj_monitor)
    
def set_commands(window, shared_window, related_app_data):
    window["open_cmd"]=window["filenpa_exe"]
    window["cmds_after_open"]=[]

    if has_prop("title", related_app_data):
        if has_prop("title", window):
            title=related_app_data["title"].format(TITLE=window["title"])
        else:
            title=app_params.get_title(window)

        if title != "":
            window["open_cmd"]+=" "+related_app_data["title"].format(TITLE=title)
    
    if has_prop("paths", window):
        for p, path in enumerate(window["paths"]):
            if p == 0:
                if has_prop("new_window", related_app_data):
                    window["open_cmd"]+= " "+related_app_data["new_window"].format(PATH=path)
                else:
                    window["open_cmd"]+= " '"+path+"'"
            else:
                if has_prop("new_tab", related_app_data):
                    if related_app_data["new_tab"] == "app_parameters":
                        window["cmds_after_open"].append("app_parameters")
                        break
                    else:
                        window["cmds_after_open"].append(
                            window["filenpa_exe"]+" "+related_app_data["new_tab"].format(PATH=path)
                        )
                else:
                    window["cmds_after_open"].append(window["filenpa_exe"]+" '"+path+"'")
    else:
        if has_prop("new_window", related_app_data):
            window["open_cmd"]+=" "+related_app_data["new_window"].replace(" '{PATH}'", "")

    if has_prop("exec_cmds", related_app_data):
        if has_prop("rcfile_cmds", window):
            window["open_cmd"]+=" "+related_app_data["exec_cmds"]

def launch_windows(windows_data, obj_monitor):
    windows_hex_ids=[]
    for window_data in windows_data:
        window=""
        if window_data["hex_id"] == "create":
            filenpa_tmp=""
            if has_prop("rcfile_cmds", window_data):
                fd, filenpa_tmp = tempfile.mkstemp()
                filenpa_bashrc=os.path.join(os.environ["HOME"], ".bashrc")
                with os.fdopen(fd, 'w') as f:
                    f.write("#!/bin/bash")
                    with open(filenpa_bashrc, "r") as content_bashrc:
                        f.write(content_bashrc.read())
                    for cmd in window_data["rcfile_cmds"]:
                        f.write(cmd)

                window_data["open_cmd"]=window_data["open_cmd"].format(PATH=filenpa_tmp)

            launch_window=Window_open(window_data["open_cmd"])
            while not launch_window.has_window():
                user_continue=Prompt_boolean(dict(monitor=obj_monitor, title="Scriptjob open", prompt_text="Can't open a window with cmd\n'{}'\nDo you want to retry?".format(window_data["open_cmd"]))).loop().output
                if not user_continue:
                    message("Scriptjob command 'open' aborted.", "error", obj_monitor)
                    sys.exit(1)
            
            window=launch_window.window
            if filenpa_tmp:
                os.remove(filenpa_tmp)

        else:
            window=Window(window_data["hex_id"])

        windows_hex_ids.append(window.hex_id)
    
        window.focus()
        for cmd in window_data["cmds_after_open"]:
            if cmd == "app_parameters":
                app_params.set_cmds_after_open(window_data, window)
            else:
                os.system(cmd)

        if window_data["hex_id"] == "create":
            monitors=Monitors().monitors
            if len(monitors) == 1:
                window_data["monitor"]=0
            else:
                if window_data["monitor"] > len(monitors)-1:
                    window_data["monitor"]=0

            window.tile(window_data["tile"], window_data["monitor"])

    return windows_hex_ids

