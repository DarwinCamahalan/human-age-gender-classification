import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

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

        # Get the requested width of the widget
        widget_width = self.winfo_reqwidth()

        for i in range(start_index, end_index):
            if i < len(self.image_paths):
                image_path = self.image_paths[i]
                image = Image.open(image_path)

                # Calculate the aspect ratio to maintain image proportions
                aspect_ratio = image.width / image.height

                # Calculate the new width and height based on the available space
                new_width = int(widget_width / 5)  # 5 columns
                new_height = int(new_width / aspect_ratio)

                # Check if the calculated width and height are greater than zero
                if new_width > 0 and new_height > 0:
                    # Resize the image using Lanczos resampling
                    image = image.resize((new_width, new_height), Image.LANCZOS)

                    tk_image = ImageTk.PhotoImage(image)

                    label = tk.Label(self.image_frame, image=tk_image, bg="white")
                    label.image = tk_image  # Keep a reference to avoid garbage collection
                    row, col = divmod(i - start_index, 5)
                    label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # Configure row and column weights to make images expand and center
        for i in range(5):
            self.image_frame.columnconfigure(i, weight=1)
            self.image_frame.rowconfigure(i, weight=1)

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

# If you want to test this module separately, you can use the following block:
if __name__ == "__main__":
    root = tk.Tk()
    app = CapturedImagesTab(root, bg="white")
    app.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    root.mainloop()
