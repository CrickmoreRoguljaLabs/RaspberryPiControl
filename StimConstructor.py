# An interface for constructing light stimulation protocols out of short "blocks" of the same type
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk
from StimulusBlock import StimulusBlock
import json

class StimConstructor(object):
	def __init__(self,window,protocol,colors,pi=None):
		# Build a stimulus constructor to be used in any well
		# Restricted to using a single "protocol" type, but should be fairly flexible anyways
		self.protocol = protocol
		self.colors = colors
		self.window = window
		# blocks are stored as a list of blocks, in "order of appearance"
		self.blocks = []
		initialFrame = tk.Frame(window)
		initialFrame.pack(side=tk.TOP)

		self.new_block_button = tk.Button(initialFrame,text="New block",command = lambda: self.new_block_window())
		self.new_block_button.pack(side=tk.LEFT)

		self.name_text = tk.StringVar()
		self.name = tk.Entry(initialFrame,textvariable=self.name_text)
		self.name.pack(side=tk.LEFT)
		self.name_text.set("Stimulus name")

		self.save_stimulus_button = tk.Button(initialFrame,text="Save stimulus",command = lambda: self.save_stimulus())
		self.save_stimulus_button.pack(side=tk.LEFT)
		
		self.pi = pi

	def new_block_window(self):
		# create a new block with a list of parameters
		block = StimulusBlock(self.protocol, self.colors)
		# create a new frame to put the block in
		blockFrame = tk.Frame(self.window, bd=5, relief=tk.RAISED)
		blockFrame.pack()
		# new window to configure the block
		blockWindow = tk.Toplevel(self.window)
		create_frame = tk.Frame(blockWindow)
		create_frame.pack(side=tk.BOTTOM)
		command_entries = {}
		# Duration of the block
		durationFrame = tk.Frame(blockWindow)
		durationFrame.pack(side=tk.TOP)
		tk.Label(durationFrame,text="Block duration").pack(side=tk.LEFT)
		blockDuration = []
		blockDuration.append(tk.Entry(durationFrame))
		blockDuration[0].insert(0,"0")
		blockDuration[0].pack(side=tk.LEFT)
		unit_string = tk.StringVar(durationFrame)
		unit_string.set("min")
		blockDuration.append(unit_string)
		tk.OptionMenu(durationFrame,unit_string, *["min","sec"]).pack(side=tk.LEFT)
		# Create entry fields for each color
		for color in block.colors:
			# create lists of each entry for each color. Bloaty but more understandable.
			command_entries[color] = {}
			color_frame = tk.Frame(blockWindow)
			color_frame.pack(side=tk.LEFT)
			tk.Label(color_frame,text=color).pack(side=tk.TOP)
			for field in block.param_fields:
				tk.Label(color_frame,text=field).pack(anchor=tk.NW)
				command_entries[color][field]= tk.Entry(color_frame)
				command_entries[color][field].pack(anchor=tk.NW)
		# set them to be 0 to reflect the defaults
		for color in block.colors:
			for (name, entry) in command_entries[color].iteritems():
				entry.insert(0,"0")
		block.buttons = command_entries
		tk.Button(create_frame, text="Create block", command = lambda: self.create_block(block,blockWindow,blockFrame,blockDuration)).pack(side=tk.BOTTOM)

	def create_block(self,block,blockWindow,blockFrame,blockDuration):
		# Create a new block and display it in the stimulus constructor window
		duration = float(blockDuration[0].get())*float((1/60.0)**(int(blockDuration[1].get() == "sec")))
		block.set_duration(duration)
		tk.Label(blockFrame,text="Duration: %f minutes" % block.duration).pack(side=tk.TOP)
		for color in block.colors:
			# window for each color
			color_frame = tk.Frame(blockFrame)
			color_frame.pack(side=tk.LEFT)
			tk.Label(color_frame,text=color).pack(side=tk.TOP)
			for (field, entry) in block.buttons[color].iteritems():
				block.color_params[color][field] = entry.get()
			for field in block.param_fields:
				tk.Label(color_frame,text="%s: %s" % (field, block.color_params[color][field])).pack(side=tk.TOP)
		self.blocks.append(block)
		print(block.duration)
		blockWindow.destroy()


	def save_stimulus(self):
		# save the stimulus as a ".pi" file, which contains the JSON formatted stimulation blocks
		self.window.destroy()
		if self.pi is not None:
			with self.pi.sftp_client.open("stimuli//%s//%s.pi" %(self.protocol,self.name_text.get()),mode='w') as stim_file:
				stimcoll = [block.attributes for block in self.blocks]
				json.dump(stimcoll,stim_file)
				print("on pi")
		else:
			with open("stimuli//%s.pi" %self.name_text.get(),'w') as stim_file:
				stimcoll = [block.attributes for block in self.blocks]
				json.dump(stimcoll,stim_file)
		self.pi.window.update_stimuli_menus()

def load_block(attributes):
	# builds a stimulus block from the attributes and returns the block
	block = StimulusBlock(protocol = attributes["protocol"],colors = attributes["colors"])
	block.param_fields = attributes["param_fields"]
	block.color_params = attributes["color_params"]
	block.duration = attributes["duration"]
	block.attributes = attributes
	return block
