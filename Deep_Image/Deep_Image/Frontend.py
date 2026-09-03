
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


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


        # ---------------------------------------------------------
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

        image.thumbnail(
            (760, 523)
        )

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

        training_thread = threading.Thread(
            target  =self.backend.train_model, # bound task
            args    =(self.backend.epochs,),   # epoch # 
            kwargs={
                "on_training_complete": self.training_complete # pass it the callback function to the backend so that it can call it when training is complete
            },
            daemon=True # background thread so that the GUI does not freeze while PyTorch is training the model
        )

        training_thread.start()



    # =============================================================
    # pop uo for trainign complete - needs to be moved toa class for these 
    # =============================================================


    def training_complete(self):

        save_model = messagebox.askyesno(
            "Training Complete",
            "Model training has completed...\n\n"
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

