#!/usr/bin/env python3
# author: Gabriel Auger
# version: 5.0.0
# name: scriptjob
# license: MIT

import sys, os
import modules.options.options as ops
import importlib
import tempfile
from modules.json_config.json_config import Json_config
from modules.guitools.guitools import Windows
from dev.update_groups import update_groups
from dev.helpers import message
from pprint import pprint

if __name__ == "__main__":
    conf_options=Json_config()
    
    filenpa_script=os.path.realpath(__file__)
    direpa_script=os.path.dirname(filenpa_script)
    filenpa_gpm_json=os.path.join(direpa_script, "gpm.json")
    conf=Json_config(filenpa_gpm_json)

    conf_options.data.update(description=conf.data["description"])
    args, this_help=ops.get_args(sys.argv, conf_options.data)

    conf.data["args"]=vars(args)

    filenpa_scriptjob_json=os.path.join(
    tempfile.gettempdir(),
    conf.data["filen_scriptjob_json"]
    )

    if not os.path.exists(filenpa_scriptjob_json):
        with open(filenpa_scriptjob_json, "w") as f:
            f.write("{}")
            
    scriptjob_conf=Json_config(filenpa_scriptjob_json)
    scriptjob_conf.data["filenpa_scriptjob_json"]=filenpa_scriptjob_json

    if not args.help and not args.version:
        update_groups(conf.data, scriptjob_conf) 

    if args.help:
        print(this_help)
        sys.exit(0)

    if args.add_group:
        from dev.add_group import add_group
        add_group(conf.data, scriptjob_conf)
        scriptjob_conf.set_file_with_data()
        sys.exit(0)

    if args.focus_command:
        from dev.focus_command import focus_command
        focus_command(conf.data, scriptjob_conf)
        scriptjob_conf.set_file_with_data()
        sys.exit(0)

    if args.close:
        from dev.close import close
        if args.close is True:
            close(conf.data, scriptjob_conf)
        else:
            close(conf.data, scriptjob_conf, list(args.close))
        scriptjob_conf.set_file_with_data()
        sys.exit(0)

    if args.open:
        from dev.open import open_json
        if args.open is True:
            open_json(conf.data, scriptjob_conf)
        else:
            if len(args.open) > 1:
                open_json(conf.data, scriptjob_conf, args.open[0], args.open[1:] )
            else:
                open_json(conf.data, scriptjob_conf, args.open[0] )

        scriptjob_conf.set_file_with_data()
        sys.exit(0)

    if args.open_explorer:
        from dev.open_explorer import open_explorer
        open_explorer(conf.data, scriptjob_conf)
        scriptjob_conf.set_file_with_data()
        sys.exit(0)

    if args.switch_group:
        from dev.switch_group import switch_group
        if args.switch_group is True:
            switch_group(scriptjob_conf)
        else:
            switch_group(scriptjob_conf, *args.switch_group)
        sys.exit(0)

    if args.previous_window:
        from dev.previous_window import previous_window

        previous_window(scriptjob_conf, args.previous_window[0])
        scriptjob_conf.set_file_with_data()
        sys.exit(0)

    if args.save:
        from dev.save import save
        if args.save is True:
            save(conf.data, scriptjob_conf)
        elif len(args.save) == 1:
            save(conf.data, scriptjob_conf, args.save[0])
        else:
            save(conf.data, scriptjob_conf, args.save[0], args.save[1:])
        
        scriptjob_conf.set_file_with_data()
        sys.exit(0)
    
    if args.get_active_group_path is True:
        from dev.get_active_group_path import get_active_group_path
        print(get_active_group_path(scriptjob_conf))
        sys.exit(0)

    if args.quick_action:
        from dev.quick_action import quick_action
        quick_action(conf.data, scriptjob_conf, args.quick_action[0])
        scriptjob_conf.set_file_with_data()
        sys.exit(0)
        
    if args.switch_window:
        from dev.switch_window import switch_window
        switch_window(scriptjob_conf, args.switch_window[0])

        scriptjob_conf.set_file_with_data()
        sys.exit(0)

    if args.execute:
        from dev.execute import execute
        execute(conf.data, scriptjob_conf)
        scriptjob_conf.set_file_with_data()
        sys.exit(0)

    if args.search_open:
        from dev.search_open import search_open
        search_open(conf.data, args.search_open[0])
        sys.exit(0)

    if args.version is True:
        from modules.message.format_text import Format_text as ft
        lspace="  "
        print(lspace+ft.bold("Name: ")+conf.data["name"])
        print(lspace+ft.bold("Author(s): ")+", ".join(conf.data["authors"]))
        print(lspace+ft.bold("License(s): ")+", ".join(conf.data["licenses"]))
        print(lspace+ft.bold("Version: ")+conf.data["version"])
        sys.exit(0)
