// DesktopDuplicationCapture.cs
// This is a stub for Desktop Duplication capture.
// Implementing the full Desktop Duplication API requires Direct3D11 interop and
// more code; for now this class provides the API surface and falls back to the
// GDI capture in `CaptureService`. Replace the implementations with a proper
// Desktop Duplication implementation when ready.

using System.Drawing;

namespace TradeSensei.UI.Capture
{
    public class DesktopDuplicationCapture
    {
        public bool IsRunning { get; private set; } = false;

        public DesktopDuplicationCapture()
        {
        }

        public void Start()
        {
            // TODO: Initialize Direct3D device and Desktop Duplication here.
            IsRunning = true;
        }

        public void Stop()
        {
            // TODO: Clean up Direct3D resources.
            IsRunning = false;
        }

        public Bitmap TryCaptureFrame()
        {
            // TODO: return frame from Desktop Duplication if implemented.
            // Fallback to GDI capture for now.
            return CaptureService.CapturePrimaryScreen();
        }
    }
}
