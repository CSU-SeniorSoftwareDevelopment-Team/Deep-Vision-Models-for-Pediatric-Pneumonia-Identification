
import threading
import tkinter as tk
from NET.protocol import MsgType

# PAGES - window views for UI 
# see internal documentation for details on how to extract these tho

from UI.Pages.LoginPage import LoginPage
from UI.Pages.DashboardPage import DashboardPage 
from UI.Pages.SettingsPage import SettingsPage 

class Frontend:
    def __init__(self, root, network_):

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
    
            "DANGER": "#C03939",
            "DANGER_HOVER": "#A93232",
            "DANGER_ACTIVE": "#922B21",

    
            # NETWORK INDICATORS
    
            "ONLINE": "#4CAF50",
            "OFFLINE": "#E05252",
            "CONNECTING": "#E0A03B",

    
            # GENERAL UI
    
            "DISABLED": "#555D6B",
            "SELECTION": "#3984E8",
            "WHITE": "#FFFFFF",
            "BLACK": "#000000",

            # INDICATOR BAR COLORS
            "INDICATOR_BAR": "#f0f0f0",
        }

        self.root = root
        self.root.title("DeepImage - Client")
        self.root.geometry("900x700")
        self.root.configure(bg=self.theme["BG"])
        self.inDash             = False
        self.insettingsPage     = False

       
       
        # Dependency injection
        self.network = network_


        # Build persistent indicators at the top layout
        self.create_indicator_bar()

        # Dynamic Page Container
        self.container = tk.Frame(self.root)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        


        # Initialize tracking frames using the explicitly imported class targets
        # Ensure custom Dashboard view is listed here once extracted into its own file
        for PageClass in (LoginPage, DashboardPage , SettingsPage ): 
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.pages[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the login frame layout first
        self.show_page("LoginPage")
        
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
        bar.pack(side="bottom", fill="x")

        # Live Network connection check status
        tk.Label(bar, text="Network Live:", bg=self.theme["INDICATOR_BAR"], font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.net_indicator = tk.Canvas(bar, width=15, height=15, bg=self.theme["INDICATOR_BAR"], highlightthickness=0)
        self.net_indicator.pack(side="left", padx=5)
        self.net_dot = self.net_indicator.create_oval(2, 2, 14, 14, fill="red")




    '''
    Show_page: Raises the specified page frame to the top of the stack, making it visible.
    '''
    def show_page(self, page_name):

        if page_name in self.pages:
            frame = self.pages[page_name]
            frame.tkraise()
        else:
            print(f"Error: View component '{page_name}' has not been registered inside Frontend initialization.")



    # ========================================================================
    # USER INTERACTION TRIGGERS
    # =======================================================================

    '''
    Trigger_login_attempt: Validates the provided username and password against the system credentials.
    Parameters:
        username (str): The username to validate.
        password (str): The password to validate.
    '''
    def trigger_login_attempt(self, username, password):
        # test auto send login attemot 
        credentials = f"{username}:{password}"
        self.network.send_packet(MsgType.LOGIN, credentials.encode('utf-8'))


    '''
    Triggerd log off: 
        Forced view to loginpage 
    '''
    def trigger_logoff(self):
        # Redirect the frontend viewport back to the LoginPage frame array
        credentials = ""
        self.network.send_packet(MsgType.LOGOUT, credentials.encode('utf-8'))
        self.inDash = False
        self.show_page("LoginPage")
        
    '''
    GotoSettingsPage: Navigates the user to the SettingsPage if they are currently logged in and connected.
    '''
    def GotoSettingsPage(self):
        if self.inDash == True: # is loged in and connected / short circuit check 
            self.insettingsPage = True
            self.show_page("SettingsPage")

    '''
    GoBacktoDash: Navigates the user back to the DashboardPage from the SettingsPage.
    '''
    def GoBacktoDash(self):
        if self.inDash == True:
             self.insettingsPage = False 
             self.show_page("DashboardPage")
     




    #========================================================================
    #  UPDATE LOOP / Bootstrap
    #========================================================================

    '''
    Boot: Starts the Tkinter main event loop, allowing the GUI to run and respond to user interactions.
    '''
    def boot(self):
         self.root.mainloop()
         

    '''
        thread safe update / 30 FPS
    '''
    def update(self):
        if self.network.is_loggedin == True and self.inDash == False :
           self.show_page("DashboardPage")
           self.inDash  = True

        # forced logout
        if self.network.forcedLogOut == True:
           self.inDash                  = False
           self.insettingsPage          = False
           self.network.forcedLogOut    = False
           self.show_page("LoginPage") # kick user offline 

        # Update the dashboard page with the latest prediction result if available
        if self.network.prediction_result != None and self.inDash == True:
            # update the dashboard page with the new prediction result
            dashboard_page = self.pages.get("DashboardPage")
            if dashboard_page:
                dashboard_page.update_prediction_result(self.network.prediction_result)

             # indicator 
        if self.network and self.network.is_connected:
            self.net_indicator.itemconfig(self.net_dot, fill="green")
        else:
            self.net_indicator.itemconfig(self.net_dot, fill="red")
