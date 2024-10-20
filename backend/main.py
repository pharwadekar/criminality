from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import base64
import numpy as np
import cv2
import dlib
from deepface import DeepFace
import eventlet
from collections import deque

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Dlib's face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Load Haar cascades for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Blink detection parameters
blink_count = 0
eyes_closed = False  # State to track if eyes were closed in the previous frame
blink_frame_count = 0  # Frame count for the duration of a blink
HIGH_SPEED_BLINK_FRAME_THRESHOLD = 3  # Threshold for high-speed blink in frames

# Face orientation tracking with smoothing
face_orientation = "Unknown"
orientation_buffer = deque(maxlen=10)  # Buffer to smooth face orientation changes

# Gaze direction tracking
gaze_direction = "Center"
gaze_buffer = deque(maxlen=10)  # Buffer to smooth gaze direction changes

# Threshold to determine face orientation stability
ORIENTATION_STABILITY_THRESHOLD = 7  # Number of consecutive frames required for stable orientation

def calculate_eye_aspect_ratio(eye):
    A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))  # vertical
    B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))  # vertical
    C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))  # horizontal
    ear = (A + B) / (2.0 * C)  # Eye Aspect Ratio
    return ear

def detect_blinking_eye_tracking_and_micro_expressions(frame):
    global blink_count, eyes_closed, blink_frame_count, face_orientation, gaze_direction

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    micro_expressions = []
    high_speed_blink = False
    current_orientation = "Unknown"
    current_gaze = "Center"

    for face in faces:
        landmarks = predictor(gray, face)
        left_eye = [(landmarks.part(36).x, landmarks.part(36).y),
                    (landmarks.part(37).x, landmarks.part(37).y),
                    (landmarks.part(38).x, landmarks.part(38).y),
                    (landmarks.part(39).x, landmarks.part(39).y),
                    (landmarks.part(40).x, landmarks.part(40).y),
                    (landmarks.part(41).x, landmarks.part(41).y)]
        
        right_eye = [(landmarks.part(42).x, landmarks.part(42).y),
                     (landmarks.part(43).x, landmarks.part(43).y),
                     (landmarks.part(44).x, landmarks.part(44).y),
                     (landmarks.part(45).x, landmarks.part(45).y),
                     (landmarks.part(46).x, landmarks.part(46).y),
                     (landmarks.part(47).x, landmarks.part(47).y)]
        
        ear_left = calculate_eye_aspect_ratio(left_eye)
        ear_right = calculate_eye_aspect_ratio(right_eye)

        # Blink detection logic based on eye aspect ratio
        eyes_detected = ear_left >= 0.2 and ear_right >= 0.2

        if not eyes_detected and not eyes_closed:  # Eyes have just closed
            blink_frame_count = 0
            eyes_closed = True  # Update state to indicate eyes are closed
        elif not eyes_detected and eyes_closed:  # Eyes are still closed
            blink_frame_count += 1
        elif eyes_detected and eyes_closed:  # Eyes have just opened
            if blink_frame_count < HIGH_SPEED_BLINK_FRAME_THRESHOLD:
                high_speed_blink = True
                blink_count += 1
            eyes_closed = False  # Reset state to indicate eyes are open

        # Detect micro-expressions
        left_brow = (landmarks.part(22).x, landmarks.part(22).y)
        right_brow = (landmarks.part(24).x, landmarks.part(24).y)
        mouth_left = (landmarks.part(48).x, landmarks.part(48).y)
        mouth_right = (landmarks.part(54).x, landmarks.part(54).y)

        eyebrow_distance = np.linalg.norm(np.array(left_brow) - np.array(right_brow))
        mouth_distance = np.linalg.norm(np.array(mouth_left) - np.array(mouth_right))

        if eyebrow_distance > 15:
            micro_expressions.append("Eyebrow twitch detected!")
        
        if mouth_distance > 25:
            micro_expressions.append("Mouth twitch detected!")

        # Eye position detection
        face_rect = (face.left(), face.top(), face.width(), face.height())
        roi_gray = gray[face_rect[1]:face_rect[1] + int(0.6 * face_rect[3]), face_rect[0]:face_rect[0] + face_rect[2]]
        roi_color = frame[face_rect[1]:face_rect[1] + int(0.6 * face_rect[3]), face_rect[0]:face_rect[0] + face_rect[2]]

        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=3)
        eye_positions = [ex for (ex, ey, ew, eh) in eyes]

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            eye_roi = roi_gray[ey:ey + eh, ex:ex + ew]
            _, threshold_eye = cv2.threshold(eye_roi, 50, 255, cv2.THRESH_BINARY_INV)

            contours, _ = cv2.findContours(threshold_eye, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                max_contour = max(contours, key=cv2.contourArea)
                (cx, cy), _ = cv2.minEnclosingCircle(max_contour)
                pupil_position = int(cx)

                cv2.circle(roi_color, (ex + int(cx), ey + int(cy)), 2, (0, 0, 255), -1)

                if pupil_position < ew * 0.3:
                    current_gaze = "Right"
                elif pupil_position > ew * 0.7:
                    current_gaze = "Left"
                else:
                    current_gaze = "Center"

        if len(eye_positions) == 2:
            eye_diff = abs(eye_positions[0] - eye_positions[1])
            if eye_diff < face_rect[2] * 0.4:
                current_orientation = "Front"
            elif eye_positions[0] < eye_positions[1]:
                current_orientation = "Left"
            else:
                current_orientation = "Right"
        elif len(eye_positions) == 1:
            current_orientation = "Left" if eye_positions[0] > face_rect[2] / 2 else "Right"

        orientation_buffer.append(current_orientation)

        if orientation_buffer.count("Front") >= ORIENTATION_STABILITY_THRESHOLD:
            face_orientation = "Front"
        elif orientation_buffer.count("Left") >= ORIENTATION_STABILITY_THRESHOLD:
            face_orientation = "Left"
        elif orientation_buffer.count("Right") >= ORIENTATION_STABILITY_THRESHOLD:
            face_orientation = "Right"

        gaze_buffer.append(current_gaze)

        gaze_direction = max(set(gaze_buffer), key=gaze_buffer.count)

    return frame, high_speed_blink, micro_expressions, face_orientation, gaze_direction

@socketio.on('video_frame')
def handle_video_frame(data):
    try:
        image_data = data['image']
        print('Received image data:', image_data[:100])  # Log the first 100 characters of the received image data

        encoded = image_data.split(",", 1)[1]
        img_data = base64.b64decode(encoded)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image")

        emotion_analysis = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        
        img, high_speed_blink, micro_expressions, face_orientation, gaze_direction = detect_blinking_eye_tracking_and_micro_expressions(img)

        # Encode the processed image back to base64
        _, buffer = cv2.imencode('.jpg', img)
        processed_image = base64.b64encode(buffer).decode('utf-8')

        response = {
            'emotion': emotion_analysis[0]['dominant_emotion'],
            'high_speed_blink': high_speed_blink,
            'micro_expressions': micro_expressions,
            'face_orientation': face_orientation,
            'gaze_direction': gaze_direction,
        }
        emit('analysis_result', response)
    except Exception as e:
        print('Error:', e)
        emit('analysis_error', {'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5173, debug=True)