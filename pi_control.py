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

def pi_connect(address,ID):
	## Connect to a raspberry pi at location address.
	try:
		ID = [address,ID]
		this_pi = Raspberry_Pi(ID,master,colors=color_dict[ID[1]])
		ListOfPis.append(this_pi)
	except:
		print sys.exc_info()
		#connection_error()

def connection_error():
	error_window = tk.Toplevel(master)
	tk.Label(error_window,text="Error connecting to raspberry pis.\nMake sure you're on TCH network").pack()
	tk.Button(error_window,text="OK",command=error_window.destroy).pack()

def close_down():
	for pi in ListOfPis:
		pi.close_pi()
	master.destroy()

def add_address():
	pass

master = tk.Tk()
master.title('Raspberry Pi Manager')
menubar = tk.Menu(master,tearoff=0)
menubar.add_command(label="New address", command=lambda: add_address())
menubar.add_command(label="Quit", command=master.quit)
master.config(menu=menubar)

ListOfPis = []

tk.Label(master, text="Pi address").grid(row=0)

# PUT THE IP ADDRESSES OF EACH PI HERE
# you can use a dictionary to make aliases and do it that way
# if you need help remembering who's who
ListOfAddresses=[ "10.32.64.132",
	"10.32.64.93", 
	"10.32.64.135",
	"10.32.64.180", 
	"10.32.64.110",
	"10.32.64.69",
	"10.32.64.134"]
ListOfAliases=["Single Wells (1)", 
	"RGBW Right",
	"Water (red) (left)" ,
	"Green / red water", 
	"Green / red",
	"Red / green / blue / water",
	"Many wells"]

color_dict = {"Single Wells (1)":["Red"], 
<<<<<<< HEAD
	"RGBW Right":["Red", "Green", "Blue"],
=======
	"RGBW Right":["Red","Green","Blue"],
>>>>>>> bbbc1b54c0348259fd3691412da17409a6f155f4
	"Water (red) (left)":["Red"],
	"Green / red water":["Red","Green"], 
	"Green / red":["Red","Green"],
	"Red / green / blue / water":["Red","Green","Blue"],
	"Many wells":["Red"]}

alias_address_map = dict(zip(ListOfAliases,ListOfAddresses))

add = tk.StringVar(master)
add.set(ListOfAliases[0]) # default value

w = tk.OptionMenu(master, add, *ListOfAliases)
w.grid(row=0, column=1)
print alias_address_map[add.get()],add.get()
conn_button = tk.Button(master, text='Connect', command=lambda: pi_connect(alias_address_map[add.get()],add.get()))
conn_button.grid(row=0, column=2)
tk.Button(master, text='Quit', command=lambda: close_down()).grid(row=7, column=0, pady=4)
master.mainloop()
