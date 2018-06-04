# Clumsily assembled ~05/15/2018 - SCT
import os
import datetime
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk

class Experiment(object):
	# This creates an "Experiment" object and tracks everything about the experiment in a .log file
	def __init__(self, IP_ADDRESS,colors,protocol,video_name=str(datetime.datetime.now())):
		# name the file
		self.name_of_video = video_name
		# put it in the proper directory
		self.start_time = datetime.datetime.now()
		self.colors = colors
		self.protocol = protocol
		today = datetime.date.today()
		date = "%s-%s-%s" %(today.year, today.month, today.day)
		dir_path = os.path.dirname(os.path.realpath(__file__))
		directory = "%s/log/%s" %(dir_path, date)
		print(directory)
		self.log_dir = directory
		name_of_log = "%s/%s.xpt" %(directory,self.name_of_video)
		print(name_of_log)
		if not os.path.exists(directory):
			os.makedirs(directory)
			print("made directory %s" %directory)
		self.name_of_log = name_of_log
		log_file = open(self.name_of_log,"w")
		log_file.write("Established connection with Raspberry Pi at address %s" %(IP_ADDRESS))
		log_file.write("\nColors:\t%s" %(self.colors))
		log_file.write("\nProtocol:\t%s"%(self.protocol))
		log_file.close()

	def change_name(self,name):
		# changes the name of the log file
		os.rename(self.name_of_log, "%s/%s.xpt" %(self.log_dir, name))
		self.name_of_log = "%s/%s.xpt" %(self.log_dir, name)
		self.name_of_video = name
		self.note_change("\nRenamed file to %s" %(name))

	def change_time_zero(self):
		self.start_time = datetime.datetime.now()

	def note_change(self, command):
		# easy access to the experiment's log
		# enter the time, then enter the command
		log_file = open(self.name_of_log,"a")
		time_of_command = str(datetime.datetime.now()-self.start_time)
		log_file.write("\n%s:\t %s" %(time_of_command,command))
		log_file.close()

	def note_pulse(self, pulse):
		log_file = open(self.name_of_log,"a")
		time_of_command = str(datetime.datetime.now()-self.start_time)
		log_file.write("\nPulse:\t%s\t%s" %(pulse,time_of_command))
		log_file.close()

	def start_mating(self, wellnum):
		log_file = open(self.name_of_log,"a")
		time_of_command = str(datetime.datetime.now()-self.start_time)
		log_file.write("\nMating started:\tWell %s\t%s" %(str(wellnum), time_of_command))
		log_file.close()

	def stop_mating(self, wellnum):
		log_file = open(self.name_of_log,"a")
		time_of_command = str(datetime.datetime.now()-self.start_time)
		log_file.write("\nMating ended:\tWell %s\t%s" %(str(wellnum), time_of_command))
		log_file.close()