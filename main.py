import cv2
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FaceApp:
    def __init__(self, root):
        self.sort_column = None
        self.sort_direction = None

        self.root = root
        self.root.title("Human Age and Gender Classification")

        # Initialize tabs
        self.tabControl = ttk.Notebook(root)
        self.logs_tab = ttk.Frame(self.tabControl)
        self.graphs_tab = ttk.Frame(self.tabControl)
        self.images_captured_tab = ttk.Frame(self.tabControl)
        self.realtime_video_tab = ttk.Frame(self.tabControl)

        self.tabControl.add(self.logs_tab, text="Logs")
        self.tabControl.add(self.graphs_tab, text="Graphs")
        self.tabControl.add(self.images_captured_tab, text="Images Captured")
        self.tabControl.add(self.realtime_video_tab, text="Realtime Video")

        self.tabControl.pack(expand=1, fill="both")

        # Set the video source (you may need to change this)
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)

        # Realtime Video tab UI
        self.canvas_realtime_video = tk.Canvas(self.realtime_video_tab, width=720, height=720)
        self.canvas_realtime_video.pack()

        self.faceProto = "opencv_face_detector.pbtxt"
        self.faceModel = "opencv_face_detector_uint8.pb"
        self.ageProto = "age_deploy.prototxt"
        self.ageModel = "age_net.caffemodel"
        self.genderProto = "gender_deploy.prototxt"
        self.genderModel = "gender_net.caffemodel"

        self.faceNet = cv2.dnn.readNet(self.faceModel, self.faceProto)
        self.ageNet = cv2.dnn.readNet(self.ageModel, self.ageProto)
        self.genderNet = cv2.dnn.readNet(self.genderModel, self.genderProto)

        self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        self.ageList = ['11-15', '16-20', '21-25', '26-30', '31-35', '36-40', '41-45', '46-50', '51-55']
        self.genderList = ['Male', 'Female']

        self.padding = 20
        self.line_margin = 5

        self.capture_interval = 10  # seconds
        self.start_time = datetime.now()

        # Create the output folder if it doesn't exist
        os.makedirs("images_captured", exist_ok=True)

        # Open the JSON file for writing in append mode
        self.json_file = "log.json"

        # Create a TreeView for the Logs tab
        self.log_tree = ttk.Treeview(self.logs_tab, columns=("Date", "Time", "Gender", "Age"), show="headings")
        self.log_tree.heading("Date", text="Date")
        self.log_tree.heading("Time", text="Time")
        self.log_tree.heading("Gender", text="Gender")
        self.log_tree.heading("Age", text="Age")
        self.log_tree.pack(fill="both", expand=True)

        # Display existing data from the JSON file
        self.display_logs_realtime()

        # Start the main update loop
        self.update()
        self.root.mainloop()

    def capture(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.flip(frame, 1)  # Horizontal flip
            frame, bboxs = self.faceBox(frame)
            for i, bbox in enumerate(bboxs):
                face = frame[max(0, bbox[1] - self.padding):min(bbox[3] + self.padding, frame.shape[0] - 1),
                       max(0, bbox[0] - self.padding):min(bbox[2] + self.padding, frame.shape[1] - 1)]

                blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
                self.genderNet.setInput(blob)
                genderPred = self.genderNet.forward()
                gender = self.genderList[genderPred[0].argmax()]

                self.ageNet.setInput(blob)
                agePred = self.ageNet.forward()
                age = self.ageList[agePred[0].argmax()]

                label_gender = "Gender: {}".format(gender)
                label_age = "Age: {}".format(age)

                text_size_gender = cv2.getTextSize(label_gender, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]
                text_size_age = cv2.getTextSize(label_age, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]

                cv2.putText(frame, label_gender, (bbox[0], bbox[3] + text_size_gender[1] + self.line_margin),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, label_age, (bbox[0], bbox[3] + text_size_gender[1] + text_size_age[1] + 2 * self.line_margin),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

                # Save captured image with face detection and labels
                now = datetime.now()
                date_str = now.strftime("%m/%d/%Y")
                time_str = now.strftime("%I:%M %p")
                image_name = f"captured_{i}_{now.strftime('%Y%m%d%H%M%S')}.png"
                image_path = os.path.join("images_captured", image_name)
                cv2.imwrite(image_path, frame)

                # Log to JSON file
                with open(self.json_file, 'a') as jsonfile:
                    json.dump({
                        "Date": date_str,
                        "Time": time_str,
                        "Gender": gender,
                        "Age": age,
                        "Image Filename": image_name
                    }, jsonfile)
                    jsonfile.write('\n')

                # Print age and gender information
                print(f"Gender: {gender}, Age: {age} - Image saved: {image_path}")

    def faceBox(self, frame):
        frameWidth = frame.shape[1]
        frameHeight = frame.shape[0]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (227, 227), [104, 117, 123], swapRB=False)
        self.faceNet.setInput(blob)
        detection = self.faceNet.forward()
        bboxs = []
        for i in range(detection.shape[2]):
            confidence = detection[0, 0, i, 2]
            if confidence > 0.7:
                x1 = int(detection[0, 0, i, 3] * frameWidth)
                y1 = int(detection[0, 0, i, 4] * frameHeight)
                x2 = int(detection[0, 0, i, 5] * frameWidth)
                y2 = int(detection[0, 0, i, 6] * frameHeight)
                bboxs.append([x1, y1, x2, y2])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)  # Set box color to red (BGR: 0, 0, 255)
        return frame, bboxs

    def display_graphs(self):
        try:
            with open(self.json_file) as jsonfile:
                data = jsonfile.readlines()

                # Check if data is empty
                if not data:
                    # Clear previous widgets
                    self.clear_graphs_tab()

                    tk.Label(self.graphs_tab, text="No data available for graphs", relief='ridge', width=20).pack(side=tk.LEFT)
                    return

                # Extract age and gender data from the JSON file
                age_data = [json.loads(line)["Age"] for line in data]
                gender_data = [json.loads(line)["Gender"] for line in data]

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
                    self.canvas = FigureCanvasTkAgg(self.figure, master=self.graphs_tab)
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
                for widget in self.graphs_tab.winfo_children():
                    if isinstance(widget, tk.Label) and widget.cget("text") == "No data available for graphs":
                        widget.destroy()

        except (json.JSONDecodeError, FileNotFoundError):
            # Clear previous widgets
            self.clear_graphs_tab()

            tk.Label(self.graphs_tab, text="Error reading or no data in JSON file", relief='ridge', width=20).pack(side=tk.LEFT)

    
    def clear_graphs_tab(self):
        # Clear all widgets in the graphs_tab
        for widget in self.graphs_tab.winfo_children():
            widget.destroy()

        # Close any existing figures
        plt.close('all')
        
    def update(self):
        # Update the pie chart periodically
        self.display_graphs()
        
        # Check if it's time to capture
        current_time = datetime.now()
        if (current_time - self.start_time).seconds >= self.capture_interval:
            self.capture()
            self.start_time = current_time

            # Update TreeView with newly captured data
            self.display_logs_realtime()

        # Display the frame using Tkinter
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.flip(frame, 1)  # Horizontal flip
            frame, bboxs = self.faceBox(frame)

            # Display the live video with labels
            for bbox in bboxs:
                face = frame[max(0, bbox[1] - self.padding):min(bbox[3] + self.padding, frame.shape[0] - 1),
                       max(0, bbox[0] - self.padding):min(bbox[2] + self.padding, frame.shape[1] - 1)]

                blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
                self.genderNet.setInput(blob)
                genderPred = self.genderNet.forward()
                gender = self.genderList[genderPred[0].argmax()]

                self.ageNet.setInput(blob)
                agePred = self.ageNet.forward()
                age = self.ageList[agePred[0].argmax()]

                label_gender = "Gender: {}".format(gender)
                label_age = "Age: {}".format(age)

                text_size_gender = cv2.getTextSize(label_gender, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]
                text_size_age = cv2.getTextSize(label_age, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]

                cv2.putText(frame, label_gender, (bbox[0], bbox[3] + text_size_gender[1] + self.line_margin),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, label_age, (bbox[0], bbox[3] + text_size_gender[1] + text_size_age[1] + 2 * self.line_margin),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

            self.photo_realtime_video = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas_realtime_video.create_image(0, 0, image=self.photo_realtime_video, anchor=tk.NW)

        self.root.after(10, self.update)

    def display_logs_realtime(self):
        # Clear existing data from the TreeView
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        try:
            with open(self.json_file) as jsonfile:
                # Read all lines into a list and reverse it
                lines = jsonfile.readlines()[::-1]

                # Display data
                for line in lines:
                    data = json.loads(line)
                    self.log_tree.insert("", "end", values=(
                        data["Date"], data["Time"], data["Gender"], data["Age"]
                    ))
        except json.JSONDecodeError:
            tk.Label(self.logs_tab, text="No data available", relief='ridge', width=20).pack(side=tk.LEFT)

        # Add sorting functionality to the headers
        for col in ["Date", "Time", "Gender", "Age"]:
            self.log_tree.heading(col, text=col, command=lambda c=col: self.sort_logs(c))

        # Center-align text in the TreeView
        for col in ["Date", "Time", "Gender", "Age"]:
            self.log_tree.column(col, anchor=tk.CENTER)

    def sort_logs(self, column):
        if column in ["Date", "Time", "Gender", "Age"]:
            current_data = [(self.log_tree.set(item, "Date"), self.log_tree.set(item, "Time"),
                            self.log_tree.set(item, "Gender"), self.log_tree.set(item, "Age"), item)
                            for item in self.log_tree.get_children('')]

            # Determine the sort direction
            if self.sort_column == column:
                self.sort_direction = "asc" if self.sort_direction == "desc" else "desc"
            else:
                self.sort_direction = "asc"

            # Sort the data
            current_data.sort(key=lambda x: x[["Date", "Time", "Gender", "Age"].index(column)],
                            reverse=(self.sort_direction == "desc"))

            # Rearrange items in the TreeView based on the sorted data
            for index, (date, time, gender, age, item) in enumerate(current_data):
                self.log_tree.move(item, '', index)

            # Update the sort column
            self.sort_column = column
        else:
            print(f"Ignore sorting for the column: {column}")


    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

root = tk.Tk()
app = FaceApp(root)
