import tkinter as tk

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.title_label = tk.Label(self, text="Dashboard Workspace", font=("Arial", 16))
        self.title_label.pack(pady=50)
        
        # Styled with a red background matching standard dashboard logouts
        logoff_btn = tk.Button(
            self, text="Logoff Session", bg="#d32f2f", fg="white", font=("Arial", 11, "bold"),
            command=self.trigger_logoff
        )
        logoff_btn.pack(pady=20)


    def trigger_logoff(self):
        # Redirect the frontend viewport back to the LoginPage frame array
        self.controller.show_page("LoginPage")