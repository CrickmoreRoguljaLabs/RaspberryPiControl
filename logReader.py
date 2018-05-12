import os
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk
import tkFileDialog
import re
import datetime

# For the GUI to select directory
root = tk.Tk()
root.withdraw()

dir_path = os.path.dirname(os.path.realpath(__file__))
log_directory = "%s/log/" %(dir_path)

filename = tkFileDialog.askopenfilename(title = "Choose log file", initialdir=log_directory,filetypes=[("Pi Control log files","*.xpt")])

with open(filename) as file:
	# read the log's lines then close the file
	lines = file.readlines()

# find mating start and stop times and assemble them in a dict
starttimes = {}
stoptimes = {}
for line in lines:
	if line.startswith("Mating started:"):
		[dummy, well, event_time] = re.split(r'\t+',line)
		if starttimes.get(well) == None:
			starttimes[well] = []
		starttimes[well].append(datetime.datetime.strptime(event_time.strip("\n"),'%H:%M:%S.%f'))
	if line.startswith("Mating ended:"):
		[dummy, well, event_time] = re.split(r'\t+',line)
		if stoptimes.get(well) == None:
			stoptimes[well] = []
		stoptimes[well].append(datetime.datetime.strptime(event_time.strip("\n"),'%H:%M:%S.%f'))

# for now I'm just going to assume that no mistakes are made putting starts and stops. I will build in failsafes at some later point.
durations = {}
for well in starttimes:
	# list of mating durations in seconds for each well
	durations[well] = list(map(lambda x,y: (x - y).total_seconds(), stoptimes[well], starttimes[well]))
print durations
print starttimes
print stoptimes
