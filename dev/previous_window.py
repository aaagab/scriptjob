#!/usr/bin/env python3
import os
import sys

from . import notify
from .set_previous import set_previous

from ..gpkgs.guitools import Regular_windows

def previous_window(
    dy_state,
    active_monitor,
    active_window_hex_id,
    previous_type,
):
    if previous_type == "global":
        if data["previous_window"] != active_window_hex_id:
            Regular_windows.focus(data["previous_window"])
            set_previous(dy_state, "global", active_window_hex_id)
        else:
            pass
    elif previous_type == "active_group":
        group_names=[group["name"] for group in data["groups"]]

        if not group_names:
            notify.warning("There is no group for previous_window", active_monitor)
            sys.exit(1)

        active_group_index=group_names.index(data["active_group"])
        active_group=data["groups"][active_group_index]
        active_group_hex_ids=[win["hex_id"] for win in active_group["windows"]]

        if active_window_hex_id in active_group_hex_ids:
            if active_window_hex_id != active_group["previous_window"]:
                Regular_windows.focus(active_group["previous_window"])
                set_previous(dy_state, "active_group", active_window_hex_id)
            else:
                pass
        else:
            Regular_windows.focus(active_group["previous_window"])
