
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
        self.root = root
        self.root.title("DeepImage - Server")
        self.root.geometry("900x700")
        self.root.configure(bg="#f8f9fa")
        self.inDash             = False
        self.insettingsPage     = False


        


        # Dependency injection

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
        for PageClass in (LoginPage, DashboardPage , SettingsPage ): 
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.pages[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the login frame layout first
        self.show_page("LoginPage")
        
        print(" [Frontend] Initialized")


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
        bar = tk.Frame(self.root, height=40, bg="#f0f0f0", bd=1, relief="groove")
        bar.pack(side="top", fill="x")

        # Live Network connection check status
        tk.Label(bar, text="Network Live:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.net_indicator = tk.Canvas(bar, width=15, height=15, bg="#f0f0f0", highlightthickness=0)
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
        

    def GotoSettingsPage(self):
        if self.inDash == True: # is loged in and connected / short circuit check 
            self.insettingsPage = True
            self.show_page("SettingsPage")


    def GoBacktoDash(self):
        if self.inDash == True:
             self.insettingsPage = False 
             self.show_page("DashboardPage")
     


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

           # indicator 
        if self.network and self.network.is_connected:
            self.net_indicator.itemconfig(self.net_dot, fill="green")
        else:
            self.net_indicator.itemconfig(self.net_dot, fill="red")
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

