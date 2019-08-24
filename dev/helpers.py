#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.0.0
# name: scriptjob
# license: MIT

from modules.notification.notification import set_notification
import modules.message.message as msg
import sys, os

def message(msg_type, text, obj_monitor):
    if msg_type in ["error","user_error"]:
        msg.user_error(text)
        msg_type="error"
    elif msg_type == "app_error":
        msg.app_error(text)
        msg_type="error"
    elif msg_type == "warning":
        msg.warning(text)
    elif msg_type == "info":
        msg.info(text)
    elif msg_type == "success":
        msg.success(text)
    
    set_notification(text, msg_type, obj_monitor)

def generate_group_name(group_name, scriptjob_conf):
    existing_group_names=[group["name"] for group in scriptjob_conf.data["groups"]]

    index=2
    new_group_name=group_name
    while new_group_name in existing_group_names:
        new_group_name=group_name+"_"+str(index)
        index+=1

    return new_group_name
