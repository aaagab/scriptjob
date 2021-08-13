#!/usr/bin/env python3
from pprint import pprint
import hashlib
import os
import re
import sys
import yaml

from . import notify
from ..gpkgs.bwins import Radio_button_list

def generate_group_name(group_name, dy_groups):
    existing_group_names=[name for name in sorted(dy_groups)]
    index=2
    new_group_name=group_name
    while new_group_name in existing_group_names:
        new_group_name=group_name+"_"+str(index)
        index+=1
    return new_group_name

def get_dy_group_info(group_name, direpa_groups, dy_settings, prompt_group, active_monitor):
    dy_groups=dict()
    for elem in sorted(os.listdir(direpa_groups)):
        path_elem=os.path.join(direpa_groups, elem)
        if os.path.isfile(path_elem):
            filer, ext = os.path.splitext(path_elem)
            if ext == ".yaml":
                dy_groups[os.path.basename(filer)]=path_elem

    if len(dy_groups) == 0:
        notify.error("No YAML group definition can be found in '{}'".format(direpa_groups), obj_monitor=active_monitor, exit=1)

    selected_group=None
    prefix=None
    if group_name is None:
        if prompt_group is True:
            options=dict(
                monitor=active_monitor, 
                prompt_text="Select a group name:", 
                title="ScriptJob",
                items=sorted(dy_groups),
                values=sorted(dy_groups),
            )
            selected_group=Radio_button_list(options).loop().output
            if selected_group == "_aborted":
                notify.warning("select group name canceled.", obj_monitor=active_monitor)
                sys.exit(1)
        elif "default_group" in dy_settings:
            prefix="At settings 'default_group'"
            selected_group=dy_settings["default_group"]
        else:
            pkg.notify.error("At --launch GROUP_NAME has not been provided. Either set 'default_group' in settings or add --prompt-group.", obj_monitor=active_monitor, exit=1)
    else:
        prefix="At GROUP_NAME value from --launch"
        selected_group=group_name

    if prefix is not None:
        if selected_group not in dy_groups:
            notify.error("{}: group '{}' not found in {} from '{}'.".format(prefix, selected_group, sorted(dy_groups), direpa_groups), obj_monitor=active_monitor, exit=1)

    return dict(
        name=selected_group,
        filenpa=dy_groups[selected_group],
    )

def is_parse_syntax(
    filenpa_group,
    filenpa_md5,
    parse_syntax,
):
    if parse_syntax is True:
        return True
    elif os.path.exists(filenpa_md5):
        stored_mda5=None
        with open(filenpa_md5, "r") as f:
            stored_mda5=f.read()
        current_mda5=hashlib.md5(open(filenpa_group,'rb').read()).hexdigest()
        if stored_mda5 == current_mda5:
            return False
        else:
            return True
    else:
        return True

def execute_regexes():
    return [
        r"^\s*(?P<cmd>send-keys)\s+(?P<value>[1-9][0-9]*|last|next|previous)\s(?P<keys>.+?)\s*$",
        r"^\s*(?P<cmd>sleep)\s+(?P<value>[1-9][0-9]*|\.[0-9]*|[1-9][0-9]*\.[0-9]*)\s*$",
        r"^\s*(?P<cmd>focus)\s+(?P<value>[1-9][0-9]*|last|next|previous)\s*$",
    ]  

def get_dy_group(
    direpa_groups,
    group_name, 
    filenpa_group,
    dy_settings,
    active_monitor,
    parse_syntax,
):
    filenpa_md5=os.path.join(direpa_groups, "."+group_name+".mda5")
    dy_group=dict()

    with open(filenpa_group, "r") as f:
        dy_group=yaml.safe_load(f)

    if dy_group is None:
        dy_group=dict()

    if is_parse_syntax(filenpa_group, filenpa_md5, parse_syntax) is True:
        elems=["send_keys", "sleep", "focus"]
        win_num=1

        if "windows" in dy_group:
            for dy_win in dy_group["windows"]:
                win_name=None
                if "name" in dy_win:
                    win_name=dy_win["name"]
                else:
                    notify.error("key 'name' not found at window '{}' in group '{}' at '{}'.".format(win_num, group_name, filenpa_group), obj_monitor=active_monitor, exit=1)

                if "execute" in dy_win:
                    for line in dy_win["execute"].splitlines():
                        line=line.strip()
                        if line != "" and line[0] != "#":
                            reg_found=False
                            for reg_txt in execute_regexes():
                                reg=re.match(reg_txt, line)
                                if reg:
                                    reg_found=True
                                    break
                            if reg_found is False:
                                notify.error("At execute for window '{}' line '{}' does not match any regexes from '{}' in group '{}' at '{}'.".format(win_num, line, execute_regexes(), group_name, filenpa_group), obj_monitor=active_monitor, exit=1)
                else:
                    notify.error("key 'execute' not found at window '{}' in group '{}' at '{}'.".format(win_name, group_name, filenpa_group), obj_monitor=active_monitor, exit=1)

                if "rcfile" in dy_win:
                    for key in [ "content", "path" ]:
                        if key not in dy_win["rcfile"]:
                            notify.error("At windows section for window '{}' in 'rcfile' key '{}' not found in group '{}' at '{}'.".format(win_name, key, group_name, filenpa_group), obj_monitor=active_monitor, exit=1)

                win_num+=1

            if "variables" in dy_group:
                if "vars_default_sets" in dy_settings:
                    if group_name in dy_settings["vars_default_sets"]:
                        default_set=dy_settings["vars_default_sets"][group_name]
                        if default_set not in dy_group["variables"]:
                            notify.error("Default vars set '{}' found in settings is not found at variables section at window '{}' in group '{}' at '{}'.".format(default_set, win_name, group_name, filenpa_group), obj_monitor=active_monitor, exit=1)

            with open(filenpa_md5, "w") as f:
                f.write(hashlib.md5(open(filenpa_group,'rb').read()).hexdigest())
        else:
            notify.error("key 'windows' not found in group '{}' at '{}'.".format(group_name, filenpa_group), obj_monitor=active_monitor, exit=1)
        
    return dy_group


