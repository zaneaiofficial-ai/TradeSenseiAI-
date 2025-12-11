using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using TradeSensei.UI.Voice;

namespace TradeSensei.UI
{
    public partial class VoiceChatWindow : Window
    {
        private static readonly HttpClient Http = new();
        private VoiceChatService voiceService;
        private string? lastTranscription;
        private string? lastResponse;

        public VoiceChatWindow()
        {
            InitializeComponent();
            voiceService = new VoiceChatService();
            voiceService.OnTranscriptionReceived += (s, text) =>
            {
                lastTranscription = text;
                Dispatcher.Invoke(() =>
                {
                    TxtTranscription.Text = text;
                    TxtStatus.Text = "Transcribed. Waiting for AI response...";
                });
            };
            voiceService.OnError += (s, ex) =>
            {
                Dispatcher.Invoke(() =>
                {
                    TxtStatus.Text = "Error: " + ex.Message;
                    EltRecordingIndicator.Fill = (Brush)Application.Current.FindResource("FreeBrush");
                });
            };

            // Setup push-to-talk button
            BtnTalkToMentor.PreviewMouseDown += async (s, e) =>
            {
                e.Handled = true;
                TxtStatus.Text = "Recording...";
                EltRecordingIndicator.Fill = (Brush)Application.Current.FindResource("AccentBrush");
                voiceService.StartRecording();
            };

            BtnTalkToMentor.PreviewMouseUp += async (s, e) =>
            {
                e.Handled = true;
                TxtStatus.Text = "Transcribing...";
                EltRecordingIndicator.Fill = (Brush)Application.Current.FindResource("FreeBrush");
                var transcription = await voiceService.StopRecordingAndTranscribeAsync();
                if (!string.IsNullOrEmpty(transcription))
                {
                    await GetAiResponse(transcription);
                }
                else
                {
                    TxtStatus.Text = "Failed to transcribe. Try again.";
                }
            };
        }

        private async System.Threading.Tasks.Task GetAiResponse(string userInput)
        {
            try
            {
                TxtStatus.Text = "Getting AI response...";
                var payload = new { user_input = userInput, context = new { }, openai_key = ApiConfig.OpenAiApiKey, elevenlabs_key = ApiConfig.ElevenLabsApiKey };
                using var resp = await Http.PostAsJsonAsync(ApiConfig.GetFullUrl("mentor/ask"), payload);
                if (!resp.IsSuccessStatusCode)
                {
                    TxtStatus.Text = "Mentor currently unavailable.";
                    return;
                }

                var data = await resp.Content.ReadFromJsonAsync<JsonElement>();
                string? mentorResponse = null;
                if (data.ValueKind != JsonValueKind.Undefined && data.TryGetProperty("response", out var respElem))
                {
                    mentorResponse = respElem.GetString();
                }
                if (string.IsNullOrEmpty(mentorResponse) && data.TryGetProperty("advice", out var adviceElem))
                {
                    mentorResponse = adviceElem.GetString();
                }
                lastResponse = string.IsNullOrEmpty(mentorResponse)
                    ? "Mentor returned no message. Try again with more detail."
                    : mentorResponse;

                TxtResponse.Text = lastResponse;
                TxtStatus.Text = "Response ready. Click Play to hear it.";
            }
            catch (Exception ex)
            {
                TxtStatus.Text = "Error: " + ex.Message;
            }
        }

        private async void BtnSendManual_Click(object sender, RoutedEventArgs e)
        {
            var prompt = TxtManualPrompt.Text?.Trim();
            if (string.IsNullOrEmpty(prompt))
            {
                TxtStatus.Text = "Enter a question before sending.";
                return;
            }

            BtnSendManual.IsEnabled = false;
            try
            {
                TxtStatus.Text = "Sending question to mentor...";
                await GetAiResponse(prompt);
            }
            finally
            {
                BtnSendManual.IsEnabled = true;
            }
        }

        private async void BtnPlayResponse_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(lastResponse))
            {
                MessageBox.Show("No response to play. Record a message first.", "Voice Chat", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            TxtStatus.Text = "Playing audio response...";
            await voiceService.PlayTtsAsync(lastResponse);
            TxtStatus.Text = "Ready";
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            voiceService?.Dispose();
            this.Close();
        }
    }
}
