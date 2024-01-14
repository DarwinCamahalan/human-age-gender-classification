import os
import json
from datetime import datetime
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

class CapturedImagesTab(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.images_folder = "captured_images"  # Change this to your actual folder path
        self.current_page = 1
        self.items_per_page = 20  # 4x5 grid
        self.sort_order_var = tk.StringVar(value="Ascending")
        self.age_filter_var = tk.StringVar(value="All")
        self.gender_filter_var = tk.StringVar(value="All")

        self.load_images()
        self.create_widgets()

    def load_images(self):
        self.image_paths = [os.path.join(self.images_folder, filename) for filename in os.listdir(self.images_folder)
                            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

        # Sort the image paths based on date and time from log.json
        self.image_paths.sort(key=lambda path: self.get_datetime_from_log(path), reverse=False)

    def get_datetime_from_log(self, path):
        file_name = os.path.basename(path)

        log_json_path = "log.json"
        with open(log_json_path, 'r') as log_file:
            log_json = json.load(log_file)

        for log_entry in log_json:
            if log_entry["Image Captured Filename"] == file_name:
                date_object = datetime.strptime(log_entry['Date'], '%Y-%m-%d')
                formatted_time = datetime.strptime(log_entry['Time'], '%H:%M:%S').strftime('%I:%M %p')
                return datetime.combine(date_object, datetime.strptime(formatted_time, '%I:%M %p').time())

        return datetime.min  # Return a default value (minimum datetime) in case of an error

    def create_widgets(self):
        # Your existing code to create the image frame
        self.image_frame = tk.Frame(self, bg="white")
        self.image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.show_images()

        # Pagination and Sorting
        self.pagination_sort_frame = tk.Frame(self, bg="white")
        self.pagination_sort_frame.pack(side=tk.BOTTOM, pady=10, padx=10, fill=tk.X, anchor='e')

        prev_button = ttk.Button(self.pagination_sort_frame, text="Previous", command=self.show_prev_page)
        prev_button.grid(row=0, column=0, padx=5)

        next_button = ttk.Button(self.pagination_sort_frame, text="Next", command=self.show_next_page)
        next_button.grid(row=0, column=1, padx=5)

        # Sort order dropdown
        sort_label = tk.Label(self.pagination_sort_frame, text="Sort Order:", bg="white")
        sort_label.grid(row=0, column=2, padx=(20, 5))

        sort_options = ["Ascending", "Descending"]
        sort_dropdown = ttk.Combobox(self.pagination_sort_frame, textvariable=self.sort_order_var, values=sort_options)
        sort_dropdown.grid(row=0, column=3, padx=5)
        sort_dropdown.bind("<<ComboboxSelected>>", self.apply_filters)

        # Filter by age
        age_label = tk.Label(self.pagination_sort_frame, text="Filter by Age:", bg="white")
        age_label.grid(row=0, column=4, padx=(20, 5))

        age_options = ["All", "11-15", "16-20", "21-25", "26-30", "31-35", "36-40", "41-45", "46-50", "51-55"]
        age_dropdown = ttk.Combobox(self.pagination_sort_frame, textvariable=self.age_filter_var, values=age_options)
        age_dropdown.grid(row=0, column=5, padx=5)
        age_dropdown.bind("<<ComboboxSelected>>", self.apply_filters)

        # Filter by gender
        gender_label = tk.Label(self.pagination_sort_frame, text="Filter by Gender:", bg="white")
        gender_label.grid(row=0, column=6, padx=(20, 5))

        gender_options = ["All", "Male", "Female"]
        gender_dropdown = ttk.Combobox(self.pagination_sort_frame, textvariable=self.gender_filter_var, values=gender_options)
        gender_dropdown.grid(row=0, column=7, padx=5)
        gender_dropdown.bind("<<ComboboxSelected>>", self.apply_filters)

        # Clear filters and sorting button
        clear_button = ttk.Button(self.pagination_sort_frame, text="Clear Filters", command=self.clear_filters)
        clear_button.grid(row=0, column=8, padx=5)

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

        # Bind the MouseWheel event to the canvas
        canvas2.bind_all("<MouseWheel>", lambda e: canvas2.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        for i in range(start_index, end_index):
            if i < len(self.image_paths):
                file_name = os.path.basename(self.image_paths[i])

                image_path = self.image_paths[i]
                image = Image.open(image_path)
                image = image.resize((200, 200))  # Adjust the size as needed

                photo = ImageTk.PhotoImage(image)
                card_frame = tk.Frame(inner_frame, bg="white", highlightbackground="gray", highlightthickness=1)

                label_image = tk.Label(card_frame, image=photo, bg="white")
                label_image.image = photo

                # Double-click event binding for image preview
                label_image.bind("<Double-1>", lambda event, path=image_path: self.show_image_popup(path))

                label_image.grid(row=0, column=0, sticky='nsew')

                # Display information from log.json
                log_json_path = "log.json"
                with open(log_json_path, 'r') as log_file:
                    log_json = json.load(log_file)

                for log_entry in log_json:
                    if log_entry["Image Captured Filename"] == file_name:
                        date_object = datetime.strptime(log_entry['Date'], '%Y-%m-%d')
                        formatted_date = date_object.strftime('%m/%d/%Y')
                        formatted_time = datetime.strptime(log_entry['Time'], '%H:%M:%S').strftime('%I:%M %p')
                        info_label_text = f"Date: {formatted_date} \nTime: {formatted_time}"

                        info_label = tk.Label(card_frame, text=info_label_text, wraplength=200, justify=tk.LEFT, bg="white")
                        info_label.grid(row=1, column=0, pady=(5, 10), sticky='w')

                        # Update the label configuration with the new text
                        info_label.config(text=f"Date: {formatted_date} \nTime: {formatted_time}")

                        break  # Break out of the loop once information is found

                card_frame.grid(row=(i - start_index) // 5, column=(i - start_index) % 5, padx=10, pady=10, sticky='nsew')

        for row_num in range(inner_frame.grid_size()[1]):
            inner_frame.grid_rowconfigure(row_num, weight=1)

        for col_num in range(inner_frame.grid_size()[0]):
            inner_frame.grid_columnconfigure(col_num, weight=1)

        canvas2.update_idletasks()
        canvas2.config(scrollregion=canvas2.bbox('all'))

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

    def show_image_popup(self, image_path):
        try:
            image = Image.open(image_path)
            image_popup = tk.Toplevel(self)
            image_popup.title("Image Preview")

            width, height = image.size
            max_width = 800
            max_height = 600
            if width > max_width or height > max_height:
                ratio = min(max_width / width, max_height / height)
                width = int(width * ratio)
                height = int(height * ratio)
                image = image.resize((width, height), Image.ANTIALIAS)

            tk_image = ImageTk.PhotoImage(image)

            image_label = tk.Label(image_popup, image=tk_image)
            image_label.image = tk_image
            image_label.pack()

            screen_width = image_popup.winfo_screenwidth()
            screen_height = image_popup.winfo_screenheight()

            x_coordinate = (screen_width - width) // 2
            y_coordinate = (screen_height - height) // 2

            image_popup.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

            image_popup.resizable(False, False)
            image_popup.attributes("-toolwindow", 1)

        except FileNotFoundError:
            tk.messagebox.showerror("Error", f"Image not found: {image_path}")

    def sort_images(self, event=None):
        # Sort the image paths based on date and time from log.json and the selected sort order
        reverse_order = self.sort_order_var.get() == "Descending"
        self.image_paths.sort(key=lambda path: self.get_datetime_from_log(path), reverse=reverse_order)

        # Redraw the images with the new order and filters
        self.show_images()

    def apply_filters(self, event=None):
        # Apply filters and sorting
        self.load_images()
        self.filter_images()
        self.sort_images()

    def filter_images(self, event=None):
        # Filter the images based on age and gender
        age_filter = self.age_filter_var.get()
        gender_filter = self.gender_filter_var.get()

        filtered_paths = []

        for path in self.image_paths:
            file_name = os.path.basename(path)
            age, gender = self.get_age_gender_from_log(file_name)

            # Apply filters
            if (age_filter == "All" or age_filter == age) and (gender_filter == "All" or gender_filter.lower() == gender.lower()):
                filtered_paths.append(path)

        # Update image paths with filtered paths
        self.image_paths = filtered_paths

    def get_age_gender_from_log(self, file_name):
        log_json_path = "log.json"
        with open(log_json_path, 'r') as log_file:
            log_json = json.load(log_file)

        for log_entry in log_json:
            if log_entry["Image Captured Filename"] == file_name:
                age = log_entry.get('Age', 'N/A')
                gender = log_entry.get('Gender', 'N/A')
                return age, gender

        return 'N/A', 'N/A'

    def clear_filters(self):
        # Clear all filters and sorting
        self.age_filter_var.set("All")
        self.gender_filter_var.set("All")
        self.sort_order_var.set("Ascending")

        # Reload images and show
        self.load_images()
        self.show_images()

if __name__ == "__main__":
    root = tk.Tk()
    app = CapturedImagesTab(root)
    root.mainloop()
