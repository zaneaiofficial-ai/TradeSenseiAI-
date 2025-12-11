import base64
import io
import numpy as np
import cv2
from fastapi.testclient import TestClient
from .main import app


def create_blank_jpg_bytes(width=160, height=120, color=(50, 100, 150)):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = color
    is_success, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()


def test_webcam_analyze_endpoint():
    client = TestClient(app)
    img_bytes = create_blank_jpg_bytes()
    b64 = base64.b64encode(img_bytes).decode('ascii')
    resp = client.post('/webcam/analyze', json={'image_base64': b64})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get('ok') is True
    result = payload.get('result')
    assert 'faces' in result
    assert 'attention' in result
