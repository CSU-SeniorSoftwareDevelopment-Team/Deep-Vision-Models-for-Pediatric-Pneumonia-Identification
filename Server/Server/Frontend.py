import tkinter as tk


class Frontend:

    def __init__(self, root, backend_, network_):

        # ROOT WINDOW
        self.root = root

        self.root.title("DeepImage - Server")
        self.root.geometry("900x700")

        # Dependency injection
        self.backend = backend_
        self.network = network_

        print(" [Frontend] Initialized")

    def boot(self):
         self.root.mainloop()
