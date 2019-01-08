#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-beta-1546986728
# name: scriptjob
# license: MIT

import os, sys
from pprint import pprint

def get_active_group_path(scriptjob_conf):

    data=scriptjob_conf.data
    if data["active_group"]:
        active_group=[group for group in data["groups"] if group["name"] == data["active_group"]][0]
        return active_group["direpa_save_json"]
    else:
        return ""
