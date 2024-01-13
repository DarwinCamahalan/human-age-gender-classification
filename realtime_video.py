import tkinter as tk
from PIL import Image, ImageTk
import cv2
import os
import json
from datetime import datetime, timedelta

class RealtimeVideoTab(tk.Frame):
    # Initialize last_capture_time and capture_interval at the class level
    last_capture_time = datetime.now()
    capture_interval = 10

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        tk.Label(self, text="Realtime Video Tab Content", font=("Arial", 14)).pack(pady=20)

        # Create a canvas for displaying video
        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack()

        # Initialize video streaming
        self.start_video_stream()

    def face_box(self, face_net, frame):
        frameWidth = frame.shape[1]
        frameHeight = frame.shape[0]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (227, 227), [104, 117, 123], swapRB=False)
        face_net.setInput(blob)
        detection = face_net.forward()
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

    def start_video_stream(self):
        # Create the output folder if it doesn't exist
        output_folder = "captured_images"
        os.makedirs(output_folder, exist_ok=True)

        faceProto = "opencv_face_detector.pbtxt"
        faceModel = "opencv_face_detector_uint8.pb"

        ageProto = "age_deploy.prototxt"
        ageModel = "age_net.caffemodel"

        genderProto = "gender_deploy.prototxt"
        genderModel = "gender_net.caffemodel"

        faceNet = cv2.dnn.readNet(faceModel, faceProto)
        ageNet = cv2.dnn.readNet(ageModel, ageProto)
        genderNet = cv2.dnn.readNet(genderModel, genderProto)

        MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        ageList = ['11-15', '16-20', '21-25', '26-30', '31-35', '36-40', '41-45', '46-50', '51-55']
        genderList = ['Male', 'Female']

        video = cv2.VideoCapture(0)
        padding = 20
        line_margin = 5

        def update_frame(genderNet, ageNet):
            nonlocal video, faceNet

            ret, frame = video.read()
            frame = cv2.flip(frame, 1)  # Horizontal flip

            # Detect faces
            frame, bboxs = self.face_box(faceNet, frame)

            # Check if faces are detected
            if bboxs:
                # Display the live video with labels
                for bbox in bboxs:
                    face = frame[max(0, bbox[1] - padding):min(bbox[3] + padding, frame.shape[0] - 1),
                           max(0, bbox[0] - padding):min(bbox[2] + padding, frame.shape[1] - 1)]

                    blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
                    genderNet.setInput(blob)
                    genderPred = genderNet.forward()
                    gender = genderList[genderPred[0].argmax()]

                    ageNet.setInput(blob)
                    agePred = ageNet.forward()
                    age = ageList[agePred[0].argmax()]

                    label_gender = "Gender: {}".format(gender)
                    label_age = "Age: {}".format(age)

                    text_size_gender = cv2.getTextSize(label_gender, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]
                    text_size_age = cv2.getTextSize(label_age, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]

                    cv2.putText(frame, label_gender, (bbox[0], bbox[3] + text_size_gender[1] + line_margin),
                                cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.putText(frame, label_age, (bbox[0], bbox[3] + text_size_gender[1] + text_size_age[1] + 2 * line_margin),
                                cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

                # Convert the frame to RGB format for display in tkinter
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                img = ImageTk.PhotoImage(image=img)

                # Update the canvas with the new frame
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
                self.canvas.image = img  # Keep a reference to prevent garbage collection

                current_time = datetime.now()
                time_difference = current_time - RealtimeVideoTab.last_capture_time
                if time_difference.total_seconds() >= RealtimeVideoTab.capture_interval:
                    # Save the image with a timestamp in the filename
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    age_gender_timestamp = f"{age}_{gender}_{timestamp}"
                    image_number = len(os.listdir(output_folder)) + 1
                    image_filename = f"{age_gender_timestamp}_{image_number}.png"
                    image_path = os.path.join(output_folder, image_filename)

                    # Apply blur to the face region only for captured images
                    for bbox in bboxs:
                        face = frame[max(0, bbox[1] - padding):min(bbox[3] + padding, frame.shape[0] - 1),
                                max(0, bbox[0] - padding):min(bbox[2] + padding, frame.shape[1] - 1)]

                        # Apply Gaussian blur to the face region
                        blurred_face = cv2.GaussianBlur(face, (99, 99), 30)

                        # Replace the face region with the blurred face
                        frame[max(0, bbox[1] - padding):min(bbox[3] + padding, frame.shape[0] - 1),
                            max(0, bbox[0] - padding):min(bbox[2] + padding, frame.shape[1] - 1)] = blurred_face

                    # Save the image without converting to RGB
                    cv2.imwrite(image_path, frame)
                    print(f"Image captured and saved: {image_path}")

                    # Log the data to log.json
                    log_data = {
                        "Date": current_time.strftime('%Y-%m-%d'),
                        "Time": current_time.strftime('%H:%M:%S'),
                        "Gender": gender,
                        "Age": age,
                        "Image Captured Filename": image_filename
                    }

                    log_json_path = "log.json"
                    try:
                        with open(log_json_path, 'r') as log_file:
                            log_json = json.load(log_file)
                    except json.decoder.JSONDecodeError:
                        # Handle the case where the file is empty or improperly formatted
                        log_json = []

                    log_json.append(log_data)

                    with open(log_json_path, 'w') as log_file:
                        json.dump(log_json, log_file, indent=4)

                    RealtimeVideoTab.last_capture_time = current_time
            else:
                # No faces detected, update the canvas without processing and displaying faces
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img = ImageTk.PhotoImage(image=img)

                # Update the canvas with the new frame
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
                self.canvas.image = img  # Keep a reference to prevent garbage collection

            # Call the update_frame function after 10 milliseconds
            self.after(10, lambda: update_frame(genderNet, ageNet))

        # Start the update_frame function
        update_frame(genderNet, ageNet)

if __name__ == "__main__":
    root = tk.Tk()
    app = RealtimeVideoTab(root, bg="white")
    app.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    root.mainloop()
