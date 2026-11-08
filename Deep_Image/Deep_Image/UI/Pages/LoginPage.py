
import tkinter as tk

'''
Pages are the individual views that the user sees in the GUI.
Each page is a subclass of tk.Frame and is responsible for its own layout and functionality.
The Frontend class manages these pages.

This allows for easy navigation between them.

Team note: To make pages just create a new class that inherits from tk.Frame
and add it to the Frontend's page management system.
- Steven Andrews
'''

class LoginPage(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Dynamically load theme from Frontend
        self.theme = controller.theme
        self.configure(bg=self.theme["BG"])
        self.build_ui()






    def build_ui(self):

       
        # CENTER CONTAINER
        center = tk.Frame(
            self,
            bg=self.theme["BG"]
        )
        center.place(relx=0.5, rely=0.5, anchor="center")

       
        # LOGIN CARD
       

        card = tk.Frame(
            center,
            bg=self.theme["CARD"],
            highlightbackground=self.theme["BORDER"],
            highlightthickness=1
        )
        card.pack(fill="both", expand=True)

        content = tk.Frame(
            card,
            bg=self.theme["CARD"]
        )
        content.pack(padx=40, pady=35)

       
        # HEADER
       

        tk.Label(
            content,
            text    ="DeepImage",
            font    =("Arial", 24, "bold"),
            fg      =self.theme["TEXT"],
            bg      =self.theme["CARD"]
        ).pack(pady=(0, 5))

        tk.Label(
            content,
            text    ="CLIENT AUTHENTICATION",
            font    =("Arial", 9, "bold"),
            fg      =self.theme["ACCENT"],
            bg      =self.theme["CARD"]
        ).pack(pady=(0, 8))

        tk.Label(
            content,
            text    ="Sign in to access your DeepImage client.",
            font    =("Arial", 10),
            fg      =self.theme["MUTED"],
            bg      =self.theme["CARD"]
        ).pack(pady=(0, 25))

       
        # USER ID
       

        tk.Label(
            content,
            text    ="User ID",
            font    =("Arial", 10),
            fg      =self.theme["TEXT"],
            bg      =self.theme["CARD"]
        ).pack(anchor="w", pady=(0, 6))

        self.user_entry = tk.Entry(
            content,
            width    =32,
            font     =("Arial", 11),
            bg       =self.theme["INPUT"],
            fg       =self.theme["TEXT"],
            insertbackground        =self.theme["TEXT"],
            relief                  ="flat",
            highlightthickness      =1,
            highlightbackground     =self.theme["BORDER"],
            highlightcolor          =self.theme["ACCENT"]
        )
        self.user_entry.pack(
            fill="x",
            ipady=9,
            pady=(0, 18)
        )

       
        # PASSWORD
       

        tk.Label(
            content,
            text        ="Password",
            font        =("Arial", 10),
            fg          =self.theme["TEXT"],
            bg          =self.theme["CARD"]
        ).pack(anchor="w", pady=(0, 6))

        self.pass_entry = tk.Entry(
            content,
            width               =32,
            show                ="*",
            font                =("Arial", 11),
            bg                  =self.theme["INPUT"],
            fg                  =self.theme["TEXT"],
            insertbackground    =self.theme["TEXT"],
            relief              ="flat",
            highlightthickness  =1,
            highlightbackground =self.theme["BORDER"],
            highlightcolor      =self.theme["ACCENT"]
        )
        self.pass_entry.pack(
            fill="x",
            ipady=9,
            pady=(0, 22)
        )

        # Enter key submits login
        self.pass_entry.bind("<Return>", self.submit_login)

       
        # AUTHENTICATION BUTTON
       

        login_btn = self.controller.MakeButton(
            content,
            "Authenticate",
            self.submit_login,
            self.theme["ACCENT"],
            "#2868BD",
            "#1D4F91"
        )
        login_btn.pack(fill="x", ipady=2)

       
        # FOOTER
       

        tk.Label(
            content,
            text="DeepImage Client | Secure Access",
            font=("Arial", 8),
            fg=self.theme["MUTED"],
            bg=self.theme["CARD"]
        ).pack(pady=(22, 0))

        # Initial focus
        self.user_entry.focus_set()






    # =================================================================================================================
    # HELPER FUNCTIONS
    # =================================================================================================================

    def submit_login(self, event=None):

        self.controller.trigger_login_attempt(
            self.user_entry.get(),
            self.pass_entry.get()
        )
