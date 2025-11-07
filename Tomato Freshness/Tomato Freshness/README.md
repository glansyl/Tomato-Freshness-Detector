Tomato Freshness Detector

An AI-powered web app that detects and classifies tomato freshness in real-time.
It identifies four tomato states: Ripe, Unripe, Old, and Damaged.

Features
--------

Live Webcam Detection
- Real-time tomato detection and classification
- Color-coded boxes with confidence scores
- Automatic segmentation using HSV color space
- Live freshness status display

Image Upload
- Upload one or more images for analysis
- Shows detection results with position and confidence
- Download images with annotations

Modern Interface
- Responsive dark theme
- Smooth animations
- Mobile-friendly
- Color codes:
  Green   : Ripe
  Orange  : Unripe
  Dark Orange : Old
  Red     : Damaged

AI Detection
- Deep learning model trained on tomato images
- High accuracy
- Works under different lighting conditions

Quick Start
-----------

Requirements:
- Python 3.8+
- Webcam (optional)
- pip package manager

Installation:

1. Clone the repository
   git clone https://github.com/your-repo/tomatoFreshness.git
   cd tomatoFreshness

2. Install dependencies
   pip install -r requirements.txt

3. Run the app
   python app.py

4. Open in browser
   http://localhost:5000

Usage
-----

Live Webcam Detection
1. Go to Live Webcam tab
2. Allow camera access
3. Point camera at tomatoes
4. See real-time detection

Upload Image
1. Go to Upload Image tab
2. Drag and drop an image or click to browse
3. Click Analyze Image
4. View results

API Endpoints
- GET /             -> Main interface
- GET /video_feed   -> Webcam feed
- POST /analyze_image -> Analyze uploaded image
- GET /camera_status  -> Check camera

Example:
import requests

with open('tomato.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/analyze_image', files=files)
    print(response.json())

Configuration
-------------

Model:
- CNN (Convolutional Neural Network)
- Input: 224x224 pixels
- Classes: Damaged, Old, Ripe, Unripe
- TensorFlow/Keras framework

Detection Parameters:
Adjust HSV ranges in app.py:
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])

lower_green = np.array([35, 50, 50])
upper_green = np.array([90, 255, 255])

Tech Stack
----------

- Backend : Flask
- AI/ML   : TensorFlow, Keras
- Computer Vision : OpenCV
- Frontend: HTML, CSS, JavaScript
- Image Processing: NumPy, Pillow

Model Performance
-----------------

Class      | Description       | Use Case
-----------|-----------------|----------------------
Ripe       | Perfect ripeness  | Ready to eat
Unripe     | Not yet ripe      | Needs storage
Old        | Past prime        | Discount or processing
Damaged    | Physical damage   | Reject or compost

Contributing
------------

1. Fork the repo
2. Create a branch (git checkout -b feature/YourFeature)
3. Commit changes (git commit -m 'Add feature')
4. Push branch (git push origin feature/YourFeature)
5. Open a pull request

Troubleshooting
---------------

- Camera not working: Check permissions and ensure no other app uses it
- Model loading error: Ensure tomato_freshness_model.h5 exists and TensorFlow is compatible
- Port in use: Change port in app.py:
  app.run(debug=True, host='0.0.0.0', port=5001)

License
-------

MIT License

Acknowledgments
---------------

- TensorFlow & Keras
- OpenCV
- Flask

Contact
-------

Developer: Glansyl Meldon Dsouza


