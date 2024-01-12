import tkinter as tk
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphsTab(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Specify the path to your log.json file
        self.json_file = "log.json"
        self.ageList = ['11-15', '16-20', '21-25', '26-30', '31-35', '36-40', '41-45', '46-50', '51-55']
        self.genderList = ["Male", "Female"]

        # Display graphs automatically
        self.display_graphs()

    def display_graphs(self):
        try:
            with open(self.json_file) as jsonfile:
                data = json.load(jsonfile)

                # Check if the data is a list of entries
                if not isinstance(data, list):
                    # Clear previous widgets
                    self.clear_graphs_tab()

                    tk.Label(self, text="No data available for graphs", relief='ridge', width=20).pack(side=tk.LEFT)
                    return

                # Extract age and gender data from the JSON file entries
                age_data = [entry.get("Age", "") for entry in data]
                gender_data = [entry.get("Gender", "") for entry in data]

                # Count the occurrences of each age range and gender
                age_counts = {age_range: age_data.count(age_range) for age_range in self.ageList}
                gender_counts = {gender: gender_data.count(gender) for gender in self.genderList}

                # Combine age ranges with the same percentage value
                combined_age_ranges = {}
                for age_range, count in age_counts.items():
                    if count not in combined_age_ranges:
                        combined_age_ranges[count] = [age_range]
                    else:
                        combined_age_ranges[count].append(age_range)

                # Convert to a list of strings
                age_labels = [", ".join(sorted(age_ranges)) for age_ranges in combined_age_ranges.values()]

                # Create the figure for both pie charts
                if not hasattr(self, 'figure'):
                    self.figure, (self.age_ax, self.gender_ax) = plt.subplots(1, 2, figsize=(12, 6))
                    self.canvas = FigureCanvasTkAgg(self.figure, master=self)
                    self.canvas_widget = self.canvas.get_tk_widget()
                    self.canvas_widget.pack(fill=tk.BOTH, expand=True)

                # Update the age range pie chart data
                self.age_ax.clear()
                self.age_ax.pie(combined_age_ranges.keys(), labels=age_labels, autopct='%1.1f%%', startangle=90)
                self.age_ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                self.age_ax.set_title("Age Range Percentage")

                # Update the gender pie chart data
                self.gender_ax.clear()
                self.gender_ax.pie(gender_counts.values(), labels=self.genderList, autopct='%1.1f%%', startangle=90)
                self.gender_ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                self.gender_ax.set_title("Gender Percentage")

                # Update the display
                self.canvas.draw()

                # Remove the label if it exists
                for widget in self.winfo_children():
                    if isinstance(widget, tk.Label) and widget.cget("text") == "No data available for graphs":
                        widget.destroy()

        except (json.JSONDecodeError, FileNotFoundError):
            # Clear previous widgets
            self.clear_graphs_tab()
            print("")


    def clear_graphs_tab(self):
        # Clear the graphs in the tab
        if hasattr(self, 'figure'):
            plt.close(self.figure)
            delattr(self, 'figure')

        # Clear any other widgets in the tab
        for widget in self.winfo_children():
            widget.destroy()

   