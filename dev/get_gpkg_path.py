#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from . import notify

from ..gpkgs.bwins import Radio_button_list

def get_gpkg_path(
    dy_settings,
    dy_vars,
    filenpa_settings,
    active_monitor,
    direpa_search,
    app_name,
    index=None,
):
    direpa_search=None
    if direpa_search is None:
        if "root_dir" in dy_settings:
            direpa_search=dy_settings["root_dir"].format(**dy_vars)
        else:
            notify.error("root_dir is not provided neither in cli arguments nor in settings '{}'.".format(filenpa_settings), exit=1)

    if not os.path.exists(direpa_search):
        notify.error("root_dir not found '{}'.".format(direpa_search), exit=1)

    direpa_app_name=os.path.join(direpa_search, app_name[0], app_name)
    if not os.path.exists(direpa_app_name):
        notify.warning("not found '{}'".format(direpa_app_name), active_monitor)
        sys.exit(1)

    diren=None
    direns=sorted(os.listdir(direpa_app_name))
    if index is None:
        if len(direns) == 0:
            notify.error("There are no sub-folders at path '{}'.".format(direpa_app_name), exit=1)
        elif len(direns) == 1:
            diren=direns[0]
        else:
            options=dict(
                items=direns,
                values=direns,
                title="scriptjob",
                prompt_text="For '{}' select a subfolder:".format(app_name),
            )
            diren=Radio_button_list(options).loop().output
            if diren == "_aborted":
                notify.warning("scriptjob launch '{}' canceled.".format(app_name), exit=1)
    else:
        if index > len(direns) or index < 1:
            notify.error("For '{}' wrong index '{}'. min 1 and max {}.".format(app_name, index, len(direns)), exit=1)
        else:
            diren=direns[index-1]
          
    direpa_gpkg=os.path.join(direpa_app_name, diren)
    notify.success("{} found at '{}'.".format(app_name, direpa_gpkg), active_monitor)

    return direpa_gpkg
