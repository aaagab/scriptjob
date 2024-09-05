#!/usr/bin/env python3
from pprint import pprint
import sys
import time
import threading
from typing import Callable

from . import notify
from ..gpkgs.bwins import RadioButtonList, PromptBoolean, GenericWindow, CheckBoxList, GenericWindowOptions, Monitor, Monitors, RadioButtonListOptions, CheckBoxListOptions
from ..gpkgs.guitools import Windows, Window, Mouse

from tkinter import Button, Event, Radiobutton

class WindowPromptEvent():
    def __init__(self,
        desktop_win_hex_ids:list[str],
        monitor:Monitor,
        avoid_hex_id:str|None=None, 
        is_aborted:bool=False, 
        window:Window|None=None, 
    ):
        self.avoid_hex_id=avoid_hex_id
        self.desktop_win_hex_ids=desktop_win_hex_ids
        self.is_aborted=is_aborted
        self.window=window
        self.monitor=monitor

def get_window_hex_id(pevent: WindowPromptEvent):
    while pevent.window is None and pevent.is_aborted is False:
        if pevent.avoid_hex_id:
            try:
                selected_window=Windows.select_window()
                if selected_window.hex_id == pevent.avoid_hex_id:
                    notify.warning("This window can't be selected")
                elif selected_window.hex_id in pevent.desktop_win_hex_ids:
                    Mouse().left_click()
                else:
                    pevent.window=selected_window
            except BaseException as e:
                notify.error("Please try again. Unmanaged Error when selecting a window")
        else:
            time.sleep(.01)

class WindowPromptOptions(GenericWindowOptions):
    def __init__(self,
        desktop_win_hex_ids:list[str],
        monitor:Monitor|None=None,
        title:str|None=None,
        prompt_text:str|None=None,
    ) -> None:
        GenericWindowOptions.__init__(self, monitor=monitor, title=title, prompt_text=prompt_text)
        self.desktop_win_hex_ids=desktop_win_hex_ids

class WindowPrompt(GenericWindow):
    def __init__(self, options:WindowPromptOptions):
        self.options=options
        if self.options.title is None:
            self.options.title="Scriptjob"
        if self.options.prompt_text is None:
            self.options.prompt_text="Select a window."
        self.options.prompt_text+="\nPress escape to exit."
        GenericWindow.__init__(self, self.options)
        if self.lbl_prompt_text is not None:
            self.lbl_prompt_text.pack(side='top', pady=(5,5))
        
        self.frame.pack(pady=(10, 10))
        self.root.wm_attributes('-type', 'splash')

        if self.options.monitor is None:
            self.options.monitor=Monitors().get_primary_monitor()

        self.output:Window|None=None
        self.pevent=WindowPromptEvent(
            avoid_hex_id=None, 
            desktop_win_hex_ids=self.options.desktop_win_hex_ids,
            is_aborted=False, 
            window=None, 
            monitor=self.options.monitor,
        )

        thread_get_window=threading.Thread(target=get_window_hex_id, args=(self.pevent,))  # <- note extra ','
        thread_get_window.start()
        self.monitor_event()

    def monitor_event(self):
        if hasattr(self, "window"):
            if self.pevent.avoid_hex_id is None:
                self.pevent.avoid_hex_id=self.window.hex_id
            try:
                self.window.focus()
            except:
                pass
            finally:
                if self.pevent.window is None:
                    self.root.after(500, self.monitor_event)
                else:
                    self.root.destroy()
                    self.output=self.pevent.window
        else:
            self.root.after(500, self.monitor_event)

    def on_closing(self, event:Event|None=None):
        self.pevent.is_aborted=True
        self.root.destroy()
        Mouse().left_click()
        self.output=None
    

class WindowsList(RadioButtonList):
    def __init__(self, options:RadioButtonListOptions, windows_hex_ids:list[str]|None=None) -> None:
        if windows_hex_ids is None:
            windows_hex_ids=[]
        self.options=options
        RadioButtonList.__init__(self, options)
        self.windows_hex_ids=windows_hex_ids

        self.btn_ok.pack_forget()
        del self.focus_buttons[-1]
        self.btn_cancel.pack_forget()
        del self.focus_buttons[-1]

        counter=0
        for button in self.rads:
            button.bind("<Button-1>", lambda event,counter=counter: self.highlight_window(counter)) #type:ignore
            button.bind("<Button-1>", lambda event: event.widget.focus_set(), add="+")
            counter+=1

        self.btn_cancel = Button(self.bottom_frame,text='Cancel', name="btn_cancel", command=self.on_closing, **self.theme)
        self.btn_cancel.bind("<Button-1>", self.on_closing)
        self.btn_cancel.bind("<Return>", self.on_closing)
        self.bind_change_focus(self.btn_cancel)
        self.btn_cancel.pack(side='left', padx=(20,0))

        self.btn_select = Button(self.bottom_frame,text='Select', name="btn_select", **self.theme)
        self.btn_select.bind("<Button-1>", lambda event: self.validate(event))
        self.btn_select.bind("<Return>", lambda event: self.validate(event))
        self.bind_change_focus(self.btn_select)
        self.btn_select.pack(side='right', padx=(0,20))

    def loop(self):
        self.set_window_hex_id_and_center()
        self.highlight_window(self.index_selected)
        self.root.mainloop()
        return self

    def highlight_window(self, index:int) -> None:
        if self.windows_hex_ids:
            if  index < len(self.windows_hex_ids):
                self.window.set_above()
                Windows.get_window(hex_id=self.windows_hex_ids[index]).focus()
                self.window.focus()
                self.window.unset_above()
    
    def change_focus(self, e:Event, direction:str):
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
        btn_type, index_str=name.split("_")
        
        if index_str.isdigit():
            index=int(index_str)
            self.highlight_window(index)

class CustomCheckBoxList(CheckBoxList):
    def __init__(self, options:CheckBoxListOptions, windows_hex_ids:list[str]|None=None) -> None:
        if windows_hex_ids is None:
            windows_hex_ids=[]
        CheckBoxList.__init__(self, options)
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

    def highlight_window(self, group_index:int):
        if self.windows_hex_ids:
            if group_index < len(self.windows_hex_ids):
                self.window.set_above()
                Windows.get_window(hex_id=self.windows_hex_ids[group_index]).focus()
                self.window.focus()
                self.window.unset_above()
