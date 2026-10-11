import tkinter as tk

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.title_label = tk.Label(self, text="Dashboard Workspace", font=("Arial", 16))
        self.title_label.pack(pady=50)
        
