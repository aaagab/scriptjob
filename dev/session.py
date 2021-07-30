#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys

from .actions import Actions

class Session():
    def __init__(
        self,
        filenpa_settings,
        filenpa_state,
    ):
        self.dy_settings=dict()
        self.dy_state=dict()
        self.filenpa_state=filenpa_state

        with open(filenpa_settings, "r") as f:
            self.dy_settings=json.load(f)

        if os.path.exists(self.filenpa_state):
            with open(self.filenpa_state, "r") as f:
                self.dy_state=json.load(f)
        else:
            with open(self.filenpa_state, "w") as f:
                f.write("{}")

        self.dy_state_dump=json.dumps(self.dy_state)
        
        self.actions=Actions(self.dy_settings["actions"])

    def save(self):
        if self.dy_state_dump != json.dumps(self.dy_state):
            with open(self.filenpa_state, "w") as f:
                f.write(json.dumps(self.dy_state, sort_keys=True, indent=4))
        


