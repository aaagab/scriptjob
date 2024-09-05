#!/usr/bin/env python3
import os
import sys
from pprint import pprint

from . import notify
from .execute import get_window_hex_id, get_group_win_hex_ids
from .session import State, Group

from ..gpkgs.guitools import XlibHelpers

def focus_window(
    state:State,
    active_window_hex_id:str,
    window_type:str,
):
    win_hex_id=None
    if window_type == "last_global":
        win_hex_id=state.last_window_id
    else:
        if state.active_group is None:
            notify.warning("There are no available groups for focus_window.")
            sys.exit(1)
        group:Group
        try:
            group=[g for g in state.groups if g.name == state.active_group][0]
        except IndexError:
            raise NotImplementedError()
        
        group_win_hex_ids=get_group_win_hex_ids(group)
        if active_window_hex_id not in group_win_hex_ids:
            window_type="last"
        win_hex_id=get_window_hex_id(group, active_window_hex_id, window_type, group_win_hex_ids)
        for window in group.windows:
            if window.hex_id == active_window_hex_id:
                group.last_window_ref=window.ref

    state.last_window_id=active_window_hex_id
    if win_hex_id is not None:
        XlibHelpers().focus_window(hex_id=win_hex_id)
        state.last_window_id=win_hex_id
