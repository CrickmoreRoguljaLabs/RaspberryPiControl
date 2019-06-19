# Clumsily assembled ~05/15/2018 - SCT
import os
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk
import tkFileDialog
import re
import datetime
import pandas as pd
import EthogramLog
import ast

# For the GUI to select directory
root = tk.Tk()
root.withdraw()

dir_path = os.path.dirname(os.path.realpath(__file__))
log_directory = "%s/log/" %(dir_path)

filename = tkFileDialog.askopenfilename(title = "Choose log file", initialdir=log_directory,filetypes=[("Pi Control log files","*.xpt")])

condition_dict = {"Paired pulse\n": 4, "Flashing Lights\n": 2, "Blocks\n": 4}

with open(filename) as file:
	# read the log's lines then close the file
	lines = file.readlines()

# find mating start and stop times and assemble them in a dict
starttimes = {}
stoptimes = {}
pulses = {}
for line in lines:
	if line.startswith("Colors:"):
		colors = re.split(r'\t+',line)
	if line.startswith("Protocol:"):
		protocol = re.split(r'\t+',line)
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
	if line.startswith("Pulse:"):
		[dummy, command, event_time] = re.split(r'\t+',line)
		parts = re.split(r',',command)
		well = 'Well %s' %(parts[0])
		if pulses.get(well) == None:
			pulses[well] = []
		pulses[well].append([parts[1:], datetime.datetime.strptime(event_time.strip("\n"),'%H:%M:%S.%f')])
num_colors = len(ast.literal_eval(colors[1][:-1]))

# for now I'm just going to assume that no mistakes are made putting starts and stops. I will build in failsafes at some later point.
durations = {}
times = {}
t_zero = datetime.datetime(1900, 1, 1, tzinfo=None)
for well in starttimes:
	# list of mating durations in minutes for each well
	times[well] = zip(list(map(lambda x: ((x - t_zero).total_seconds())/60.0, starttimes[well])),list(map(lambda x: ((x- t_zero).total_seconds())/60.0,stoptimes[well])))
	durations[well] = list(map(lambda x,y: ((x - y).total_seconds())/60.0, stoptimes[well], starttimes[well]))

param_count = condition_dict[protocol[1]]
pulse_times = {}
# iterate through the wells and figure out when the light was on for each color
# store pulses as tuples of light on and off times, organized by color
color_list = ["Red","Green","Blue"]
for well in pulses:
	if pulse_times.get(well) == None:
			pulse_times[well] = {}
			for color in color_list:
				pulse_times[well][color] = []
	# iterate through each command for a pulse
	well_pulses = pulses[well]
	for comm in well_pulses:
		command_list = comm[0]
		time_of_command = comm[1]
		if protocol[1] == "Paired pulse\n":
			for col in range(num_colors):
				rel_pars = command_list[col*param_count:(col+1)*param_count] # get param_count worth of parameters
				p1_start = ((time_of_command-t_zero).total_seconds())/60.0000 +float(rel_pars[0])
				p1_stop = p1_start + float(rel_pars[1])/60000.0
				p2_start = p1_stop + float(rel_pars[2])/60.0
				p2_stop = p2_start + float(rel_pars[3])/60000.0
				pulse_times[well][color_list[col]].append((p1_start, p1_stop, p2_start, p2_stop))


times_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in times.items() ]))
dur_df = pd.DataFrame.from_dict(durations, orient="index")
pulse_df = pd.DataFrame.from_dict(pulse_times)

spreadsheet_name = "%s.xlsx" %(filename[:-4])
writer = pd.ExcelWriter(spreadsheet_name)
times_df.to_excel(writer,"Mating Times")
dur_df.to_excel(writer, "Durations")
pulse_df.to_excel(writer, "Pulses")
writer.save()

# written to interpret .xlsx files, not the original logs
# I thought for some reason this might be easier for people to mess with
# I'm not sure that's going to be right. Or if anyone will ever do it.
etl = EthogramLog.EthogramLog()
etl.set_mating_times(times_df)
etl.set_pulse_times(pulse_df)
etl.set_title(filename)
etl.set_recording_length(120)
etl.plot_ethogram()
