import tkinter as tk
from tkinter import messagebox
from protocol import MsgType

# PAGES - window views for UI 
# see internal documentation for details on how to extract these tho
from LoginPage import LoginPage
from DashboardPage import DashboardPage 


class Frontend:
    def __init__(self, root, backend_, network_):
        self.root = root
        self.root.title("DeepImage - Server")
        self.root.geometry("900x700")

        # i need to move this to the backend eventually - no touchy 
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
        # Ensure your custom Dashboard view is listed here once extracted into its own file
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

        # Remote server context operational status engine 
        tk.Label(bar, text="Server State:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side="left", padx=(20, 5))
        self.state_indicator = tk.Canvas(bar, width=15, height=15, bg="#f0f0f0", highlightthickness=0)
        self.state_indicator.pack(side="left", padx=5)
        self.state_dot = self.state_indicator.create_oval(2, 2, 14, 14, fill="blue")

        # Active Users display
        tk.Label(bar, text="Active Users:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side="left", padx=(20, 5))
        self.user_count_label = tk.Label(bar, text=str(self.network.numberOfActiveUsers), bg="#f0f0f0", font=("Arial", 10))
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

        if self.network and self.network.is_connected:
            self.net_indicator.itemconfig(self.net_dot, fill="green")
        else:
            self.net_indicator.itemconfig(self.net_dot, fill="red")

        if self.backend and hasattr(self.backend, 'state'):
            if self.backend.state == "PROCESSING":
                self.state_indicator.itemconfig(self.state_dot, fill="yellow")
            elif self.backend.state == "ERROR":
                self.state_indicator.itemconfig(self.state_dot, fill="red")
            else:
                self.state_indicator.itemconfig(self.state_dot, fill="blue")

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