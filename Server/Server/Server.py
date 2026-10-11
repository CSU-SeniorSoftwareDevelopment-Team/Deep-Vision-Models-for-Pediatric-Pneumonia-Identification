
'''------------------------------------------------------------------------------------------------
DEEP IMAGE ( Server ) 
---------------------------------------------------------------------------------------------------
Deep image server is a python AI model that uses Pytourch to train a neural network to predict the class of an image.
The server is designed to be used in conjunction with a client application that sends images to the server for prediction.


Architcecture:
    The server is designed to be modular and extensible, with separate components for the backend, frontend, and networking. 
    The backend handles the neural network, datasets, training, and predictions. 
    The frontend handles the GUI and user interaction. 
    The networking component handles the network communication with the client application.

Features:
    - Modular architecture for easy maintenance and extensibility.
    - GUI for user interaction and monitoring.
    - Networking component for handling client-server communication.
    - Backend component for training and predicting image classes using a neural network.
    - Secure communication using TLS/SSL for data transmission.
    - Multi-threaded design for handling multiple client connections simultaneously.
    - Background processing for training and prediction tasks to keep the GUI responsive.
    - Support for image preprocessing, including resizing, grayscaling, and normalization.
    - Support for training and testing datasets using PyTorch's ImageFolder.
    - Support for logging and error handling to ensure robustness and reliability.

----------------------------------------------------------------------------------------------------
Team Lead:                    Steven Andrews II


Students:
                            - 1. Steven Andrews II
                            - 2. Bhavik Patel
                            - 3. Jhonathan Falls
                            - 4. Ahumada Camillie

School:
                            Columbus State University
                            Fall 2026

Development Period:         15 Weeks (August 2026 - December 2026)
                            Cycle 1: 8 Weeks (August 2026 - October 2026)     - base implementation of the AI and demo
                            Cycle 2: 7 Weeks (October 2026 - December 2026)   - Server based implementation / service of AI demo 

---------------------------------------------------------------------------------------------------
'''



import time
import threading
import tkinter as tk


# Backend Dependencies
import Backend
import Frontend
import Networking


def main_loop():
    


    # =========================================================================
    # FRAME RATE SETTINGS
    # =========================================================================
    # These values are used for scheduling periodic application tasks.
    #
    # Tkinter's "after()" function is used instead of a manual while-loop.
    # This allows Tkinter to maintain control of the main application thread.


    MED_FPS                 = 30
    HIGH_FPS                = 120
    ULTRA_HIGH_FPS          = 300

    MED_INTERVAL            = int(1000 / MED_FPS)
    HIGH_INTERVAL           = int(1000 / HIGH_FPS)
    ULTRA_HIGH_INTERVAL     = int(1000 / ULTRA_HIGH_FPS)


    # APPLICATION STATE

    EXIT = False


    # =========================================================================
    # DEPENDENCY INJECTION
    # =========================================================================
    ''' The application creates the major components here and passes the
     dependencies into the classes that need them. Easier for testing and debugging this way.
    
     Backend:
         Handles the neural network, datasets, training, and predictions.
    
     Frontend:
         Handles the GUI and user interaction.
    
     Networking:
         Handles the network communication with the server.
    
     Tkinter:
         Owns the MAIN THREAD.
    '''


    root = tk.Tk()

    backend = Backend.Backend()         
    network = Networking.Networking() 

    # Frontend injected with root, backend, and network dependencies
    frontend = Frontend.Frontend(
        root,
        backend,
        network
    )
    print("--------------------------------------------------------------------------------------")
    print(" [Server] All components initialized")

    # =========================================================================
    # MEDIUM-FREQUENCY UPDATE
    # =========================================================================
    # Runs approximately 30 times per second.

    def Update_MED():

        network.Update()  # Update the network connection state handlers
        
        # Add low-frequency UI/application tasks here
        # low frequency networking, logging, processing, etc.

        if not EXIT:

            root.after(
                MED_INTERVAL,
                Update_MED
            )


    # =========================================================================
    # HIGH-FREQUENCY UPDATE
    # =========================================================================
    # Runs approximately 120 times per second.


    def Update_HIGH():

 
        # Add lightweight high-frequency UI tasks here
        # networking, logging, processing, etc.

        if not EXIT:

            root.after(
                HIGH_INTERVAL,
                Update_HIGH
            )


    # =========================================================================
    # ULTRA-HIGH-FREQUENCY UPDATE
    # =========================================================================
    # Runs approximately every 3 milliseconds.


    def Update_ULTRA_HIGH():
        
        # Add extremely lightweight real-time tasks here ! <<<<<<<<
        # networking 

        if not EXIT:
            root.after(
                ULTRA_HIGH_INTERVAL,
                Update_ULTRA_HIGH
            )



    # START APPLICATION TASKS
    # Schedule the update functions.

    root.after(
        MED_INTERVAL,
        Update_MED
    )

    root.after(
        HIGH_INTERVAL,
        Update_HIGH
    )

    root.after(
        ULTRA_HIGH_INTERVAL,
        Update_ULTRA_HIGH
    )

    # =========================================================================
    # TESTING
    # =========================================================================
    '''
     DO NOT REMOVE THESE EXAMPLES FOR TESTING:
    
         - BLACK BOX TESTING
         - WHITE BOX TESTING



     -------------------------------------------------------------------------
     Testing demo - single image prediction
     -------------------------------------------------------------------------
    
     backend.Run_Single_Img_Through()
    


     -------------------------------------------------------------------------
     Training demo
     -------------------------------------------------------------------------
     Training should run in a BACKGROUND THREAD so that the GUI does not
     freeze while PyTorch is training the model.
    
     Example:
    
     training_thread = threading.Thread(
         target=backend.train_model,
         args=(backend.epochs,),
         daemon=True
     )
    
     training_thread.start()
    
     This should eventually be started by a button in the Frontend.
     -------------------------------------------------------------------------
     '''


    # START FRONTEND
    frontend.boot()





# PROGRAM ENTRY POINT
if __name__ == "__main__":
    main_loop()


