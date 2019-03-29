#!/bin/bash
# this program switch from a define runtime environment (set its window name) to the previous used window which is generally a text editor

# get the minimum time execution for cmd sleep, in order to use it for xdotool because xdotool needs a wait time between each command
script_path="$( cd "$(dirname "$0")" ; pwd -P )"
script_full_path="$script_path/"$(basename "$0")
min_wait=0.2
cmd_name="$1"

# get_key_pressed="/mnt/data/thisdocs/config/script/my-bin/get_key_pressed"

prompt()
{
	zenity --notification --text="$1" --timeout=1 2> /dev/null
}

# 
# if command -v get_key_pressed; then
#   prompt 'Error: get_key_pressed is not installed.'
#   exit 1
# else
#   prompt 'Installed'
# fi

# get_key_pressed


# exit



get_window_full_name()
{
	local id=$1
	local win_name=$(wmctrl -l | grep $(printf '%x\n' $id)| awk '{$1=$2=$3="";print $0;}' | trim)
	echo "$win_name"
}

curr_win_id()
{
	xdotool getactivewindow
}

db=$script_path"/data.db"

db_setup()
{
	local cmd=$( cat <<-EOF
		CREATE TABLE IF NOT EXISTS script_job (
			id INTEGER PRIMARY KEY,
			var_name TEXT,
			var_value TEXT
		);
		EOF
	)
	exec_db_cmd $LINENO "$cmd"
}

exec_db_cmd()
{
	if ! sqlite3 $db "$2"; then
		prompt "Error DB $BASH_SOURCE $1"
		kill $$
	fi
}

### obsolete part start
get_db_win_name()
{
# 	local win_name="$1"
	local cmd="select id from script_job where var_name = '${cmd_name}_selected_win_name';"
	local var_name=$(exec_db_cmd $LINENO "$cmd")
	local value;
	if [ -z "$var_name" ]; then
		cmd="insert into script_job (var_name) values ('${cmd_name}_selected_win_name');"
		exec_db_cmd $LINENO "$cmd"
	else
		cmd="select var_value from script_job where var_name = '${cmd_name}_selected_win_name';"	
		value=$(exec_db_cmd $LINENO "$cmd")
	fi
	echo "$value"
}

set_db_win_name()
{
	local val="$1"
# 	local win_name="$2"
	cmd="UPDATE script_job SET var_value = '$val' WHERE var_name = '${cmd_name}_selected_win_name';"
	exec_db_cmd $LINENO "$cmd"
}

### obsolete part end

# get_previous_win_id()
# {
# # 	local cmd_name="$1"
# 	local cmd="select id from script_job where var_name = '${cmd_name}_windows_2';"
# 	local var_name=$(exec_db_cmd $LINENO "$cmd")
# 	local value;
# 	if [ -z "$var_name" ]; then
# 		cmd="insert into script_job (var_name) values ('${cmd_name}_windows_2');"
# 		exec_db_cmd $LINENO "$cmd"
# 	else
# 		cmd="select var_value from script_job where var_name = '${cmd_name}_windows_2';"	
# 		value=$(exec_db_cmd $LINENO "$cmd")
# 	fi
# 	echo "$value"
# }

# set_previous_win_id()
# {
# 	local val="$1"
# 	cmd="UPDATE script_job SET var_value = '$val' WHERE var_name = '${cmd_name}_windows_2';"
# 	exec_db_cmd $LINENO "$cmd"
# }

get_user_input_win_name()
{
	local input=$(zenity --entry --text="Enter Window Name To Focus:" --entry-text "" 2> /dev/null);
	if [ ! -z "$input" ]; then
		echo "$input"
	else
		prompt "$(basename "$0") Terminated"
		killall "$(basename "$0")"
	fi
}

get_num_win()
{
	local db_win_name="$(get_db_win_name)"
	if [ -z "$db_win_name" ]; then
		echo -1
	else
		wmctrl -l | awk -v pattern="$(get_db_win_name)" '$0 ~ pattern{ print $1 }' | wc -l
	fi
}

get_all_windows_dimensions()
{
# 	xwininfo -id $(xdotool getactivewindow)
	unset window_ids
	unset pos_X_Y
	unset win_W_H
	
	readarray -t window_ids < <(wmctrl -l | awk '!/Plasma/{print $1}')
	
	# echo "${window_ids[@]}" > /tmp/mytext.txt
	# kate -n /tmp/mytext.txt
	# kill $$
	# exit

	for win_id in "${window_ids[@]}"; do
		posX=$(xwininfo -id $win_id | grep "Absolute upper-left X" | awk '{print $4}')
		posY=$(xwininfo -id $win_id | grep "Absolute upper-left Y" | awk '{print $4}')
		winW=$(xwininfo -id $win_id | grep "Width:" | awk '{ print $2}')
		winH=$(xwininfo -id $win_id | grep "Height" | awk '{print $2}')
		win_W_H+=("${winW} ${winH}")
		pos_X_Y+=("${posX} ${posY}")		
	done
	
}

pack_all_windows()
{
	unset count
	posX=60
	posY=35
	for win_id in "${window_ids[@]}"; do
		xdotool windowunmap --sync $win_id
		sleep .1
		xdotool windowsize $win_id 400 400
		xdotool windowmap   --sync $win_id
		
		# sleep .1
		wmctrl -i -a $win_id
		xdotool windowmove $win_id $posX $posY

		posX=$((posX+60))
		posY=$((posY+35))
		# sleep .3
	done
}

restore_window_positions()
{
	unset count
	count=0
	for win_id in "${window_ids[@]}"; do
		posX=$(echo "${pos_X_Y[$count]}" | awk '{print $1}')
		posY=$(echo "${pos_X_Y[$count]}" | awk '{print $2}')
		winW=$(echo "${win_W_H[$count]}" | awk '{print $1}')
		winH=$(echo "${win_W_H[$count]}" | awk '{print $2}')
		xdotool windowunmap --sync $win_id
		xdotool windowmove $win_id $posX $posY
		xdotool windowmap   --sync $win_id
		wmctrl -i -a $win_id
		xdotool windowsize $win_id $winW $winW

		((count++))
		sleep .02
	done
}


# get_all_windows_dimensions
# pack_all_windows
# sleep 5
# restore_window_positions

# exit

# get_selected_win_id()
# {
# 	while (( $(get_num_win) < 1 )) || (( $(get_num_win) > 1 )); do
# 		if (( $(get_num_win) == 0 )); then
# 			prompt "Error: Win Name does not Exist"
# 		elif (( $(get_num_win) < 1 )); then
# 			prompt "Error: Empty Win Name in DB"
# 		elif (( $(get_num_win) > 1 )); then
# 			prompt "Error: $(get_num_win) matching windows"
# 		fi
# # 		set_db_win_name "$(get_user_input_win_name)"
# 		set_db_win_name "$(get_manual_win_id)"
# 	done
# 	
# 	echo $((16#$(wmctrl -l | awk -v pattern="$(get_db_win_name)" '$0 ~ pattern{ print $1 }' | sed 's/^..//')))
# }

# get_input()
# {
# 	local input=$(get_key_pressed)
# 	prompt "$input"
# }
# 
# get_key_pressed
# 
# exit

get_manual_win_id()
{
# 	prompt "here 2"
	
	if ! is_mutiple_monitor; then
		get_all_windows_dimensions
		pack_all_windows
	fi
	unset input
	input=$(timeout 8 get_key_pressed single)
	if [ ! -z "$input" ]; then
		# if pressed escape, then exit program
		if echo "$input" | grep 'key\[9\]' > /dev/null; then
			if ! is_mutiple_monitor; then
				restore_window_positions
			fi
			prompt "Command Cancelled"
			killall "$(basename "$0")"
		fi
		# if pressed mouse left click then select this window
		if echo "$input" | grep 'button\[1\]' > /dev/null; then
			local win_info=$(xwininfo -id $(xdotool getactivewindow))
			local win_id=$(echo "$win_info" | awk '/Window id:/{ print $4 }')
			echo $((16#$(echo $win_id | sed 's/^..//')))
# 			prompt $((16#$(echo $win_id | sed 's/^..//')))
      prompt "Window $((16#$(echo $win_id | sed 's/^..//'))) Selected."
			break
		fi
	else
		if ! is_mutiple_monitor; then
			restore_window_positions
		fi
		prompt "Command Cancelled"
		killall "$(basename "$0")"
	fi
	
	if ! is_mutiple_monitor; then
		restore_window_positions
	fi
}

# prompt "select your window"
# get_manual_win_id
# 
# exit

get_app_pid()
{
	app=$1
	main_pid=$(pgrep $app)

	if [ -z "$main_pid" ]; then
		eval "{ $app & } &>/dev/null" && main_pid=$(pgrep $app)
		timer=0
		while (( $(wmctrl -lp | grep $main_pid | wc -l) == 0 )); do
			if (( timer > 20 )); then
				prompt "$app cannot start"
				killall "$(basename "$0")"
			fi
			sleep 1
			((timer++))
		done
		readarray -t pid_arr_1 < <(wmctrl -lp | grep $main_pid | awk '{ print $1}' |  sed 's/^..//' )
		echo $((16#${pid_arr_1[0]}))
	else
		readarray -t pid_arr_1 < <(wmctrl -lp | grep $main_pid | awk '{ print $1}' |  sed 's/^..//' )
		first_count=$(wmctrl -lp | grep $main_pid | wc -l)
		eval "{ $app & } &>/dev/null"
		
		timer=0
		while (( $(wmctrl -lp | grep $main_pid | wc -l) == $first_count )); do
			if (( timer > 20 )); then
				prompt "$app cannot start"
				killall "$(basename "$0")"
			fi
			sleep 1
			((timer++))
		done
		
		readarray -t pid_arr_2 < <(wmctrl -lp | grep $main_pid | awk '{ print $1}' |  sed 's/^..//' )

		i=0
		for p2 in "${pid_arr_2[@]}";do
			found=false
			j=0
			for p1 in "${pid_arr_1[@]}";do
				if [ "${pid_arr_2[i]}" == "${pid_arr_1[j]}" ]; then
					found=true
				fi
				((j++))
			done
			if ! $found; then
				echo $((16#${pid_arr_2[i]}))
				break
			fi
			((i++))
		done
	fi
}

db_delete_cmd_name()
{
	local val="$1"
	cmd="DELETE FROM script_job WHERE var_name LIKE '$val%';"
	exec_db_cmd $LINENO "$cmd"
  prompt "script_job cmd $val reset"

}

db_delete_all()
{
	cmd="DELETE FROM script_job;"
	exec_db_cmd $LINENO "$cmd"
  prompt "script_job cmd all reset"
}

cmd_save()
{
	# is_editor1=$(get_window_full_name $(curr_win_id) | grep "Kate")
	# is_editor2=$(get_window_full_name $(curr_win_id) | grep "Visual Studio Code")
	is_editor1="$(xprop -id $(curr_win_id) WM_CLASS) | grep kate"
	is_editor2="$(xprop -id $(curr_win_id) WM_CLASS) | grep code"
	if [ ! -z "$is_editor1" ] || [ ! -z "$is_editor2" ] ; then
		sleep $min_wait
		xdotool key ctrl+s
	fi
}

cmd_up_enter()
{
	sleep $min_wait
	xdotool key "Up"; xdotool key KP_Enter;
}

cmd_refresh()
{
	sleep $min_wait
	xdotool key F5;
}

get_num_screen()
{
	xrandr | grep ' connected' | wc -l
}

is_mutiple_monitor()
{
	if (( $(get_num_screen) > 1 )); then
		true
	else
		false
	fi
}

get_firefox()
{
	if pgrep -x "firefox" > /dev/null; then
		wmctrl -a "Mozilla Firefox"
	else
		{ firefox & } &> /dev/null && wmctrl -a "Mozilla Firefox"
	fi
}

get_db_win_id()
{
  local win_num="$1"
  local cmd="select id from script_job where var_name = '${cmd_name}_window_$win_num';"
  local var_name=$(exec_db_cmd $LINENO "$cmd")
  local value
  if [ -z "$var_name" ]; then
    cmd="insert into script_job (var_name) values ('${cmd_name}_window_$win_num');"
    exec_db_cmd $LINENO "$cmd"
  else
    cmd="select var_value from script_job where var_name = '${cmd_name}_window_$win_num';" 
    value=$(exec_db_cmd $LINENO "$cmd")
  fi
  echo "$value"
}

set_db_win_id()
{
  local win_num="$1"
  local win_id="$2"
  cmd="UPDATE script_job SET var_value = '$win_id' WHERE var_name = '${cmd_name}_window_$win_num';"
  exec_db_cmd $LINENO "$cmd"
}

in_db_win_num()
{
  local win_num="$1"
  if [ "$(get_db_win_id "$win_num")" == "" ] || [ -z "$(get_window_full_name $(get_db_win_id "$win_num"))" ]; then
    false
  else
    true
  fi
}

db_setup

if [ "$1" == "toggle" ]; then
# 	if db empty
	if ! in_db_win_num "2"; then
		# store curr_win_id in db
		set_db_win_id "2" $(curr_win_id)
		# then ask to select a new window and get its id in temporary variable
		prompt "Select another Toggle Win"
		tmp_id=$(get_manual_win_id)
		# then move to the tmp win
		wmctrl -i -a $tmp_id
 	# if db is not empty
	else
 		# if window exist
		# if active window == window in db
		if (( $(curr_win_id) == $(get_db_win_id "2") )); then 
			# ask to select a new window and get its id in temporary variable
			prompt "Select another Toggle Win"
			tmp_id=$(get_manual_win_id)
		else
		# else if active window != window in db
			# get previous__win_id in temp
			tmp_id=$(get_db_win_id "2")
			# store curr_win_id in db
			set_db_win_id "2" $(curr_win_id)
		fi
		# then move to the tmp win
		wmctrl -i -a $tmp_id;
	fi
# toggle-focus is for one window fixed and any other window
elif [ "$1" == "toggle-focus" ]; then
  if ! in_db_win_num "1"; then
    prompt "Click on Win To Focus"
    set_db_win_id "1" "$(get_manual_win_id)"
  fi
  
  if ! in_db_win_num "2"; then
    if (( $(get_db_win_id "1") == $(curr_win_id) )); then
      prompt "Click on Win To Toggle"
      set_db_win_id "2" "$(get_manual_win_id)"
    else
      set_db_win_id "2" $(curr_win_id)
    fi
  else
    if (( $(curr_win_id) == $(get_db_win_id "1") )); then
      wmctrl -i -a $(get_db_win_id "2")
    else
      set_db_win_id "2" $(curr_win_id)
      wmctrl -i -a $(get_db_win_id "1")
    fi
  fi
# toggle-two is for two chosen window
elif [ "$1" == "toggle-two" ]; then
  if ! in_db_win_num "1"; then
    prompt "Click on First Window"
    set_db_win_id "1" "$(get_manual_win_id)"
  fi
  
#   exit
    
  if ! in_db_win_num "2"; then
      prompt "Click on Second Window"
      set_db_win_id "2" "$(get_manual_win_id)"
      if (( $(get_db_win_id "1") == $(get_db_win_id "2") )); then
        prompt "Error Win Num 1 id == Win Num 2 id"
        db_delete_cmd_name ${cmd_name}
        exit
      fi
  else
    if (( $(get_db_win_id "1") == $(get_db_win_id "2") )); then
      prompt "Error Win Num 1 id == Win Num 2 id"
      db_delete_cmd_name ${cmd_name}
      exit
    elif (( $(curr_win_id) == $(get_db_win_id "1") )); then
      wmctrl -i -a $(get_db_win_id "2")
    else
      wmctrl -i -a $(get_db_win_id "1")
    fi
  fi
elif [ "$1" == "web-search" ]; then
# 	get_firefox
	if echo "$(get_window_full_name $(curr_win_id))" | grep "Mozilla Firefox"; then
		xdotool windowminimize $(curr_win_id)
	else
		get_firefox
	fi
elif [ "$1" == "web-dev" ] || [ "$1" == "bash" ]; then
	# if no selected window in db or if selected id does not match with any existing window
	if ! in_db_win_num "1"; then
		# select windows
		prompt "Click on $cmd_name Win"
		set_db_win_id "1" "$(get_manual_win_id)"
	fi
	
	# if no previous window in db or if previous id does not match any existing window
	if ! in_db_win_num "2"; then
# 		set previous window
		prompt "Click on toggle Win"
		set_db_win_id "2" $(get_manual_win_id)
		wmctrl -i -a $(get_db_win_id "1")
		if [ "$1" == "web-dev" ]; then
			cmd_refresh
		elif [ "$1" == "bash" ]; then
			cmd_up_enter
		fi
		
# 		wmctrl -i -a $(get_previous_win_id)
	else
		# from here both selected and previous win have been defined
		if (( $(curr_win_id) == $(get_db_win_id "2") )); then
			cmd_save
			wmctrl -i -a $(get_db_win_id "1")
			if [ "$1" == "web-dev" ]; then
				cmd_refresh
			elif [ "$1" == "bash" ]; then
				cmd_up_enter
			fi
# 			wmctrl -i -a $(get_previous_win_id)
		else
			if (( $(curr_win_id) == $(get_db_win_id "1") )); then
				wmctrl -i -a $(get_db_win_id "2")
			else
				set_db_win_id "2" $(curr_win_id)
				cmd_save
				wmctrl -i -a $(get_db_win_id "1")
				if [ "$1" == "web-dev" ]; then
					cmd_refresh
				elif [ "$1" == "bash" ]; then
					cmd_up_enter
				fi
# 				wmctrl -i -a $(get_previous_win_id)
			fi
		fi
	fi
elif [ "$1" == "web-search-test" ]; then
	# When a process is created it appears that the first windows has always the ID after erased and recreation
	# it means that the first window put in the database will be this ID, so instead of created a new window when one
	# already exists it just take its focus so any first window opened for the application will be the focus and any new
	# will serve for other purpose.
	if ! in_db_win_num "1"; then
		tmp_sel_id="$(get_app_pid "firefox")"
		set_db_win_id "1" "$tmp_sel_id"
	fi
	
	if [ "$(get_db_win_id "2")" == "" ]; then
		set_db_win_id "2" $(curr_win_id)
		tmp_id=$(get_manual_win_id)
		wmctrl -i -a $tmp_id
	else
		if [ -z "$(get_window_full_name $(get_db_win_id "2"))" ]; then
			set_db_win_id "2" $(curr_win_id)
			tmp_id=$(get_manual_win_id)
			wmctrl -i -a $tmp_id
		else
			if (( $(curr_win_id) == $(get_db_win_id "2") )); then 
				set_db_win_id "2" $(curr_win_id)
				if (( $(curr_win_id) == $(get_db_win_id "1") )); then
					tmp_id=$(get_manual_win_id)
					wmctrl -i -a $tmp_id
				else
					set_db_win_id "2" $(curr_win_id)
					wmctrl -i -a $(get_db_win_id "1")
				fi
			else
				tmp_id=$(get_db_win_id "2")
				set_db_win_id "2" $(curr_win_id)
				if (( $(curr_win_id) == $(get_db_win_id "1") )); then
					wmctrl -i -a $tmp_id
				else
					wmctrl -i -a $(get_db_win_id "1")
				fi
			fi
		fi
	fi
elif [ "$1" == "reset-db" ]; then
	case "$2" in
		toggle|toggle-focus|bash|web-dev|web-search|toggle-two)
			db_delete_cmd_name $2
			;;
		all)
			db_delete_all
			;;
	esac
fi

exit
# list pid before opening application





# then open application
# create another array
# compare value
# keep only the value that corresponds
# and do conversion


# echo
# i=0
# for p in "${pid_arr[@]}";do
# 	echo ${pid_arr[$i]}
# 	((i++))
# done

# 











