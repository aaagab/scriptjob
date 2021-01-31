#!/usr/bin/env python3
import os, sys
from pprint import pprint
import shutil
from distutils.dir_util import copy_tree
import subprocess, shlex

from dev.helpers import message
from modules.guitools.guitools import Monitors
from modules.bwins.bwins import Check_box_list

def search_open(
    dy_app, 
    alias_app,
    direpa_wrk=None,
    index=None,
):
    active_monitor=Monitors().get_active()
    direpa_app_name=os.path.join(direpa_wrk, alias_app[0], alias_app)
    if not os.path.exists(direpa_app_name):
        message("warning", "not found '{}'".format(direpa_app_name), active_monitor)
        sys.exit(1)

    filenpa_jsons=[]
    indexes=[]
    count=0
    for elem in sorted(os.listdir(direpa_app_name)):
        filenpa_json=os.path.join(direpa_app_name, elem, dy_app["filen_save_json"])
        if os.path.exists(filenpa_json):
            indexes.append("{}: {}".format(count, elem))
            filenpa_jsons.append(filenpa_json)
            count+=1

    filenpa_json=None
    index_found=False
    if len(indexes) > 1:
        if index is not None:
            index=int(index)
            try:
                filenpa_json=filenpa_jsons[index]
                index_found=True
            except:
                message("warning", "Index not found: '{}'".format(index), active_monitor)

    elif len(indexes) == 1:
        index_found=True
        filenpa_json=filenpa_jsons[0]

    if index_found is False:
        message("warning", "Multiple Packages\nProvide index:\n'{}'".format("\n".join(indexes)), active_monitor)
        sys.exit(1)

    print(indexes)
    print(filenpa_json)

    message("success","{} {} found.".format(alias_app, dy_app["filen_save_json"]), active_monitor)
    command="scriptjob --open '{}'".format(filenpa_json)
    process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ( stdout, stderr ) = process.communicate()
    if stderr:
        message("app_error", stderr.decode("utf-8"), active_monitor)
