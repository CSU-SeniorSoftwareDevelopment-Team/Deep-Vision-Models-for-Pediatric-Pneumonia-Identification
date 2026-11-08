import tkinter as tk
from tkinter import messagebox
from NET.protocol import MsgType

# PAGES - window views for UI 
# see internal documentation for details on how to extract these tho
from UI.Pages.LoginPage import LoginPage
from UI.Pages.DashboardPage import DashboardPage 


class Frontend:
    def __init__(self, root, backend_, network_):


         # theme 
        self.theme = {
    
            # BASE COLORS
    
            "BG": "#171A21",          # Main application background
            "CARD": "#222733",        # Cards and panels
            "INPUT": "#171D28",       # Input fields and image preview
            "BORDER": "#343C4B",      # Borders and outlines

    
            # TEXT COLORS
    
            "TEXT": "#E6EAF0",        # Primary text
            "MUTED": "#929BAA",       # Secondary text
            "PLACEHOLDER": "#687386", # Placeholder text

    
            # ACCENT COLORS
    
            "ACCENT": "#3984E8",      # Primary accent
            "ACCENT_HOVER": "#2868BD",
            "ACCENT_ACTIVE": "#1D4F91",

    
            # BUTTON COLORS
    
            "BUTTON": "#343C4B",
            "BUTTON_HOVER": "#414B5D",
            "BUTTON_ACTIVE": "#283140",

 
            # STATUS COLORS        
    
            "SUCCESS": "#4CAF50",
            "WARNING": "#E0A03B",
            "ERROR": "#E05252",
            "INFO": "#3984E8",

  
            # DESTRUCTIVE ACTIONS
    
            "DANGER": "#C03939",         # logoff button 
            "DANGER_HOVER": "#A93232",
            "DANGER_ACTIVE": "#922B21",

    
            # NETWORK INDICATORS
    
            "ONLINE": "#4CAF50",        # inidicator bars / text inidcaotrs 
            "OFFLINE": "#E05252",
            "CONNECTING": "#E0A03B",

    
            # GENERAL UI
    
            "DISABLED": "#555D6B",     
            "SELECTION": "#3984E8",
            "WHITE": "#FFFFFF",
            "BLACK": "#000000",

            # INDICATOR BAR
            "INDICATOR_BAR": "#f0f0f0",


        }



        self.root = root
        self.root.title("DeepImage - Server")
        self.root.geometry("900x700")
        

        # i need to move this to the backend eventually - no touchy -or users
        self.system_ID              = "12345"
        self.system_password        = "54321"


        # Dependency injection
        self.backend = backend_
        self.network = network_

        # Dynamic Page Container
        self.container = tk.Frame(self.root)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        
        # Build persistent indicators at the top layout
        self.create_indicator_bar()

        # Initialize tracking frames using the explicitly imported class targets
        # Ensure custom Dashboard view is listed here once extracted into its own file
        # add pages here
        for PageClass in (LoginPage, DashboardPage): 
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.pages[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the login frame layout first
        self.show_page("LoginPage")
        
        # Kick off continuous, thread-safe asynchronous state checks
        self.update_network_status_loop()
        print(" [Frontend] Initialized")







    '''
        MakeButton: Creates a styled button with hover and click effects.
    '''
    def MakeButton(self,parent, text, command, bg_color="#007bff", hover_color="#005cbf", click_color="#004085"):
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg="#ffffff",
            activebackground=click_color,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=20,
            pady=5,
            cursor="hand2",
            command=command
        )
              # Bind explicit hover shifts
        btn.bind("<Enter>", lambda e, b=btn, c=hover_color: b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.config(bg=c))
        return btn




    '''
    create_indicator_bar: Creates a top bar in the GUI that displays the network connection status and server state.
    '''
    def create_indicator_bar(self):
        bar = tk.Frame(self.root, height=40, bg=self.theme["INDICATOR_BAR"], bd=1, relief="groove")
        bar.pack(side="top", fill="x")

        # Live Network connection check status
        tk.Label(bar, text="Network Live:", bg=self.theme["INDICATOR_BAR"], font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.net_indicator = tk.Canvas(bar, width=15, height=15, bg=self.theme["INDICATOR_BAR"], highlightthickness=0)
        self.net_indicator.pack(side="left", padx=5)
        self.net_dot = self.net_indicator.create_oval(2, 2, 14, 14, fill="red")

        # Remote server context operational status engine 
        tk.Label(bar, text="Server State:", bg=self.theme["INDICATOR_BAR"], font=("Arial", 10, "bold")).pack(side="left", padx=(20, 5))
        self.state_indicator = tk.Canvas(bar, width=15, height=15, bg=self.theme["INDICATOR_BAR"], highlightthickness=0)
        self.state_indicator.pack(side="left", padx=5)
        self.state_dot = self.state_indicator.create_oval(2, 2, 14, 14, fill="blue")

        # Active Users display
        tk.Label(bar, text="Active Users:", bg=self.theme["INDICATOR_BAR"], font=("Arial", 10, "bold")).pack(side="left", padx=(20, 5))
        self.user_count_label = tk.Label(bar, text=str(self.network.numberOfActiveUsers), bg=self.theme["INDICATOR_BAR"], font=("Arial", 10))
        self.user_count_label.pack(side="left", padx=5)



    '''
    Show_page: Raises the specified page frame to the top of the stack, making it visible.
    '''
    def show_page(self, page_name):

        if page_name in self.pages:
            frame = self.pages[page_name]
            frame.tkraise()
        else:
            print(f"Error: View component '{page_name}' has not been registered inside Frontend initialization.")




    '''
    Update_network_status_loop: Continuously checks the network and backend state, updating the indicator colors accordingly.
    '''
    def update_network_status_loop(self):

        if self.network and self.network.is_running:
            self.net_indicator.itemconfig(self.net_dot, fill="green")
        else:
            self.net_indicator.itemconfig(self.net_dot, fill="red")


        if self.backend.Training == True:
             self.state_indicator.itemconfig(self.state_dot, fill="yellow")
        else:
             self.state_indicator.itemconfig(self.state_dot, fill="green")
        # blip indicator
        if self.backend.Processing == True:
            self.state_indicator.itemconfig(self.state_dot, fill="blue")
            self.backend.Processing = False


        self.root.after(200, self.update_network_status_loop)




    '''
    Trigger_login_attempt: Validates the provided username and password against the system credentials.
    Parameters:
        username (str): The username to validate.
        password (str): The password to validate.
    '''
    def trigger_login_attempt(self, username, password):

        if username == self.system_ID:
            if password == self.system_password:
               messagebox.showerror("Success", "Loged in through backend ")
               self.show_page("DashboardPage")  # next page after login
               return    
        messagebox.showerror("Error", "Failed to login to the server backend... ")

       


    '''
    Boot: Starts the Tkinter main event loop, allowing the GUI to run and respond to user interactions.
    '''
    def boot(self):
         self.root.mainloop()

    def Update(self):
        # refresh stats 
        self.user_count_label.config(text=str(self.network.numberOfActiveUsers)) 