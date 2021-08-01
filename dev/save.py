#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys
import configparser
import contextlib

from . import notify
from .custom_check_box_list import Custom_check_box_list

from ..gpkgs.guitools import Window, Windows, Regular_windows
from ..gpkgs.bwins import Prompt_boolean, Path_dialog, Input_box, Path_dialog

from tkinter.filedialog import askopenfilename, askdirectory

class Custom_path_dialog(Path_dialog):
    def __init__(self, options):
        Path_dialog.__init__(self, options)

    def browse(self, e):
        focused_btn=self.root.focus_get()
        focused_btn_value="_".join(str(focused_btn).split("_")[1:])

        if e.widget._name != "btn_browse" and focused_btn_value != self.state.get():
            focused_btn.invoke()

        state=self.state.get()

        if state in ["file_dialog", "folder_dialog"]:
            if state == "file_dialog":
                path=askopenfilename()
            elif state == "folder_dialog":
                path=askdirectory()
        
            if isinstance(path, tuple):
                if path:
                    self.paths.append(path)
            elif path != "":
                self.paths.append(path)

            if len(self.paths) == 1:
                self.validate()

            return "break"
        elif state == "none":
            self.paths.append("default")
            self.validate()

    def validate(self, e=None):
        if self.paths:
            self.output=self.paths
        else:
            if self.state.get() == "none":
                self.output=["default"]
            else:
                self.output=[]

        self.root.destroy()

def save(
    app_name,
    filen_scriptjob_json,
    dy_exes,
    dy_state,
    active_monitor,
    active_window_hex_id,
    obj_monitors,
    actions,
    dst_path=None,
    selected_group_names=[],
):
    direpa_current=os.getcwd()
        
    filen_scriptjob_json=filen_scriptjob_json
    filer_scriptjob_json, ext=os.path.splitext(filen_scriptjob_json)
    filen_save_json="{}_save{}".format(filer_scriptjob_json, ext)
    filenpa_save_json=""

    if dst_path:
        if os.path.exists(dst_path):
            if os.path.isdir(dst_path): # existing folder:
                filenpa_save_json=os.path.join(dst_path, filen_save_json)
            else:
                filenpa_save_json=dst_path
        else:
            direpa_dst=os.path.dirname(dst_path)
            if not os.path.exists(direpa_dst):
                notify.error("dst_path folder '{}' does not exist".format(direpa_dst), active_monitor)
                sys.exit(1)
            else:
                filenpa_save_json=dst_path
    else:
        filenpa_default=os.path.join(direpa_current, filen_save_json)
        path_dialog=Custom_path_dialog(dict(monitor=active_monitor, title="Scriptjob save", prompt_text="Select a path to save groups:"))
        path_dialog.rad_file_dialog.configure(text="Select existing file")
        path_dialog.rad_none.configure(justify="left", anchor="w", text="Current path with defaut name\n{}".format(filenpa_default))
        
        user_path=path_dialog.loop().output
        if not user_path:
            notify.warning("scriptjob 'save' cancelled", active_monitor)
            sys.exit(1)
        else:
            if user_path == "_aborted":
                notify.warning("scriptjob 'save' cancelled", active_monitor)
                sys.exit(1)

            path_user=user_path[0]
            if path_user == "default":
                filenpa_save_json=filenpa_default
            else:
                if os.path.isdir(path_user):
                    filen_user=Input_box(dict(monitor=active_monitor, title=app_name, prompt_text="Input save filename: ", default_text=filen_save_json)).loop().output
                    filenpa_save_json=os.path.join(path_user, filen_user)
                else:
                    filenpa_save_json=path_user

    filenpa_symlink=os.path.abspath(filenpa_save_json)
    filenpa_save_json=get_new_filenpa_save_json_if_symlink(filenpa_save_json)

    if os.path.isdir(filenpa_save_json):
        notify.error("save filename '{}' is a directory".format(filenpa_save_json), active_monitor)
        sys.exit(1)
    else:
        if os.path.exists(filenpa_save_json):
            user_choice=Prompt_boolean(dict(monitor=active_monitor, title="Scriptjob save", prompt_text="Do you want to overwrite '{}'?".format(filenpa_save_json), YN="n")).loop().output
            if user_choice == "_aborted" or user_choice is False:
                notify.warning("scriptjob 'save' cancelled", active_monitor)
                sys.exit(1)

    with open(filenpa_save_json, "w") as f:
        f.write("{}")
    

    if filenpa_symlink != filenpa_save_json:
        with contextlib.suppress(FileNotFoundError):
            os.remove(filenpa_symlink)

        os.symlink(
            filenpa_save_json,
            filenpa_symlink
        )

    dict_groups=[]

    group_names=[group["name"] for group in dy_state["groups"]]
    groups_first_window_hex_ids=[group["windows"][0]["hex_id"] for group in dy_state["groups"]]

    if not group_names:
        notify.warning("There is no group to save", active_monitor)
        sys.exit(1)

    if not selected_group_names:
        options=dict(
            monitor=active_monitor,
            items=group_names,
            values=group_names,
            prompt_text="Select Group(s) to save: ",
            title="Scriptjob save",
            checked=[True] * len(group_names)
        )
        selected_group_names=Custom_check_box_list(options, groups_first_window_hex_ids).loop().output

        if not isinstance(selected_group_names, list):
            if selected_group_names == "_aborted":
                notify.warning("Scriptjob save cancelled", active_monitor)
                sys.exit(1)
        
        if not selected_group_names:
            notify.warning("Scriptjob save cancelled", active_monitor)
            sys.exit(1)

    for group_name in selected_group_names:
        if not group_name in group_names:
            notify.warning("There is no group with name '{}' to save".format(group_name), active_monitor)
            sys.exit(1)
        
        selected_group_index=group_names.index(group_name)
        dict_groups.append(dy_state["groups"][selected_group_index])

    dy_conf=dict()

    dy_conf["groups"]=[]
    dy_conf["windows"]=[]
    dy_conf["diren"]=os.path.basename(direpa_current)

    obj_windows=[]
    found_hex_ids=[]
    all_windows=Windows(obj_monitors=obj_monitors).sorted_by_class().filter_regular_type().windows
    all_windows_hex_ids=[window.hex_id for window in all_windows]

    for group in dict_groups:
        tmp_group={}
        tmp_group["name"]=group["name"]
        tmp_group["windows"]=[]
        for window in group["windows"]:
            win_id=""
            # if window not already found ( create it )
            if not window["hex_id"] in found_hex_ids:
                found_hex_ids.append(window["hex_id"])
                win_id=get_win_id(window["hex_id"], len(found_hex_ids)-1, obj_monitors)
                dy_conf["windows"].append(get_window_obj(window["hex_id"], win_id, group["name"], dy_exes, active_monitor, obj_monitors))
            else: # if window already found ( in actions or other group )
                win_id=get_win_id(window["hex_id"], found_hex_ids.index(window["hex_id"]), obj_monitors)
                # then add new group_name to this window
                already_found_window=[win for win in dy_conf["windows"]][found_hex_ids.index(window["hex_id"])]
                if group["name"] not in already_found_window["groups"]:
                    already_found_window["groups"].append(group["name"])

            tmp_group["windows"].append(dict(
                id=win_id,
                actions=[],
            ))

            for action in window["actions"]:
                selected_action_index=[act.name for act in actions.obj_actions].index(action["name"])
                selected_action=actions.obj_actions[selected_action_index]

                tmp_parameters=[]
                for p, parameter in enumerate(action["parameters"]):
                    if selected_action.parameters[p]["type"] in ["window_hex_id", "active_window"]:
                        if not parameter in found_hex_ids: # if window not already found
                            found_hex_ids.append(parameter)
                            win_id=get_win_id(parameter, len(found_hex_ids)-1, obj_monitors)
                            dy_conf["windows"].append(get_window_obj(parameter, win_id, group["name"], dy_exes, active_monitor, obj_monitors))
                            tmp_parameters.append("win_id:"+str(win_id))
                        else: # if window already found ( in actions or other group )
                            win_id=get_win_id(parameter, found_hex_ids.index(parameter), obj_monitors)
                            tmp_parameters.append("win_id:"+str(win_id))
                            already_found_window=[win for win in dy_conf["windows"]][found_hex_ids.index(parameter)]
                            if group["name"] not in already_found_window["groups"]:
                                already_found_window["groups"].append(group["name"])
                    elif selected_action.parameters[p]["type"] == "previous_window_hex_id":
                        tmp_parameters.append("previous_window_hex_id")
                    else:
                        tmp_parameters.append(parameter)

                tmp_group["windows"][-1]["actions"].append(dict(
                    name=action["name"],
                    parameters=tmp_parameters
                ))
                    
        dy_conf["groups"].append(tmp_group)

    with open(filenpa_save_json, "w") as f:
        f.write(json.dumps(dy_conf, sort_keys=True, indent=4 ))

    Regular_windows.focus(active_window_hex_id)
    notify.success("Scriptjob saved '[{}]' to '{}'".format(
        ", ".join(selected_group_names),
        filenpa_save_json
        ), active_monitor)

def get_new_filenpa_save_json_if_symlink(filenpa_save_json):
    direpa_save_json=os.path.abspath(os.path.dirname(filenpa_save_json))
    filen_save_json=os.path.basename(filenpa_save_json)
    direpa_src=os.path.join(direpa_save_json, "src")
    filenpa_git_config=os.path.join(direpa_src, ".git", "config")
    direpa_git_user=""
    if os.path.exists(filenpa_git_config):
        config=configparser.ConfigParser()
        config.read(filenpa_git_config)
        if "user" in config.sections():
            if "name" in [key for key in config["user"]]:
                git_user_name=config["user"]["name"]
                if git_user_name != "":
                    direpa_git_user=os.path.join(direpa_save_json, "mgt", git_user_name)

    if direpa_git_user != "":
        if os.path.exists(direpa_git_user):
            return os.path.join(direpa_git_user, filen_save_json)

    return filenpa_save_json

def get_win_id(hex_id, index, obj_monitors):
    return "{}_{}".format(
        Window(hex_id=hex_id, obj_monitors=obj_monitors).exe_name[0:2],
        index
    )

def get_paths(dy_exes, window, group_name, active_monitor):
    paths=[]
    for exe in dy_exes:
        if window.exe_name == exe["name"]:
            if "path_dialog" in exe and exe["path_dialog"] is True:
                prompt_text="Select path(s) for:\n'{}' with title '{}'".format(
                    window.exe_name,
                    window.name
                )
                paths=Path_dialog(dict(monitor=active_monitor, title=group_name, prompt_text=prompt_text)).loop().output
                if not isinstance(paths, list):
                    if paths == "_aborted":
                        notify.warning("Scriptjob save cancelled", active_monitor)
                        sys.exit(1)
    return paths

def get_window_obj(hex_id, win_id, group_name, dy_exes, active_monitor, obj_monitors):
    window=Window(hex_id, obj_monitors)

    tmp_windows=dict(
        id=win_id,
        _class=window._class,
        exe=window.exe_name,
        name=window.name,
        filenpa_exe=window.filenpa_exe,
        cmd_parameters=window.command.replace(window.filenpa_exe, "").strip(),
        paths=get_paths(dy_exes, window, group_name, active_monitor),
        groups=[group_name],
        tile=window.get_tile(),
        monitor=window.monitor.index
    )

    return tmp_windows
