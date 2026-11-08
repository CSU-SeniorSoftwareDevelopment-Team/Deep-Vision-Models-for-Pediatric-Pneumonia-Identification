
import tkinter as tk
from tkinter import messagebox
import ipaddress

class DashboardPage(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.theme["BG"])

        self.controller = controller
        self.theme = controller.theme

        self.build_ui()

    # ========================================
    # UI CONSTRUCTION
    # ========================================

    def build_ui(self):

        # Main scrollable canvas
        self.main_canvas = tk.Canvas(
            self,
            bg=self.theme["BG"],
            highlightthickness=0
        )
        self.main_canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.main_canvas.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        self.main_canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        # Scrollable content frame
        content = tk.Frame(
            self.main_canvas,
            bg=self.theme["BG"]
        )

        self.canvas_window = self.main_canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw"
        )

        # Update scroll region when content changes
        content.bind(
            "<Configure>",
            self.update_scroll_region
        )

        # Keep content width matched to canvas
        self.main_canvas.bind(
            "<Configure>",
            self.resize_content
        )

        # Mouse wheel bindings
        self.main_canvas.bind("<Enter>", self.enable_mousewheel)
        self.main_canvas.bind("<Leave>", self.disable_mousewheel)
        self.scrollbar.bind("<Enter>", self.enable_mousewheel)
        self.scrollbar.bind("<Leave>", self.disable_mousewheel)

        # ========================================
        # HEADER
        # ========================================

        header = tk.Frame(content, bg=self.theme["BG"])
        header.pack(fill="x", padx=20, pady=(12, 15))

        title_area = tk.Frame(header, bg=self.theme["BG"])
        title_area.pack(side="left")

        tk.Label(
            title_area,
            text    ="Dashboard",
            font    =("Arial", 20, "bold"),
            fg      =self.theme["TEXT"],
            bg      =self.theme["BG"]
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text    ="Manage your application and network configuration.",
            font    =("Arial", 10),
            fg      =self.theme["MUTED"],
            bg      =self.theme["BG"]
        ).pack(anchor="w", pady=(3, 0))

        # Log Out
        logoff_btn = self.controller.MakeButton(
            header,
            "Log Out",
            self.trigger_logoff,
            self.theme["DANGER"],
            self.theme["DANGER_HOVER"],
            self.theme["DANGER_ACTIVE"]
        )
        logoff_btn.pack(side="right", anchor="n")

        # ========================================
        # NETWORK CONFIGURATION
        # ========================================

        network_card = tk.Frame(
            content,
            bg=self.theme["CARD"],
            highlightbackground=self.theme["BORDER"],
            highlightthickness=1
        )
        network_card.pack(fill="x", padx=20, pady=(0, 10))

        card_content = tk.Frame(
            network_card,
            bg=self.theme["CARD"]
        )
        card_content.pack(fill="x", padx=14, pady=10)

        tk.Label(
            card_content,
            text    ="Network Configuration",
            font    =("Arial", 13, "bold"),
            fg      =self.theme["TEXT"],
            bg      =self.theme["CARD"]
        ).pack(anchor="w")

        tk.Label(
            card_content,
            text    ="Configure the server IP address used by the application.",
            font    =("Arial", 9),
            fg      =self.theme["MUTED"],
            bg      =self.theme["CARD"]
        ).pack(anchor="w", pady=(3, 9))

        # IP input
        ip_row = tk.Frame(card_content, bg=self.theme["CARD"])
        ip_row.pack(fill="x")

        tk.Label(
            ip_row,
            text    ="Server IP Address",
            font    =("Arial", 9),
            fg      =self.theme["TEXT"],
            bg      =self.theme["CARD"]
        ).pack(anchor="w", pady=(0, 4))

        input_row = tk.Frame(ip_row, bg=self.theme["CARD"])
        input_row.pack(fill="x")

        self.IP_entry = tk.Entry(
            input_row,
            font    =("Arial", 10),
            bg      =self.theme["INPUT"],
            fg      =self.theme["TEXT"],
            insertbackground        =self.theme["TEXT"],
            relief                  ="flat",
            highlightthickness      =1,
            highlightbackground     =self.theme["BORDER"],
            highlightcolor          =self.theme["ACCENT"]
        )
        self.IP_entry.pack(
            side    ="left",
            fill    ="x",
            expand  =True,
            ipady   =4,
            padx    =(0, 10)
        )

        self.Applybtn = self.controller.MakeButton(
            input_row,
            "Apply Changes",
            self.ApplySettings,
            self.theme["ACCENT"],
            self.theme["ACCENT_HOVER"],
            self.theme["ACCENT_ACTIVE"]
        )
        self.Applybtn.pack(side="right")

        # ========================================
        # USER MANAGEMENT
        # ========================================

        user_card = tk.Frame(
            content,
            bg=self.theme["CARD"],
            highlightbackground=self.theme["BORDER"],
            highlightthickness=1
        )
        user_card.pack(fill="x", padx=20, pady=(0, 10))

        user_content = tk.Frame(
            user_card,
            bg=self.theme["CARD"]
        )
        user_content.pack(fill="x", padx=14, pady=10)

        tk.Label(
            user_content,
            text        ="User Management",
            font        =("Arial", 13, "bold"),
            fg          =self.theme["TEXT"],
            bg          =self.theme["CARD"]
        ).pack(anchor="w")

        tk.Label(
            user_content,
            text    ="Create and register new users authorized to access DeepImage.",
            font    =("Arial", 9),
            fg      =self.theme["MUTED"],
            bg      =self.theme["CARD"]
        ).pack(anchor="w", pady=(3, 9))

        # User ID
        tk.Label(
            user_content,
            text        ="User ID",
            font        =("Arial", 9),
            fg          =self.theme["TEXT"],
            bg          =self.theme["CARD"]
        ).pack(anchor="w", pady=(0, 3))

        self.user_id_entry = tk.Entry(
            user_content,
            font        =("Arial", 10),
            bg          =self.theme["INPUT"],
            fg          =self.theme["TEXT"],
            insertbackground        =self.theme["TEXT"],
            relief                  ="flat",
            highlightthickness      =1,
            highlightbackground     =self.theme["BORDER"],
            highlightcolor          =self.theme["ACCENT"]
        )
        self.user_id_entry.pack(
            fill="x",
            ipady=4,
            pady=(0, 7)
        )

        # Password
        tk.Label(
            user_content,
            text    ="Password",
            font    =("Arial", 9),
            fg      =self.theme["TEXT"],
            bg      =self.theme["CARD"]
        ).pack(anchor="w", pady=(0, 3))

        self.new_password_entry = tk.Entry(
            user_content,
            font    =("Arial", 10),
            show    ="*",
            bg      =self.theme["INPUT"],
            fg      =self.theme["TEXT"],
            insertbackground        =self.theme["TEXT"],
            relief                  ="flat",
            highlightthickness      =1,
            highlightbackground     =self.theme["BORDER"],
            highlightcolor          =self.theme["ACCENT"]
        )
        self.new_password_entry.pack(
            fill="x",
            ipady=4,
            pady=(0, 7)
        )

        # Input IP Address - Tailnet
        tk.Label(
            user_content,
            text    ="VPN IP ADDRESS",
            font    =("Arial", 9),
            fg      =self.theme["TEXT"],
            bg      =self.theme["CARD"]
        ).pack(anchor="w", pady=(0, 3))

        self.InputIP = tk.Entry(
            user_content,
            font    =("Arial", 10),
            bg      =self.theme["INPUT"],
            fg      =self.theme["TEXT"],
            insertbackground        =self.theme["TEXT"],
            relief                  ="flat",
            highlightthickness      =1,
            highlightbackground     =self.theme["BORDER"],
            highlightcolor          =self.theme["ACCENT"]
        )
        self.InputIP.pack(
            fill="x",
            ipady=4,
            pady=(0, 9)
        )

        # Create User
        self.add_user_btn = self.controller.MakeButton(
            user_content,
            "Create User",
            self.AddUser,
            self.theme["ACCENT"],
            self.theme["ACCENT_HOVER"],
            self.theme["ACCENT_ACTIVE"]
        )
        self.add_user_btn.pack(anchor="e")

        # ========================================
        # MODEL MANAGEMENT CARD
        # ========================================


        model_card = tk.Frame(
            content,
            bg                  =self.theme["CARD"],
            highlightthickness  =1,
            highlightbackground =self.theme["BORDER"]
        )
        model_card.pack(fill="x", pady=(0, 12))

        model_content = tk.Frame(model_card, bg=self.theme["CARD"])
        model_content.pack(fill="x", padx=14, pady=10)

        tk.Label(
            model_content,
            text    ="MODEL MANAGEMENT",
            font    =("Arial", 11, "bold"),
            fg      =self.theme["TEXT"],
            bg      =self.theme["CARD"]
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            model_content,
            text        ="Retrain the image classification model.",
            font        =("Arial", 9),
            fg          =self.theme["MUTED"],
            bg          =self.theme["CARD"]
        ).pack(anchor="w", pady=(0, 10))

        self.train_button = tk.Button(
            model_content,
            text        ="Train Model",
            command=self.TrainModel,
            font        =("Arial", 10, "bold"),
            bg          =self.theme["ACCENT"],
            fg          =self.theme["WHITE"],
            activebackground    =self.theme["ACCENT_ACTIVE"],
            activeforeground    =self.theme["WHITE"],
            relief              ="flat",
            cursor              ="hand2",
            padx                =12,
            pady                =6
        )
        self.train_button.pack(fill="x")
   
       
        
        
        
        
        
    # ========================================
    # SCROLLING
    # ========================================

    def update_scroll_region(self, event=None):
        self.main_canvas.configure(
            scrollregion=self.main_canvas.bbox("all")
        )

    def resize_content(self, event):
        self.main_canvas.itemconfigure(
            self.canvas_window,
            width=event.width
        )

    def enable_mousewheel(self, event=None):
        self.main_canvas.bind_all(
            "<MouseWheel>",
            self._on_mousewheel
        )

    def disable_mousewheel(self, event=None):
        self.main_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )






    #========================================================================================================
    # HELPERS
    #========================================================================================================



    def AddUser(self):

        user_id = self.user_id_entry.get().strip()
        password = self.new_password_entry.get()
        ip = self.InputIP.get().strip()

        # Check required fields
        if not user_id or not password or not ip:
            messagebox.showwarning(
                "Missing Information",
                "Please complete all user fields."
            )
            return

        # Validate password
        if len(password) < 8:
            messagebox.showwarning(
                "Weak Password",
                "Password must contain at least 8 characters."
            )
            return

       

        # Validate VPN IP
        try:
            vpn_ip = ipaddress.ip_address(ip)

            if not isinstance(vpn_ip, ipaddress.IPv4Address):
                raise ValueError("Only IPv4 addresses are supported.")

            # Tailscale IPv4 address range: 100.64.0.0/10
            tailscale_network = ipaddress.ip_network("100.64.0.0/10")

            if vpn_ip not in tailscale_network:
                raise ValueError(
                    "IP address must be within the Tailscale VPN range "
                    "(100.64.0.0/10)."
                )

        except ValueError as e:
            messagebox.showerror(
                "Invalid VPN IP",
                str(e)
            )
            return

        # Create account
        try:
            check = self.controller.network.user_manager.add_user(
                user_id,
                password,
                str(vpn_ip)
            )

            if not check:
                messagebox.showerror(
                    "User Creation Failed",
                    f"User '{user_id}' already exists."
                )
                return

            self.controller.network.user_manager.SaveAllUsers()

            messagebox.showinfo(
                "User Management",
                f"User '{user_id}' was successfully created."
            )

            self.user_id_entry.delete(0, tk.END)
            self.new_password_entry.delete(0, tk.END)
            self.InputIP.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror(
                "User Creation Failed",
                str(e)
            )





    def ApplySettings(self):
        # TODO: Validate IP and update backend network configuration.
        self.controller.network.Restart()



    def trigger_logoff(self):
        self.controller.show_page("LoginPage")


    def TrainingProgress(self, progress):
        print(f"Training Progress: {progress}")


    def TrainingComplete(self, *args):
        self.train_button.config(
            state="normal",
            text="Train Model"
        )

        messagebox.showinfo(
            "Training Complete",
            "Model training has completed successfully."
        )

    def TrainModel(self):

        confirm = messagebox.askyesno(
            "Train Model",
            "Are you sure you want to begin model training?"
        )

        if not confirm:
            return

        try:
            self.train_button.config(
                state="disabled",
                text="Training..."
            )

            self.controller.backend.train_model(
                progress_callback       =self.TrainingProgress,
                on_training_complete    =self.TrainingComplete
            )

        except Exception as e:
            self.train_button.config(
                state="normal",
                text="Train Model"
            )

            messagebox.showerror(
                "Training Error",
                str(e)
            )