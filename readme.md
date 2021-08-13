
# Scriptjob Incomplete minimal documentation

```bash
# Recommended Hotkeys:
	F3:           | scriptjob --execute
	Shift F3:     | scriptjob --focus-window next
	Alt e:        | scriptjob --focus-group --next
	Alt f:        | scriptjob --focus-group toggle
	Alt Shift f:  | scriptjob --focus-group --next
    Alt t:        | scriptjob --launch --prompt-group --prompt-windows

# Command typed often:
scriptjob --close
scriptjob --launch --search message
# line above is equivalent to line below
scriptjob -l -s message
# it works with default variables set in settings: root_dir, default_group, vars_default_sets
scriptjob --focus-group --add
scriptjob --fg --add
scriptjob --focus-group --delete
scriptjob --fg --delete
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
    execute: |
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
    execute: |
      send-keys 2 Ctrl+s
      sleep .05
      focus 1
      send-keys 1 Up
      sleep .05
      send-keys 1 Return
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
    "active_group": "message_2",
    "focus": {
        "last_window_id": null,
        "windows": []
    },
    "groups": {
        "message": {
            "last_window_ref": "2",
            "timestamp": 1628864581.397561,
            "windows": {
                "1": {
                    "execute": [
                        "focus last"
                    ],
                    "hex_id": "0x7200007",
                    "refs": [],
                    "timestamp": 1628864582.1277504
                },
                "2": {
                    "execute": [
                        "send-keys 2 Ctrl+s",
                        "sleep .05",
                        "focus 1",
                        "send-keys 1 Up",
                        "sleep .05",
                        "send-keys 1 Return"
                    ],
                    "hex_id": "0x600008a",
                    "refs": [
                        "1"
                    ],
                    "timestamp": 1628864583.1044211
                }
            }
        },
        "message_2": {
            "last_window_ref": "2",
            "timestamp": 1628864744.1166492,
            "windows": {
                "1": {
                    "execute": [
                        "focus last"
                    ],
                    "hex_id": "0x7800007",
                    "refs": [],
                    "timestamp": 1628864744.8942006
                },
                "2": {
                    "execute": [
                        "send-keys 2 Ctrl+s",
                        "sleep .05",
                        "focus 1",
                        "send-keys 1 Up",
                        "sleep .05",
                        "send-keys 1 Return"
                    ],
                    "hex_id": "0x600008a",
                    "refs": [
                        "1"
                    ],
                    "timestamp": 1628864745.9618664
                }
            }
        }
    },
    "last_window_id": "0x7000007"
}
```
