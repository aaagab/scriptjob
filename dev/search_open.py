#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import shutil
from distutils.dir_util import copy_tree
import subprocess
import shlex

from . import notify
from .helpers import generate_group_name
from .open import open_json

from ..gpkgs.bwins import Check_box_list

def get_search_open(
    filen_save_json,
    active_monitor,
    alias_app,
    direpa_wrk=None,
    index=None,
):
    direpa_app_name=os.path.join(direpa_wrk, alias_app[0], alias_app)
    if not os.path.exists(direpa_app_name):
        notify.warning("not found '{}'".format(direpa_app_name), active_monitor)
        sys.exit(1)

    filenpa_jsons=[]
    indexes=[]
    count=0
    for elem in sorted(os.listdir(direpa_app_name)):
        filenpa_json=os.path.join(direpa_app_name, elem, filen_save_json)
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
                notify.warning("Index not found: '{}'".format(index), active_monitor)

    elif len(indexes) == 1:
        index_found=True
        filenpa_json=filenpa_jsons[0]

    if index_found is False:
        notify.warning("Multiple Packages\nProvide index:\n'{}'".format("\n".join(indexes)), active_monitor)
        sys.exit(1)

    notify.success("{} {} found.".format(alias_app, filen_save_json), active_monitor)

    return filenpa_json
