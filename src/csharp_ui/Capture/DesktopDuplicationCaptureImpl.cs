using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

#if DESKTOP_DUPLICATION
using Vortice.Direct3D11;
using Vortice.DXGI;
using static Vortice.DXGI.DXGI;
using static Vortice.Direct3D11.D3D11;
#endif

namespace TradeSensei.UI.Capture
{
#if DESKTOP_DUPLICATION
    // Desktop Duplication implementation using Vortice (Direct3D11 + DXGI).
    // This implementation attempts to use IDXGIOutputDuplication to capture the
    // primary output. If any step fails, callers should fall back to GDI capture.
    public class DesktopDuplicationCaptureImpl : DesktopDuplicationCapture, IDisposable
    {
        private ID3D11Device? _device;
        private ID3D11DeviceContext? _context;
        private IDXGIOutputDuplication? _duplication;
        private IDXGIOutput? _output;
        private IDXGIAdapter? _adapter;
        private bool _started = false;

        public DesktopDuplicationCaptureImpl() : base()
        {
        }

        public void Dispose()
        {
            Stop();
            _duplication?.Release();
            _output?.Release();
            _adapter?.Release();
            _context?.Release();
            _device?.Release();
        }

        public override void Start()
        {
            if (_started) return;
            try
            {
                // Create D3D11 device
                var result = D3D11CreateDevice(null, DriverType.Hardware, DeviceCreationFlags.BGRA_SUPPORT, null, out _device, out _context);
                if (result.Failure || _device == null)
                {
                    throw new Exception("Failed to create D3D11 device");
                }

                // Get DXGI factory -> adapter -> output
                using var dxgiDevice = _device.QueryInterface<IDXGIDevice2>();
                dxgiDevice.GetAdapter(out _adapter);
                if (_adapter == null) throw new Exception("Failed to get DXGI adapter");

                // Use the first output (primary monitor)
                _adapter.EnumOutputs(0, out _output);
                if (_output == null) throw new Exception("Failed to get output");

                var output1 = _output.QueryInterface<IDXGIOutput1>();
                // Create duplication
                output1.DuplicateOutput(_device, out _duplication);
                if (_duplication == null) throw new Exception("Failed to create output duplication");

                _started = true;
            }
            catch (Exception ex)
            {
                // If any step fails, ensure resources are cleaned and mark not started
                _started = false;
                Console.WriteLine("DesktopDuplication start error: " + ex.Message);
                Stop();
            }
        }

        public override void Stop()
        {
            if (!_started) return;
            try
            {
                _duplication?.Release();
            }
            catch { }
            finally
            {
                _duplication = null;
                _started = false;
            }
        }

        public override Bitmap TryCaptureFrame()
        {
            if (!_started || _duplication == null || _device == null || _context == null)
            {
                return base.TryCaptureFrame(); // fallback to GDI
            }

            try
            {
                // Acquire next frame (timeout 100ms)
                var frameInfo = new OutduplFrameInfo();
                IDXGIResource? desktopResource = null;
                var hr = _duplication.AcquireNextFrame(100, out frameInfo, out desktopResource);
                if (hr.Failure || desktopResource == null)
                {
                    // timeout or failure - return fallback
                    desktopResource?.Release();
                    return base.TryCaptureFrame();
                }

                // Get texture2D from resource
                var desktopTexture = desktopResource.QueryInterface<ID3D11Texture2D>();
                if (desktopTexture == null)
                {
                    _duplication.ReleaseFrame();
                    desktopResource.Release();
                    return base.TryCaptureFrame();
                }

                // Create a staging texture to copy the GPU texture to CPU accessible memory
                var desc = desktopTexture.Description;
                var stagingDesc = desc;
                stagingDesc.Usage = Vortice.Direct3D11.ResourceUsage.Staging;
                stagingDesc.BindFlags = Vortice.Direct3D11.BindFlags.None;
                stagingDesc.CPUAccessFlags = Vortice.Direct3D11.CpuAccessFlags.Read;
                stagingDesc.MiscFlags = Vortice.Direct3D11.ResourceMiscFlag.None;

                var staging = _device.CreateTexture2D(stagingDesc);
                _context.CopyResource(staging, desktopTexture);

                // Map staging texture
                var mapped = _context.Map(staging, 0, Vortice.Direct3D11.MapMode.Read, Vortice.Direct3D11.MapFlags.None);
                if (mapped.Data == IntPtr.Zero)
                {
                    // cleanup
                    _context.Unmap(staging, 0);
                    staging.Release();
                    desktopTexture.Release();
                    _duplication.ReleaseFrame();
                    desktopResource.Release();
                    return base.TryCaptureFrame();
                }

                // Read pixel data
                int width = desc.Width;
                int height = desc.Height;
                int rowPitch = mapped.RowPitch; // bytes per row

                // Create a bitmap and copy rows
                var bmp = new Bitmap(width, height, PixelFormat.Format32bppArgb);
                var bmpData = bmp.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.WriteOnly, bmp.PixelFormat);

                // Copy row by row
                for (int y = 0; y < height; y++)
                {
                    IntPtr srcPtr = mapped.Data + y * rowPitch;
                    IntPtr dstPtr = bmpData.Scan0 + y * bmpData.Stride;
                    CopyMemory(dstPtr, srcPtr, (uint)(Math.Min(bmpData.Stride, rowPitch)));
                }

                bmp.UnlockBits(bmpData);

                // Cleanup
                _context.Unmap(staging, 0);
                staging.Release();
                desktopTexture.Release();
                _duplication.ReleaseFrame();
                desktopResource.Release();

                return bmp;
            }
            catch (Exception ex)
            {
                Console.WriteLine("DesktopDuplication capture error: " + ex.Message);
                try { _duplication.ReleaseFrame(); } catch { }
                return base.TryCaptureFrame();
            }
        }

        [DllImport("kernel32.dll", EntryPoint = "RtlMoveMemory", SetLastError = false)]
        private static extern void CopyMemory(IntPtr dest, IntPtr src, uint count);
    }
#else
    // Stub implementation when Desktop Duplication is disabled
    public class DesktopDuplicationCaptureImpl : DesktopDuplicationCapture
    {
        public DesktopDuplicationCaptureImpl() : base() { }
        public void Dispose() { }
        public void Start() { }
        public void Stop() { }
        public System.Drawing.Bitmap? TryCaptureFrame() => null;
    }
#endif
}
