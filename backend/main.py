from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import cv2
import dlib
from deepface import DeepFace

app = Flask(__name__)
CORS(app)

# Initialize Dlib's face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def calculate_eye_aspect_ratio(eye):
    # Calculate the distances to determine EAR (Eye Aspect Ratio)
    A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))  # vertical
    B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))  # vertical
    C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))  # horizontal
    ear = (A + B) / (2.0 * C)  # Eye Aspect Ratio
    return ear

def detect_blinking(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        # Get eye landmarks
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
        
        # Calculate Eye Aspect Ratio (EAR)
        ear_left = calculate_eye_aspect_ratio(left_eye)
        ear_right = calculate_eye_aspect_ratio(right_eye)

        # A threshold to classify a blink
        if ear_left < 0.2 or ear_right < 0.2:
            print("Blink detected!")

def detect_micro_expressions(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        # Sample landmark points for eyebrows and mouth to track subtle movements
        left_brow = (landmarks.part(22).x, landmarks.part(22).y)
        right_brow = (landmarks.part(24).x, landmarks.part(24).y)
        mouth_left = (landmarks.part(48).x, landmarks.part(48).y)
        mouth_right = (landmarks.part(54).x, landmarks.part(54).y)

        # Calculate distances for twitch detection
        eyebrow_distance = np.linalg.norm(np.array(left_brow) - np.array(right_brow))
        mouth_distance = np.linalg.norm(np.array(mouth_left) - np.array(mouth_right))

        # Define thresholds for micro-expressions (to be tuned)
        if eyebrow_distance > 10:  # Example threshold
            print("Eyebrow twitch detected!")
        
        if mouth_distance > 20:  # Example threshold
            print("Mouth twitch detected!")

@app.route('/analyze', methods=['POST'])
def analyze_image():
    data = request.json
    image_data = data['image']

    print("Received image data")

    # Decode the base64 image
    try:
        header, encoded = image_data.split(",", 1)
        img_data = base64.b64decode(encoded)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Perform emotion analysis
        emotion_analysis = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        
        # Check for blinks and micro-expressions
        detect_blinking(img)
        detect_micro_expressions(img)

        response = {
            'success': True,
            'emotion': emotion_analysis[0]['dominant_emotion'],
            # Additional information on blinks and micro-expressions can be added here
        }
    except Exception as e:
        response = {
            'success': False,
            'error': str(e)
        }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
