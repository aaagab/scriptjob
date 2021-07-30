#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from ..gpkgs.guitools import Windows, Window

def set_previous(dy_state, previous_type, start_hex_id):

    # data=scriptjob_conf.data
    # active_window_hex_id=Windows.get_active_hex_id()

    # os.system("zenity --info --text='{}'".format(data["active_group"]))
    # os.system("zenity --info --text='{}'".format(start_hex_id))

    if previous_type == "global":
        # if start_hex_id != active_window_hex_id:
        dy_state["previous_window"]=start_hex_id
        # else:
            # pass
    elif previous_type == "active_group":
        group_names=[group["name"] for group in dy_state["groups"]]
        active_group_index=group_names.index(dy_state["active_group"])
        active_group=dy_state["groups"][active_group_index]
        active_group_windows_hex_ids=[win["hex_id"] for win in active_group["windows"]]
        # if active_window_hex_id in active_group_windows_hex_ids:
        if start_hex_id in active_group_windows_hex_ids:
        #         if start_hex_id != active_window_hex_id:
        #             os.system("zenity --info --text='{}'".format(1))
            dy_state["groups"][active_group_index]["previous_window"]=start_hex_id
        #         else:
        #             os.system("zenity --info --text='{}'".format(2))
        #             pass
        #     else:
        #         os.system("zenity --info --text='{}'".format(3))
        #         pass
        # else:
        #     os.system("zenity --info --text='{}'".format(4))
        #     pass

    # scriptjob_conf.set_file_with_data()
    
