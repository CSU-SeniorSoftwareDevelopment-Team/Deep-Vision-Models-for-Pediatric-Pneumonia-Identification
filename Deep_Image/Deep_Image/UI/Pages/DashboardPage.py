
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk, ImageOps
from NET.protocol import MsgType


class DashboardPage(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.theme = controller.theme

        # Image state
        self.currentImageBytes = None
        self.pil_image = None
        self.tk_image = None

        self.canvas_w = 700
        self.canvas_h = 420

        self.last_prediction_result = None

        self.configure(bg=self.theme["BG"])

        # ========================================
        # SCROLLABLE PAGE CONTAINER
        # ========================================

        self.scroll_canvas = tk.Canvas(
            self,
            bg=self.theme["BG"],
            highlightthickness=0,
            borderwidth=0
        )

        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.scroll_canvas.yview,
            bg=self.theme["CARD"],
            troughcolor=self.theme["BG"],
            activebackground=self.theme["ACCENT"]
        )

        self.scroll_canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        # Main frame that holds the entire dashboard
        self.scrollable_frame = tk.Frame(
            self.scroll_canvas,
            bg=self.theme["BG"]
        )

        self.canvas_window = self.scroll_canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        # Update scrolling region when content changes
        self.scrollable_frame.bind(
            "<Configure>",
            self._update_scroll_region
        )

        # Make inner frame match canvas width
        self.scroll_canvas.bind(
            "<Configure>",
            self._resize_scroll_frame
        )

        # Mouse wheel support
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

        self.build_ui()






    # ========================================
    # UI CONSTRUCTION / LAYOUT
    # ========================================

    def build_ui(self):

        content = tk.Frame(
            self.scrollable_frame,
            bg=self.theme["BG"]
        )
        content.pack(fill="both", expand=True, padx=30, pady=20)

       
        # HEADER
       

        header = tk.Frame(content, bg=self.theme["BG"])
        header.pack(fill="x", pady=(0, 20))

        title_area = tk.Frame(header, bg=self.theme["BG"])
        title_area.pack(side="left")

        tk.Label(
            title_area,
            text    ="DeepImage",
            font    =("Arial", 21, "bold"),
            fg      =self.theme["TEXT"],
            bg      =self.theme["BG"]
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text    ="CLIENT WORKSPACE",
            font    =("Arial", 9, "bold"),
            fg      =self.theme["ACCENT"],
            bg      =self.theme["BG"]
        ).pack(anchor="w", pady=(3, 0))

        header_buttons = tk.Frame(header, bg=self.theme["BG"])
        header_buttons.pack(side="right")

        settings_btn = self.controller.MakeButton(
            header_buttons,
            "Settings",
            self.controller.GotoSettingsPage,
            self.theme["BORDER"],
            self.theme["BUTTON_HOVER"], 
            self.theme["BUTTON_ACTIVE"]
        )
        settings_btn.pack(side="left", padx=(0, 10))

        logoff_btn = self.controller.MakeButton(
            header_buttons,
            "Log Out",
            self.controller.trigger_logoff,
            self.theme["DANGER"],
            self.theme["DANGER_HOVER"],
            self.theme["DANGER_ACTIVE"]
        )
        logoff_btn.pack(side="left")

       
        # WORKSPACE HEADER
       

        workspace_header = tk.Frame(content, bg=self.theme["BG"])
        workspace_header.pack(fill="x", pady=(0, 12))

        tk.Label(
            workspace_header,
            text    ="Image Processing Workspace",
            font    =("Arial", 14, "bold"),
            fg      =self.theme["TEXT"],
            bg      =self.theme["BG"]
        ).pack(anchor="w")

        tk.Label(
            workspace_header,
            text    ="Load an image and submit it to the DeepImage processing server.",
            font    =("Arial", 9),
            fg      =self.theme["MUTED"],
            bg      =self.theme["BG"]
        ).pack(anchor="w", pady=(4, 0))

       
        # IMAGE VIEWPORT CARD
       

        image_card = tk.Frame(
            content,
            bg                          =self.theme["CARD"],
            highlightbackground         =self.theme["BORDER"],
            highlightthickness          =1
        )
        image_card.pack(fill            ="both", expand=True)

        image_content = tk.Frame(
            image_card,
            bg=self.theme["CARD"]
        )
        image_content.pack(
            fill        ="both",
            expand      =True,
            padx        =15,
            pady        =15
        )

        # Viewport header
        viewport_header = tk.Frame(
            image_content,
            bg=self.theme["CARD"]
        )
        viewport_header.pack(fill="x", pady=(0, 10))

        tk.Label(
            viewport_header,
            text        ="Image Preview",
            font        =("Arial", 11, "bold"),
            fg          =self.theme["TEXT"],
            bg          =self.theme["CARD"]
        ).pack(side="left")

        # Image canvas
        self.image_canvas = tk.Canvas(
            image_content,
            bg                      =self.theme["INPUT"],
            highlightbackground     =self.theme["BORDER"],
            highlightthickness      =1,
            relief                  ="flat"
        )
        self.image_canvas.pack(fill="both", expand=True)

        # Redraw preview when canvas dimensions change
        self.image_canvas.bind(
            "<Configure>",
            self.on_canvas_resize
        )

        self.show_empty_preview()

       
        # IMAGE STATUS
       

        status_frame = tk.Frame(
            content,
            bg=self.theme["BG"]
        )
        status_frame.pack(fill="x", pady=(12, 8))

        self.status_label = tk.Label(
            status_frame,
            text        ="Waiting for image",
            font        =("Arial", 9),
            fg          =self.theme["MUTED"],
            bg          =self.theme["BG"]
        )
        self.status_label.pack(side="left")

       
        # ACTION BAR
       

        action_card = tk.Frame(
            content,
            bg=self.theme["CARD"],
            highlightbackground=self.theme["BORDER"],
            highlightthickness=1
        )
        action_card.pack(fill="x", pady=(5, 0))

        action_content = tk.Frame(
            action_card,
            bg=self.theme["CARD"]
        )
        action_content.pack(fill="x", padx=15, pady=12)

        left_actions = tk.Frame(
            action_content,
            bg=self.theme["CARD"]
        )
        left_actions.pack(side="left")

        load_btn = self.controller.MakeButton(
            left_actions,
            "Load Image",
            self.load_image,
            self.theme["BORDER"],
            self.theme["BUTTON_HOVER"],
            self.theme["BUTTON_ACTIVE"]
        )
        load_btn.pack(side="left", padx=(0, 8))

        cancel_btn = self.controller.MakeButton(
            left_actions,
            "Clear",
            self.Cancel,
            self.theme["DANGER"],
            self.theme["DANGER_HOVER"],
            self.theme["DANGER_ACTIVE"]
        )
        cancel_btn.pack(side="left")

        self.send_btn = self.controller.MakeButton(
            action_content,
            "Send for Processing",
            self.Send,
            self.theme["ACCENT"],
            "#2868BD",
            "#1D4F91"
        )
        self.send_btn.pack(side="right")



        # TEST RESULTS CARD

        results_card = tk.Frame(
            content,
            bg=self.theme["CARD"],
            highlightbackground=self.theme["BORDER"],
            highlightthickness=1
        )
        results_card.pack(fill="both", expand=False, pady=(12, 0))

        results_header = tk.Frame(
            results_card,
            bg=self.theme["CARD"]
        )
        results_header.pack(fill="x", padx=15, pady=(12, 5))

        tk.Label(
            results_header,
            text="Test Results",
            font=("Arial", 11, "bold"),
            fg=self.theme["TEXT"],
            bg=self.theme["CARD"]
        ).pack(side="left")

        self.result_status = tk.Label(
            results_header,
            text="Waiting for results",
            font=("Arial", 9),
            fg=self.theme["MUTED"],
            bg=self.theme["CARD"]
        )
        self.result_status.pack(side="right")

        # Results display
        results_body = tk.Frame(
            results_card,
            bg=self.theme["INPUT"]
        )
        results_body.pack(fill="both", padx=15, pady=(5, 12))

        self.result_text = tk.Text(
            results_body,
            height=7,
            wrap="word",
            font=("Consolas", 10),
            bg=self.theme["INPUT"],
            fg=self.theme["TEXT"],
            insertbackground=self.theme["TEXT"],
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            state="disabled"
        )
        self.result_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        results_scrollbar = tk.Scrollbar(
            results_body,
            command=self.result_text.yview
        )
        results_scrollbar.pack(side="right", fill="y")

        self.result_text.configure(
            yscrollcommand=results_scrollbar.set
        )

        self.result_text.configure(state="normal")
        self.result_text.insert(
            "1.0",
            "No test results received yet."
        )
        self.result_text.configure(state="disabled")

   
    # IMAGE PREVIEW
   

    def show_empty_preview(self):

        self.image_canvas.delete("all")

        width = max(self.image_canvas.winfo_width(), 1)
        height = max(self.image_canvas.winfo_height(), 1)

        self.image_canvas.create_text(
            width // 2,
            height // 2,
            text    ="No Image Loaded\n\nLoad an image to begin processing.",
            font    =("Arial", 12),
            fill    =self.theme["MUTED"],
            justify ="center",
            tags    ="placeholder"
        )

    def on_canvas_resize(self, event):

        if self.pil_image is None:
            self.show_empty_preview()
        else:
            self.render_preview()

    def render_preview(self):

        if self.pil_image is None:
            self.show_empty_preview()
            return

        width = self.image_canvas.winfo_width()
        height = self.image_canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Leave some space around the image
        available_width = max(width - 30, 1)
        available_height = max(height - 30, 1)

        preview = self.pil_image.copy()
        preview.thumbnail(
            (available_width, available_height),
            Image.Resampling.LANCZOS
        )

        self.tk_image = ImageTk.PhotoImage(preview)

        self.image_canvas.delete("all")

        self.image_canvas.create_image(
            width // 2,
            height // 2,
            anchor="center",
            image=self.tk_image
        )



    # ==================================================================================================================================
    # HELPER FUNCTIONS
    # ==================================================================================================================================


    # Scrollable frame update functions
    def _update_scroll_region(self, event=None):

        self.scroll_canvas.configure(
            scrollregion=self.scroll_canvas.bbox("all")
        )


    def _resize_scroll_frame(self, event):

        self.scroll_canvas.itemconfigure(
            self.canvas_window,
            width=event.width
        )


    def _on_mousewheel(self, event):

        # Only scroll when the mouse is over this dashboard
        widget = self.winfo_containing(event.x_root, event.y_root)

        if widget is None:
            return

        current = widget

        while current is not None:

            if current == self:

                if event.num == 4:
                    self.scroll_canvas.yview_scroll(-1, "units")

                elif event.num == 5:
                    self.scroll_canvas.yview_scroll(1, "units")

                else:
                    self.scroll_canvas.yview_scroll(
                        int(-event.delta / 120),
                        "units"
                    )

                return

            current = getattr(current, "master", None)


    '''
    update_prediction_result: Updates the test results display based on the prediction result received from the server
    '''
    def update_prediction_result(self, prediction_result):

        if not isinstance(prediction_result, dict):
            return

        if prediction_result == self.last_prediction_result:
            return

        self.last_prediction_result = prediction_result

        status          = prediction_result.get("status", "UNKNOWN")
        diagnosis       = prediction_result.get("diagnosis", "Unavailable")
        confidence      = prediction_result.get("confidence", 0.0)

        self.result_text.configure(state="normal")
        self.result_text.delete( "1.0" , tk.END) # Clear previous results

        if status == "OK":

            self.result_status.config(
                text="Analysis Complete",
                fg=self.theme["SUCCESS"]
            )

            self.result_text.insert(
                tk.END,
                f"DIAGNOSIS\n{diagnosis}\n\n"
                f"CONFIDENCE\n{confidence:.2f}%\n\n"
                f"STATUS\n{status}"
            )

        else:

            self.result_status.config(
                text="Analysis Failed",
                fg=self.theme["ERROR"]
            )

            self.result_text.insert(
                tk.END,
                f"STATUS\n{status}\n\n"
                f"DIAGNOSIS\n{diagnosis}"
            )

        self.result_text.configure(state="disabled")


    '''
    Send: Sends the currently loaded image to the server for processing
    '''
    def Send(self):

        if self.currentImageBytes is None:
            self.status_label.config(
                text="No image available to send",
                fg=self.theme["WARNING"]
            )
            return

        try:

            self.controller.network.send_packet(
                MsgType.IMAGE,
                self.currentImageBytes
            )

            self.status_label.config(
                text="Image submitted for processing",
                fg=self.theme["SUCCESS"]
            )

        except Exception as e:

            self.status_label.config(
                text="Failed to submit image",
                fg=self.theme["ERROR"]
            )

            messagebox.showerror(
                "Network Error",
                f"Unable to send image:\n{e}"
            )

    '''
    Cancel: Clears the currently loaded image and resets the preview and status
    '''
    def Cancel(self):

        self.currentImageBytes = None
        self.pil_image = None
        self.tk_image = None

        self.show_empty_preview()

        self.status_label.config(
            text="Waiting for image",
            fg=self.theme["MUTED"]
        )


    '''
    load_image: Opens a file dialog to select an image, loads it, and updates the preview and status
    '''
    def load_image(self):

        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        try:

            # Read original image bytes.
            # These are the bytes sent to the server.
            with open(file_path, "rb") as file:
                image_bytes = file.read()

            # Load and normalize the image for preview.
            with Image.open(file_path) as image:
                image = ImageOps.exif_transpose(image)
                image.load()

                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGBA")

                self.pil_image = image.copy()

            # Update image state only after successful loading.
            self.currentImageBytes = image_bytes

            # Display preview using current canvas dimensions.
            self.render_preview()

            self.status_label.config(
                text="Image loaded and ready to submit",
                fg=self.theme["SUCCESS"]
            )

            print(f"Successfully loaded: {file_path}")

        except Exception as e:

            self.currentImageBytes = None
            self.pil_image = None
            self.tk_image = None

            self.show_empty_preview()

            self.status_label.config(
                text="Unable to load image",
                fg=self.theme["ERROR"]
            )

            messagebox.showerror(
                "Image Error",
                f"Unable to load image:\n{e}"
            )

            print(f"Error loading image: {e}")
