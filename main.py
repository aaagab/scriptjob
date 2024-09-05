#!/usr/bin/env python3

if __name__ == "__main__":
    from pprint import pprint
    import importlib
    import json
    import os
    import sys
    import typing
    import yaml
    import time
    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(direpa_script)
    module_name=os.path.basename(direpa_script)
    sys.path.insert(0, direpa_script_parent)
    if typing.TYPE_CHECKING:
        import __init__ as package #type:ignore

    pkg:"package" = importlib.import_module(module_name)
    del sys.path[0]

    def get_msg(text, main_arg, args):
        prefix="At command-line '{}'".format(main_arg._get_cmd_line())
        args_text=", ".join(sorted([arg._default_alias for arg in args]))
        return "{} {}: {}".format(prefix, text, args_text)

    def seed(pkg_major, direpas_configuration=dict(), fun_auto_migrate=None):
        fun_auto_migrate()
    etconf=pkg.Etconf(enable_dev_conf=False, tree=dict(), seed=seed)

    try:
        nargs=pkg.Nargs(
            metadata=dict(executable="scriptjob"), 
            options_file="config/options.yaml",
            path_etc=etconf.direpa_configuration,
            raise_exc=True,
        )
        args=nargs.get_args()

        filenpa_state=args.state._value
        direpa_tmp=os.path.join(os.path.expanduser("~"), "fty", "tmp", "s", "scriptjob")
        os.makedirs(direpa_tmp, exist_ok=True)
        if filenpa_state is None:
            filen_scriptjob_json="scriptjob-state-{}.json".format(nargs.metadata["version"].split(".")[0])
            filenpa_state=os.path.join(direpa_tmp, filen_scriptjob_json)

        timeit=pkg._TimeIt()
        session=pkg.Session(
            direpa_tmp,
            filenpa_state,
        )

        if args.launch._here:
            if args.launch.prompt_group._here:
                if args.launch.search._here is False:
                    pkg.notify.error("--search is required when using --prompt-group")
                    sys.exit(1)
            filenpa_settings=os.path.join(etconf.direpa_configuration, "settings.json")
            dy_settings:dict[str, str]=dict()
            with open(filenpa_settings, "r") as f:
                dy_settings=json.load(f)

            direpa_groups=args.launch.groups._value
            if direpa_groups is None:
                direpa_groups=os.path.join(etconf.direpa_configuration, "groups")
            os.makedirs(direpa_groups, exist_ok=True)

            dy_group_info=pkg.get_dy_group_info(
                group_name=args.launch._value,
                direpa_groups=direpa_groups,
                prompt_group=args.launch.prompt_group._here,
                default_group=dy_settings.get("default_group")
            )
            group_name=dy_group_info["name"]
            filenpa_group=dy_group_info["filenpa"]
            session.vars.GROUP=group_name
            dy_group=pkg.get_dy_group(
                direpa_groups=direpa_groups,
                group_name=group_name,
                filenpa_group=filenpa_group,
                parse_syntax=args.launch.syntax._here,
                vars_default_sets=dy_settings.get("vars_default_sets"),
            )

            is_prompt_windows=False
            vars_set_name=None
            if args.launch.search._here is True:
                direpa_pkg=pkg.get_gpkg_path(
                    root_dir=dy_settings.get("root_dir"),
                    vars=session.vars,
                    filenpa_settings=filenpa_settings,
                    direpa_search=args.launch.search.root_dir._value,
                    app_name=args.launch.search._value,
                    index=args.launch.search.index._value,
                )

                session.vars.GROUP=args.launch.search._value
                session.vars.PATH_APP=direpa_pkg
                vars_set_name=args.launch.search.vars._value
            elif args.launch.from_._here is True:
                if args.launch.from_._value is None:
                    session.vars.PATH_APP=os.getcwd()
                else:
                    session.vars.PATH_APP=os.path.dirname(args.launch.from_._value)

                session.vars.GROUP=args.launch.from_.group._value
                if session.vars.GROUP is None:
                    session.vars.GROUP=group_name
                
                vars_set_name=args.launch.from_.vars._value
            elif args.launch.prompt_windows._here is True:
                session.vars.GROUP=group_name
                is_prompt_windows=True
            else:
                error_message=get_msg("missing one required argument from", args.launch, [args.launch.from_, args.launch.search, args.launch.prompt_windows])
                pkg.notify.error(error_message)
                sys.exit(1)

            dy_vars=dict()
            if is_prompt_windows is False:
                if "variables" in dy_group:
                    var_key="vars_default_sets"
                    if var_key in dy_settings:
                        if vars_set_name is None:
                            if group_name in dy_settings[var_key]:
                                vars_set_name=dy_settings[var_key][group_name]
                            else:
                                pkg.notify.error("launcher '{}' not found as a key in '{}' at '{}'.".format(group_name, var_key, filenpa_settings))
                                sys.exit(1)
                        if vars_set_name in dy_group["variables"]:
                            dy_vars=dy_group["variables"][vars_set_name]
                        else:
                            pkg.notify.error("For launcher '{}' key '{}' not found in 'variables' at '{}'.".format(group_name, vars_set_name, filenpa_group))        
                            sys.exit(1)
                    else:
                        pkg.notify.error("'{}' not set in '{}'.".format(var_key, filenpa_settings))
                        sys.exit(1)

                    for var_name in sorted(dy_vars):
                        dy_vars[var_name]=dy_vars[var_name].format(**session.vars.__dict__)

            pkg.launch(
                dy_group=dy_group,
                session_vars=session.vars,
                state=session.state,
                dy_group_vars=dy_vars,
                is_prompt=is_prompt_windows,
                active_window_hex_id=session.active_window_hex_id,
                desktop_win_hex_ids=session.desktop_win_hex_ids,
            )
        elif args.execute._here:
            pkg.execute(
                state=session.state,
                active_window_hex_id=session.active_window_hex_id,
                shortcuts=args.execute._values,
                window_ref=args.execute.window._value,
                group_name=args.execute.group._value,
            )
        elif args.switch_group._here:
            direction:str|None=None
            if args.switch_group._value is None:
                if args.switch_group.previous._here:
                    direction="previous"
                elif args.switch_group.next._here:
                    direction="next"

            pkg.switch_group(
                state=session.state,
                active_window_hex_id=session.active_window_hex_id,
                direction=direction,
                group_name=args.switch_group._value
            )
        elif args.close._here:
            pkg.close(
                state=session.state,
                to_close_group_names=args.close._values,
                close_all=args.close.all._here,
            )
        elif args.focus._here:
            if args.focus.window._here:
                window_type=None
                if args.focus.window.active_group._here:
                    if args.focus.window.active_group.last._here:
                        window_type="last"
                    elif args.focus.window.active_group.next._here:
                        window_type="next"
                    elif args.focus.window.active_group.previous._here:
                        window_type="previous"
                elif args.focus.window.last_global._here:
                    window_type="last_global"

                pkg.focus_window(
                    state=session.state,
                    active_window_hex_id=session.active_window_hex_id,
                    window_type=window_type,
                )
            elif args.focus.group._here:
                command:str|None=None
                if args.focus.group.last._here:
                    command="last"
                elif args.focus.group.next._here:
                    command="next"
                elif args.focus.group.previous._here:
                    command="previous"
                elif args.focus.group.add._here:
                    command="add"
                elif args.focus.group.delete._here:
                    command="delete"
                elif args.focus.group.toggle._here:
                    command="toggle"

                pkg.focus_group(
                    state=session.state,
                    active_window_hex_id=session.active_window_hex_id,
                    dy_existing_regular_windows=session.dy_existing_regular_windows,
                    desktop_win_hex_ids=session.desktop_win_hex_ids,
                    command=command,
                )

        session.save()
    except pkg.EndUserError as ex:
        pkg.notify.error(ex)
        sys.exit(1)
    