#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import re
import time

from . import notify
from .get_dy_group import generate_group_name
from .get_dy_group import execute_regexes
from .custom_windows import WindowPrompt, WindowPromptOptions

from ..gpkgs.guitools import Window, WindowOpen, TileMove
from ..gpkgs.bwins import PromptBoolean, Monitors, Monitor, PromptBooleanOptions

from .session import Vars, State, Group, Window as SWindow, Execute

def launch(
    dy_group:dict,
    session_vars:Vars,
    state:State,
    dy_group_vars:dict,
    is_prompt:bool,
    active_window_hex_id:str,
    desktop_win_hex_ids:list[str],
):
    if session_vars.GROUP is None:
        raise NotImplementedError()

    new_group_name=generate_group_name(session_vars.GROUP, state.groups)
    bwin_obj_monitors=Monitors()
    bwin_monitor=bwin_obj_monitors.get_primary_monitor()

    tmp_group=Group(
        last_window_ref=None,
        name=new_group_name,
        windows=[],
    )

    win_num=0
    for dy_win in dy_group["windows"]:
        win_num+=1
        refs=set()

        execute:list[Execute]=[]
        for cmd_name in dy_win["execute"]:
            commands:list[str]=[]
            shortcut:str=cmd_name
            for line in dy_win["execute"][cmd_name].splitlines():
                for reg_txt in execute_regexes():
                    reg=re.match(reg_txt, line)
                    if reg:
                        if reg.groupdict()["cmd"] in ["send-keys", "focus"]:
                            try:
                                win_ref=int(reg.groupdict()["value"])
                                if win_ref != win_num:
                                    refs.add(win_ref)
                            except:
                                pass

                        commands.append(line)
                        break
            execute.append(Execute(shortcut=shortcut, commands=commands))

        tmp_group.windows.append(SWindow(
            execute=execute,
            ref=win_num,
            hex_id=None,
            refs=list(refs),
        ))

        window:Window|None=None
        if is_prompt is True or "command" not in dy_win:
            window=WindowPrompt(options=WindowPromptOptions(
                desktop_win_hex_ids=desktop_win_hex_ids,
                monitor=bwin_monitor,
                prompt_text="Choose Window '{}'".format(dy_win["name"]),
            )).loop().output

            if window is None:
                notify.warning("open command canceled.")
                sys.exit(1)

            notify.success("window '{}' selected.".format(window.name))
        else:
            if "rcfile" in dy_win:
                filenpa_rc=dy_win["rcfile"]["path"].format(**dy_group_vars)
                cmds=[]
                for line in dy_win["rcfile"]["content"].splitlines():
                    cmds.append(line.format(**dy_group_vars))
                set_rc_path(filenpa_rc, cmds)
            cmd:list[str]=[]
            for line in dy_win["command"].splitlines():
                cmd.append(line.format(**dy_group_vars))

            win_class=None
            if "class" in dy_win:
                win_class=dy_win["class"]
            else:
                raise NotImplementedError()
        
            window=get_launch_window(cmd, win_class, bwin_monitor)

        tmp_win=[w for w in tmp_group.windows if w.ref == win_num][0]
        tmp_win.hex_id=window.hex_id
        tmp_win.timestamp=time.time()
        dy_group_monitors=dict()
        if "monitors" in dy_group:
            dy_group_monitors=dy_group["monitors"]

        position_window(dy_win["name"], bwin_obj_monitors, dy_group_monitors, window)

    state.last_window_id=active_window_hex_id
    state.active_group=new_group_name
    tmp_group.last_window_ref=win_num
    state.groups.append(tmp_group)
    notify.success("group '{}' opened".format(new_group_name))

def get_launch_window(cmd:list[str], win_class:str, monitor:Monitor) -> Window:
    launch_window=WindowOpen().execute(cmd)
    while not launch_window.has_window(win_class):
        user_continue=PromptBoolean(PromptBooleanOptions(
            monitor=monitor, 
            title="Scriptjob open", 
            prompt_text="Can't open a window with cmd\n'{}'\nDo you want to wait?".format(cmd)
        )).loop().output
        if user_continue is False or user_continue is None:
            notify.error("Scriptjob command 'open' canceled.")
            sys.exit(1)
    window=launch_window.window
    if window is None:
        raise NotImplementedError()
    return window

def position_window(win_name:str, obj_monitors:Monitors, dy_group_monitors:dict[int,dict], window:Window):
    window.focus()
    tile:str|None=None
    monitor_index:int=0
    num_monitors=len(obj_monitors.monitors)

    if num_monitors in dy_group_monitors:
        if win_name in dy_group_monitors[num_monitors]:
            if "monitor" in dy_group_monitors[num_monitors][win_name]:
                user_monitor=dy_group_monitors[num_monitors][win_name]["monitor"]
                monitor_index=user_monitor-1
            if "tile" in dy_group_monitors[num_monitors][win_name]:
                tile=dy_group_monitors[num_monitors][win_name]["tile"]

    if tile is None:
        raise NotImplementedError()
    
    tile_obj:TileMove
    if tile == "left":
        tile_obj=TileMove.LEFT
    elif tile == "right":
        tile_obj=TileMove.RIGHT
    elif tile == "maximize":
        tile_obj=TileMove.MAXIMIZE
    else:
        raise NotImplementedError(f"tile {tile}")

    window.tile(tile_obj, monitor_index)

def set_rc_path(filenpa_rc, cmds):
    with open(filenpa_rc, "w") as f:
        f.write("#!/bin/bash\n")
        filenpa_bashrc=os.path.join(os.path.expanduser("~"), ".bashrc")
        with open(filenpa_bashrc, "r") as content_bashrc:
            f.write("{}\n".format(content_bashrc.read()))
        for cmd in cmds:
            f.write("{}\n".format(cmd))
        f.write("rm '{}'\n".format(filenpa_rc))
