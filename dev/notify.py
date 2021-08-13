#!/usr/bin/env python3
import os
import sys

from ..gpkgs import message as msg
from ..gpkgs.notification import set_notification

def add_prefix(text):
    return "scriptjob: {}".format(text)

def error(text, obj_monitor=None, exit=None):
    text=add_prefix(text)
    msg.error(text)
    cmd("error", obj_monitor, text, exit)

def info(text, obj_monitor=None, exit=None):
    text=add_prefix(text)
    msg.info(text)
    cmd("info", obj_monitor, text, exit)

def success(text, obj_monitor=None, exit=None):
    text=add_prefix(text)
    msg.success(text)
    cmd("success", obj_monitor, text, exit)

def warning(text, obj_monitor=None, exit=None):
    text=add_prefix(text)
    msg.warning(text)
    cmd("warning", obj_monitor, text, exit)

def cmd(msg_type, obj_monitor, text, exit):
    # istty=sys.stdout.isatty() 
    # if istty is False:   
    set_notification(text, msg_type, obj_monitor)
    if exit is not None:
        sys.exit(exit)