
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading

class Frontend:

    def __init__(self, root, backend_):

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
            width=30,
            height=3
        )

        self.result_window.pack(
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



        # UPDATE RESULT 
        self.result_window.config(
            text=result_text
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
                f"Accuracy:  {accuracy * 100:.2f}%\n"
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

        self.root.mainloop()

