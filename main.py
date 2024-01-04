import cv2
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class FaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Human Age and Gender Classification")
        self.video_source = 0  # Set the video source (you may need to change this)
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(root, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

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
        self.ageList = ['(11-15)', '(16-20)', '(21-25)', '(26-30)', '(31-35)', '(36-40)', '(41-45)', '(46-50)', '(51-55)']
        self.genderList = ['Male', 'Female']

        self.padding = 20
        self.line_margin = 5

        self.capture_interval = 5  # seconds
        self.start_time = datetime.now()

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
                now = datetime.now().strftime("%Y%m%d%H%M%S")
                image_name = f"captured_{i}_{now}.png"
                image_path = os.path.join("images_captured", image_name)
                cv2.imwrite(image_path, frame)

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
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Set box color to red (BGR: 0, 0, 255)
        return frame, bboxs

    def update(self):
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

            # Display the frame using Tkinter
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

            # Check if it's time to capture
            current_time = datetime.now()
            if (current_time - self.start_time).seconds >= self.capture_interval:
                self.capture()
                self.start_time = current_time

        self.root.after(10, self.update)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create the output folder if it doesn't exist
os.makedirs("images_captured", exist_ok=True)

root = tk.Tk()
app = FaceApp(root)
