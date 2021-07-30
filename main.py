#!/usr/bin/env python3

if __name__ == "__main__":
    import importlib
    import json
    import os
    from pprint import pprint
    import sys
    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(direpa_script)
    module_name=os.path.basename(direpa_script)
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    def seed(pkg_major, direpas_configuration=dict(), fun_auto_migrate=None):
        fun_auto_migrate()
    etconf=pkg.Etconf(enable_dev_conf=False, tree=dict( files=dict({ "settings.json": dict() })), seed=seed)
    # print(etconf.direpa_configuration)

    # args, dy_app=pkg.Options(
    #     direpa_configuration=etconf.direpa_configuration,

    args, dy_app=pkg.Options(
        direpa_configuration=etconf.direpa_configuration,
        examples=None, 
        filenpa_app="gpm.json", 
        filenpa_args="config/options.json"
    ).get_argsns_dy_app()

    filen_save_json="scriptjob_save.json"
    filen_scriptjob_json="scriptjob-{}.json".format(dy_app["version"])
    direpa_wrk=os.path.join(os.path.expanduser("~"), "fty", "wrk")
    filenpa_settings=os.path.join(etconf.direpa_configuration, "settings.json")

    direpa_tmp=os.path.join(os.path.expanduser("~"), "fty", "tmp", "s", "scriptjob")
    os.makedirs(direpa_tmp, exist_ok=True)
    filenpa_state=os.path.join(direpa_tmp, filen_scriptjob_json)

    session=pkg.Session(
        filenpa_settings,
        filenpa_state,
    )

    pkg.update_groups(
        session.dy_settings["default_applications"],
        session.dy_state,
        session.actions,
    )

    if args.add_group.here:
        pkg.add_group(dy_app["name"], session.actions, session.dy_state)
    elif args.focus_command.here:
        pkg.focus_command(session.dy_settings["default_applications"], session.dy_state, args.focus_command.value)
    elif args.close.here:
        pkg.close(
            session.dy_settings["default_applications"],
            session.dy_state,
            session.actions,
            to_close_group_names=args.close.values,
        )
    elif args.open.here:
        pkg.open_json(
            dy_exes=session.dy_settings["exes"],
            dy_state=session.dy_state,
            filen_save_json=filen_save_json,
            filenpa_save_json=args.path_json.value,
            group_names=args.open.values,
        )
    elif args.open_explorer.here:
        pkg.open_explorer(session.dy_settings["default_applications"], session.dy_state, filen_scriptjob_json)
    elif args.switch_group.here:
        action="group"
        if args.previous.here:
            action="previous"
        elif args.next.here:
            action="next"
        pkg.switch_group(session.dy_state, action=action, group_name=args.switch_group.value)
    elif args.previous_window.here:
        pkg.previous_window(session.dy_state, args.previous_window.value)
    elif args.save.here:
        pkg.save(
            dy_app["name"],
            filen_scriptjob_json,
            session.dy_settings["exes"],
            session.dy_state,
            session.actions,
            dst_path=args.path_json.value,
            selected_group_names=args.save.values,
        )
    elif args.get_active_group_path.here:
        print(pkg.get_active_group_path(session.dy_state))
    elif args.quick_action.here:
        pkg.quick_action(dy_app["name"], session.actions, session.dy_state, args.quick_action.value)
    elif args.switch_window.here:
        pkg.switch_window(session.dy_state, args.switch_window.value)
    elif args.execute.here:
        pkg.execute(session.actions.obj_actions, session.dy_state)
    elif args.search_open.here:
        filenpa_save_json=pkg.get_search_open(
            filen_save_json,
            args.search_open.value,
            direpa_wrk=direpa_wrk,
            index=args.index.value,
        )

        pkg.open_json(
            dy_exes=session.dy_settings["exes"],
            dy_state=session.dy_state,
            filen_save_json=filen_save_json,
            filenpa_save_json=filenpa_save_json,
        )

    session.save()
