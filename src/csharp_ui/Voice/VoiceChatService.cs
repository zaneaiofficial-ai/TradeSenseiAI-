using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;
using NAudio.Wave;

namespace TradeSensei.UI.Voice
{
    /// <summary>
    /// VoiceChatService handles microphone capture, TTS playback, and backend communication.
    /// </summary>
    public class VoiceChatService : IDisposable
    {
        private WaveInEvent? waveInEvent;
        private WaveFileWriter? writer;
        private string recordingPath = "";
        private IWavePlayer? player;
        private bool isRecording;
        private bool isPlaying;

        public event EventHandler<string>? OnTranscriptionReceived;
        public event EventHandler<Exception>? OnError;

        public bool IsRecording => isRecording;
        public bool IsPlaying => isPlaying;

        public VoiceChatService()
        {
            recordingPath = Path.Combine(Path.GetTempPath(), "TradeSensei_Voice");
            Directory.CreateDirectory(recordingPath);
        }

        public void StartRecording()
        {
            try
            {
                if (isRecording) return;
                
                waveInEvent = new WaveInEvent();
                var fileName = Path.Combine(recordingPath, $"recording_{DateTime.UtcNow:yyyyMMdd_HHmmss}.wav");
                writer = new WaveFileWriter(fileName, waveInEvent.WaveFormat);
                waveInEvent.DataAvailable += (s, e) =>
                {
                    writer?.Write(e.Buffer, 0, e.BytesRecorded);
                };
                waveInEvent.RecordingStopped += (s, e) =>
                {
                    writer?.Dispose();
                };
                waveInEvent.StartRecording();
                isRecording = true;
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
            }
        }

        public async Task<string?> StopRecordingAndTranscribeAsync()
        {
            if (!isRecording) return null;

            try
            {
                waveInEvent?.StopRecording();
                waveInEvent?.Dispose();
                writer?.Dispose();
                isRecording = false;

                // Get latest recording file
                var files = Directory.GetFiles(recordingPath, "recording_*.wav");
                if (files.Length == 0) return null;
                Array.Sort(files);
                var lastFile = files[^1];

                // Send to backend for transcription
                var http = new HttpClient();
                var audioBytes = File.ReadAllBytes(lastFile);
                var audioBase64 = Convert.ToBase64String(audioBytes);
                var payload = new { audio_base64 = audioBase64, api_key = ApiConfig.OpenAiApiKey };
                var resp = await http.PostAsJsonAsync(ApiConfig.GetFullUrl("transcribe"), payload);
                if (resp.IsSuccessStatusCode)
                {
                    var data = await resp.Content.ReadFromJsonAsync<JsonElement>();
                    string? transcription = null;
                    if (data.TryGetProperty("transcription", out var transElem))
                    {
                        transcription = transElem.GetString();
                    }
                    else if (data.TryGetProperty("text", out var textElem))
                    {
                        transcription = textElem.GetString();
                    }

                    if (!string.IsNullOrEmpty(transcription))
                    {
                        OnTranscriptionReceived?.Invoke(this, transcription);
                        return transcription;
                    }
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
            }

            return null;
        }

        public async Task PlayTtsAsync(string text)
        {
            try
            {
                if (isPlaying) return;
                isPlaying = true;

                var http = new HttpClient();
                var payload = new { text = text, api_key = ApiConfig.ElevenLabsApiKey };
                var resp = await http.PostAsJsonAsync(ApiConfig.GetFullUrl("tts"), payload);
                
                if (resp.IsSuccessStatusCode)
                {
                    var audioBytes = await resp.Content.ReadAsByteArrayAsync();
                    var ms = new MemoryStream(audioBytes);

                    player = new WaveOutEvent();
                    using var reader = new Mp3FileReader(ms);
                    player.Init(reader);
                    player.PlaybackStopped += (s, e) => isPlaying = false;
                    player.Play();
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, ex);
                isPlaying = false;
            }
        }

        public void Dispose()
        {
            waveInEvent?.Dispose();
            writer?.Dispose();
            player?.Dispose();
        }
    }
}
