#!/bin/bash
 
echo "Hello! this is the Bash startup script for our Arduino controller"
 
# Build the full path name of our file
py_script_name="/home/cohenlab/Desktop/light_monitor_project/light_monitor.py"
echo $py_script_name
 
while true; do
	echo "Launching the Python script"
	lxterminal -e "python $py_script_name" # Launch a new terminal with our script
 
	echo "Waiting for the Python script to finish before launching a new one"
	sleep 2 # Wait a bit so we're sure the process was launched 
 
	PID=$(pgrep -f light_monitor.py) # Find the process name
	echo "Waiting for process $PID"
	while [ -d /proc/$PID ]; do
		sleep 5
	done
done