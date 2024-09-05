#!/usr/bin/env python3
from pprint import pprint
import hashlib
import os
import re
import sys
import yaml

from .session import Group
from . import notify
from ..gpkgs.bwins import RadioButtonList, RadioButtonListOptions, Monitors, RadioButtonItem

def generate_group_name(group_name:str, groups:list[Group]):
    existing_group_names=sorted([g.name for g in groups])
    index=2
    new_group_name=group_name
    while new_group_name in existing_group_names:
        new_group_name=group_name+"_"+str(index)
        index+=1
    return new_group_name

def get_dy_group_info(
    group_name:str,
    direpa_groups:str,
    prompt_group:bool,
    default_group:str|None,
):
    groups:list[RadioButtonItem]=[]
    for elem in sorted(os.listdir(direpa_groups)):
        path_elem=os.path.join(direpa_groups, elem)
        if os.path.isfile(path_elem):
            filer, ext = os.path.splitext(path_elem)
            if ext == ".yaml":
                groups.append(RadioButtonItem(label=os.path.basename(filer), value=path_elem))

    if len(groups) == 0:
        notify.error("No YAML group definition can be found in '{}'".format(direpa_groups))
        sys.exit(1)

    selected_group=None
    prefix=None
    if group_name is None:
        if prompt_group is True:
            options=RadioButtonListOptions(
                monitor=Monitors().get_primary_monitor(),
                prompt_text="Select a group name:", 
                title="ScriptJob",
                items=groups,
            )
            output=RadioButtonList(options).loop().output
            if output is None:
                notify.warning("select group name canceled.")
                sys.exit(1)
            else:
                selected_group=output.label
        elif default_group is not None:
            prefix="At settings 'default_group'"
            selected_group=default_group
        else:
            notify.error("At --launch GROUP_NAME has not been provided. Either set 'default_group' in settings or add --prompt-group.")
            sys.exit(1)
    else:
        prefix="At GROUP_NAME value from --launch"
        selected_group=group_name

    if prefix is not None:
        group_names=[g.label for g in groups]
        if selected_group not in group_names:
            notify.error("{}: group '{}' not found in {} from '{}'.".format(prefix, selected_group, sorted(group_names), direpa_groups))
            sys.exit(1)

    return dict(
        name=selected_group,
        filenpa=[g for g in groups if g.label == selected_group][0].value,
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
        r"^\s*(?P<cmd>click)\s+(?P<value>[1-9][0-9]*|last|next|previous)\s(?P<keys>[1-9])\s*$",
        r"^\s*(?P<cmd>send-keys)\s+(?P<value>[1-9][0-9]*|last|next|previous)\s(?P<keys>.+?)\s*$",
        r"^\s*(?P<cmd>sleep)\s+(?P<value>[1-9][0-9]*|\.[0-9]*|[1-9][0-9]*\.[0-9]*)\s*$",
        r"^\s*(?P<cmd>focus)\s+(?P<value>[1-9][0-9]*|last|next|previous)\s*$",
    ]  

def get_dy_group(
    direpa_groups:str,
    group_name:str, 
    filenpa_group:str,
    parse_syntax:bool,
    vars_default_sets:dict[str, str]|None,
):
    filenpa_md5=os.path.join(direpa_groups, "."+group_name+".mda5")
    dy_group=dict()

    with open(filenpa_group, "r") as f:
        dy_group=yaml.safe_load(f)

    if dy_group is None:
        dy_group=dict()

    if is_parse_syntax(filenpa_group, filenpa_md5, parse_syntax) is True:
        win_num=1

        if "windows" in dy_group:
            for dy_win in dy_group["windows"]:
                win_name=None
                if "name" in dy_win:
                    win_name=dy_win["name"]
                else:
                    notify.error("key 'name' not found at window '{}' in group '{}' at '{}'.".format(win_num, group_name, filenpa_group))
                    sys.exit(1)

                if "execute" in dy_win:
                    for cmd_name in dy_win["execute"]:
                        for line in dy_win["execute"][cmd_name].splitlines():
                            line=line.strip()
                            if line != "" and line[0] != "#":
                                reg_found=False
                                for reg_txt in execute_regexes():
                                    reg=re.match(reg_txt, line)
                                    if reg:
                                        reg_found=True
                                        break
                                if reg_found is False:
                                    notify.error("At execute for window '{}' line '{}' does not match any regexes from '{}' in group '{}' at '{}'.".format(win_num, line, execute_regexes(), group_name, filenpa_group))
                                    sys.exit(1)

                else:
                    notify.error("key 'execute' not found at window '{}' in group '{}' at '{}'.".format(win_name, group_name, filenpa_group))
                    sys.exit(1)

                if "rcfile" in dy_win:
                    for key in [ "content", "path" ]:
                        if key not in dy_win["rcfile"]:
                            notify.error("At windows section for window '{}' in 'rcfile' key '{}' not found in group '{}' at '{}'.".format(win_name, key, group_name, filenpa_group))
                            sys.exit(1)

                win_num+=1

            if "variables" in dy_group:
                if vars_default_sets is not None:
                    if group_name in vars_default_sets:
                        default_set=vars_default_sets[group_name]
                        if default_set not in dy_group["variables"]:
                            notify.error("Default vars set '{}' found in settings is not found at variables section at window '{}' in group '{}' at '{}'.".format(default_set, win_name, group_name, filenpa_group))
                            sys.exit(1)

            with open(filenpa_md5, "w") as f:
                f.write(hashlib.md5(open(filenpa_group,'rb').read()).hexdigest())
        else:
            notify.error("key 'windows' not found in group '{}' at '{}'.".format(group_name, filenpa_group))
            sys.exit(1)
        
    return dy_group


