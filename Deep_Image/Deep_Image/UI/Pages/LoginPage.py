import tkinter as tk

'''
Pages are the individual views that the user sees in the GUI.
Each page is a subclass of tk.Frame and is responsible for its own layout and functionality.
The Frontend class manages these pages.

This allows for easy navigation between them 

Team note: To make pages just create a new class that inherits from tk.Frame and add it to the Frontend's page management system.
- Steven Andrews
'''
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent) 
        self.controller = controller
        # window lable
        label = tk.Label(self, text="DeepImage Client Login", font=("Arial", 18, "bold"))
        label.pack(pady=40)

        # input 
        tk.Label(self, text="User ID", font=("Arial", 11)).pack(pady=5)
        self.user_entry = tk.Entry(self, width=30, font=("Arial", 12))
        self.user_entry.pack(pady=5)

        tk.Label(self, text="Password", font=("Arial", 11)).pack(pady=5)
        self.pass_entry = tk.Entry(self, width=30, show="*", font=("Arial", 12))
        self.pass_entry.pack(pady=5)

        # button

        login_btn =  self.controller.MakeButton(self,
                                                "Authenticate:",
                                                lambda: self.controller.trigger_login_attempt(self.user_entry.get(), self.pass_entry.get()),
                                                "#4CAF50", "#388E3C", "#1B5E20")
        login_btn.pack(pady=10)