## Read .xlsx files directly instead of using the logReader, useful for merging logs
import EthogramLog
import os
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk
import tkFileDialog
import pandas as pd
import numpy as np

root = tk.Tk()
root.withdraw()

dir_path = os.path.dirname(os.path.realpath(__file__))
log_directory = "%s/log/" %(dir_path)

filename = tkFileDialog.askopenfilename(title = "Choose Excel file", initialdir=log_directory,filetypes=[("Excel spreadsheets","*.xlsx")])

xls = pd.ExcelFile(filename)
times_df = pd.read_excel(xls, 'Mating Times')
pulse_df = pd.read_excel(xls, 'Pulses')

etl = EthogramLog.EthogramLog()
etl.set_mating_times(times_df)
etl.set_pulse_times(pulse_df)
etl.set_title(filename)
etl.set_recording_length(80)
etl.plot_ethogram()