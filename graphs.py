import tkinter as tk
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import PercentFormatter

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

        # Display graphs automatically
        self.create_widgets()
        self.display_graphs()

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

    def display_graphs(self, *args):
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

                if self.selected_graph_type.get() == "Pie Chart":
                    # Display Pie Chart
                    self.display_pie_chart(age_data, gender_data)

                elif self.selected_graph_type.get() == "Bar Graph":
                    # Display Bar Graph
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
        self.age_ax.pie(age_counts.values(), labels=age_counts.keys(), autopct='%1.1f%%', startangle=90, colors=[age_colors[age] for age in age_counts.keys()])
        self.age_ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        self.age_ax.set_title("Age Range Percentage")

        # Update the gender pie chart data
        self.gender_ax.clear()
        self.gender_ax.pie(gender_counts.values(), labels=self.genderList, autopct='%1.1f%%', startangle=90, colors=['#038cfc', '#f803fc'])
        self.gender_ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
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
        age_percentages = [count / sum(age_counts.values()) * 100 for count in age_counts.values()]
        age_bars = self.age_ax.bar(
            self.ageList, age_percentages, color=[age_colors[age] for age in self.ageList]
        )
        self.age_ax.set_title("Age Range Percentage")
        self.age_ax.set_ylabel("Percentage")
        self.age_ax.set_xlabel("Age Range")
        self.age_ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))  # Format y-axis as percentage from 0% to 100%

        # Rotate x-axis labels to avoid overlapping
        self.age_ax.tick_params(axis='x', rotation=45)

        # Add a legend for age ranges
        self.age_ax.legend(age_bars, self.ageList, title="Age Range")

        # Update the gender bar chart data
        self.gender_ax.clear()
        gender_percentages = [count / sum(gender_counts.values()) * 100 for count in gender_counts.values()]
        colors = ['#038cfc', '#f803fc']  # Set colors for male and female
        self.gender_ax.bar(self.genderList, gender_percentages, color=colors)
        self.gender_ax.set_title("Gender Percentage")
        self.gender_ax.set_ylabel("Percentage")
        self.gender_ax.set_xlabel("Gender")
        self.gender_ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))  # Format y-axis as percentage from 0% to 100%

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
