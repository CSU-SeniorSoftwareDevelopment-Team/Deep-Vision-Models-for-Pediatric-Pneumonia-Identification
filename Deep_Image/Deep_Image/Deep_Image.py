
''' ---------------------------------------------------------------------------------------------
DEEP IMAGE ( overview ):
---------------------------------------------------------------------------------------------------
Deep image is a student lead senior software engineering project at Columbus State Univeristy. 
The goal of this project is to create a deep learning image processing application to identify
phnemonia in pediatric patients that can be used to enhance and manipulate images
using state-of-the-art deep learning techniques.

The application will be built using Python and will utilize various deep learning
libraries such as TensorFlow, PyTorch, etc. 

The application will be designed to be user-friendly and will provide a simple 
interface for users to upload images, process them, and view the results.
    
-------------------------------------------------------------------------------------------------
Students:
                            - 1. Steven Andrews II      
                            - 2. Bhavik Patel           
                            - 3.
                            - 4.

School:
                            Columbus State University
                            Fall 2026 

Development Period:         15 Weeks  ( August 2026 - December 2026 )

           

----------------------------------------------------------------------------------------------'''




import time
import Backend


import threading




def main_loop():
    
    # Frame rate intervals (fps)
    MED_FPS                     = 30
    HIGH_FPS                    = 120
    ULTRA_HIGH_FPS              = 300

    # Calculate time intervals for each FPS
    MED_INTERVAL                = 1 / MED_FPS           
    HIGH_INTERVAL               = 1 / HIGH_FPS          
    ULTRA_HIGH_INTERVAL         = 1 / ULTRA_HIGH_FPS    

    ULTRA_skip                  = 0  # current skip ammount 
    ULTRA_max_skip              = 2  # Max skip for high FPS

    med_tick                    = 0  # clocks
    high_tick                   = 0
    ultra_tick                  = 0 
    last_tick                   = time.time()
    EXIT = False

    
    backend = Backend.Backend()
 
    # Background training thread // need to set thiw on and off with a button in the UI
    training_thread = threading.Thread(
        target=backend.train_model,
        args=(backend.epochs,),
        daemon=True
      )

    training_thread.start()

        

 
    def Update_MED():
        # use threads for all training and all run of images 
        #// background tasks ( anything that runs at a low frame rate )
        #print("threating is working, main thread running fine...")
        # Add UI and background data tasks here like saving or loai=ding quick data 
        pass
        
     
    def Update_HIGH():
        #// User interface here ( moderate frame rate ))

        pass 
        

    def Update_ULTRA_HIGH():
        #anything that needs to run in real time like audio, graphics, high speed clocks 
        pass
            



    # Task loop
    while not EXIT:
        # Time elapsed since last frame
        cur_tick                =  time.time()
        delta_time              =  cur_tick - last_tick
        last_tick               =  cur_tick  

        # Accumulate time for each frame rate
        med_tick                += delta_time
        high_tick               += delta_time
        ultra_tick              += delta_time

        # MED FPS function call 
        if med_tick >= MED_INTERVAL:
            Update_MED()
            med_tick                                -= MED_INTERVAL

        # HIGH FPS function call 
        if high_tick >= HIGH_INTERVAL:
            Update_HIGH()
            high_tick                               -= HIGH_INTERVAL

        # ULTRA HIGH FPS function call  ( has dynamic frame skipping )
        if ultra_tick >= ULTRA_HIGH_INTERVAL: 
            ultra_tick                              -= ULTRA_HIGH_INTERVAL
            if delta_time > HIGH_INTERVAL:  # FPS is lagging
                ULTRA_skip                           = min(ULTRA_skip + 1, ULTRA_max_skip)  # Increase skip, max 2
            else:
                ULTRA_skip                           = max(ULTRA_skip - 1, 0)  # Reduce skip if FPS is stable
            if ULTRA_skip == 0:  
                Update_ULTRA_HIGH()
        

       

# Run the asyncio event loop
if __name__ == "__main__":
    main_loop()
