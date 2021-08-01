#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys

from . import notify
from .actions import Actions

from ..gpkgs.guitools import Monitors, Windows

class Session():
    def __init__(
        self,
        filenpa_settings,
        filenpa_state,
    ):
        self.dy_settings=dict()
        self.dy_state=dict()
        self.filenpa_state=filenpa_state
        self.filenpa_settings=filenpa_settings

        with open(self.filenpa_settings, "r") as f:
            self.dy_settings=json.load(f)

        if os.path.exists(self.filenpa_state):
            with open(self.filenpa_state, "r") as f:
                self.dy_state=json.load(f)
        else:
            with open(self.filenpa_state, "w") as f:
                f.write("{}")

        self.dy_state_dump=json.dumps(self.dy_state)
        
        self.actions=Actions(self.dy_settings["actions"])
        self.active_window_hex_id=Windows.get_active_hex_id()
        self.obj_monitors=Monitors()
        self._dy_monitors_lookup_user_real=dict()
        self.set_monitors()
        self.active_monitor=self.obj_monitors.get_active(self.active_window_hex_id)

    def get_monitor_real_index(self, user_index):
        return self._dy_monitors_lookup_user_real[user_index]

    def set_monitors(self):
        dy_existing_monitors={monitor.name:monitor.index for monitor in self.obj_monitors.monitors}
        if "monitors" in self.dy_settings:
            user_monitor_names=sorted(self.dy_settings["monitors"])
            for name, index in dy_existing_monitors.items():
                self._dy_monitors_lookup_user_real[index]=index
                if name in user_monitor_names:
                    user_monitor_names.remove(name)
                    self._dy_monitors_lookup_user_real[index]=self.dy_settings["monitors"][name]


            if len(user_monitor_names) > 0:
                notify.error("monitor name(s) unknown {} in '{}'".format(user_monitor_names, self.filenpa_settings), exit=1)

            setattr(self.obj_monitors, "get_real_index", self.get_monitor_real_index)
        else:
            notify.error("monitors not set in '{}'".format(self.filenpa_settings), exit=1)

    def save(self):
        if self.dy_state_dump != json.dumps(self.dy_state):
            with open(self.filenpa_state, "w") as f:
                f.write(json.dumps(self.dy_state, sort_keys=True, indent=4))
        


