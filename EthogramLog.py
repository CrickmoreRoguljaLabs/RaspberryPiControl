# Clumsily assembled ~05/15/2018 - SCT
import matplotlib
matplotlib.use('TkAgg')
#import matplotlib.pyplot as plt
import matplotlib.patches as patches
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

from matplotlib.figure import Figure
import numpy as np
import ast
import math
import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

matplotlib.rcParams['svg.fonttype'] = 'none'
hfont = {'fontname':'Arial'}
genotype_space = 2

class EthogramLog(object):
	# This creates an "EthogramLog" object for viewing copulation data
	def __init__(self, mating_times = None, pulse_times = None, recording_length = 80, led_dict = ["Red","Green","Blue"]):
		self.mating_times = mating_times
		self.pulse_times = pulse_times
		self.root = Tk.Tk()
		self.fig = matplotlib.figure.Figure(figsize=(3, 1.25), dpi=200)
		self.ax = self.fig.add_subplot(111)
#		self.ax.patch.set_visible(False)
#		self.fig.patch.set_visible(False)
		self.ax.get_xaxis().set_tick_params(direction='out')
		self.ax.get_xaxis().set_visible(False)
		self.ax.get_yaxis().set_visible(False)
		self.ax.axis('off')
		self.recording_length = recording_length
		self.led_dict = led_dict
		self.color_dict = None

	def set_mating_times(self, mating_times):
		self.mating_times = mating_times

	def set_title(self, title):
		# make title for window
		self.root.wm_title(title)

	def set_pulse_times(self, pulses):
		self.pulse_times = pulses

	def plot_ethogram(self):
		# set all the ticks to black if there isn't a custom colormap
		if self.color_dict == None:
			self.color_dict = {}
			for key in self.mating_times:
				self.color_dict[key] = [0.0,0.0,0.0]

		# find all the unique wells and sort them to align pulses and lights
		unique_wells = uniquify(list(self.mating_times.keys()) + list(self.pulse_times.keys()))
		total_animals = len(unique_wells)
		y_axis_vals = range(total_animals)
		mapping = dict(zip(unique_wells,y_axis_vals))

		ticks = np.zeros((self.recording_length,1))
		if not self.mating_times is None:
			for animal in self.mating_times:
				animal_num = mapping[animal]
				#ref_animal_num = int(animal[-1])
				matings = self.mating_times[animal]
				for mating in matings:
					arr = np.array(mating)
					if not np.isnan(arr).any():
						# plot each mating as a tick
						self.ax.add_patch(patches.Rectangle((arr[0],(animal_num+1.2)), arr[1]-arr[0],0.8,facecolor=self.color_dict[animal],edgecolor="none"))

		if not self.pulse_times is None:
			pulse_color_list = [[0.0,0.0,1.0,0.5],[0.0,1.0,0.0,0.5],[1.0,0.0,0.0,0.5]] # blue, green, red list of RGBalpha colors (sorry) (alphabetical)
			for animal in self.pulse_times:
				p_animal_num = mapping[animal]
				pulses = self.pulse_times[animal] # per well pulses
				for color_number in range(len(self.led_dict)):
					pulse_set = pulses[color_number]
					#pulse_set = str(pulse_set)
					for pulse in pulse_set:
						arr = np.array(pulse)
						if not np.isnan(arr).any():
							self.ax.add_patch(patches.Rectangle((float(pulse[0]),
								(p_animal_num+1.15)),float(pulse[1])-float(pulse[0]),0.9,facecolor=pulse_color_list[color_number],edgecolor="none"))
							if len(pulse) > 2:
								self.ax.add_patch(patches.Rectangle((float(pulse[2]),
									(p_animal_num+1.15)),float(pulse[3])-float(pulse[2]),0.9,facecolor=pulse_color_list[color_number],edgecolor="none"))


		# # put in a 10 minute long scale bar
		self.ax.plot([self.recording_length/2.0, self.recording_length/2.0 + 10], [(total_animals+4.1)]*2, '-', color='k', lw=1)
		self.ax.text(self.recording_length/2.0 - 5, total_animals+2.1, "10 minutes", color='k', fontsize=9,**hfont)

		# Indicate which row is which well
		for well, value in mapping.items():
			self.ax.text(-5, value+1.2, well, color='k', fontsize=5, **hfont)

		# # make a line at time = 0
		self.ax.plot([0,0],[0,total_animals+1.1],'-',color='k', lw=0.1)
		# #plt.plot([120,120],[0,animal_num+1.1+genotype_num+2.0],'-',color='k', lw=0.1)
		# #plt.plot([240,240],[0,animal_num+1.1+genotype_num+2.0],'-',color='k', lw=0.1)
		self.ax.set_xlim(right=self.recording_length)
		self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

		#toolbar = NavigationToolbar2TkAgg(canvas, self.root)
		#toolbar.update()
		self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
		q_button = Tk.Button(master=self.root, text='Quit', command=lambda: self.quit_window())
		q_button.pack(side=Tk.BOTTOM)
		Tk.mainloop()
		#self._play_nice_with_Tk()


	def quit_window(self):
		self.root.quit()
		self.root.destroy()

	def set_figure_size(self, width, height):
		self.fig.set_size_inches(width,height)

	def set_recording_length(self, length):
		self.recording_length = length

	def set_color_dict(self, color_dict):
		self.color_dict = color_dict

	def _play_nice_with_Tk(self):
		self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

		#toolbar = NavigationToolbar2TkAgg(canvas, self.root)
		#toolbar.update()
		self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
		q_button = Tk.Button(master=self.root, text='Quit', command=lambda: self.quit_window())
		q_button.pack(side=Tk.BOTTOM)
		Tk.mainloop()

	def export_ethogram(self, path, name):
		plt.savefig('%s/%s.svg' %(path, name), format='svg', dpi=300)

def uniquify(seq):
   # Not order preserving
   keys = {}
   for e in seq:
       keys[e] = 1
   return keys.keys()