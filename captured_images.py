import os
import re
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox

class CapturedImagesTab(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.images_folder = "captured_images"  # Change this to your actual folder path
        self.current_page = 1
        self.items_per_page = 25  # 5x5 grid

        self.load_images()
        self.create_widgets()

    def load_images(self):
        self.image_paths = [os.path.join(self.images_folder, filename) for filename in os.listdir(self.images_folder)
                            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    def create_widgets(self):
        # Your existing code to create the image frame
        self.image_frame = tk.Frame(self, bg="white")
        self.image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.show_images()

        # Pagination
        self.pagination_frame = tk.Frame(self, bg="white")
        self.pagination_frame.pack(side=tk.BOTTOM, pady=10)

        prev_button = ttk.Button(self.pagination_frame, text="Previous", command=self.show_prev_page)
        prev_button.grid(row=0, column=0, padx=5)

        next_button = ttk.Button(self.pagination_frame, text="Next", command=self.show_next_page)
        next_button.grid(row=0, column=1, padx=5)

    def show_images(self):
        # Clear existing images
        self.clear_images()

        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page

        # Your code to create the scrollable frame
        scrollable_frame = tk.Frame(self.image_frame, bg="white")
        scrollable_frame.pack(fill=tk.BOTH, expand=True)

        canvas2 = tk.Canvas(scrollable_frame, bg="white")
        canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(scrollable_frame, orient=tk.VERTICAL, command=canvas2.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas2.configure(yscrollcommand=scrollbar.set)
        canvas2.bind('<Configure>', lambda e: canvas2.configure(scrollregion=canvas2.bbox('all')))
        inner_frame = tk.Frame(canvas2, bg="white")
        canvas2.create_window((0, 0), window=inner_frame, anchor='nw')

        # Bind the MouseWheel event to the inner frame
        inner_frame.bind('<MouseWheel>', lambda e: canvas2.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        for i in range(start_index, end_index):
            if i < len(self.image_paths):
                file_name = os.path.basename(self.image_paths[i])

                image_path = self.image_paths[i]
                image = Image.open(image_path)
                image = image.resize((200, 200))  # Adjust the size as needed

                photo = ImageTk.PhotoImage(image)
                label = tk.Label(inner_frame, image=photo)
                label.image = photo

                row = (i - start_index) // 5
                col = (i - start_index) % 5

                label.grid(row=row, column=col, padx=10, pady=(30, 2))

                file_label = tk.Label(inner_frame, text=file_name, wraplength=180, justify=tk.CENTER)
                file_label.grid(row=row + 1, column=col, pady=(0, 10), sticky='n')

                # Bind the delete_image function to the label click event
                label.bind("<Button-1>", lambda e, path=image_path: self.delete_image(path))
                label.bind("<Enter>", lambda e, label=label, path=image_path: self.hover_in(e, label, path))
                label.bind("<Leave>", lambda e, label=label, path=image_path: self.hover_out(e, label, path))

        canvas2.update_idletasks()
        canvas2.config(scrollregion=canvas2.bbox('all'))

    # Your existing methods for pagination
    def show_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.clear_images()
            self.show_images()

    def show_next_page(self):
        if self.current_page < (len(self.image_paths) + self.items_per_page - 1) // self.items_per_page:
            self.current_page += 1
            self.clear_images()
            self.show_images()

    def clear_images(self):
        for widget in self.image_frame.winfo_children():
            widget.destroy()

    # Your existing methods for image interactions
    def delete_image(self, image_path):
        result = messagebox.askquestion("Delete Image", "Are you sure you want to delete this image?")
        if result == 'yes':
            os.remove(image_path)
            # Update the image display after deletion
            self.show_images()

    def hover_in(self, event, image_label, image_path):
        event.widget.config(cursor="hand2")
        event.widget.config(borderwidth=2, relief="solid", bd=1, fg="#880808", highlightbackground="#880808")

    def hover_out(self, event, image_label, image_path):
        event.widget.config(cursor="")
        event.widget.config(borderwidth=0)
