#!/usr/bin/env python3
import sys
import os

def generate_group_name(group_name, groups):
    existing_group_names=[group["name"] for group in groups]

    index=2
    new_group_name=group_name
    while new_group_name in existing_group_names:
        new_group_name=group_name+"_"+str(index)
        index+=1

    return new_group_name
