#!/usr/bin/env python3
import os
import sys

from ..gpkgs import message as msg
from ..gpkgs.notification import set_notification
from ..gpkgs.guitools import Monitor, Monitors, Windows

def add_prefix(text):
    return "scriptjob: {}".format(text)

def error(text, obj_monitor:Monitor|None=None, exit:int|None=None):
    text=add_prefix(text)
    msg.error(text)
    cmd("error", text, obj_monitor, exit)

def info(text, obj_monitor:Monitor|None=None, exit:int|None=None):
    text=add_prefix(text)
    msg.info(text)
    cmd("info", text, obj_monitor, exit)

def success(text, obj_monitor:Monitor|None=None, exit:int|None=None):
    text=add_prefix(text)
    msg.success(text)
    cmd("success", text, obj_monitor, exit)

def warning(text, obj_monitor:Monitor|None=None, exit:int|None=None):
    text=add_prefix(text)
    msg.warning(text)
    cmd("warning", text, obj_monitor, exit)

def cmd(msg_type:str, text:str, obj_monitor:Monitor|None=None, exit:int|None=None):
    # istty=sys.stdout.isatty() 
    # if istty is False:   
    if obj_monitor is None:
        obj_monitor=Monitors().get_active(Windows().get_active_hex_id())
    set_notification(text, msg_type, obj_monitor)
    if exit is not None:
        sys.exit(exit)