#!/usr/bin/env python3
import sys
import os

from ..gpkgs import message as msg
from ..gpkgs.notification import set_notification

def error(text, obj_monitor=None, exit=None):
    msg.error(text)
    set_notification(text, "error", obj_monitor)
    if exit is not None:
        sys.exit(exit)
def info(text, obj_monitor=None, exit=None):
    msg.info(text)
    set_notification(text, "info", obj_monitor)
    if exit is not None:
        sys.exit(exit)
def success(text, obj_monitor=None, exit=None):
    msg.success(text)
    set_notification(text, "success", obj_monitor)
    if exit is not None:
        sys.exit(exit)
def warning(text, obj_monitor=None, exit=None):
    msg.warning(text)
    set_notification(text, "warning", obj_monitor)
    if exit is not None:
        sys.exit(exit)