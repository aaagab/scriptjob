
# Scriptjob

Scriptjob is a coding production tool for X11. It is close to a windows manager at the difference that it works at a higher level. It gathers windows into groups that are defined by the user. Each window in a group can be set with one or multiple actions. Scriptjob allows to work on multiple coding projects at the same time without being overwhelmed by the number of opened windows. Each setup can be saved in order to be restored later. The commands of this software are intended to be triggered with hotkeys (.i.e xbindkeys).  


## Incomplete minimal documentation

.xbindkeysrc  
```rcfile
# ; prompt
# ; sudo apt-get install zenity
# ; killall
# ; sudo apt-get install psmisc

# List of modifier:
#   Release, Control, Shift, Mod1 (Alt), Mod2 (NumLock),
#   Mod3 (CapsLock), Mod4, Mod5 (Scroll).

"prompt 'Xbindkeys config loaded'"
    control+shift + q

"killall xbindkeys; xbindkeys && prompt 'Xbindkeys config reloaded'"
    Mod4 + F3

"/usr/bin/code ~/.xbindkeysrc"
    Mod4 + Shift + F3

"scriptjob --execute f3"
    F3

"scriptjob --execute shiftF1"
    Shift + F1

"scriptjob --focus --window --active-group --next"
    Shift + F3

"scriptjob --focus --group --add"
    Mod1 + a

"scriptjob --switch-group"
    Mod1 + g

"scriptjob --focus --group --next"
    Mod1 + Shift + f

"scriptjob --focus --group --toggle"
    Mod1 + f

"scriptjob --launch --prompt-group --prompt-windows"
    Mod1 + t
```

```bash
# get application class:  
wmctrl -lGpx
```

```json
//  examples built-in variables when populated
{
    "GROUP": "message",
    "PATH_APP": "/home/john/fty/wrk/m/message/1",
    "PWD": "/home/john/fty/wrk/s/scriptjob/1/src",
    "SEP": "/",
    "TMP_FILE": "/home/john/fty/tmp/s/scriptjob/scriptjob-tmp-16288737554948573",
    "USER": "john",
    "USERPROFILE": "/home/john"
}
```

```json
// settings.json sample
{
    "root_dir": "{USERPROFILE}{SEP}fty{SEP}wrk",
    "default_group": "cmd-dev",
    "vars_default_sets": {
        "cmd-dev": "default"
    },
}
```

```yaml
# groups\cmd-dev.yaml sample
windows:
  - class: "konsole"
    command: |
      konsole
      -p
      tabtitle={APP_NAME}
      -e
      bash
      --rcfile
      {RCFILE_PATH}
    execute: 
      f3: |
        focus last
      shiftF1: |
        focus last
    name: terminal
    rcfile:
      path: "{RCFILE_PATH}"
      content: |
        cd "{PATH_SRC}"
  - class: "vscodium"
    command: |
      codium
      --new-window
      {PATH_EDITOR}
    execute: 
      f3: |
        send-keys 2 Ctrl+s
        sleep .05
        focus 1
        send-keys 1 Up
        sleep .05
        send-keys 1 Return
      shiftF1: |
        sleep .05
        send-keys 2 Ctrl+c
        sleep .3
        focus 1
        send-keys 1 Ctrl+Shift+v
    name: editor

variables:
  default:
    APP_NAME: "{GROUP}"
    PATH_EDITOR: "{PATH_APP}"
    RCFILE_PATH: "{TMP_FILE}"
    PATH_SRC: "{PATH_APP}{SEP}src"
  flat:
    APP_NAME: "{GROUP}"
    PATH_EDITOR: "{PATH_APP}"
    RCFILE_PATH: "{TMP_FILE}"
    PATH_SRC: "{PATH_APP}"

monitors:
  1:
    editor:
      tile: maximize
    terminal:
      tile: left
  2:
    editor:
      tile: maximize
      monitor: 2
    terminal:
      tile: right
      monitor: 1
```

```json
// tmp/s/scriptjob/scriptjob-state-{major_version}.json
// this file is generated automatically ()
{
    "active_group": "bwins",
    "focus": {
        "last_window_id": "0x840000c",
        "windows": [
            "0x7a0000c",
            "0x840000c"
        ]
    },
    "groups": [
        {
            "last_window_ref": 2,
            "name": "guitools",
            "timestamp": 1725568197.9459069,
            "windows": [
                {
                    "execute": [
                        {
                            "commands": [
                                "focus last"
                            ],
                            "shortcut": "f3"
                        },
                        {
                            "commands": [
                                "focus last"
                            ],
                            "shortcut": "shiftF1"
                        }
                    ],
                    "hex_id": "0x900000d",
                    "ref": 1,
                    "refs": [],
                    "timestamp": 1725568198.5902817
                },
                {
                    "execute": [
                        {
                            "commands": [
                                "send-keys 2 Ctrl+s",
                                "sleep .05",
                                "focus 1",
                                "send-keys 1 Up",
                                "sleep .05",
                                "send-keys 1 Return"
                            ],
                            "shortcut": "f3"
                        },
                        {
                            "commands": [
                                "sleep .05",
                                "send-keys 2 Ctrl+c",
                                "sleep .3",
                                "focus 1",
                                "send-keys 1 Ctrl+Shift+v",
                                "sleep .05",
                                "send-keys 1 Return"
                            ],
                            "shortcut": "shiftF1"
                        }
                    ],
                    "hex_id": "0x6e00058",
                    "ref": 2,
                    "refs": [
                        1
                    ],
                    "timestamp": 1725568199.523551
                }
            ]
        },
        {
            "last_window_ref": 2,
            "name": "bwins",
            "timestamp": 1725568205.5930552,
            "windows": [
                {
                    "execute": [
                        {
                            "commands": [
                                "focus last"
                            ],
                            "shortcut": "f3"
                        },
                        {
                            "commands": [
                                "focus last"
                            ],
                            "shortcut": "shiftF1"
                        }
                    ],
                    "hex_id": "0x920000d",
                    "ref": 1,
                    "refs": [],
                    "timestamp": 1725568206.3183305
                },
                {
                    "execute": [
                        {
                            "commands": [
                                "send-keys 2 Ctrl+s",
                                "sleep .05",
                                "focus 1",
                                "send-keys 1 Up",
                                "sleep .05",
                                "send-keys 1 Return"
                            ],
                            "shortcut": "f3"
                        },
                        {
                            "commands": [
                                "sleep .05",
                                "send-keys 2 Ctrl+c",
                                "sleep .3",
                                "focus 1",
                                "send-keys 1 Ctrl+Shift+v",
                                "sleep .05",
                                "send-keys 1 Return"
                            ],
                            "shortcut": "shiftF1"
                        }
                    ],
                    "hex_id": "0x6e00059",
                    "ref": 2,
                    "refs": [
                        1
                    ],
                    "timestamp": 1725568207.2767572
                }
            ]
        }
    ],
    "last_window_id": "0x6a0000d"
}
```
