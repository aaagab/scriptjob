#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from . import notify
from .session import Vars

from ..gpkgs.bwins import RadioButtonList, RadioButtonListOptions, RadioButtonItem, Monitors

def get_gpkg_path(
    root_dir:str|None,
    vars:Vars,
    filenpa_settings:str,
    direpa_search:str|None,
    app_name:str,
    index:int|None=None,
):
    if direpa_search is None:
        if root_dir is not None:
            direpa_search=root_dir.format(**vars.__dict__)
        else:
            notify.error("root_dir is not provided neither in cli arguments nor in settings '{}'.".format(filenpa_settings))
            sys.exit(1)

    if not os.path.exists(direpa_search):
        notify.error("root_dir not found '{}'.".format(direpa_search))
        sys.exit(1)

    direpa_app_name=os.path.join(direpa_search, app_name[0], app_name)
    if not os.path.exists(direpa_app_name):
        notify.warning("not found '{}'".format(direpa_app_name))
        sys.exit(1)

    diren:str
    items:list[RadioButtonItem]=[]
    for d in sorted(os.listdir(direpa_app_name)):
        items.append(RadioButtonItem(label=d))
    if index is None:
        if len(items) == 0:
            notify.error("There are no sub-folders at path '{}'.".format(direpa_app_name))
            sys.exit(1)
        elif len(items) == 1:
            diren=items[0].label
        else:
            options=RadioButtonListOptions(
                monitor=Monitors().get_primary_monitor(),
                items=items,
                title="scriptjob",
                prompt_text="For '{}' select a subfolder:".format(app_name),
            )
            output=RadioButtonList(options).loop().output
            if output is None:
                notify.warning("scriptjob launch '{}' canceled.".format(app_name))
                sys.exit(1)
            else:
                diren=output.label
    else:
        if index > len(items) or index < 1:
            notify.error("For '{}' wrong index '{}'. min 1 and max {}.".format(app_name, index, len(items)))
            sys.exit(1)
        else:
            diren=items[index-1].label
          
    direpa_gpkg=os.path.join(direpa_app_name, diren)
    notify.success("{} found at '{}'.".format(app_name, direpa_gpkg))

    return direpa_gpkg
