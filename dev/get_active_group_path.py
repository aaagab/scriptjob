#!/usr/bin/env python3
import os
import sys
from pprint import pprint

def get_active_group_path(dy_state):
    if dy_state["active_group"]:
        active_group=[group for group in dy_state["groups"] if group["name"] == dy_state["active_group"]][0]
        return active_group["direpa_save_json"]
    else:
        return ""
