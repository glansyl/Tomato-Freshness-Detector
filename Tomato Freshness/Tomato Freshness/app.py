from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import base64
import io
from PIL import Image

app = Flask(__name__)

# ----------------------------
# Load model
# ----------------------------
model = load_model("tomato_freshness_model.h5")
class_names = ['Damaged', 'Old', 'Ripe', 'Unripe']
IMG_SIZE = (224, 224)

# Global camera instance
camera = None

def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
    return camera

def process_frame(frame):
    """Process frame and detect tomatoes"""
    # Convert to HSV for color segmentation
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Red/green tomato mask (adjust ranges if needed)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    red_mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)

    lower_green = np.array([35, 50, 50])
    upper_green = np.array([90, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    mask = red_mask + green_mask

    # Morphological operations to clean noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Skip small noise
        if w < 30 or h < 30:
            continue

        # Crop tomato region
        tomato_crop = frame[y:y+h, x:x+w]
        tomato_img = cv2.resize(tomato_crop, IMG_SIZE)
        tomato_img = tomato_img.astype("float32") / 255.0
        tomato_img = np.expand_dims(tomato_img, axis=0)

        # Predict
        preds = model.predict(tomato_img, verbose=0)
        label = class_names[np.argmax(preds)]
        confidence = np.max(preds)

        # Store detection info
        detections.append({
            'label': label,
            'confidence': float(confidence),
            'bbox': [int(x), int(y), int(w), int(h)]
        })

        # Draw bounding box + label with color coding
        color_map = {
            'Ripe': (0, 255, 0),      # Green
            'Unripe': (0, 165, 255),  # Orange
            'Old': (0, 140, 255),     # Dark orange
            'Damaged': (0, 0, 255)    # Red
        }
        color = color_map.get(label, (0, 255, 0))
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
        
        # Add label background
        label_text = f"{label} ({confidence*100:.1f}%)"
        (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(frame, (x, y-text_height-10), (x+text_width, y), color, -1)
        cv2.putText(frame, label_text, (x, y-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return frame, detections

def generate_frames():
    """Generate frames for video streaming"""
    while True:
        cap = get_camera()
        ret, frame = cap.read()
        
        if not ret or frame is None:
            continue

        processed_frame, _ = process_frame(frame)

        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    """Analyze uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        image_bytes = file.read()
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'error': 'Invalid image'}), 400

        # Process the image
        processed_frame, detections = process_frame(frame)

        # Encode processed image to base64
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'success': True,
            'detections': detections,
            'processed_image': img_base64
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/camera_status')
def camera_status():
    """Check if camera is available"""
    cap = get_camera()
    return jsonify({'available': cap.isOpened()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
