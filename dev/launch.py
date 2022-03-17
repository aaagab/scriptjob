#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import re
import time

from . import notify
from .get_dy_group import generate_group_name
from .get_dy_group import execute_regexes
from .custom_windows import Window_Prompt

from ..gpkgs.guitools import Window, Window_open
from ..gpkgs.bwins import Prompt_boolean

def launch(
    dy_group,
    dy_session_vars,
    dy_state,
    dy_group_vars,
    is_prompt,
    active_window_hex_id,
    active_monitor,
    obj_monitors,
    dy_desktop_windows,
):
    new_group_name=generate_group_name(dy_session_vars["GROUP"], dy_state["groups"])
    dy_tmp_group=dict(
        last_window_ref=None,
        timestamp=time.time(),
        windows=dict(),
    )

    win_num=0
    for dy_win in dy_group["windows"]:
        win_num+=1
        refs=set()

        tmp_executes=dict()
        for cmd_name in dy_win["execute"]:
            tmp_execute=[]
            for line in dy_win["execute"][cmd_name].splitlines():
                for reg_txt in execute_regexes():
                    reg=re.match(reg_txt, line)
                    if reg:
                        if reg.groupdict()["cmd"] in ["send-keys", "focus"]:
                            try:
                                win_ref=int(reg.groupdict()["value"])
                                if win_ref != win_num:
                                    refs.add(str(win_ref))
                            except:
                                pass

                        tmp_execute.append(line)
                        break
            tmp_executes[cmd_name]=tmp_execute

        dy_tmp_group["windows"][str(win_num)]=dict(
            execute=tmp_executes,
            hex_id=None,
            refs=list(refs),
            timestamp=None,
        )

        dy_tmp_win=dy_tmp_group["windows"][str(win_num)]
        window=None
        if is_prompt is True or "command" not in dy_win:
            window=Window_Prompt(options=dict(
                desktop_win_hex_ids=sorted(dy_desktop_windows),
                monitor=active_monitor,
                obj_monitors=obj_monitors,
                prompt_text="Choose Window '{}'".format(dy_win["name"]),
            )).loop().output

            if window is "_aborted":
                notify.warning("open command canceled.", obj_monitor=active_monitor, exit=1)

            notify.success("window '{}' selected.".format(window.name), obj_monitor=active_monitor)
        else:
            if "rcfile" in dy_win:
                filenpa_rc=dy_win["rcfile"]["path"].format(**dy_group_vars)
                cmds=[]
                for line in dy_win["rcfile"]["content"].splitlines():
                    cmds.append(line.format(**dy_group_vars))
                set_rc_path(filenpa_rc, cmds)
            cmd=[]
            for line in dy_win["command"].splitlines():
                cmd.append(line.format(**dy_group_vars))

            win_class=None
            if "class" in dy_win:
                win_class=dy_win["class"]
        
            window=get_launch_window(cmd, win_class, active_monitor, obj_monitors)

        dy_tmp_win["hex_id"]=window.hex_id
        dy_tmp_win["timestamp"]=time.time()
        dy_group_monitors=dict()
        if "monitors" in dy_group:
            dy_group_monitors=dy_group["monitors"]

        position_window(dy_win["name"], obj_monitors, dy_group_monitors, window)

    dy_state["last_window_id"]=active_window_hex_id
    dy_state["active_group"]=new_group_name
    dy_state["groups"][new_group_name]=dy_tmp_group
    dy_state["groups"][new_group_name]["last_window_ref"]=str(win_num)

    notify.success("group '{}' opened".format(new_group_name), obj_monitor=active_monitor)

def get_launch_window(cmd, win_class, active_monitor, obj_monitors):
    launch_window=Window_open(obj_monitors=obj_monitors).execute(cmd)
    while not launch_window.has_window(win_class):
        user_continue=Prompt_boolean(dict(monitor=active_monitor, title="Scriptjob open", prompt_text="Can't open a window with cmd\n'{}'\nDo you want to wait?".format(cmd))).loop().output
        if user_continue is False or user_continue == "_aborted":
            notify.error("Scriptjob command 'open' canceled.", obj_monitor=active_monitor)
            sys.exit(1)
    window=launch_window.window
    return window

def position_window(win_name, obj_monitors, dy_group_monitors, window):
    window.focus()
    tile=None
    monitor=0
    num_monitors=len(obj_monitors.monitors)

    if num_monitors in dy_group_monitors:
        if win_name in dy_group_monitors[num_monitors]:
            if "monitor" in dy_group_monitors[num_monitors][win_name]:
                user_monitor=dy_group_monitors[num_monitors][win_name]["monitor"]
                monitor=obj_monitors.get_real_index(user_monitor)
            if "tile" in dy_group_monitors[num_monitors][win_name]:
                tile=dy_group_monitors[num_monitors][win_name]["tile"]

    window.tile(tile, monitor)

def set_rc_path(filenpa_rc, cmds):
    with open(filenpa_rc, "w") as f:
        f.write("#!/bin/bash\n")
        filenpa_bashrc=os.path.join(os.path.expanduser("~"), ".bashrc")
        with open(filenpa_bashrc, "r") as content_bashrc:
            f.write("{}\n".format(content_bashrc.read()))
        for cmd in cmds:
            f.write("{}\n".format(cmd))
        f.write("rm '{}'\n".format(filenpa_rc))

# class MyRadio_button_list(pkg.Radio_button_list):
#     def __init__(self, options):
#         pkg.Radio_button_list.__init__(self, options)
#         self.rads[0].bind("<Button-3>", lambda event: self.my_function()) # disable typing in text
#         self.rads[0].bind("<Button-1>", lambda event: self.my_overrided_binding(event))
#         self.rads[0].bind("<Button-1>", self.added_function_on_bind, add="+")

#     def added_function_on_bind(self, event):
#         print("I added another function to bind Button-1")

#     def my_function(self):
#         print("I added a bind to an existing element")

#     def my_overrided_binding(self, event):
#         print("I added an my_overrided_binding to an existing element")
#         event.widget.focus_set()

#     def validate(self, e=None):
#         if e is not None:
#             name=str(e.widget).split(".")[-1]
#             e.widget.focus_set()
#             if name != "btn_ok":
#                 if hasattr(e.widget, 'invoke'):
#                     e.widget.invoke()
            
#         self.output="I overrided a function"

#         self.root.destroy()

# print(MyRadio_button_list(options).loop().output)

# print(pkg.Prompt_boolean(dict(prompt_text="Do you want to continue?")).loop().output)
# print(pkg.Prompt_boolean(dict(prompt_text="Do you want to continue?", YN="n")).loop().output)
