#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-beta-1546974802
# name: scriptjob
# license: MIT

from modules.bwins.bwins import Check_box_list
from modules.guitools.guitools import Regular_windows
import time

class Custom_check_box_list(Check_box_list):
    def __init__(self, options, windows_hex_ids):
        Check_box_list.__init__(self, options)
        self.windows_hex_ids=windows_hex_ids
        if hasattr(self, 'chk_all'):
            self.chk_all.focus_set()
        else:
            self.check_buttons[0].focus_set()

    def loop(self):
        self.set_window_hex_id_and_center()
        if not hasattr(self, 'chk_all'):
            self.highlight_window(0)

        self.root.mainloop()
        return self

    def highlight_window(self, group_index):
        if self.windows_hex_ids:
            if group_index < len(self.windows_hex_ids):
                self.set_above()
                Regular_windows.focus(self.windows_hex_ids[group_index])
                self.focus()
                self.unset_above()

    def change_focus(self, e, direction):
        btn_index=self.focus_buttons.index(e.widget)
        max_index=len(self.focus_buttons)-1
        
        if btn_index == 0 and direction == "up":
                selected_index=max_index
        elif btn_index == max_index and direction == "down":
                selected_index=0                
        else:
            if direction == "up":
                selected_index=btn_index-1
            elif direction == "down":
                selected_index=btn_index+1

        self.focus_buttons[selected_index].focus()

        name=str(self.root.focus_get()).split(".")[-1]
        btn_type, index=name.split("_")
        
        if index.isdigit():
            index=int(index)
            self.highlight_window(index)

