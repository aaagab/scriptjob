#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-draft-1544978140
# name: scriptjob
# license: MIT

import os, sys
from modules.notification.notification import set_notification
import modules.message.message as msg

from dev.windows_list import Windows_list
from dev.set_previous import set_previous
from modules.guitools.guitools import Regular_windows, Windows

def switch_group(scriptjob_conf, direction="", group_name=""):
    data=scriptjob_conf.data
   
    group_names=[group["name"] for group in data["groups"]]

    if not group_names:
        msg_error="There is no group to select"
        set_notification(msg_error, "warning")
        msg.warning(msg_error)
        sys.exit(0)
    
    active_group_index=group_names.index(data["active_group"])
    start_hex_id=Windows.get_active_hex_id()

    process_switch_group=False
    if not direction:
        groups_previous_window_hex_ids=[group["previous_window"] for group in data["groups"]]
        group_index=Windows_list(dict(
            items=group_names, 
            prompt_text="Select a Group:", 
            checked=active_group_index,
            title="ScriptJob"), groups_previous_window_hex_ids).loop().output

        if group_index == "_aborted":
            sys.exit()
    
    else:
        if direction == "next":
            if active_group_index == len(group_names) -1:
                group_index=0
            else:
                group_index=active_group_index+1
        elif direction == "previous":
            if active_group_index == 0:
                group_index=len(group_names) - 1
            else:
                group_index=active_group_index-1
        elif direction == "group":
            if not group_name:
                text="Group Name needs to be given when group is selected."
                msg.user_error(text)
                set_notification("error", text)
                sys.exit(1)

            group_index=group_names.index(group_name)
        else:
            if not group_name:
                text="Unknow direction '{}'".format(direction)
                msg.user_error(text)
                set_notification(text, "error")
                sys.exit(1)

    if data["active_group"] != group_names[group_index]:
        set_previous(scriptjob_conf, "active_group", start_hex_id)

        data["active_group"]=group_names[group_index]
        scriptjob_conf.set_file_with_data()

        set_previous(scriptjob_conf, "global", start_hex_id)
    else:
        active_group_hex_ids=[win["hex_id"] for win in data["groups"][active_group_index]["windows"]]
        if start_hex_id in active_group_hex_ids:
            Regular_windows.focus(start_hex_id)
        else:
            Regular_windows.focus(data["groups"][active_group_index]["previous_window"])
            set_previous(scriptjob_conf, "global", start_hex_id)

    set_notification("Active_Group: {}".format(data["active_group"]))
