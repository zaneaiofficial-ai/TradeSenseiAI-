using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using OpenCvSharp;

namespace TradeSensei.UI.Services
{
    public sealed class WebcamFace
    {
        public int X { get; set; }
        public int Y { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }
    }

    public sealed class WebcamAnalysisResult
    {
        public bool Ok { get; set; }
        public List<WebcamFace> Faces { get; } = new();
        public Dictionary<string, string> Emotions { get; } = new();
        public float Attention { get; set; }
        public int[] ImageShape { get; set; } = Array.Empty<int>();
    }

    public sealed class WebcamVisionService : IDisposable
    {
        private readonly HttpClient _httpClient = new();
        private readonly string _analysisUrl;
        private VideoCapture? _capture;
        private CancellationTokenSource? _cts;
        private readonly TimeSpan _interval = TimeSpan.FromMilliseconds(800);
        private readonly object _sync = new();

        public WebcamVisionService(string backendBaseUrl)
        {
            _analysisUrl = backendBaseUrl.TrimEnd('/') + "/webcam/analyze";
        }

        public bool IsRunning => _capture?.IsOpened() ?? false;

        public event Action<WebcamAnalysisResult>? ResultReceived;
        public event Action<string>? Log;

        public Task StartAsync()
        {
            lock (_sync)
            {
                if (IsRunning)
                {
                    Log?.Invoke("Webcam already running");
                    return Task.CompletedTask;
                }

                _capture = new VideoCapture(0);
                if (!_capture.IsOpened())
                {
                    _capture.Dispose();
                    _capture = null;
                    throw new InvalidOperationException("Unable to open webcam");
                }

                _cts = new CancellationTokenSource();
                Task.Run(() => RunLoopAsync(_cts.Token), _cts.Token);
                Log?.Invoke("Webcam capture started");
                return Task.CompletedTask;
            }
        }

        public void Stop()
        {
            lock (_sync)
            {
                if (_cts != null)
                {
                    _cts.Cancel();
                    _cts.Dispose();
                    _cts = null;
                }

                _capture?.Release();
                _capture?.Dispose();
                _capture = null;
                Log?.Invoke("Webcam capture stopped");
            }
        }

        public void Dispose()
        {
            Stop();
            _httpClient.Dispose();
        }

        private async Task RunLoopAsync(CancellationToken token)
        {
            var mat = new Mat();
            while (!token.IsCancellationRequested)
            {
                try
                {
                    lock (_sync)
                    {
                        if (_capture == null || !_capture.IsOpened())
                        {
                            break;
                        }
                        _capture.Read(mat);
                    }

                    if (mat.Empty())
                    {
                        await Task.Delay(_interval, token);
                        continue;
                    }

                    var bytes = mat.ImEncode(".jpg");
                    var payload = new
                    {
                        image_base64 = Convert.ToBase64String(bytes)
                    };

                    var json = JsonSerializer.Serialize(payload);
                    using var content = new StringContent(json, Encoding.UTF8, "application/json");
                    using var response = await _httpClient.PostAsync(_analysisUrl, content, token);
                    if (!response.IsSuccessStatusCode)
                    {
                        Log?.Invoke($"Webcam API error: {response.StatusCode}");
                        await Task.Delay(_interval, token);
                        continue;
                    }

                    var respText = await response.Content.ReadAsStringAsync(token);
                    var result = ParseResponse(respText);
                    if (result != null)
                    {
                        ResultReceived?.Invoke(result);
                    }
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    Log?.Invoke($"Webcam loop error: {ex.Message}");
                }

                await Task.Delay(_interval, token);
            }
        }

        private WebcamAnalysisResult? ParseResponse(string json)
        {
            try
            {
                using var doc = JsonDocument.Parse(json);
                var root = doc.RootElement;
                var ok = root.GetProperty("ok").GetBoolean();
                var result = new WebcamAnalysisResult { Ok = ok };
                if (!ok)
                {
                    Log?.Invoke("Webcam API reported failure");
                    return result;
                }

                if (root.TryGetProperty("result", out var payload))
                {
                    if (payload.TryGetProperty("faces", out var faces))
                    {
                        foreach (var arr in faces.EnumerateArray())
                        {
                            if (arr.GetArrayLength() >= 4)
                            {
                                result.Faces.Add(new WebcamFace
                                {
                                    X = arr[0].GetInt32(),
                                    Y = arr[1].GetInt32(),
                                    Width = arr[2].GetInt32(),
                                    Height = arr[3].GetInt32()
                                });
                            }
                        }
                    }

                    if (payload.TryGetProperty("emotions", out var emotions))
                    {
                        foreach (var property in emotions.EnumerateObject())
                        {
                            result.Emotions[property.Name] = property.Value.GetString() ?? "unknown";
                        }
                    }

                    if (payload.TryGetProperty("attention", out var attention))
                    {
                        result.Attention = (float)attention.GetDouble();
                    }

                    if (payload.TryGetProperty("image_shape", out var shape))
                    {
                        var list = new List<int>(shape.GetArrayLength());
                        foreach (var value in shape.EnumerateArray())
                        {
                            list.Add(value.GetInt32());
                        }
                        result.ImageShape = list.ToArray();
                    }
                }

                return result;
            }
            catch (Exception ex)
            {
                Log?.Invoke($"Webcam response parse error: {ex.Message}");
                return null;
            }
        }
    }
}