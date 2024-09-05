#!/usr/bin/env python3
import os
import sys

from ..gpkgs import message as msg
from ..gpkgs.notification import set_notification, NotificationType, Monitor, Monitors

def add_prefix(text):
    return "scriptjob: {}".format(text)

def error(text:str, monitor:Monitor|None=None):
    text=add_prefix(text)
    msg.error(text)
    cmd(NotificationType.ERROR, text, monitor)

def info(text:str, monitor:Monitor|None=None):
    text=add_prefix(text)
    msg.info(text)
    cmd(NotificationType.INFO, text, monitor)

def success(text:str, monitor:Monitor|None=None):
    text=add_prefix(text)
    msg.success(text)
    cmd(NotificationType.SUCCESS, text, monitor)

def warning(text:str, monitor:Monitor|None=None):
    text=add_prefix(text)
    msg.warning(text)
    cmd(NotificationType.WARNING, text, monitor)

def cmd(ntype:NotificationType, text:str, monitor:Monitor|None=None):
    if monitor is None:
        monitor=Monitors().get_primary_monitor()
    set_notification(text=text, ntype=ntype, monitor=monitor)