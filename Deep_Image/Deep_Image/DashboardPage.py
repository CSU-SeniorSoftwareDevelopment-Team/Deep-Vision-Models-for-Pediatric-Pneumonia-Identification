import tkinter as tk
'''
Pages are the individual views that the user sees in the GUI.
Each page is a subclass of tk.Frame and is responsible for its own layout and functionality.
The Frontend class manages these pages.

This allows for easy navigation between them 

Team note: To make pages just create a new class that inherits from tk.Frame and add it to the Frontend's page management system.
- Steven Andrews
'''
class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # window lable
        self.title_label = tk.Label(self, text="Dashboard Workspace", font=("Arial", 16))
        self.title_label.pack(pady=50)
        
        # button with red BG
        logoff_btn = tk.Button(
            self, text="Logoff Session", bg="#d32f2f", fg="white", font=("Arial", 11, "bold"),
            command=self.controller.trigger_logoff
        )
        logoff_btn.pack(pady=20)



 