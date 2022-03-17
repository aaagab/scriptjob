
# Scriptjob Incomplete minimal documentation

```bash
# Recommended Hotkeys:
	shiftF1:           | scriptjob --execute shiftF1
	F3:           | scriptjob --execute F3
	Shift F3:     | scriptjob --focus --window --active-group --next
    Alt a:        | scriptjob --focus --group --add
	Alt f:        | scriptjob --focus --group --toggle
	Alt Shift f:  | scriptjob --focus --group --next
    Alt t:        | scriptjob --launch --prompt-group --prompt-windows

# Command typed often:
scriptjob --close
scriptjob --launch --search message
# line above is equivalent to line below
scriptjob -l@s=message
# it works with default variables set in settings: root_dir, default_group, vars_default_sets
scriptjob --focus --group --add
scriptjob --fg --add
scriptjob --focus --group --delete
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
    "monitors": {
        "VGA-1": 1,
        "HDMI-1": 2,
        "rdp0": 1
    }
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
// tmp/s/scriptjob/scriptjob-state-{major_version}-dev.json
// this file is generated automatically ()
{
    "active_group": "message",
    "focus": {
        "last_window_id": null,
        "windows": []
    },
    "groups": {
        "message": {
            "last_window_ref": "2",
            "timestamp": 1647525455.9285493,
            "windows": {
                "1": {
                    "execute": {
                        "f3": [
                            "focus last"
                        ],
                        "shiftF1": [
                            "focus last"
                        ]
                    },
                    "hex_id": "0x7c00007",
                    "refs": [],
                    "timestamp": 1647525456.5545356
                },
                "2": {
                    "execute": {
                        "f3": [
                            "send-keys 2 Ctrl+s",
                            "sleep .05",
                            "focus 1",
                            "send-keys 1 Up",
                            "sleep .05",
                            "send-keys 1 Return"
                        ],
                        "shiftF1": [
                            "sleep .05",
                            "send-keys 2 Ctrl+c",
                            "sleep .3",
                            "focus 1",
                            "send-keys 1 Ctrl+Shift+v"
                        ]
                    },
                    "hex_id": "0x620007a",
                    "refs": [
                        "1"
                    ],
                    "timestamp": 1647525457.5716422
                }
            }
        },
        "options": {
            "last_window_ref": "2",
            "timestamp": 1647525446.5373795,
            "windows": {
                "1": {
                    "execute": {
                        "f3": [
                            "focus last"
                        ],
                        "shiftF1": [
                            "focus last"
                        ]
                    },
                    "hex_id": "0x7e00007",
                    "refs": [],
                    "timestamp": 1647525447.0468535
                },
                "2": {
                    "execute": {
                        "f3": [
                            "send-keys 2 Ctrl+s",
                            "sleep .05",
                            "focus 1",
                            "send-keys 1 Up",
                            "sleep .05",
                            "send-keys 1 Return"
                        ],
                        "shiftF1": [
                            "sleep .05",
                            "send-keys 2 Ctrl+c",
                            "sleep .3",
                            "focus 1",
                            "send-keys 1 Ctrl+Shift+v"
                        ]
                    },
                    "hex_id": "0x6200079",
                    "refs": [
                        "1"
                    ],
                    "timestamp": 1647525447.8824177
                }
            }
        }
    },
    "last_window_id": "0x200007"
}
```
