import tkinter as tk

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="DeepImage Platform Login", font=("Arial", 18, "bold"))
        label.pack(pady=40)

        tk.Label(self, text="Username", font=("Arial", 11)).pack(pady=5)
        self.user_entry = tk.Entry(self, width=30, font=("Arial", 12))
        self.user_entry.pack(pady=5)

        tk.Label(self, text="Password", font=("Arial", 11)).pack(pady=5)
        self.pass_entry = tk.Entry(self, width=30, show="*", font=("Arial", 12))
        self.pass_entry.pack(pady=5)

        login_btn = tk.Button(
            self, text="Authenticate", width=15, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
            command=lambda: self.controller.trigger_login_attempt(self.user_entry.get(), self.pass_entry.get())
        )
        login_btn.pack(pady=30)