import tkinter as tk

class CapturedImagesTab(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        tk.Label(self, text="Captured Images Tab Content", font=("Arial", 14)).pack(pady=20)
