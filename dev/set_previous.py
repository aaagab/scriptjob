#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from ..gpkgs.guitools import Windows, Window

def set_previous(dy_state, previous_type, start_hex_id):
    if previous_type == "global":
        dy_state["previous_window"]=start_hex_id
    elif previous_type == "active_group":
        group_names=[group["name"] for group in dy_state["groups"]]
        active_group_index=group_names.index(dy_state["active_group"])
        active_group=dy_state["groups"][active_group_index]
        active_group_windows_hex_ids=[win["hex_id"] for win in active_group["windows"]]
        if start_hex_id in active_group_windows_hex_ids:
            dy_state["groups"][active_group_index]["previous_window"]=start_hex_id
    
