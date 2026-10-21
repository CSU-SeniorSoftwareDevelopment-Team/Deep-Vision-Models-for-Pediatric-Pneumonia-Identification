import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from sympy import cancel
from NET.protocol import MsgType
'''
Pages are the individual views that the user sees in the GUI.
Each page is a subclass of tk.Frame and is responsible for its own layout and functionality.
The Frontend class manages these pages.

This allows for easy navigation between them 
'''
class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack_propagate(False)   # Stops frames packed inside from resizing the window
        self.grid_propagate(False)   # Stops grid layouts from resizing the window
        

        #  WINDOW TITLE:
        self.title_label = tk.Label(self, text="Dashboard Workspace:", font=("Arial", 16))
        self.title_label.pack(pady=20)



        # upper boind buttons 
        upper_row_frame = tk.Frame(self)
        upper_row_frame.pack(side="top", padx=20) 

       
        #LOGOFF BUTTON
        logoff_btn =  self.controller.MakeButton(upper_row_frame,"Logoff Session:",self.controller.trigger_logoff,"#d32f2f", "#b71c1c", "#9a0007")
        logoff_btn.pack(pady=10)

        back_btn =  self.controller.MakeButton(upper_row_frame,"Back:",self.controller.GoBacktoDash,"#d32f2f", "#b71c1c", "#9a0007")
        back_btn.pack(pady=10)



