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
        

        logoff_btn =  self.controller.MakeButton(self,"Logoff Session:",self.trigger_logoff,"#d32f2f", "#b71c1c", "#9a0007")
        logoff_btn.pack(pady=10)


    def trigger_logoff(self):
        # Redirect the frontend viewport back to the LoginPage frame array
        self.controller.show_page("LoginPage")