#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-beta-1546986728
# name: scriptjob
# license: MIT

from modules.bwins.bwins import *
from modules.guitools.guitools import Regular_windows
import time

class Windows_list(Radio_button_list):
    def __init__(self, options, windows_hex_ids=""):
        Radio_button_list.__init__(self, options)
        self.windows_hex_ids=windows_hex_ids

        self.btn_ok.pack_forget()
        del self.focus_buttons[-1]
        self.btn_cancel.pack_forget()
        del self.focus_buttons[-1]

        counter=0
        for button in self.rads:
            button.bind("<Button-1>", lambda event,counter=counter: self.highlight_window(counter))
            button.bind("<Button-1>", lambda event,counter=counter: self.rads[counter].focus_set(), add="+")

            counter+=1

        self.btn_cancel = Button(self.bottom_frame,text='Cancel', name="btn_cancel")
        self.btn_cancel.bind("<Button-1>", lambda event: self.validate(event))
        self.btn_cancel.bind("<Return>", lambda event: self.validate(event))
        self.bind_change_focus(self.btn_cancel)
        self.btn_cancel.pack(side='left', padx=(20,0))

        self.btn_done = Button(self.bottom_frame,text='Done', name="btn_done")
        self.btn_done.bind("<Button-1>", lambda event: self.validate(event))
        self.btn_done.bind("<Return>", lambda event: self.validate(event))
        self.bind_change_focus(self.btn_done)
        self.btn_done.pack(side='left', padx=(10,10))

        self.btn_select = Button(self.bottom_frame,text='Select', name="btn_select")
        self.btn_select.bind("<Button-1>", lambda event: self.validate(event))
        self.btn_select.bind("<Return>", lambda event: self.validate(event))
        self.bind_change_focus(self.btn_select)
        self.btn_select.pack(side='right', padx=(0,20))

    def loop(self):
        self.set_window_hex_id_and_center()
        self.highlight_window(self.index_selected)
        self.root.mainloop()
        return self

    def highlight_window(self, index):
        if self.windows_hex_ids:
            if index < len(self.windows_hex_ids):
                self.set_above()
                Regular_windows.focus(self.windows_hex_ids[index])
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

    def validate(self, e=None):
        name=""
        if e is not None: # event
            name=str(e.widget).split(".")[-1]
            e.widget.focus_set()
            if name not in  ["btn_done", "btn_select", "btn_cancel"]:
                if hasattr(e.widget, 'invoke'):
                    e.widget.invoke()
            
        if name == "btn_done":
            self.output="_done"
        elif name == "btn_cancel":
            self.output="_aborted"
        else:
            self.output=self.state.get()

        self.root.destroy()
        return "break"

