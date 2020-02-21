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
import pickle
from command_window import Command_Window
from logExperimentPC import Experiment

use_ssh = True
test_video = True

class Raspberry_Pi(object):
	# Defines the raspberry pi class with address IP_ADDRESS, controls shell interactions with the Pi using paramiko
	
	def __init__(self,ID,master,colors=["Red"], numpis=0):
		self.IP_ADDRESS = ID[0]
		ListOfProtocols = ["Paired pulse", "Flashing Lights", "Blocks", "Random"]
		self.colors = colors
		self.master = master
		self.port = numpis + 5000
		self.window = Command_Window(tk.Toplevel(master),ListOfProtocols,pi=self,colors=colors, port=self.port)
		self.window.set_title(ID[1])
		self.intensity_colors = ["Green"]

		if use_ssh:
			try:
				ssh = paramiko.SSHClient()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				ssh.connect(ID[0],username='pi',password='raspberry',timeout=1.0)
				self.ssh = ssh
				self.sftp_client = self.ssh.open_sftp()
				# check for config file
				self.sftp_client.stat('/home/pi/config/config.config')
				custom_alert = tk.Toplevel(master)
				tk.Label(custom_alert,text="The Raspberry Pi you have connected to uses a custom configuration\n Make sure you know which settings are different!").pack()
				with self.sftp_client.open('/home/pi/config/config.config') as config:
					config_dict = pickle.load(config)
					self.colors = config_dict["Colors"]
					self.intensity_colors = config_dict["Intensities"]
				self.window = Command_Window(tk.Toplevel(master),ListOfProtocols,pi=self,colors=self.colors, port=self.port)
				self.window.set_title(ID[1])
			except IOError, e:
				if e[0] == 2:
					# means the config file doesn't exist
					self.window = Command_Window(tk.Toplevel(master),ListOfProtocols,pi=self,colors=self.colors, port=self.port)
					self.window.set_title(ID[1])
			except:
				print("OTHER ERROR!!!")
				self.connection_error()
				self.close_pi()
				raise

		self.window.protocol_button(self)
		self.window.quit_button(lambda: self.close_pi())
		self.intensity = 0.178
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
		if not ( (videoName is None) or (videoName is "Name of the video") ):
			stream_string = "raspivid -t 0 -fps 20 -ex night -awb shade -b 500000 -o - | tee %s.h264 | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=%s port=%s"%(videoName,self.IP_ADDRESS,str(self.port))
			self.stdin_v, self.stdout_v, self.stderr_v = self.ssh.exec_command(stream_string, get_pty=True)
			self.expt.note_change("Began video: %s" %(videoName))
			self.expt.change_name(videoName)
			self.expt.change_time_zero()
			self.expt.note_change("Reset time")
		else:
			stream_string = "raspivid -t 0 -fps 20 -ex night -awb shade -b 500000 -o - | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=%s port=%s"%(self.IP_ADDRESS,str(self.port))

			self.stdin_v, self.stdout_v, self.stderr_v = self.ssh.exec_command(stream_string, get_pty=True)
		self.videoName = videoName

	def terminate_video_file(self):
		# terminates the video initiated by create_video_file
		self.stdin_v.write("\x03")
		self.expt.note_change("Ended video: %s" %self.videoName)

	def run_prot(self,protocol_listed):
		# runs the protocol listed by sending a command to the Pi, which commands the Arduino
		command_dict = {"Paired pulse":"PairedPulseStim.py","Flashing Lights":"WellStim.py","Blocks":"blockStim.py", "Random":"randomStim.py"}
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

	def update_intensity(self, entry_list):
		# Updates the green light intensity
		if use_ssh:
			intensities_list = [str(float(intensity.get())) for intensity in entry_list]
			intensity_command = ",".join(intensities_list)
			self.stdin.write("i,%s\n" %intensity_command)
			self.stdin.flush()
			print("i,%s" %intensity_command)
			self.expt.note_change("Changed green intensity: " + intensity_command)
			#self.intensity = float(new_intensity)

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

	def connection_error(self):
		error_window = tk.Toplevel(self.master)
		tk.Label(error_window,text="Error connecting to raspberry pis.\nMake sure you're on TCH network\nDouble check the IP address book").pack()
		tk.Button(error_window,text="OK",command=error_window.destroy).pack()

	def close_pi(self):
		# End the ssh session and close the window
		if use_ssh:
			self.ssh.close()
		#if not self.window.stream is None:
		#	self.window.stream.stop()
		self.window.destroy()