
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
        for PageClass in (LoginPage, DashboardPage , SettingsPage): 
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
            pady=10,
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






'''old stuff not used: good for refernece  - origonal build of the UI 
class Frontend:

    def __init__(self, root, backend_, network_):

        # ROOT WINDOW

        # i made this dependency injection so
        # that the backend can be tested without the UI

        self.root = root

        self.root.title(
            "Pneumonia Detection"
        )

        self.root.geometry(
            "900x700"
        )

 
        # dependency injection for backend
        self.backend = backend_
        self.network = network_

        # image_path:
        #     Stores the path of the currently selected image.
        # display_image:
        #     Stores the Tkinter-compatible image object.

        self.image_path = None
        self.display_image = None


        # deisplay image window - this is where the selected image will be displayed


        self.image_window = tk.Label(
            self.root,
            text="No image loaded",
            relief=tk.SUNKEN
        )

        self.image_window.pack(
            padx=20,
            pady=20,
            expand=True
        )

   
        # buttons frame

        button_frame = tk.Frame(
            self.root
        )

        button_frame.pack(
            pady=20
        )


        # RESULT WINDOW

        self.result_window = tk.Label(
            self.root,
            text="Prediction: Waiting...",
            font=("Arial", 16),
            relief=tk.SUNKEN,
            width=45
        )

        self.result_window.pack(
            padx=20,
            pady=10
        )

        # STATS WINDOW - shows currently loaded model's test metrics
        self.stats_window = tk.Label(
            self.root,
            text="Model Statistics: Loading...",
            font=("Arial", 12),
            relief=tk.SUNKEN,
            width=40,
            justify=tk.LEFT,
            anchor=tk.W
        )

        self.stats_window.pack(
            padx=20,
            pady=10
        )

        # Training buttonm
        self.train_button = tk.Button(
            button_frame,
            text="Start Training",
            command=self.start_training,
            width=20,
            height=2
        )

        self.train_button.pack(
            side=tk.LEFT,
            padx=10
        )

        # trainign window 

        self.training_window = tk.Label(
            self.root,
            text="Training: Not Started",
            font=("Arial", 12),
            relief=tk.SUNKEN,
            width=35,
            height=6,
            justify=tk.LEFT,
            anchor=tk.W
        )

        

        # ---------------------------------------------------------
        # LOAD IMAGE BUTTON
        # ---------------------------------------------------------
        # Opens a file-selection dialog and allows the user to select
        # an X-ray image from the filesystem....
        # ---------------------------------------------------------

        self.load_button = tk.Button(
            button_frame,
            text="Load Image",
            command=self.load_image,
            width=20,
            height=2
        )

        self.load_button.pack(
            side=tk.LEFT,
            padx=10
        )

        # ---------------------------------------------------------
        # RUN PREDICTION BUTTON
        # ---------------------------------------------------------
        # Runs the currently selected image through the backend model.
        # 98.5% accurate on the test set. The backend handles all preprocessing and
        # prediction logic.
        #
        # The frontend only handles the user interface and passes the image path to the backend
        # This way we can test each independently and ensure that the backend is
        #  working correctly without the UI.
        #
        # ~ Steven
        # ---------------------------------------------------------

        self.predict_button = tk.Button(
            button_frame,
            text="Run Prediction",
            command=self.run_prediction,
            width=20,
            height=2
        )

        self.predict_button.pack(
            side=tk.LEFT,
            padx=10
        )







    # =============================================================
    # LOAD IMAGE
    # =============================================================
    # Ask the user to select an image from the filesystem.
    #
    # The returned value is the complete filesystem path
    # I made this use a lot of images 
    # ---------------------------------------------------------
    def load_image(self):

        file_path = filedialog.askopenfilename(
            title="Select X-Ray Image",
            filetypes=[
                (
                    "Image Files",
                    "*.jpg *.jpeg *.png *.bmp"
                ),
                (
                    "All Files",
                    "*.*"
                )
            ]
        )

        # wser cancelled the file dialog.
        if not file_path:
            return

        # Store the selected path so the prediction function can
        # later pass the same file to the backend.
        self.image_path = file_path
        
        # load image using PIL

        image = Image.open(
            file_path
        )

        # RESIZE IMAGE - make it big 
        # *( this is funky and cant be done in the backend because the backend is not aware of the UI )

        image.thumbnail((699, 481))

        # ---------------------------------------------------------
        # TKINTER IMAGE CONVERSION
        # ---------------------------------------------------------
        # Tkinter cannot directly display a PIL Image object.
        # ImageTk.PhotoImage converts it into a format Tkinter can
        # render tho
        # ---------------------------------------------------------

        self.display_image = ImageTk.PhotoImage(
            image
        )

        # Replace the "No image loaded" text with the selected image.
        self.image_window.config(
            image=self.display_image,
            text=""
        )






    # =============================================================
    # RUN PREDICTION
    # =============================================================

    def run_prediction(self):

        # CHECK FOR IMAGE
        if self.image_path is None:

            self.result_window.config(
                text="Prediction: No image loaded"
            )

            return

        # RUN MODEL
        label, confidence = (
            self.backend.predict_from_file(
                self.image_path
            )
        )

        # FORMAT RESULT
        result_text = (
            f"Prediction: {label}\n"
            f"Confidence: {confidence * 100:.2f}%"
        )

        # CHECK CONFIDENCE THRESHOLD
        below_threshold = (confidence * 100) < self.backend.threshold

        if below_threshold:
            result_text += (
                f"\n !!! WARNING !!!: Confidence is below "
                f"the {self.backend.threshold}% threshold.\n"
                f"Consider manual review."
            )

        # UPDATE RESULT 
        self.result_window.config(
            text=result_text,
            fg="red" if below_threshold else "black"
        )

        # CONSOLE OUTPUT
        # Keep this for debugging plz

        print(
            f"Prediction: {label}"
        )

        print(
            f"Confidence: "
            f"{confidence * 100:.2f}%"
        )








        
    # =============================================================
    # start training - this is a button that will start the training process in a separate thread
    # =============================================================
    def start_training(self):

        # CONFIRM BEFORE STARTING
        confirm = messagebox.askyesno(
            "Start Training",
            f"This will train the model for {self.backend.epochs} epochs.\n\n"
            "This may take a while and will use your CPU/GPU heavily.\n\n"
            "Do you want to continue?"
        )

        if not confirm:
            return  # user clicked "No" - do nothing

        self.training_window.pack(
            padx=20,
            pady=10
        )


        # PREVENT MULTIPLE TRAINING JOBS

        self.train_button.config(
            state=tk.DISABLED
        )
        # UPDATE RESULT WINDOW

        self.training_window.config(
            text="Training Status\n\nStatus: Starting..."
        )


        # start background threading task for training the model
        training_thread = threading.Thread(
            target=self.backend.train_model,
            args=(self.backend.epochs,),
            kwargs={ 
                "progress_callback": self.update_training_readout, 
                "on_training_complete": self.training_complete   
            },  
            daemon = True # background pinning thread so that it does not block the main thread
        )
        training_thread.start()


        # Check the training thread periodically.
        self.check_training_status(
            training_thread
        )





    # =============================================================
    # CHECK TRAINING STATUS
    # =============================================================

    def check_training_status(self, training_thread):

        if training_thread.is_alive():

            # Training is still running.
            # Ask Tkinter to check again in 100 ms.

            self.root.after(
                100,
                self.check_training_status, 
                training_thread
            )

        else:


            # TRAINING FINISHED
            # We are back on the Tkinter main thread, so it is now
            # safe to update GUI widgets or display a popup.
 

            self.train_button.config(
                state = tk.NORMAL
            )

            self.result_window.config(
                text = "Training: Complete"
            )
            # remove training window
            self.training_window.pack_forget()

    def _update_training_readout(
            self,
            epoch,
            total_epochs,
            loss,
            accuracy
        ):

        self.training_window.config(
            text=(
                f"Training Status\n\n"
                f"Epoch:     {epoch} / {total_epochs}\n"
                f"Loss:      {loss:.4f}\n"
                f"Accuracy:  {accuracy: .2f}%\n"
                f"Status:    Training..."
            )
        )

    def update_training_readout(
            self,
            epoch,
            total_epochs,
            loss,
            accuracy
        ):

            self.root.after(
                0,
                self._update_training_readout,
                epoch,
                total_epochs,
                loss,
                accuracy
            )

    # =============================================================
    # pop uo for trainign complete - needs to be moved toa class for these 
    # =============================================================


    def training_complete(self):

        self.root.after(
            0,
            self.show_training_complete_popup
        )

    def show_training_complete_popup(self):

        save_model = messagebox.askyesno(
            "Training Complete",
            "Model training has completed.\n\n"
            "Would you like to save the trained ResNet50 model?"
        )

        if save_model:

            self.backend.saveModel()

            messagebox.showinfo(
                "Model Saved",
                "The trained model has been saved successfully."
            )

            # refresh stats to reflect the newly saved model
            self.load_initial_stats()
        else:
            messagebox.showinfo(
                "Not Saved",
                "The newly trained weights were not saved. "
                "The previous saved model file is unchanged."
            )           


    # =============================================================
    # LOAD INITIAL STATS - show pretrained model's test performance
    # =============================================================

    # This function is called when the application starts to load the initial statistics of the pretrained model.
    def load_initial_stats(self):

        self.stats_window.config(
            text="Model Statistics: Evaluating pretrained model..."
        )

        stats_thread = threading.Thread(
            target=self._load_initial_stats_worker,
            daemon=True
        )
        stats_thread.start()

    # This function runs in a separate thread to evaluate the pretrained model and retrieve its statistics.
    def _load_initial_stats_worker(self):

        if not self.backend.model_path.exists():
            self.root.after(
                0,
                lambda: self.stats_window.config(
                    text="Model Statistics: No trained model found. Train a model first."
                )
            )
            return

        accuracy, sensitivity, f1_score, precision = self.backend.test_model()

        self.root.after(
            0,
            self._display_stats,
            accuracy,
            sensitivity,
            f1_score, 
            precision
        )

    # This function updates the statistics window with the provided model statistics.
    def _display_stats(self, accuracy, sensitivity, f1_score, precision):

        self.stats_window.config(
            text=(
                f"Pretrained Model Statistics\n"
                f"----------------------------------------------\n"
                f"Accuracy:  {accuracy:.2f}%\n"
                f"Precision: {precision * 100:.2f}%\n"
                f"Recall (Sensitivity): {sensitivity * 100:.2f}%\n"
                f"F1 Score:  {f1_score * 100:.2f}%"
            )
        )

    # =============================================================
    # START APPLICATION
    # =============================================================
    # mainloop() keeps the application running and waits for
    # user interaction such as button clicks and window events.
    #
    # This should be called once after the Frontend object has
    # been initialized.
    # ---------------------------------------------------------

    def boot(self):

        # Load the initial statistics of the pretrained model when the application starts.
        self.load_initial_stats()
        self.root.mainloop()

        '''