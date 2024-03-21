import tkinter as tk
from tkinter import ttk
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

        # Variable to store the selected graph type
        self.selected_graph_type = tk.StringVar()
        self.selected_graph_type.set("Pie Chart")  # Default selected graph type

        # Variable to store the selected date
        self.selected_date = tk.StringVar()
        self.selected_date.set("All")  # Default selected date

        # Display graphs automatically
        self.create_widgets()

        # Set the selected date to the oldest date with data
        self.set_initial_selected_date()

        self.display_graphs()

    def set_initial_selected_date(self):
        try:
            with open(self.json_file) as jsonfile:
                data = json.load(jsonfile)
                available_dates = [entry.get("Date", "") for entry in data if entry.get("Date")]
                unique_dates = sorted(set(available_dates))

                # Set the selected date to "All" if no unique dates are available
                if not unique_dates:
                    self.selected_date.set("All")

        except (json.JSONDecodeError, FileNotFoundError):
            pass  # Handle file not found or invalid JSON

    def create_widgets(self):
        # Create a label and text label for mimicking the select field
        label_text = tk.StringVar()
        label_text.set("Pie Chart ▼")  # Default label text with arrow down symbol

        label = tk.Label(self, textvariable=label_text, bg="white", bd=1, relief=tk.SOLID, padx=10, font=("Arial", 15))
        label.pack(side=tk.TOP, anchor=tk.NE, padx=(10, 50), pady=(10, 20), ipadx=10, ipady=10)

        # Center the label inside its container
        label.pack_configure(anchor='center')

        # Add a binding to open a menu on label click
        label.bind("<Button-1>", lambda event: self.show_menu(event, label, label_text))

        # Create a date picker using ttkcalendar
        date_picker = ttk.Combobox(self, values=["All"] + self.get_unique_dates(), font=("Arial", 12), width=15)
        date_picker.set("All")  # Default value
        date_picker.pack(side=tk.TOP, anchor=tk.NW, padx=(10, 0), pady=(0, 20))  # Updated configuration
        date_picker.bind("<<ComboboxSelected>>", self.update_date)

    def show_menu(self, event, label, label_text):
        # Create a menu
        graph_type_options = ["Pie Chart", "Bar Graph"]
        menu = tk.Menu(self, tearoff=0)

        for option in graph_type_options:
            menu.add_command(label=option, command=lambda value=option: self.update_label(value, label_text))

        # Display the menu at the click location
        menu.post(event.x_root, event.y_root)

    def update_label(self, value, label_text):
        label_text.set(value + " ▼")
        self.selected_graph_type.set(value)
        self.display_graphs()

    def update_date(self, event):
        self.selected_date.set(event.widget.get())
        self.display_graphs()

    def get_unique_dates(self):
        try:
            with open(self.json_file) as jsonfile:
                data = json.load(jsonfile)
                dates = set(entry.get("Date", "") for entry in data)
                return sorted(list(dates))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def display_graphs(self, *args):
        try:
            with open(self.json_file) as jsonfile:
                data = json.load(jsonfile)

                # Filter data based on the selected date
                if self.selected_date.get() != "All":
                    data = [entry for entry in data if entry.get("Date") == self.selected_date.get()]

                # Check if the data is a list of entries
                if not isinstance(data, list):
                    # Clear previous widgets
                    self.clear_graphs_tab()

                    tk.Label(self, text="No data available for graphs", relief='ridge', width=20).pack(side=tk.LEFT)
                    return

                # Extract age and gender data from the JSON file entries
                age_data = [entry.get("Age", "") for entry in data]
                gender_data = [entry.get("Gender", "") for entry in data]

                # Display the graph based on the selected graph type
                if self.selected_graph_type.get() == "Pie Chart":
                    self.display_pie_chart(age_data, gender_data)
                elif self.selected_graph_type.get() == "Bar Graph":
                    self.display_bar_graph(age_data, gender_data)

        except (json.JSONDecodeError, FileNotFoundError):
            # Clear previous widgets
            self.clear_graphs_tab()
            print("")

    def display_pie_chart(self, age_data, gender_data):
        # Create the figure for both pie charts
        if not hasattr(self, 'figure'):
            self.figure, (self.age_ax, self.gender_ax) = plt.subplots(1, 2, figsize=(12, 6))
            self.canvas = FigureCanvasTkAgg(self.figure, master=self)
            self.canvas_widget = self.canvas.get_tk_widget()
            self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Count the occurrences of each age range and gender
        age_counts = {age_range: age_data.count(age_range) for age_range in self.ageList}
        gender_counts = {gender: gender_data.count(gender) for gender in self.genderList}

        # Create a color map for age ranges
        age_colors = {
            '11-15': '#adfc03',
            '16-20': '#62fc03',
            '21-25': '#03fc90',
            '26-30': '#03fcf4',
            '31-35': '#0398fc',
            '36-40': '#a103fc',
            '41-45': '#db03fc',
            '46-50': '#6b047a',
            '51-55': '#472d01'
        }

        # Update the age range pie chart data
        self.age_ax.clear()
        self.age_ax.pie(age_counts.values(), labels=age_counts.keys(), autopct='%1.1f%%', startangle=90, colors=[age_colors.get(age, 'gray') for age in age_counts.keys()])
        self.age_ax.axis('equal')  # Equal aspect ratio ensures that the pie is drawn as a circle.
        self.age_ax.set_title("Age Range Percentage")

        # Update the gender pie chart data
        self.gender_ax.clear()
        self.gender_ax.pie(gender_counts.values(), labels=self.genderList, autopct='%1.1f%%', startangle=90, colors=['#038cfc', '#f803fc'])
        self.gender_ax.axis('equal')  # Equal aspect ratio ensures that the pie is drawn as a circle.
        self.gender_ax.set_title("Gender Percentage")

        # Update the display
        self.canvas.draw()

        # Remove the label if it exists
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text") == "No data available for graphs":
                widget.destroy()

    def display_bar_graph(self, age_data, gender_data):
        # Create the figure for both bar charts
        if not hasattr(self, 'figure'):
            self.figure, (self.age_ax, self.gender_ax) = plt.subplots(1, 2, figsize=(12, 6))
            self.canvas = FigureCanvasTkAgg(self.figure, master=self)
            self.canvas_widget = self.canvas.get_tk_widget()
            self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Count the occurrences of each age range and gender
        age_counts = {age_range: age_data.count(age_range) for age_range in self.ageList}
        gender_counts = {gender: gender_data.count(gender) for gender in self.genderList}

        # Create a color map for age ranges
        age_colors = {
            '11-15': '#adfc03',
            '16-20': '#62fc03',
            '21-25': '#03fc90',
            '26-30': '#03fcf4',
            '31-35': '#0398fc',
            '36-40': '#a103fc',
            '41-45': '#db03fc',
            '46-50': '#6b047a',
            '51-55': '#472d01'
        }

        # Update the age range bar chart data
        self.age_ax.clear()
        age_quantities = [age_counts.get(age, 0) for age in self.ageList]  # Use counts directly as quantities
        age_bars = self.age_ax.bar(
            self.ageList, age_quantities, color=[age_colors.get(age, 'gray') for age in self.ageList]
        )
        self.age_ax.set_title("Age Range Quantity")
        self.age_ax.set_ylabel("Quantity")
        self.age_ax.set_xlabel("Age Range")

        # Dynamically set y-axis lower limit based on the maximum value
        max_age_quantity = max(age_quantities)
        threshold = 5  # Threshold value for small data
        if max_age_quantity <= threshold:
            self.age_ax.set_ylim(bottom=0, top=max(threshold, max_age_quantity) + 1)  # Set lower limit to threshold or max_age_quantity, whichever is greater
        else:
            self.age_ax.set_ylim(bottom=0, top=max_age_quantity + 1)  # Add a small margin

        # Rotate x-axis labels to avoid overlapping
        self.age_ax.tick_params(axis='x', rotation=45)

        # Add data labels on top of each bar with absolute values
        for bar, count in zip(age_bars, age_quantities):
            self.age_ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(count), ha='center', va='bottom')

        # Update the gender bar chart data
        self.gender_ax.clear()
        gender_quantities = [gender_counts.get(gender, 0) for gender in self.genderList]  # Use counts directly as quantities
        colors = ['#038cfc', '#f803fc']  # Set colors for male and female
        self.gender_ax.bar(self.genderList, gender_quantities, color=colors)
        self.gender_ax.set_title("Gender Quantity")
        self.gender_ax.set_ylabel("Quantity")
        self.gender_ax.set_xlabel("Gender")

        # Dynamically set y-axis lower limit based on the maximum value
        max_gender_quantity = max(gender_quantities)
        self.gender_ax.set_ylim(bottom=0, top=max_gender_quantity + 1)  # Add a small margin

        # Add data labels on top of each bar with absolute values
        for bar, count in zip(self.gender_ax.patches, gender_quantities):
            self.gender_ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(count), ha='center', va='bottom')

        # Update the display
        self.canvas.draw()

        # Remove the label if it exists
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text") == "No data available for graphs":
                widget.destroy()





    def clear_graphs_tab(self):
        # Clear the graphs in the tab
        if hasattr(self, 'figure'):
            plt.close(self.figure)
            delattr(self, 'figure')

        # Clear any other widgets in the tab
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphsTab(root)
    app.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    root.mainloop()
