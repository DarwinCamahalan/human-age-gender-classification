import cv2
import os
from datetime import datetime, timedelta

def faceBox(faceNet, frame):
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (227, 227), [104, 117, 123], swapRB=False)
    faceNet.setInput(blob)
    detection = faceNet.forward()
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

def capture_frame(frame, bboxs, output_path):
    for i, bbox in enumerate(bboxs):
        face = frame[max(0, bbox[1] - padding):min(bbox[3] + padding, frame.shape[0] - 1),
               max(0, bbox[0] - padding):min(bbox[2] + padding, frame.shape[1] - 1)]

        # Save captured image with face detection
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        image_name = f"captured_{i}_{now}.png"
        image_path = os.path.join(output_path, image_name)
        cv2.imwrite(image_path, frame)

        # Print information
        print(f"Image saved: {image_path}")

# Create the output folder if it doesn't exist
output_folder = "images_captured"
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
ageList = ['(11-15)', '(16-20)', '(21-25)', '(26-30)', '(31-35)', '(36-40)', '(41-45)', '(46-50)', '(51-55)']
genderList = ['Male', 'Female']

video = cv2.VideoCapture(0)
padding = 20
line_margin = 5

capture_interval = 5  # seconds
start_time = datetime.now()

while True:
    ret, frame = video.read()
    frame = cv2.flip(frame, 1)  # Horizontal flip
    frame, bboxs = faceBox(faceNet, frame)

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

    cv2.imshow("Age Gender Classification", frame)
    k = cv2.waitKey(1)
    if k == ord('q'):
        break

    # Check for capture interval
    elapsed_time = datetime.now() - start_time
    if elapsed_time.total_seconds() >= capture_interval:
        capture_frame(frame.copy(), bboxs, output_folder)
        start_time = datetime.now()

video.release()
cv2.destroyAllWindows()
