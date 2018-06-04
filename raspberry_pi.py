# Painful references and exchange of info back and forth between here and command_window 
import paramiko
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk
import time
import json
import StimConstructor
import threading
from command_window import Command_Window
from logExperimentPC import Experiment

use_ssh = True
test_video = True

class Raspberry_Pi(object):
	# Defines the raspberry pi class with address IP_ADDRESS, controls shell interactions with the Pi using paramiko
	
	def __init__(self,ID,master,colors=["Red"]):
		self.IP_ADDRESS = ID[0]
		ListOfProtocols = ["Paired pulse", "Flashing Lights", "Blocks"]
		self.colors = colors
		self.window = Command_Window(tk.Toplevel(master),ListOfProtocols,pi=self,colors=colors)
		self.window.set_title(ID[1])

		self.window.protocol_button(self)
		self.window.quit_button(lambda: self.close_pi())

		if use_ssh:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(ID[0],username='pi',password='raspberry')
			self.ssh = ssh
			self.sftp_client = self.ssh.open_sftp()
			#vid_shell = paramiko.SSHClient()
			#vid_shell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			#vid_shell.connect(ID[0],username='pi',password='raspberry')
			#self.vid_shell = vid_shell
			#self.build_video_frame(self.vid_shell)
	
	def retrieve_stim_dict(self,protocol):
 	# return a dict mapping file name to a collection of blocks
 		list_of_stimuli_files = [file for file in self.sftp_client.listdir('/home/pi/stimuli/%s' %protocol) if file.endswith('.pi')]
 		stim_dict = {}
 		for file in list_of_stimuli_files:
 			#print './stimuli/%s'%file
 			remote_file = self.sftp_client.open('/home/pi/stimuli/%s/%s'%(protocol,file),mode='r')
 			try:
	 			data = json.load(remote_file)
		 		block_list = []
		 		for block_attributes in data:
		 			block_list.append(StimConstructor.load_block(block_attributes))
		 		remote_file.close()
		 		stim_dict[file] = block_list
		 	except:
		 		# Live dangerously
		 		pass
	 	return stim_dict

	def create_video_file(self, videoName=None):
		# create a stream targeted to "receiver"
		if not videoName is None:
			stream_string = "raspivid -t 0 -fps 20 -ex night -awb shade -b 500000 -o - | tee %s.h264 | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=%s port=5000"%(videoName,self.IP_ADDRESS)
			self.stdin_v, self.stdout_v, self.stderr_v = self.ssh.exec_command(stream_string, get_pty=True)
		else:
			stream_string = "raspivid -t 0 -fps 20 -ex night -awb shade -b 500000 -o - | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=%s port=5000"%(videoName,self.IP_ADDRESS)
			self.stdin_v, self.stdout_v, self.stderr_v = self.ssh.exec_command(stream_string, get_pty=True)
		self.expt.note_change("Began video: %s" %(videoName))
		self.expt.change_name(videoName)
		self.expt.change_time_zero()
		self.expt.note_change("Reset time")
		self.videoName = videoName

	def terminate_video_file(self):
		# terminates the video initiated by create_video_file
		self.stdin_v.write("\x03")
		self.expt.note_change("Ended video: %s" %self.videoName)

	def run_prot(self,protocol_listed):
		# runs the protocol listed by sending a command to the Pi, which commands the Arduino
		command_dict = {"Paired pulse":"PairedPulseStim.py","Flashing Lights":"WellStim.py","Blocks":"blockStim.py"}
		if use_ssh:
			self.stdin, self.stdout, self.stderr = self.ssh.exec_command("python "+command_dict[protocol_listed])
		self.window.prot_specs(protocol_listed,self)
		self.window.open_timers()
		self.window.make_video_frame()
		self.stim_dict = self.retrieve_stim_dict(protocol_listed)
		self.expt = Experiment(IP_ADDRESS=self.IP_ADDRESS, colors=self.colors, protocol = protocol_listed)
		self.expt.note_change("Initiated protocol: "+str(protocol_listed))
		self.window.rename_log_button(self.expt)
		self.window.note_button(self.expt)

	def update_intensity(self, new_intensity):
		# Updates the green light intensity
		if use_ssh:
			self.stdin.write("i,%s\n" %new_intensity)
			self.stdin.flush()
			print("i,%s" %new_intensity)
			self.expt.note_change("Changed green intensity: " + new_intensity)

	def send_command(self, command_entries = []):
		# For when stimulus constructor is not supported
		if command_entries == []:
			command_entries = self.window.command_entries
			command_params = [entry.get() for entry in command_entries]
			command = ",".join(command_params)
		else:
			pass
		# Sends the command from the command window to the raspberry pi
		self.update_history(command)
		self.expt.note_pulse(command)
		if use_ssh:
			self.stdin.write(command+'\n')
			self.stdin.flush()

	def command_verbatim(self,command):
		# This just explicitly sends exactly the command we want to use without messing with joining stuff
		if use_ssh:
			self.stdin.write(command+'\n')
			self.stdin.flush()
			self.expt.note_change("Sent command: "+command)

	def lights_out(self):
		if use_ssh:
			pass

	def update_history(self,command):
		# Updates the command history
		self.window.command_history.append(command)
		col_size,row_size= self.window.historyValFrame.grid_size()
		tk.Label(self.window.historyValFrame,text= time.strftime('%H:%M:%S')).grid(column=0,row=row_size)
		tk.Label(self.window.historyValFrame,text= command).grid(column=2,row=row_size)

	def close_pi(self):
		# End the ssh session and close the window
		if use_ssh:
			self.ssh.close()
		#if not self.window.stream is None:
		#	self.window.stream.stop()
		self.window.destroy()