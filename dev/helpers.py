#!/usr/bin/env python3
import sys
import os

from ..gpkgs import message as msg

from ..gpkgs.notification import set_notification

def message(msg_type, text, obj_monitor):
    if msg_type == "error":
        msg.error(text)
        msg_type="error"
    elif msg_type == "warning":
        msg.warning(text)
    elif msg_type == "info":
        msg.info(text)
    elif msg_type == "success":
        msg.success(text)
    
    set_notification(text, msg_type, obj_monitor)

def generate_group_name(group_name, groups):
    existing_group_names=[group["name"] for group in groups]

    index=2
    new_group_name=group_name
    while new_group_name in existing_group_names:
        new_group_name=group_name+"_"+str(index)
        index+=1

    return new_group_name
