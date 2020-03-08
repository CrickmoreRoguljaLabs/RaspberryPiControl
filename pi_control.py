## GUI for raspis. I'm just learning paramiko, don't make fun of me =(
# This has turned into an organizational shitshow. I'm sorry to anyone who has to try to work on this. Probably including future me.
# Spaghetti code
## SCT Feb. 2017

import paramiko
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk
import time
from command_window import Command_Window
from raspberry_pi import Raspberry_Pi
import threading
import subprocess

def pi_connect(address,ID):
	## Connect to a raspberry pi at location address.
	try:
		ID = [address,ID]
		this_pi = Raspberry_Pi(ID,master,colors=color_dict[ID[1]],numpis=len(ListOfPis))
		ListOfPis.append(this_pi)
	except:
		print(sys.exc_info())

def connect_to_pi(address,ID):
	pi_thread = threading.Thread(target=pi_connect,args=(alias_address_map[add.get()],add.get()))
	pi_threads.append(pi_thread)
	pi_thread.start()

def close_down():
	for pi in ListOfPis:
		pi.close_pi()
	master.destroy()

def manage_address():
	# for making and modifying Pis
	# throwing everything together in one place
	# sorry if it's a huge mess by the time this is all done.

	def update_info(evt):
		for widget in info_container.winfo_children():
			widget.destroy()
		info = alias_map[alias_listbox.get(alias_listbox.curselection())]
		tk.Label(info_container, text="IP Address: ").grid(row=0,column=0)
		tk.Label(info_container, text=info["address"]).grid(row=0,column=1)
		tk.Label(info_container, text="Colors: ").grid(row=1,column=0)
		tk.Label(info_container, text=info["colors"]).grid(row=1,column=1)

	def add_pi():
		new_pi_window = tk.Toplevel(add_window)
		entries_frame = tk.Frame(new_pi_window)
		entries_frame.pack()
		buttons_frame = tk.Frame(new_pi_window)
		buttons_frame.pack()
		tk.Button(buttons_frame,text="Add Pi", command=lambda: add_pi_to_list()).pack()

		tk.Label(entries_frame, text="Alias").grid(row=0,column=0)
		alias_entry = tk.Entry(entries_frame)
		alias_entry.grid(row=0,column=1)
		tk.Label(entries_frame, text="IP address").grid(row=1,column=0)
		ip_entry = tk.Entry(entries_frame)
		ip_entry.grid(row=1,column=1)
		tk.Label(entries_frame, text="Colors").grid(row=2,column=0)
		box_frame = tk.Frame(entries_frame)
		box_frame.grid(row=2,column=1)
		color_list = [tk.IntVar(),tk.IntVar(),tk.IntVar()]
		tk.Checkbutton(box_frame, text='Red',variable=color_list[0], onvalue=1, offvalue=0).grid(row=0,column=0)
		tk.Checkbutton(box_frame, text='Green',variable=color_list[1], onvalue=1, offvalue=0).grid(row=0,column=1)	
		tk.Checkbutton(box_frame, text='Blue',variable=color_list[2], onvalue=1, offvalue=0).grid(row=0,column=2)

		def add_pi_to_list():
			colors = []
			if color_list[0].get():
				colors.append("Red")
			if color_list[1].get():
				colors.append("Green")
			if color_list[2].get():
				colors.append("Blue")
			alias_map[alias_entry.get()]={"address": ip_entry.get(), "colors": colors}
			with open(alias_map_location, 'wb') as fp:
				pickle.dump(alias_map,fp)
			# refresh the listbox when done
			alias_listbox.delete(0,tk.END)
			for alias in alias_map.keys():
				alias_listbox.insert(tk.END,alias)
			new_pi_window.destroy()

	def edit_pi():
		# same code as the "add pi" functionality, but with default info filled in
		new_pi_window = tk.Toplevel(add_window)
		entries_frame = tk.Frame(new_pi_window)
		entries_frame.pack()
		buttons_frame = tk.Frame(new_pi_window)
		buttons_frame.pack()
		tk.Button(buttons_frame,text="Save changes", command=lambda: add_pi_to_list()).pack()

		tk.Label(entries_frame, text="Alias").grid(row=0,column=0)
		alias_entry = tk.Entry(entries_frame)
		alias_entry.insert(0,alias_listbox.get(alias_listbox.curselection()))
		alias_entry.grid(row=0,column=1)
		tk.Label(entries_frame, text="IP address").grid(row=1,column=0)
		ip_entry = tk.Entry(entries_frame)
		ip_entry.insert(0,alias_map[alias_listbox.get(alias_listbox.curselection())]["address"])
		ip_entry.grid(row=1,column=1)
		tk.Label(entries_frame, text="Colors").grid(row=2,column=0)
		box_frame = tk.Frame(entries_frame)
		box_frame.grid(row=2,column=1)
		color_list = [tk.IntVar(),tk.IntVar(),tk.IntVar()]
		tk.Checkbutton(box_frame, text='Red',variable=color_list[0], onvalue=1, offvalue=0).grid(row=0,column=0)
		tk.Checkbutton(box_frame, text='Green',variable=color_list[1], onvalue=1, offvalue=0).grid(row=0,column=1)	
		tk.Checkbutton(box_frame, text='Blue',variable=color_list[2], onvalue=1, offvalue=0).grid(row=0,column=2)

		def add_pi_to_list():
			colors = []
			if color_list[0].get():
				colors.append("Red")
			if color_list[1].get():
				colors.append("Green")
			if color_list[2].get():
				colors.append("Blue")
			alias_map[alias_entry.get()]={"address": ip_entry.get(), "colors": colors}
			with open(alias_map_location, 'wb') as fp:
				pickle.dump(alias_map,fp)
			# refresh the listbox when done
			alias_listbox.delete(0,tk.END)
			for alias in alias_map.keys():
				alias_listbox.insert(tk.END,alias)
			new_pi_window.destroy()

		with open(alias_map_location, 'wb') as fp:
			pickle.dump(alias_map,fp)
		# refresh the listbox when done
		alias_listbox.delete(0,tk.END)
		for alias in alias_map.keys():
			alias_listbox.insert(tk.END,alias)

	def delete_pi():
		del alias_map[alias_listbox.get(alias_listbox.curselection())]

		with open(alias_map_location, 'wb') as fp:
			pickle.dump(alias_map,fp)
		# refresh the listbox when done
		alias_listbox.delete(0,tk.END)
		for alias in alias_map.keys():
			alias_listbox.insert(tk.END,alias)

	add_window = tk.Toplevel(master)
	alias_frame = tk.Frame(add_window)
	info_frame = tk.Frame(add_window)
	info_container = tk.Frame(info_frame)
	info_container.pack()
	alias_frame.grid(row=0,column=0)
	info_frame.grid(row=0, column=1)
	tk.Label(alias_frame,text="Aliases").pack(side=tk.TOP)
	alias_listbox = tk.Listbox(alias_frame)
	alias_listbox.pack()
	for alias in alias_map.keys():
		alias_listbox.insert(tk.END,alias)
	alias_listbox.bind('<<ListboxSelect>>',update_info)
	button_frame = tk.Frame(add_window) # buttons to interact with addresses
	button_frame.grid(row=1) 
	tk.Button(button_frame,text="Add new Pi",command = lambda: add_pi()).grid(row=0,column=0)
	tk.Button(button_frame,text="Delete Pi", command=lambda: delete_pi()).grid(row=0,column=2)
	tk.Button(button_frame,text="Edit information", command= lambda: edit_pi()).grid(row=0,column=1)

def update_pi_control():
	# pull my latest github repo, update everything
	curr_loc = os.path.join(os.path.dirname(__file__))
	os.chdir("%s"%(curr_loc))
	print(os.getcwd())
	update_cmd = "sudo git pull https://github.com/CrickmoreRoguljaLabs/RaspberryPiControl"
	import shlex
	update_window = tk.Toplevel(master)
	update_window.title("Updating...")
	update_string = tk.StringVar()
	update_string.set("Updating!")
	update_frame = tk.Frame(update_window, width=500, height = 400)
	update_lines = tk.Label(update_frame,textvariable=update_string)
	update_lines.pack()
	popen = subprocess.Popen(shlex.split(update_cmd), stdout=subprocess.PIPE, universal_newlines=True)
	#for stdout_line in iter(popen.stdout.readline, ""):
	#	update_string.set(stdout_line)
	#	print(stdout_line)
	#	yield stdout_line
	popen.stdout.close()
	#return_code = popen.wait()
	#if return_code:
	#	raise subprocess.CalledProcessError(return_code, update_cmd)
	tk.Label(tk.Toplevel(master),text="Update finished!").pack()
	update_window.destroy()

# Master window
master = tk.Tk()
master.title('Raspberry Pi Manager')
menubar = tk.Menu(master,tearoff=0)
file = tk.Menu(menubar)
address_manager = tk.Menu(menubar)
address_manager.add_command(label="Edit raspberry pi list", command=lambda: manage_address())
file.add_command(label="Quit", command=lambda: close_down())
update = tk.Menu(menubar)
update.add_command(label="Update Pi Control (I think it works now?)", command=lambda: update_pi_control())
menubar.add_cascade(label="File", menu=file)
menubar.add_cascade(label="Address Manager", menu=address_manager)
menubar.add_cascade(label="Update", menu=update)
master.config(menu=menubar)

ListOfPis = []

tk.Label(master, text="Pi address").grid(row=0)


## Keep track of all the pi's info in these files
try:
    import cPickle as pickle
except ImportError:  # python 3.x
    import pickle
import os

alias_map_location = os.path.join(os.path.dirname(__file__),'alias_map.p')
with open(alias_map_location, 'rb') as fp:
	alias_map = pickle.load(fp)

alias_address_map = {}
color_dict = {}
for alias,contents in alias_map.iteritems():
	alias_address_map[alias] = contents["address"]
	color_dict[alias] = contents["colors"]

add = tk.StringVar(master)
add.set(alias_address_map.keys()[0]) # default value

ListOfAliases = alias_address_map.keys()

w = tk.OptionMenu(master, add, *ListOfAliases)
w.grid(row=0, column=1)
print(alias_address_map[add.get()],add.get())

pi_threads = []

# take care of the master controller which will generate the other threads

conn_button = tk.Button(master, text='Connect', command=lambda: connect_to_pi(alias_address_map[add.get()],add.get()))
conn_button.grid(row=0, column=2)
tk.Button(master, text='Quit', command=lambda: close_down()).grid(row=7, column=0, pady=4)
master.mainloop()
