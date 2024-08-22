#!/usr/bin/env python3
import os
import sys
from pprint import pprint

from . import notify
from .execute import get_window_hex_id, get_group_win_hex_ids

from ..gpkgs.guitools import Regular_windows, Monitors, Windows
from .timeit import TimeIt

def focus_window(
    dy_state,
    # active_monitor,
    active_window_hex_id,
    window_type,
):
    win_hex_id=None
    if window_type == "last_global":
        win_hex_id=dy_state["last_window_id"]
    else:
        if dy_state["active_group"] is None:
            notify.warning("There are no available groups for focus_window.", exit=1)
        dy_group=dy_state["groups"][dy_state["active_group"]]
        group_win_hex_ids=get_group_win_hex_ids(dy_group)
        if active_window_hex_id not in group_win_hex_ids:
            window_type="last"
        win_hex_id=get_window_hex_id(dy_group, active_window_hex_id, window_type, group_win_hex_ids)
        for win_ref in dy_group["windows"]:
            dy_win=dy_group["windows"][win_ref]
            if dy_win["hex_id"] == active_window_hex_id:
                dy_group["last_window_ref"]=active_window_hex_id

    dy_state["last_window_id"]=active_window_hex_id

    if win_hex_id is not None:
        Regular_windows().focus(win_hex_id)
