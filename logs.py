import tkinter as tk
from tkinter import ttk
import json
from json.decoder import JSONDecodeError
from datetime import datetime

class LogsTab(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Create a Treeview widget for displaying the table
        self.tree = ttk.Treeview(self, columns=("Date", "Time", "Gender", "Age", "Image Captured Filename"), show="headings", height=10)
        self.tree.heading("Date", text="Date", command=lambda: self.sort_column("Date", False), anchor="center")
        self.tree.heading("Time", text="Time", command=lambda: self.sort_column("Time", False), anchor="center")
        self.tree.heading("Gender", text="Gender", command=lambda: self.sort_column("Gender", False), anchor="center")
        self.tree.heading("Age", text="Age", command=lambda: self.sort_column("Age", False), anchor="center")
        self.tree.heading("Image Captured Filename", text="Image Captured Filename", command=lambda: self.sort_column("Image Captured Filename", False), anchor="center")

        # Set alternate background colors for rows
        self.tree.tag_configure("oddrow", background="#f0f0f0")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Load data from the log.json file
        try:
            with open("log.json", "r") as file:
                log_data = json.load(file)
            self.populate_table(log_data)
        except FileNotFoundError:
            tk.Label(self, text="Log file not found.", font=("Arial", 12), fg="red").pack(pady=10)
        except JSONDecodeError:
            print("")
            
    def populate_table(self, log_data):
        # Insert data into the table with centered text alignment for all columns
        for col in self.tree["columns"]:
            self.tree.heading(col, anchor="center")
            self.tree.column(col, anchor="center")

        for i, log_entry in enumerate(log_data):
            date_str = log_entry.get("Date", "")
            time_str = log_entry.get("Time", "")
            
            # Parse the date string and format it in "Month Day, Year" format
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
            
            # Parse the time string and format it in 12-hour format
            time_obj = datetime.strptime(time_str, "%H:%M:%S")
            formatted_time = time_obj.strftime("%I:%M %p")
            
            gender = log_entry.get("Gender", "")
            age = log_entry.get("Age", "")
            image_filename = log_entry.get("Image Captured Filename", "")
            values = (formatted_date, formatted_time, gender, age, image_filename)
            
            # Centered text alignment for all columns
            tags = ("oddrow",) if i % 2 == 1 else ()
            self.tree.insert("", "end", values=values, tags=tags)

    def sort_column(self, col, reverse):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]
        data.sort(reverse=reverse)
        for i, item in enumerate(data):
            self.tree.move(item[1], "", i)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse), anchor="center")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogsTab(root)
    root.mainloop()
