"""Webcam vision utilities for TradeSensei AI.

Provides simple frame analysis (face detection + placeholder emotion estimate)
as a lightweight service for the frontend to call.
"""
from typing import Dict, Any, Optional
import cv2
import numpy as np
import base64
import os

# Load Haar cascade for face detection shipped with OpenCV
_face_cascade = None
try:
    _cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    if os.path.exists(_cascade_path):
        _face_cascade = cv2.CascadeClassifier(_cascade_path)
except Exception:
    _face_cascade = None


def _decode_image_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    try:
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def analyze_frame_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """Analyze a frame and return detection results.

    Returns a dictionary with keys:
      - faces: list of [x,y,w,h]
      - emotions: placeholder mapping (face_index -> emotion)
      - attention: estimated attention score (0-1)
    """
    img = _decode_image_bytes(image_bytes)
    if img is None:
        return {"error": "invalid_image"}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = []
    if _face_cascade is not None:
        detected = _face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in detected:
            faces.append([int(x), int(y), int(w), int(h)])

    # Placeholder emotion detection (always 'neutral' until a model is added)
    emotions = {str(i): "neutral" for i in range(len(faces))}

    # Simple attention heuristic: if at least one face and face area > small threshold
    attention = 0.0
    if faces:
        h_img, w_img = img.shape[:2]
        face_areas = [f[2] * f[3] for f in faces]
        largest = max(face_areas)
        frac = largest / (w_img * h_img)
        attention = min(1.0, max(0.05, frac * 5.0))

    return {
        "faces": faces,
        "emotions": emotions,
        "attention": round(float(attention), 3),
        "image_shape": list(img.shape)
    }


def analyze_base64_image(b64: str) -> Dict[str, Any]:
    try:
        img_bytes = base64.b64decode(b64)
    except Exception:
        return {"error": "invalid_base64"}
    return analyze_frame_bytes(img_bytes)
