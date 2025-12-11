using System;
using System.Windows;
using System.Windows.Media;
using System.Windows.Shapes;
using System.Windows.Controls;
using System.Threading.Tasks;
using System.Text;
using System.IO;
using System.Collections.Generic;
using System.Threading;
using System.Text.Json;
using System.Drawing.Imaging;
using TradeSensei.UI.Networking;
using TradeSensei.UI.Capture;
using TradeSensei.UI.Streaming;

namespace TradeSensei.UI
{
    public partial class OverlayWindow : Window
    {
        public OverlayWindow()
        {
            InitializeComponent();
            // Make window transparent click-through
            this.WindowStyle = WindowStyle.None;
            this.AllowsTransparency = true;
            this.Background = Brushes.Transparent;
            this.Topmost = true;
            this.Left = 0;
            this.Top = 0;
            this.Width = SystemParameters.PrimaryScreenWidth;
            this.Height = SystemParameters.PrimaryScreenHeight;

            // Example: draw a sample label
            var rect = new Rectangle()
            {
                Width = 200,
                Height = 40,
                Fill = new SolidColorBrush(System.Windows.Media.Color.FromArgb(120, 0, 150, 255)),
            };
            Canvas.SetLeft(rect, 50);
            Canvas.SetTop(rect, 50);
            OverlayCanvas.Children.Add(rect);

            // NOTE: Do not auto-start streaming. Use StartStreaming to begin capture and sending.
            // Start cleanup timer to remove expired overlay elements
            cleanupTimer = new Timer(_ => Dispatcher.Invoke(CleanupOverlay), null, 1000, 1000);
        }

        private WebSocketClient? wsClient;
        private bool capturing = false;
        private int captureFps = 2;
        private TradeSensei.UI.Capture.DesktopDuplicationCapture? duplicator = null;
        private List<(UIElement element, DateTime expiry)> overlayElements = new List<(UIElement, DateTime)>();
        private Timer? cleanupTimer;
        private ObsStreamingService? obsStreaming;

        private void WsClient_OnJsonMessage(JsonElement obj)
        {
            // Only process overlay commands
            if (obj.TryGetProperty("type", out var t) && t.GetString() == "overlay")
            {
                if (obj.TryGetProperty("action", out var action))
                {
                    var act = action.GetString();
                    if (act == "draw_text")
                    {
                        int x = obj.GetProperty("x").GetInt32();
                        int y = obj.GetProperty("y").GetInt32();
                        string text = obj.GetProperty("text").GetString() ?? "";
                        int ttl = obj.TryGetProperty("ttl", out var tv) ? tv.GetInt32() : 5;
                        Dispatcher.Invoke(() => DrawText(x, y, text, ttl));
                    }
                    else if (act == "draw_rect")
                    {
                        int x = obj.GetProperty("x").GetInt32();
                        int y = obj.GetProperty("y").GetInt32();
                        int w = obj.GetProperty("w").GetInt32();
                        int h = obj.GetProperty("h").GetInt32();
                        int ttl = obj.TryGetProperty("ttl", out var tv2) ? tv2.GetInt32() : 5;
                        Dispatcher.Invoke(() => DrawRect(x, y, w, h, ttl));
                    }
                    else if (act == "draw_line")
                    {
                        int x1 = obj.GetProperty("x1").GetInt32();
                        int y1 = obj.GetProperty("y1").GetInt32();
                        int x2 = obj.GetProperty("x2").GetInt32();
                        int y2 = obj.GetProperty("y2").GetInt32();
                        int ttl = obj.TryGetProperty("ttl", out var tv3) ? tv3.GetInt32() : 5;
                        Dispatcher.Invoke(() => DrawLine(x1, y1, x2, y2, ttl));
                    }
                    else if (act == "draw_arrow")
                    {
                        int x1 = obj.GetProperty("x1").GetInt32();
                        int y1 = obj.GetProperty("y1").GetInt32();
                        int x2 = obj.GetProperty("x2").GetInt32();
                        int y2 = obj.GetProperty("y2").GetInt32();
                        int ttl = obj.TryGetProperty("ttl", out var tv4) ? tv4.GetInt32() : 5;
                        Dispatcher.Invoke(() => DrawArrow(x1, y1, x2, y2, ttl));
                    }
                    else if (act == "clear")
                    {
                        Dispatcher.Invoke(ClearAllOverlay);
                    }
                }
            }
        }

        private void DrawText(int x, int y, string text, int ttlSeconds = 5)
        {
            var tb = new System.Windows.Controls.TextBlock()
            {
                Text = text,
                Foreground = Brushes.Lime,
                FontSize = 16,
                FontWeight = FontWeights.Bold
            };
            Canvas.SetLeft(tb, x);
            Canvas.SetTop(tb, y);
            OverlayCanvas.Children.Add(tb);
            overlayElements.Add((tb, DateTime.UtcNow.AddSeconds(ttlSeconds)));
        }

        private void DrawRect(int x, int y, int w, int h, int ttlSeconds = 5)
        {
            var r = new Rectangle()
            {
                Width = w,
                Height = h,
                Stroke = new SolidColorBrush(Color.FromArgb(200, 255, 100, 50)),
                StrokeThickness = 2,
                Fill = new SolidColorBrush(Color.FromArgb(40, 255, 100, 50))
            };
            Canvas.SetLeft(r, x);
            Canvas.SetTop(r, y);
            OverlayCanvas.Children.Add(r);
            overlayElements.Add((r, DateTime.UtcNow.AddSeconds(ttlSeconds)));
        }

        private void DrawLine(int x1, int y1, int x2, int y2, int ttlSeconds = 5, int thickness = 2)
        {
            var line = new System.Windows.Shapes.Line()
            {
                X1 = x1,
                Y1 = y1,
                X2 = x2,
                Y2 = y2,
                Stroke = Brushes.Cyan,
                StrokeThickness = thickness
            };
            OverlayCanvas.Children.Add(line);
            overlayElements.Add((line, DateTime.UtcNow.AddSeconds(ttlSeconds)));
        }

        private void DrawArrow(int x1, int y1, int x2, int y2, int ttlSeconds = 5)
        {
            DrawLine(x1, y1, x2, y2, ttlSeconds, 3);
            // Simple arrow head
            var angle = Math.Atan2(y2 - y1, x2 - x1);
            var len = 12;
            var ax = x2 - (int)(len * Math.Cos(angle - Math.PI / 6));
            var ay = y2 - (int)(len * Math.Sin(angle - Math.PI / 6));
            var bx = x2 - (int)(len * Math.Cos(angle + Math.PI / 6));
            var by = y2 - (int)(len * Math.Sin(angle + Math.PI / 6));
            DrawLine(x2, y2, ax, ay, ttlSeconds, 3);
            DrawLine(x2, y2, bx, by, ttlSeconds, 3);
        }

        private void CleanupOverlay()
        {
            var now = DateTime.UtcNow;
            var toRemove = new List<UIElement>();
            foreach (var (element, expiry) in overlayElements.ToArray())
            {
                if (expiry <= now)
                {
                    toRemove.Add(element);
                    overlayElements.Remove((element, expiry));
                }
            }
            foreach (var el in toRemove)
            {
                if (OverlayCanvas.Children.Contains(el)) OverlayCanvas.Children.Remove(el);
            }
        }

        private void ClearAllOverlay()
        {
            OverlayCanvas.Children.Clear();
            overlayElements.Clear();
        }

        private void StartCaptureLoop()
        {
            if (capturing) return;
            capturing = true;
            _ = Task.Run(async () =>
            {
                while (capturing)
                {
                    try
                    {
                        using var bmp = CaptureScreenRegion();
                        using var ms = new MemoryStream();
                        bmp.Save(ms, ImageFormat.Png);
                        var bytes = ms.ToArray();
                        var b64 = Convert.ToBase64String(bytes);
                        var payload = JsonSerializer.Serialize(new { type = "frame", data = b64, user_id = Auth.AuthState.UserId });
                        if (wsClient != null)
                        {
                            await wsClient.SendStringAsync(payload);
                        }
                        // Stream to OBS if enabled
                        if (obsStreaming?.IsStreaming == true)
                        {
                            await obsStreaming.WriteFrameAsync(bmp);
                        }
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine("Capture/send error: " + ex.Message);
                    }
                    await Task.Delay(1000 / Math.Max(1, captureFps));
                }
            });
        }

        public void SetObsStreaming(ObsStreamingService? obsService)
        {
            obsStreaming = obsService;
        }

        public async System.Threading.Tasks.Task StartStreamingAsync(int fps = 2)
        {
            captureFps = Math.Max(1, fps);
            if (wsClient == null)
            {
                wsClient = new WebSocketClient(ApiConfig.GetWebSocketUrl());
                wsClient.OnJsonMessage += WsClient_OnJsonMessage;
            }

            try
            {
                await wsClient.ConnectAsync();
                // Initialize Desktop Duplication capture implementation and start it.
                try
                {
                    var impl = new TradeSensei.UI.Capture.DesktopDuplicationCaptureImpl();
                    impl.Start();
                    duplicator = impl;
                }
                catch (Exception ex)
                {
                    // If Desktop Duplication couldn't be initialized, leave duplicator null and fallback to GDI capture.
                    System.Diagnostics.Debug.WriteLine("Desktop Duplication init failed: " + ex.Message);
                    duplicator = null;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("WS connect error: " + ex.Message);
            }

            StartCaptureLoop();
        }

        public void StopStreaming()
        {
            capturing = false;
            try { wsClient?.Dispose(); } catch { }
            wsClient = null;
        }

        private System.Drawing.Bitmap CaptureScreenRegion()
        {
            // Use Desktop Duplication if initialized, otherwise fallback to GDI capture.
            try
            {
                if (duplicator != null)
                {
                    var bmp = duplicator.TryCaptureFrame();
                    if (bmp != null) return bmp;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("Duplicator capture error: " + ex.Message);
            }

            return CaptureService.CapturePrimaryScreen();
        }

        protected override void OnClosed(EventArgs e)
        {
            capturing = false;
            cleanupTimer?.Dispose();
            try { duplicator?.Stop(); } catch { }
            try { (duplicator as IDisposable)?.Dispose(); } catch { }
            duplicator = null;
            wsClient?.Dispose();
            base.OnClosed(e);
        }
    }
}
