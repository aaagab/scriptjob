#!/usr/bin/env python3
from pprint import pprint
import json
import getpass
import os
import time
from Xlib.X import AnyPropertyType

from ..gpkgs.guitools import Windows as Windows, XlibHelpers, WindowType

class State():
    def __init__(self) -> None:
        self.active_group:str|None=None
        self.focus=Focus()
        self.groups:list[Group]=[]
        self.last_window_id:str|None=None

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class Focus():
    def __init__(self) -> None:
        self.last_window_id:str|None=None
        self.windows:list[str]=[]

class Execute():
    def __init__(self,
        shortcut:str,
        commands:list[str],
    ) -> None:
        self.shortcut:str=shortcut
        self.commands:list[str]=commands

class Window():
    def __init__(self,
        ref:int,
        hex_id:str|None,
        execute:list[Execute],
        refs:list[int],
        timestamp:float|None=None,
    ) -> None:
        self.ref:int=ref
        self.execute:list[Execute]=execute
        self.hex_id:str
        if hex_id is not None:
            self.hex_id=hex_id
        self.refs:list[int]=refs
        self.timestamp:float
        if timestamp is None:
            self.timestamp=time.time()
        else:
            self.timestamp=timestamp

class Group():
    def __init__(self,
        name:str,
        windows:list[Window],
        last_window_ref:int|None=None,
        timestamp:float|None=None,
    ) -> None:
        self.name:str=name
        self.last_window_ref:int|None=last_window_ref
        self.timestamp:float
        if timestamp is None:
            self.timestamp=time.time()
        else:
            self.timestamp=timestamp
        self.windows:list[Window]=windows

class Vars():
    def __init__(self, direpa_tmp:str):
        self.GROUP:str|None=None
        self.PATH_APP:str|None=None
        self.PWD:str=os.getcwd()
        self.SEP:str=os.path.sep
        self.TMP_FILE:str=os.path.join(direpa_tmp, "scriptjob-tmp-"+str(time.time()).replace(".", ""))
        self.USER:str=getpass.getuser()
        self.USERPROFILE:str=os.path.expanduser("~")

class Session():
    def __init__(
        self,
        direpa_tmp:str,
        filenpa_state:str,
    ) -> None:
        self.direpa_tmp=direpa_tmp
        self.state=State()
        self.tmp_state=State()

        self.filenpa_state=filenpa_state

        self.xlib=XlibHelpers()

        self.active_window_hex_id=self.xlib.get_active_window_hex_id()
        self.dy_existing_regular_windows:dict[str,str]=dict()
        self.desktop_win_hex_ids:list[str]=[]

        prop = self.xlib.root.get_full_property(self.xlib.display.get_atom("_NET_CLIENT_LIST"), property_type=AnyPropertyType)
        if prop is None:
            raise NotImplementedError()
        client_list=prop.value
        for window_id in client_list:
            xwin = self.xlib.display.create_resource_object('window', window_id)
            prop = xwin.get_full_property(self.xlib.display.get_atom("_NET_WM_WINDOW_TYPE"), property_type=AnyPropertyType)
            if prop is not None:
                values=list(prop.value)
                if WindowType.DESKTOP.value in values:
                    self.desktop_win_hex_ids.append(hex(window_id))
                elif WindowType.DOCK.value in values:
                    self.desktop_win_hex_ids.append(hex(window_id))
                else:
                    win_name:str="unknown"
                    prop = xwin.get_full_property(self.xlib.display.get_atom("_NET_WM_NAME"), property_type=AnyPropertyType)
                    if prop is not None:
                        win_name=prop.value.decode()[:40]

                    class_name:str="unknown"
                    obj_class=xwin.get_wm_class()
                    if obj_class is not None:
                        class_name=obj_class[-1]

                    full_name=f"{class_name} - {win_name}"
                    self.dy_existing_regular_windows[hex(window_id)]=full_name
                    
        if os.path.exists(self.filenpa_state):
            with open(self.filenpa_state, "r") as f:
                self.load_state(s=self.state, d=json.load(f))
                self.update_state()
        else:
            with open(self.filenpa_state, "w") as f:
                f.write(self.state.to_json())

        self._state_dump=self.state.to_json()

        self.vars=Vars(direpa_tmp=direpa_tmp)


    def load_state(self, s:State, d:dict):
        for key, value in sorted(d.items()):
            if key == "active_group":
                if isinstance(value, str):
                    s.active_group=value
            elif key == "last_window_id":
                if isinstance(d[key], str):
                    s.last_window_id=d[key]
            elif key == "focus":
                if isinstance(d[key], dict):
                    if "last_window_id" in d[key]:
                        if isinstance(d[key]["last_window_id"], str):
                            s.focus.last_window_id=d[key]["last_window_id"]
                    if "windows" in d[key]:
                        if isinstance(d[key]["windows"], list):
                            for w in d[key]["windows"]:
                                if isinstance(w, str):
                                    s.focus.windows.append(w)
            elif key == "groups":
                if isinstance(d[key], list):
                    for group in d[key]:
                        if isinstance(group, dict):
                            group_name:str|None=None
                            last_window_ref:int|None=None
                            gtimestamp:float|None=None
                            windows:list[Window]|None=None
                            if "name" in group and isinstance(group["name"], str):
                                group_name=group["name"]
                            if "last_window_ref" in group and isinstance(group["last_window_ref"], int):
                                last_window_ref=group["last_window_ref"]
                            if "timestamp" in group and isinstance(group["timestamp"], float):
                                gtimestamp=group["timestamp"]
                            if "windows" in group and isinstance(group["windows"], list):
                                for win in group["windows"]:
                                    hex_id:str|None=None
                                    execute:list[Execute]|None=None
                                    refs:list[int]|None=None
                                    ref:int|None=None
                                    timestamp:float|None=None
                                    if isinstance(win, dict):
                                        if "execute" in win and isinstance(win["execute"], list):
                                            for exec in win["execute"]:
                                                if isinstance(exec, dict):
                                                    shortcut:str|None=None
                                                    commands:list[str]|None=None
                                                    if "shortcut" in exec and isinstance(exec["shortcut"], str):
                                                        shortcut=exec["shortcut"]
                                                    if "commands" in exec and isinstance(exec["commands"], list):
                                                        for c in exec["commands"]:
                                                            if isinstance(c, str):
                                                                if commands is None:
                                                                    commands=[]
                                                                commands.append(c)
                                                    if shortcut is not None and commands is not None:
                                                        if execute is None:
                                                            execute=[]
                                                        execute.append(Execute(shortcut=shortcut, commands=commands))
                                                    
                                        if "hex_id" in win and isinstance(win["hex_id"], str):
                                            hex_id=win["hex_id"]
                                        if "ref" in win and isinstance(win["ref"], int):
                                            ref=win["ref"]
                                        if "refs" in win and isinstance(win["refs"], list):
                                            if refs is None:
                                                refs=[]
                                            for r in win["refs"]:
                                                if isinstance(r, int):
                                                    refs.append(r)
                                        if "timestamp" in win and isinstance(win["timestamp"], float):
                                            timestamp=win["timestamp"]

                                    if hex_id is not None and execute is not None and refs is not None and timestamp is not None and ref is not None:
                                        if windows is None:
                                            windows=[]
                                        windows.append(Window(
                                            ref=ref,
                                            hex_id=hex_id,
                                            execute=execute,
                                            refs=refs,
                                            timestamp=timestamp,
                                        ))

                            if group_name is not None and last_window_ref is not None and gtimestamp is not None and windows is not None:
                                s.groups.append(Group(
                                    name=group_name,
                                    timestamp=gtimestamp,
                                    windows=windows,
                                    last_window_ref=last_window_ref,
                                ))

    def save(self):
        current_dump=self.state.to_json()
        if self._state_dump != current_dump:
            with open(self.filenpa_state, "w") as f:
                f.write(current_dump)

    def update_state(self) -> None:
        if self.state.last_window_id not in self.dy_existing_regular_windows:
            self.state.last_window_id=None
        
        if self.state.focus.last_window_id not in self.dy_existing_regular_windows:
            self.state.focus.last_window_id=None

        focus_windows=[]
        for w in self.state.focus.windows:
            if w in self.dy_existing_regular_windows:
                focus_windows.append(w)

        self.state.focus.windows=focus_windows

        if self.state.focus.last_window_id is None and len(self.state.focus.windows) > 0:
            self.state.focus.last_window_id=self.state.focus.windows[-1]

        dy_group_timestamps:dict[float, str]=dict()
        for group in self.state.groups.copy():
            dy_window_timestamps:dict[float, int]=dict()
            for window in group.windows.copy():
                if window.hex_id in self.dy_existing_regular_windows:
                    dy_window_timestamps[window.timestamp]=window.ref
                else:
                    if group.last_window_ref == window.ref:
                        group.last_window_ref=None
                    group.windows.remove(window)

            if len(group.windows) > 0:
                if group.last_window_ref not in [w.ref for w in group.windows]:
                    group.last_window_ref=[dy_window_timestamps[t] for t in sorted(dy_window_timestamps)][-1]

                for window in group.windows:
                    for ref in window.refs.copy():
                        if ref not in [w.ref for w in group.windows]:
                            window.execute=[]
                            window.refs=[]
                            break
                        
                dy_group_timestamps[group.timestamp]=group.name
            else:
                if self.state.active_group == group.name:
                    self.state.active_group=None
                self.state.groups.remove(group)

        if len(self.state.groups) > 0:
            if self.state.active_group not in [g.name for g in self.state.groups]:
                self.state.active_group=[dy_group_timestamps[t] for t in sorted(dy_group_timestamps)][-1]

            if self.state.last_window_id is None:
                active_group=[g for g in self.state.groups if g.name == self.state.active_group][0]
                self.state.last_window_id=[w for w in active_group.windows if w.ref == active_group.last_window_ref][0].hex_id
        else:
            self.state.active_group=None
            if self.state.last_window_id is None:
                self.state.last_window_id=self.active_window_hex_id