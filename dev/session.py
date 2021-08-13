#!/usr/bin/env python3
from pprint import pprint
import json
import getpass
import os
import subprocess
import sys
import time
import tempfile

from . import notify

from ..gpkgs.guitools import Monitors, Windows, Regular_windows

class Session():
    def __init__(
        self,
        direpa_tmp,
        filenpa_settings,
        filenpa_state,
    ):
        self.direpa_tmp=direpa_tmp
        self.dy_settings=dict()
        self.dy_state=dict()
        self.filenpa_state=filenpa_state
        self.filenpa_settings=filenpa_settings
        self.set_dy_settings()

        if os.path.exists(self.filenpa_state):
            with open(self.filenpa_state, "r") as f:
                self.dy_state=json.load(f)
        else:
            with open(self.filenpa_state, "w") as f:
                f.write("{}")

        self.dy_state_dump=json.dumps(self.dy_state)

        self.active_window_hex_id=Windows.get_active_hex_id()
        self.obj_monitors=Monitors()
        self._dy_monitors_lookup_user_real=dict()
        self.set_monitors()
        self.active_monitor=self.obj_monitors.get_active(self.active_window_hex_id)

        cmd=[
            "wmctrl",
            "-lpx",
        ]
        self.dy_existing_regular_windows=dict()
        self.dy_desktop_windows=dict()
        for line in subprocess.check_output(cmd).decode().rstrip().splitlines():
            line_elems=line.split()
            hex_id=hex(int(line_elems[0], 16))
            name="{} - {}".format(line_elems[3].split(".")[0], " ".join(line_elems[5:]))[:40]
            if line_elems[1] == "-1":
                self.dy_desktop_windows[hex_id]=name
            else:
                self.dy_existing_regular_windows[hex_id]=name

        self.dy_vars=dict(
            PATH_APP=None,
            PWD=os.getcwd(),
            SEP=os.path.sep,
            TMP_FILE=os.path.join(self.direpa_tmp, "scriptjob-tmp-"+str(time.time()).replace(".", "")),
            USER=getpass.getuser(),
            USERPROFILE=os.path.expanduser("~"),
        )

        self.update_state()

    def set_dy_settings(self):
        if os.path.exists(self.filenpa_settings):
            with open(self.filenpa_settings, "r") as f:
                self.dy_settings=json.load(f)
        else:
            with open(self.filenpa_settings, "w") as f:
                f.write(json.dumps(dict(monitors=dict()), sort_keys=True, indent=4))
        
    def get_monitor_real_index(self, user_index):
        return self._dy_monitors_lookup_user_real[user_index]

    def set_monitors(self):
        dy_existing_monitors={monitor.name:monitor.index for monitor in self.obj_monitors.monitors}
        if not "monitors" in self.dy_settings:
            self.dy_settings["monitors"]=dict()
            with open(self.filenpa_settings, "w") as f:
                f.write(json.dumps(self.dy_settings, sort_keys=True, indent=4))

        for name in sorted(self.dy_settings["monitors"]):
            if name in dy_existing_monitors:
                user_index=self.dy_settings["monitors"][name]
                self._dy_monitors_lookup_user_real[user_index]=dy_existing_monitors[name]

        setattr(self.obj_monitors, "get_real_index", self.get_monitor_real_index)

    def save(self):
        if self.dy_state_dump != json.dumps(self.dy_state):
            with open(self.filenpa_state, "w") as f:
                f.write(json.dumps(self.dy_state, sort_keys=True, indent=4))

    def update_state(self):
        if not "active_group" in self.dy_state:
            self.dy_state["active_group"]=None

        if not "last_window_id" in self.dy_state or not self.dy_state["last_window_id"] in self.dy_existing_regular_windows:
            self.dy_state["last_window_id"]=None

        if not "focus" in self.dy_state:
            self.dy_state["focus"]=dict()
        
        if not "windows" in self.dy_state["focus"]:
            self.dy_state["focus"]["windows"]=[]

        if not "last_window_id" in self.dy_state["focus"]:
            self.dy_state["focus"]["last_window_id"]=None

        if self.dy_state["focus"]["last_window_id"] is not None:
            if self.dy_state["focus"]["last_window_id"] not in self.dy_existing_regular_windows:
                if len(self.dy_state["focus"]["windows"]) > 0:
                    self.dy_state["focus"]["last_window_id"]=self.dy_state["focus"]["windows"][-1]
                else:
                    self.dy_state["focus"]["last_window_id"]=None

        for window_id in self.dy_state["focus"]["windows"].copy():
            if not window_id in self.dy_existing_regular_windows:
                self.dy_state["focus"]["windows"].remove(window_id)
        
        if not "groups" in self.dy_state:
            self.dy_state["groups"]=dict()

        dy_group_timestamps=dict()
        for group_name in sorted(self.dy_state["groups"]):
            dy_group=self.dy_state["groups"][group_name]
      
            dy_window_timestamps=dict()
            for ref_num in sorted(dy_group["windows"]):
                dy_window=dy_group["windows"][ref_num]
                if dy_window["hex_id"] in self.dy_existing_regular_windows:
                    dy_window_timestamps[dy_window["timestamp"]]=ref_num
                else:
                    del dy_group["windows"][ref_num]
                    if dy_group["last_window_ref"] == ref_num:
                        dy_group["last_window_ref"]=None  

            if len(dy_group["windows"]) > 0:
                if dy_group["last_window_ref"] not in dy_group["windows"]:
                    for timestamp in sorted(dy_window_timestamps, reverse=True):
                        dy_group["last_window_ref"]=dy_window_timestamps[timestamp]
                        break

                for ref_num in sorted(dy_group["windows"]):
                    dy_window=dy_group["windows"][ref_num]
                    for other_ref_num in dy_window["refs"].copy():
                        if other_ref_num not in dy_group["windows"]:
                            dy_window["execute"]=[]
                            dy_window["refs"]=[]
                            break
                        
                dy_group_timestamps[dy_group["timestamp"]]=group_name
            else:
                del self.dy_state["groups"][group_name]
                if self.dy_state["active_group"] == group_name:
                    self.dy_state["active_group"]=None

        if len(self.dy_state["groups"]) > 0:
            if self.dy_state["active_group"] not in self.dy_state["groups"]:
                for timestamp in sorted(dy_group_timestamps, reverse=True):
                    self.dy_state["active_group"]=dy_group_timestamps[timestamp]
                    break

            if self.dy_state["last_window_id"] is None:
                active_group=self.dy_state["active_group"]
                last_window_ref=self.dy_state["groups"][active_group]["last_window_ref"]
                self.dy_state["last_window_id"]=self.dy_state["groups"][active_group]["windows"][last_window_ref]["hex_id"]
        else:
            self.dy_state["active_group"]=None
            if self.dy_state["last_window_id"] is None:
                self.dy_state["last_window_id"]=self.active_window_hex_id
