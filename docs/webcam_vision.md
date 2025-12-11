# Webcam Vision Integration

TradeSensei AI now streams webcam frames from the WPF client to the backend for face detection and attention heuristics.

## Components

1. **Backend** (`backend/webcam_vision.py`, `/webcam/analyze` endpoint)
   - Uses OpenCV on the server to detect faces and compute a simple attention score.
   - Returns face rectangles, placeholder emotion labels, and an attention float.

2. **Frontend** (`Services/WebcamVisionService.cs` and `MainWindow` UI)
   - Captures webcam frames via `OpenCvSharp.VideoCapture`.
   - Encodes each frame as JPEG/base64 and POSTs to `/webcam/analyze` every ~800ms.
   - Emits parsed results (`faces`, `attention`) back to the UI.

3. **UI Controls** (`MainWindow.xaml`)
   - Added start/stop buttons, status text, attention label, and face list.
   - Allows developers/traders to monitor webcam analysis in real time.

## Usage

1. Start the backend: `python run_server.py`.
2. Launch the WPF app and click `Start Webcam` in the `MainWindow` panel.
3. Watch attention score updates and face counts in the UI.
4. Click `Stop Webcam` to end the analysis stream.

## Next Work

- Display face overlays directly on the overlay window.
- Replace placeholder emotion labels with a trained model (e.g., ONNX emotion detector).
- Use attention/emotion signals to adapt mentor responses (tone/modality).
- Add rate limiting, error handling, and optional camera selection UI.
