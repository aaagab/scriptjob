#!/usr/bin/env python3
import os, sys
from pprint import pprint
import shutil
from distutils.dir_util import copy_tree
import subprocess, shlex

from dev.helpers import message
from modules.guitools.guitools import Monitors
from modules.bwins.bwins import Check_box_list

def search_open(dy_app, diren_app):
    index=1
    diren_splitted=diren_app.split(",")
    diren_app=diren_splitted[0]
    if len(diren_splitted) > 1:
        index=diren_splitted[1]

    active_monitor=Monitors().get_active()
    filenpa_save_json=os.path.join(dy_app["direpa_apps"], diren_app[0], diren_app, index ,dy_app["filen_save_json"])
    if os.path.exists(filenpa_save_json):
        message("success","{}/{} found.".format(diren_app, dy_app["filen_save_json"]), active_monitor)
        command="scriptjob --open '{}'".format(filenpa_save_json)
        process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ( stdout, stderr ) = process.communicate()
        if stderr:
            message("app_error", stderr.decode("utf-8"), active_monitor)
    else:
        message("warning", "{}/{} not found.".format(diren_app, dy_app["filen_save_json"]), active_monitor)
        sys.exit(1)
