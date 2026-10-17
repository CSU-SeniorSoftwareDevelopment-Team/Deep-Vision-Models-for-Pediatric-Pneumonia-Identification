import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from protocol import MsgType
'''
Pages are the individual views that the user sees in the GUI.
Each page is a subclass of tk.Frame and is responsible for its own layout and functionality.
The Frontend class manages these pages.

This allows for easy navigation between them 

Team note: To make pages just create a new class that inherits from tk.Frame and add it to the Frontend's page management system.
- Steven Andrews II 
'''
class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack_propagate(False)   # Stops frames packed inside from resizing the window
        self.grid_propagate(False)   # Stops grid layouts from resizing the window
        
        self.currentImageBytes = None

        #  WINDOW TITLE:
        self.title_label = tk.Label(self, text="Dashboard Workspace:", font=("Arial", 16))
        self.title_label.pack(pady=20)
        

        #LOGOFF BUTTON
        logoff_btn = tk.Button(
            self, text="Logoff Session", bg="#d32f2f", fg="white", font=("Arial", 11, "bold"),
            command=self.controller.trigger_logoff
        )
        logoff_btn.pack(pady=10)

        
        # IMAGE VIEWPORT
        self.canvas_w = 500 # setting 
        self.canvas_h = 350
        self.image_canvas = tk.Canvas(
            self, width=self.canvas_w, height=self.canvas_h, 
            bg="#f0f0f0", relief="sunken", borderwidth=1
        )
        self.image_canvas.pack(pady=20, expand=True)


        # LOAD IMAGE BUTTON
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", pady=20) 

        load_btn = tk.Button(
            button_frame,  
            text="Load Image", 
            bg="#2e7d32", 
            fg="white", 
            font=("Arial", 11, "bold"), 
            command=self.load_image
            )
        # Use side="left" and padx to separate them horizontally
        load_btn.pack(side="left", padx=10) 


        Send_btn = tk.Button(
            button_frame,  
            text="Send:", 
            bg="#2e7d32", 
            fg="white", 
            font=("Arial", 11, "bold"), 
            command=self.Send
        )
        # Use side="left" and padx to separate them horizontally
        Send_btn.pack(side="left", padx=10)
 
    # ----------------------------------------
    # Helpers
    #-----------------------------------------

    def Send(self):
        if self.currentImageBytes == None:
            return 

        self.controller.network.send_packet( # see - networking class
                                               MsgType.IMAGE,
                                               self.currentImageBytes
                                            )
        


    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Chest X-ray: ",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            # Load image using Pillow
            pil_image = Image.open(file_path)

            # Message box popup 
            user_choice = messagebox.askokcancel(
                title="Confirm Action:", message="Send for Processing?"
            )

            if user_choice: 
                fb_ = None
                with open(file_path, "rb") as f:
                    fb_ = f.read()
            
                if fb_ != None:
                     self.currentImageBytes = fb_
                     self.controller.network.send_packet( # see - networking class
                                                             MsgType.IMAGE,
                                                             fb_
                                                        )
            else:  
                print("User clicked Cancel. Aborting NET send...")

           
            # Defined above in the __init__ 
            pil_image.thumbnail((self.canvas_w, self.canvas_h))

            # Convert to Tkinter PhotoImage format
            tk_image = ImageTk.PhotoImage(pil_image)

      
            center_x = self.canvas_w // 2
            center_y = self.canvas_h // 2

            # replace and display it
            self.image_canvas.delete("all")
            self.image_canvas.create_image(center_x, center_y, anchor="center", image=tk_image)
            self.image_canvas.image = tk_image
            print(f"Successfully loaded and displayed: {file_path}")
           

        except Exception as e:
            print(f"Error loading image: {e}")