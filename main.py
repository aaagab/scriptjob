#!/usr/bin/env python3

if __name__ == "__main__":
    from pprint import pprint
    import importlib
    import json
    import os
    import sys
    import yaml
    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(direpa_script)
    module_name=os.path.basename(direpa_script)
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    def seed(pkg_major, direpas_configuration=dict(), fun_auto_migrate=None):
        fun_auto_migrate()
    etconf=pkg.Etconf(enable_dev_conf=False, tree=dict(), seed=seed)

    args, dy_app=pkg.Options(
        direpa_configuration=etconf.direpa_configuration,
        examples=None, 
        filenpa_app="gpm.json", 
        filenpa_args="config/options.json"
    ).get_argsns_dy_app()

    app_mode="prod"
    prefix=""
    if os.path.exists(os.path.join(direpa_script, ".git")):
        app_mode="dev"
        prefix="-dev"

    filen_scriptjob_json="scriptjob-state-{}{}.json".format(dy_app["version"].split(".")[0], prefix)
    filenpa_settings=os.path.join(etconf.direpa_configuration, "settings{}.json".format(prefix))
    direpa_tmp=os.path.join(os.path.expanduser("~"), "fty", "tmp", "s", "scriptjob")
    os.makedirs(direpa_tmp, exist_ok=True)
    filenpa_state=os.path.join(direpa_tmp, filen_scriptjob_json)

    session=pkg.Session(
        direpa_tmp,
        filenpa_settings,
        filenpa_state,
    )

    if args.launch.here:
        direpa_groups=os.path.join(etconf.direpa_configuration, "groups")
        os.makedirs(direpa_groups, exist_ok=True)

        dy_group_info=pkg.get_dy_group_info(args.launch.value, direpa_groups, session.dy_settings, args.prompt_group.here, session.active_monitor)
        group_name=dy_group_info["name"]
        filenpa_group=dy_group_info["filenpa"]
        session.dy_vars["GROUP"]=group_name
        dy_group=pkg.get_dy_group(direpa_groups, group_name, filenpa_group, session.dy_settings, session.active_monitor, args.syntax.here)

        is_prompt_windows=False
        if args.search.here is True:
            direpa_pkg=pkg.get_gpkg_path(
                session.dy_settings,
                session.dy_vars,
                session.filenpa_settings,
                session.active_monitor,
                direpa_search=args.root_dir.value,
                app_name=args.search.value,
                index=args.index.value,
            )

            session.dy_vars["GROUP"]=args.search.value
            session.dy_vars["PATH_APP"]=direpa_pkg
        elif args._from.here is True:
            if args._from.value is None:
                session.dy_vars["PATH_APP"]=os.getcwd()
            else:
                session.dy_vars["PATH_APP"]=os.path.dirname(args._from.value)

            session.dy_vars["GROUP"]=args.group.value
            if session.dy_vars["GROUP"] is None:
                session.dy_vars["GROUP"]=group_name
        elif args.prompt_windows.here is True:
            session.dy_vars["GROUP"]=group_name
            is_prompt_windows=True
        else:
            pkg.notify.error("--launch needs either --from, --search, or --prompt-windows argument.", obj_monitor=session.active_monitor, exit=1)

        dy_vars=dict()
        if is_prompt_windows is False:
            if "variables" in dy_group:
                var_key="vars_default_sets"
                if var_key in session.dy_settings:
                    vars_set_name=args.vars.value
                    if vars_set_name is None:
                        if group_name in session.dy_settings[var_key]:
                            vars_set_name=session.dy_settings[var_key][group_name]
                        else:
                            pkg.notify.error("launcher '{}' not found as a key in '{}' at '{}'.".format(group_name, var_key, session.filenpa_settings), obj_monitor=session.active_monitor, exit=1)
                    if vars_set_name in dy_group["variables"]:
                        dy_vars=dy_group["variables"][vars_set_name]
                    else:
                        pkg.notify.error("For launcher '{}' key '{}' not found in 'variables' at '{}'.".format(group_name, vars_set_name, var_key, filenpa_group), obj_monitor=session.active_monitor, exit=1)        
                else:
                    pkg.notify.error("'{}' not set in '{}'.".format(var_key, session.filenpa_settings), obj_monitor=session.active_monitor, exit=1)

                for var_name in sorted(dy_vars):
                    dy_vars[var_name]=dy_vars[var_name].format(**session.dy_vars)

        pkg.launch(
            dy_group,
            session.dy_vars,
            session.dy_state,
            dy_vars,
            is_prompt_windows,
            session.active_window_hex_id,
            session.active_monitor,
            session.obj_monitors,
            session.dy_desktop_windows,
        )
    elif args.execute.here:
        pkg.execute(
            session.dy_state,
            session.active_window_hex_id,
            session.active_monitor,
        )
    elif args.switch_group.here:
        direction=None
        if args.switch_group.value is None:
            if args.previous.here:
                direction="previous"
            elif args.next.here:
                direction="next"

        pkg.switch_group(
            session.dy_state,
            session.active_monitor,
            session.active_window_hex_id,
            direction,
            group_name=args.switch_group.value
        )
    elif args.close.here:
        pkg.close(
            session.dy_state,
            session.active_monitor,
            session.obj_monitors,
            to_close_group_names=args.close.values,
            close_all=args.all.here,
        )
    elif args.focus_window.here:
        window_type=None
        if args.active_group.here:
            if args.last.here:
                window_type="last"
            elif args.next.here:
                window_type="next"
            elif args.previous.here:
                window_type="previous"
        elif args.last_global.here:
            window_type="last_global"
        else:
            pkg.notify.warning("--focus-window needs either argument --active-group or --last-global.", obj_monitor=session.active_monitor,  exit=1)

        pkg.focus_window(
            session.dy_state,
            session.active_monitor,
            session.active_window_hex_id,
            window_type=window_type,
        )
    elif args.focus_group.here:
        command=None
        if args.last.here:
            command="last"
        elif args.next.here:
            command="next"
        elif args.previous.here:
            command="previous"
        elif args.add.here:
            command="add"
        elif args.delete.here:
            command="delete"
        elif args.toggle.here:
            command="toggle"
        else:
            pkg.notify.warning("--focus-group needs either argument --last, --next, --previous, --add, --delete, or --toggle.", obj_monitor=session.active_monitor,  exit=1)

        pkg.focus_group(
            session.dy_state,
            session.active_monitor,
            session.active_window_hex_id,
            session.obj_monitors,
            session.dy_existing_regular_windows,
            session.dy_desktop_windows,
            command=command,
        )

    session.save()