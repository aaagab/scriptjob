windows: a software window is identified by a window id
windows groups: windows groups are defined by a name
for each window a series of actions can be defined.
Actions:  
- execute_terminal:
    - window_id,
    - path,
    - exe_terminal
- send keypress to windows (ex:refresh_browser):
    - window_id
    - send-key
- active_group_previous_window
- focus_window
    - window_id
    - --next window_ids window_id
    - --previous window_ids window_id

predefined actions.


hotkeys:
	F1:         | --previous-window active_group | 
	F3:         | --execute | 
	Shift F1:   | --previous-window global | 
	Shift F2:   | --previous-window global | 
	Shift F3:   | --switch-window next | 
	Alt a:      | --add-group | 
	Alt c:      | --close | 
	Alt g:      | --switch-group | 
	Alt e:      | --focus-command explorer | 
	Alt f:      | --focus-command browser | 
	Alt o:      | --open-explorer | 
	Alt q:      | --focus-command editor | 
	Alt t:      | --quick-action terminal | 



```json
// /home/$USER/fty/etc/s/scriptjob/43f5e40be7e74ee6b3d90c6b1e29e795/8/settings.json
{
    "actions": [
        {
            "name": "execute_terminal",
            "label": "Execute terminal",
            "parameters": [
                {
                    "type": "active_window"
                },
                {
                    "prompt": "Choose a destination terminal window:",
                    "type": "window_hex_id",
                    "exe_names": ["konsole", "xterm"]
                }
            ]
        },
        {
            "name": "refresh_browser",
            "label": "Refresh Browser",
            "parameters": [
                {
                    "type": "active_window"
                },
                {
                    "prompt": "Choose a browser to refresh:",
                    "type": "window_hex_id",
                    "exe_names": ["firefox", "firefox-bin", "chrome"]
                }
            ]
        },
        {
            "name": "active_group_previous_window",
            "label": "Go to previous window on active group",
            "parameters": [
                {
                    "type": "previous_window_hex_id"
                }
            ]
        }
    ],
    "default_applications": {
        "browser": "firefox",
        "editor": "codium",
        "explorer": "dolphin",
        "terminal": "konsole"
    },
    "exes": [
        {
            "name": "dolphin",
            "new_tab": "app_parameters",
            "path_dialog": true,
            "shared": true
        },
        {
            "exec_cmds": "-e bash --rcfile '{PATH}'",
            "name": "konsole",
            "title": "-p tabtitle='{TITLE}'"
        },
        {
            "name": "firefox",
            "new_tab": "--new-tab '{PATH}'",
            "new_window": "--new-window '{PATH}'",
            "shared": true
        },
        {
            "name": "chrome",
            "new_tab": "--new-tab '{PATH}'",
            "new_window": "--new-window '{PATH}'",
            "shared": true
        },
        {
            "name": "codium",
            "new_tab": "--add",
            "new_window": "--new-window '{PATH}'",
            "path_dialog": true
        },
        {
            "name": "kate",
            "new_tab": "--block '{PATH}'",
            "new_window": "--new '{PATH}'"
        }
    ]
}
```