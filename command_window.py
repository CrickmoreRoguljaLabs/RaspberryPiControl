# a way to keep all the buttons in one place for a window corresponding to a Pi
# The most spaghetti of codes. Perhaps some day I'll rewrite it to be pretty. For now, it just works.
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk
from PIL import ImageTk, Image
import time
import stopwatch
import StimConstructor
import os
import json
import StimSelector
#import multiprocessing
import threading

class Command_Window(object):
	def __init__(self, window,ListOfProtocols,pi,colors=["Red"],port=8000):
		self.window = window
		self.ListOfProtocols = ListOfProtocols
		self.protFrame = tk.Frame(self.window)
		self.commandFrame = tk.Frame(self.window)
		self.historyFrame = tk.Frame(self.commandFrame)
		self.timerFrame = tk.Frame(self.commandFrame)
		self.videoFrame = tk.Frame(self.window)
		self.videoFrame.pack(side=tk.RIGHT)
		self.button_dict = {}
		self.command_entries = []
		self.command_labels = []
		self.command_history = []
		self.streaming = False
		self.pi = pi
		#self.stream = None
		self.panel = tk.Label(self.videoFrame)
		#self.stop_vid = threading.Event()
		self.colors = colors


	def set_title(self, title):
		self.window.title(title)
		self.title = title

	def make_video_frame(self):
		# establishes the frame for controlling the video stuff
		self.panel = tk.Label(self.videoFrame)
		self.start_vid_button = tk.Button(self.videoFrame,text="Start video",command = lambda: self.demo_start_video())
		self.start_vid_button.pack()
		self.video_name_entry = tk.Entry(self.videoFrame)
		self.video_name_entry.insert(0,"Name of the video")
		self.video_name_entry.pack()

	def demo_start_video(self):
		# for testing before ssh is implemented 
		self.start_vid_button.destroy()
		self.video_name = self.video_name_entry.get()
		self.pi.create_video_file(self.video_name)
		self.video_name_entry.destroy()

		#self.window.demo_play_video()
		self.stream_thread = threading.Thread(target=self.demo_play_video)
		self.stream_thread.start()
		self.stop_vid_button = tk.Button(self.videoFrame,text="Stop video",command = lambda: self.stop_video())
		self.stop_vid_button.pack(side=tk.BOTTOM)

	def demo_play_video(self, port=8000):
		self.streaming = True
		name_label = tk.Label(self.videoFrame,text='%s' %(self.video_name))
		name_label.pack()
		while self.streaming:
			image_path = "/Users/stephen/Desktop/Pi Control/cameraman.jpg"
			img = ImageTk.PhotoImage(Image.open(image_path))
			self.panel.image = img
			self.panel.config(image = img)
			self.panel.pack()
		self.panel.destroy()
		name_label.destroy()
		self.make_video_frame()
		self.stop_vid_button.destroy()	


#	def play_video(self,vid_shell,port=8000):
#		stream=VideoStream(port=port,vid_shell=vid_shell)
#		time.sleep(1)
#		threading.Thread(target=stream.play_video).start()
#		print self.stop_vid.is_set()
#		while not self.stop_vid.is_set():
#			frame = stream.read()
#			print frame
#			if self.panel is None:
#				self.panel = tk.Label(self.videoFrame,image=frame)
#				self.panel.image = frame
#				self.panel.pack(side=tk.TOP, padx=10, pady=10)
#		
#				# otherwise, simply update the panel
#			else:
#				self.panel.configure(image=frame)
#				self.panel.image = frame

	def stop_video(self):
		self.streaming = False
		self.pi.terminate_video_file()


	def protocol_button(self,this_pi):
		protFrame = self.protFrame
		protFrame.pack(side=tk.TOP, anchor=tk.W)
		protocols = tk.StringVar(protFrame)
		protocols.set(self.ListOfProtocols[0])
		protlist = tk.OptionMenu(protFrame,protocols, *self.ListOfProtocols)
		protlist.pack(side=tk.LEFT, anchor=tk.W)
		protbut = tk.Button(protFrame, text='Run protocol',command=lambda: this_pi.run_prot(protocols.get()))
		protbut.pack(side=tk.LEFT, anchor=tk.W)
		self.protocols = protocols
		self.button_dict['Run protocol']=protbut
		self.protFrame = protFrame
		self.mode = tk.IntVar()
		self.mode_box = tk.Checkbutton(self.protFrame, text="Use stimulus constructor", variable=self.mode)
		self.mode_box.pack()

	def quit_button(self,command):
		botFrame = tk.Frame(self.window)
		botFrame.pack(side=tk.BOTTOM, anchor=tk.SW)
		button = tk.Button(botFrame, text="Quit", command=command)
		button.pack(anchor=tk.W)
		self.button_dict["Quit"] = button

	def get_button(self,name_of_button):
		return self.button_dict[name_of_button]

	def prot_specs(self,protocol_listed,pi):
		# Establish a frame with the option to send commands

		# Clear out the old ones
		map(lambda entry: entry.destroy(), self.command_entries)
		map(lambda label: label.destroy(), self.command_labels)
		self.mode_box.destroy()
		## Make sure that the old "New stimulus" button is destroyed.
		try:
			self.new_stimulus.destroy()
			self.start_vid_button.destroy()
			self.video_name_entry.destroy()
		except:
			pass
		# If using "stim constructor"
		if self.mode.get():
			self.well_frames = []
			self.commandFrame.destroy()
			self.commandFrame = tk.Frame(self.window)
			self.commandFrame.pack(side=tk.LEFT, anchor=tk.NW)
			callFrame = tk.Frame(self.commandFrame)
			callFrame.pack(side=tk.LEFT,anchor=tk.NW)	
			self.new_stimulus = tk.Button(self.protFrame,text="New stimulus", command=lambda: self.new_stim(protocol_listed = self.protocols.get()))
			self.new_stimulus.pack(side=tk.RIGHT)
			self.protocol = self.protocols.get()
			self.stim_constructor_setup(self.protocol,callFrame)
		else:
			## OLD PROTOCOL STYLE
			if "Send command" in self.button_dict:
				self.button_dict["Send command"].destroy()
			self.command_entries = []
			self.command_labels = []
			self.command_history = []
			self.commandFrame.destroy()
			commandFrame = tk.Frame(self.window)
			commandFrame.pack(anchor=tk.NW)
			self.historyFrame.destroy()
			callFrame = tk.Frame(commandFrame)
			callFrame.pack(side=tk.LEFT,anchor=tk.NW)
			historyFrame = tk.Frame(commandFrame)
			historyFrame.pack(side=tk.LEFT,padx=15,anchor=tk.NW)
			self.set_up_protocol(callFrame,protocol_listed)
			historyLabelFrame = tk.Frame(historyFrame)
			historyLabelFrame.pack(side=tk.TOP,anchor=tk.NW)
			tk.Label(historyLabelFrame,text="Command History").grid(row= 0, column=1)
			tk.Label(historyLabelFrame,text="Time").grid(row=1,column=0)
			tk.Label(historyLabelFrame,text="Command").grid(row=1,column=2)
			historyValFrame = tk.Frame(historyFrame)
			historyValFrame.pack(side=tk.BOTTOM)

			send_command = tk.Button(callFrame,text="Send command",command=pi.send_command)
			send_command.pack(anchor=tk.S)
			self.button_dict["Send command"] = send_command
			self.commandFrame = commandFrame
			self.historyFrame = historyFrame
			self.historyValFrame = historyValFrame

	def set_up_protocol(self, commandFrame, protocol_listed):
		### Sets up the commands used. Should be rewritten now that I have the "attributes" stored .pi objects, but this works fine for now
		### but it looks like a real mess.
		if "Green" in self.colors:
			tk.Button(commandFrame,text="Update green intensity", command= lambda: self.update_intensity()).pack(side=tk.TOP)
		else:
			tk.Button(commandFrame,text="Update red intensity", command= lambda: self.update_intensity()).pack(side=tk.TOP)
		## Sets up all the fields entered for each protocol
		if protocol_listed == "Paired pulse":

			self.command_labels.append(tk.Label(commandFrame,text='Well Number'))
			self.command_labels[-1].pack(anchor=tk.N)
			self.command_entries.append(tk.Entry(commandFrame))
			self.command_entries[-1].pack(anchor=tk.N)
			# if there are multiple colors, make multiple color command frames
			colorFrame = tk.Frame(commandFrame)
			colorFrame.pack(side=tk.TOP)
			for color in self.colors:
				frame = tk.Frame(colorFrame)
				frame.pack(side=tk.LEFT)
				tk.Label(frame,text=color).pack(side=tk.TOP)
				# To revert, replace "frame" with "commandFrame"
				self.command_labels.append(tk.Label(frame,text='Wait (min)'))
				self.command_labels[-1].pack(anchor=tk.NW)
				self.command_entries.append(tk.Entry(frame,width=10))
				self.command_entries[-1].pack(anchor=tk.NW)

				self.command_labels.append(tk.Label(frame,text='First pulse (ms)'))
				self.command_labels[-1].pack(anchor=tk.NW)
				self.command_entries.append(tk.Entry(frame,width=10))
				self.command_entries[-1].pack(anchor=tk.NW)
				
				self.command_labels.append(tk.Label(frame,text='Rest duration (s)'))
				self.command_labels[-1].pack(anchor=tk.NW)
				self.command_entries.append(tk.Entry(frame,width=10))
				self.command_entries[-1].pack(anchor=tk.NW)

				self.command_labels.append(tk.Label(frame,text='Second pulse (ms)'))
				self.command_labels[-1].pack(anchor=tk.NW)
				self.command_entries.append(tk.Entry(frame,width=10))
				self.command_entries[-1].pack(anchor=tk.NW)

		if protocol_listed == "Flashing Lights":
			self.command_labels.append(tk.Label(commandFrame,text='Well Number'))
			self.command_labels[-1].pack(anchor=tk.N)
			self.command_entries.append(tk.Entry(commandFrame,width=10))
			self.command_entries[-1].pack(anchor=tk.N)
			colorFrame = tk.Frame(commandFrame)
			colorFrame.pack(side=tk.TOP)
			for color in self.colors:
				frame = tk.Frame(colorFrame)
				frame.pack(side=tk.LEFT)
				tk.Label(frame,text=color).pack(side=tk.TOP)

				self.command_labels.append(tk.Label(frame,text='Frequency (Hz)'))
				self.command_labels[-1].pack(anchor=tk.NW)
				self.command_entries.append(tk.Entry(frame,width=10))
				self.command_entries[-1].pack(anchor=tk.NW)

				self.command_labels.append(tk.Label(frame,text='Pulse duration (ms)'))
				self.command_labels[-1].pack(anchor=tk.NW)
				self.command_entries.append(tk.Entry(frame,width=10))
				self.command_entries[-1].pack(anchor=tk.NW)
		if protocol_listed == "Blocks":
			self.command_labels.append(tk.Label(commandFrame,text='Well Number'))
			self.command_labels[-1].pack(anchor=tk.N)
			self.command_entries.append(tk.Entry(commandFrame,width=10))
			self.command_entries[-1].pack(anchor=tk.N)
			colorFrame = tk.Frame(commandFrame)
			colorFrame.pack(side=tk.TOP)
			for color in self.colors:
				frame = tk.Frame(colorFrame)
				frame.pack(side=tk.LEFT)
				tk.Label(frame,text=color).pack(side=tk.TOP)

				self.command_labels.append(tk.Label(frame,text='Frequency (Hz)'))
				self.command_labels[-1].pack(anchor=tk.NW)
				self.command_entries.append(tk.Entry(frame,width=10))
				self.command_entries[-1].pack(anchor=tk.NW)

				self.command_labels.append(tk.Label(frame,text='Pulse duration (ms)'))
				self.command_labels[-1].pack(anchor=tk.NW)
				self.command_entries.append(tk.Entry(frame,width=10))
				self.command_entries[-1].pack(anchor=tk.NW)

				self.command_labels.append(tk.Label(frame,text='Duration of block (ms)'))
				self.command_labels[-1].pack(anchor=tk.NW)
				self.command_entries.append(tk.Entry(frame,width=10))
				self.command_entries[-1].pack(anchor=tk.NW)

				self.command_labels.append(tk.Label(frame,text='Time between start\nof each block (ms)'))
				self.command_labels[-1].pack(anchor=tk.NW)
				self.command_entries.append(tk.Entry(frame,width=10))
				self.command_entries[-1].pack(anchor=tk.NW)
		for entry in self.command_entries:
			entry.insert(0,"0")

	def update_intensity(self):
		## For updating the intensity of the green lights
		intensity_window = tk.Toplevel(self.window)
		intensity_window.title("Update green intensity (%s)" %self.title)
		intensity_entry = tk.Entry(intensity_window)
		intensity_entry.insert(tk.END, "Intensity (between 0 and 1) (Default is .178)")
		intensity_entry.pack(side=tk.LEFT)
		# Ok so this looks ridiculous: I cast to a float, then back to a string, from a string, but it's so people
		# can type floats their own way and it all gets treated the same by the Arduino, which interprets input poorly
		update = tk.Button( intensity_window,command=lambda: self.pi.update_intensity(str(float(intensity_entry.get()))) ,
			text="Update intensity")
		update.pack()

	def open_timers(self):
		self.timerFrame.destroy()
		self.timerFrame = tk.Frame(self.commandFrame)
		self.timerFrame.pack(side=tk.LEFT,anchor=tk.NW,padx=40)
		tk.Label(self.timerFrame,text='Well Timers').pack(side=tk.TOP)
		self.indTimersFrame = tk.Frame(self.timerFrame)
		self.indTimersFrame.pack(side=tk.BOTTOM)
		butt = tk.Button(self.indTimersFrame,text="New timer",command=self.make_new_timer)
		butt.pack(side=tk.BOTTOM,anchor=tk.N)
		self.make_new_timer()

	def make_new_timer(self):
		new_timer = tk.Frame(self.indTimersFrame)
		new_timer.pack(side=tk.TOP,anchor=tk.N)
		timer = tk.Entry(new_timer,width=5)
		timer.insert(tk.END, 'Well #')
		timer.pack(side=tk.LEFT)
		sw = stopwatch.StopWatch(parent=new_timer)
		sw.pack(side=tk.LEFT)
		start_button = tk.Button(new_timer,text="Start",command=sw.Start)
		start_button.pack(side=tk.LEFT)
		stop_button = tk.Button(new_timer,text="Stop",command=sw.Stop)
		stop_button.pack(side=tk.LEFT)
		reset_button = tk.Button(new_timer,text="Reset",command=sw.Reset)
		reset_button.pack(side=tk.LEFT)
		destroy_button = tk.Button(new_timer,text="Destroy",command= lambda: self.destroy_timer(timer,sw,start_button,stop_button,reset_button,destroy_button))
		destroy_button.pack(side=tk.LEFT)

	def destroy_timer(self, *args):
		for arg in args:
			arg.destroy()

	def new_stim(self, protocol_listed):
	# Set up a condition for making a new stimulation protocol
		StimConstructor.StimConstructor(tk.Toplevel(self.window),protocol_listed, self.colors,pi=self.pi)

	def new_well_entry(self):
		# Create the buttons to select a stimulus for a particular well
		well_frame = tk.Frame(self.framesForWells)
		well_frame.pack(side=tk.TOP)
		self.well_frames.append(well_frame)
		well_num_entry = tk.Entry(well_frame, width = 5)
		well_num_entry.insert(0,"Well #")
		well_num_entry.pack(side=tk.LEFT)
		stim_string = tk.StringVar()
		stim_string.set("No stimulus")
		stim_select_button = tk.Button(well_frame, text="Select stim", command= lambda: self.select_stim(self,self.pi,stim_string))
		stim_select_button.pack(side=tk.LEFT)

		stimlist = tk.OptionMenu(well_frame,stim_string, *list(self.pi.retrieve_stim_dict(self.protocol).keys()))
		print (list(self.pi.retrieve_stim_dict(self.protocol).keys()))
		self.stimuli_menu_dict[stimlist] = stim_string
		stimlist.config(width=15)
		stimlist.pack(side=tk.LEFT)
		send_command_button = tk.Button(well_frame,text="Send commands",command= lambda: self.block_thread(well_num_entry.get(), stim_string.get()))
		send_command_button.pack(side=tk.RIGHT)

	def select_stim(self,command_window,pi,stim_string):
		StimSelector.StimSelector(command_window,pi,stim_string)

	def block_thread(self,well_num,stimulus):
		try:
			thr = threading.Thread(target=self.run_block, args=(well_num, stimulus))
			thr.daemon = True
			thr.start()
		except:
			# Eventually throw error
			pass

	def run_block(self,well_num, stimulus):
		# Run the block in the input well well_num
		block_list = self.pi.retrieve_stim_dict(self.protocol)[stimulus]
		for block in block_list:
			# returns, in string form, the commands for that well
			comm = block.return_commands()
			self.pi.command_verbatim(",".join([well_num,comm]))
			print(",".join([well_num,comm]))
			print(block.duration)
			time.sleep(60.0*float(block.duration))
			if float(block.duration) == 0:
				break
		self.lights_out(well_num)

	def lights_out(self,well_num):
		# Turn off the lights.
		#everything_off = 
		#self.pi.command_verbatim(",".join([well_num,everything_off]))
		pass

	def stim_constructor_setup(self, protocol_listed,callFrame):
	## Sets up the command window for using saved .pi files
	# First clear out the old wells
		try:
			map(lambda frame: frame.destroy(),self.well_frames)
			self.button_dict["New Well"].destroy()
		except:
			pass
		#self.commandFrame.pack(anchor=tk.NW)
		if "Green" in self.colors:
				tk.Button(self.protFrame,text="Update green intensity", command= lambda: self.update_intensity()).pack(side=tk.TOP)

		# Make a list for the stimuli menus so that we can update it when we make new stimuli
		self.stimuli_menu_dict = {}
		tk.Label(callFrame, text="Send commands").pack(side=tk.TOP, anchor=tk.N)
		self.framesForWells = tk.Frame(callFrame)
		self.framesForWells.pack(side=tk.TOP)
		tk.Button(callFrame, text="New well", command = lambda: self.new_well_entry()).pack(side=tk.BOTTOM)

	def update_stimuli_menus(self):
		if self.stimuli_menu_dict:
			for (stim_menu, stim_string) in self.stimuli_menu_dict.iteritems():
				m = stim_menu["menu"]
        		m.delete(0, "end")
        		for string in list(self.pi.retrieve_stim_dict(self.protocol).keys()):
        			m.add_command(label=string, command= tk._setit(stim_string, string))

	def remove_button(self,name_of_button):
		self.button_dict[name_of_button].pack_forget()

	def destroy(self):
		self.window.destroy()
