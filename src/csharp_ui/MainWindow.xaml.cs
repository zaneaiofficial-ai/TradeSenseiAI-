using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Diagnostics;
using System.Windows.Threading;
using System.Windows;
using TradeSensei.UI.Services;

namespace TradeSensei.UI
{
    public partial class MainWindow : Window
    {
        private OverlayWindow? overlayWindow;
        private DispatcherTimer? subsTimer;
        private int pollIntervalSeconds = 30;
        private bool enableDevFeatures = false;
        private string defaultTier = "free";
        private WebcamVisionService? _webcamService;
        private readonly List<string> _webcamFaceDescriptions = new();

        public MainWindow()
        {
            InitializeComponent();
            UpdateLoginStatus();
            _ = UpdateSubscriptionStatusAsync();
            subsTimer = new DispatcherTimer();
            subsTimer.Interval = TimeSpan.FromSeconds(pollIntervalSeconds);
            subsTimer.Tick += async (s, e) =>
            {
                if (ChkAutoRefresh.IsChecked == true && !string.IsNullOrEmpty(Auth.AuthState.UserId))
                {
                    await UpdateSubscriptionStatusAsync();
                }
            };
            subsTimer.Start();
            LoadSettings();
        }

        private void LoadSettings()
        {
            pollIntervalSeconds = 30;
            enableDevFeatures = false;
            defaultTier = "free";
        }

        private void SaveSettings()
        {
            if (subsTimer != null)
            {
                subsTimer.Interval = TimeSpan.FromSeconds(pollIntervalSeconds);
            }
        }

        private void UpdateLoginStatus()
        {
            if (!string.IsNullOrEmpty(Auth.AuthState.UserId))
            {
                TxtLoginStatus.Text = $"Signed in: {Auth.AuthState.UserId}";
            }
            else
            {
                TxtLoginStatus.Text = "Not signed in";
            }
            _ = UpdateSubscriptionStatusAsync();
            if (!string.IsNullOrEmpty(Auth.AuthState.UserId))
            {
                if (subsTimer != null && !subsTimer.IsEnabled) subsTimer.Start();
            }
            else
            {
                if (subsTimer != null && subsTimer.IsEnabled) subsTimer.Stop();
            }
        }

        private async System.Threading.Tasks.Task UpdateSubscriptionStatusAsync()
        {
            if (string.IsNullOrEmpty(Auth.AuthState.UserId))
            {
                TxtSubStatus.Text = "Subscription: Free";
                return;
            }
            try
            {
                var http = new HttpClient();
                var resp = await http.GetAsync(ApiConfig.GetFullUrl($"subscriptions/check?user_id={Auth.AuthState.UserId}"));
                if (!resp.IsSuccessStatusCode)
                {
                    TxtSubStatus.Text = "Subscription: Unknown";
                    return;
                }
                var data = await resp.Content.ReadFromJsonAsync<System.Text.Json.JsonElement>();
                if (data.TryGetProperty("tier", out var tierElem))
                {
                    var tier = tierElem.GetString();
                    if (!string.IsNullOrEmpty(tier))
                    {
                        TxtSubStatus.Text = $"Subscription: {tier}";
                        // color code
                        var brush = (System.Windows.Media.Brush)Application.Current.FindResource("FreeBrush");
                        if (tier.ToLower() == "pro") brush = (System.Windows.Media.Brush)Application.Current.FindResource("AccentBrush");
                        if (tier.ToLower() == "master") brush = (System.Windows.Media.Brush)Application.Current.FindResource("GoldBrush");
                        TxtSubStatus.Foreground = brush;
                        // update small badge color
                        try
                        {
                            EltSubBadge.Fill = brush;
                        }
                        catch { }
                        TxtSubStatus.ToolTip = $"Tier: {tier}\nPremium features: { (data.TryGetProperty("is_premium", out var p) && p.GetBoolean() ? "Enabled" : "Disabled") }";
                    }
                    else
                        TxtSubStatus.Text = "Subscription: Free";
                }
                else
                {
                    TxtSubStatus.Text = "Subscription: Free";
                }
            }
            catch
            {
                TxtSubStatus.Text = "Subscription: Error";
            }
        }

        private void BtnRefreshSub_Click(object sender, RoutedEventArgs e)
        {
            _ = UpdateSubscriptionStatusAsync();
        }

        private void BtnManageSub_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(Auth.AuthState.UserId))
            {
                MessageBox.Show("Please sign in first.", "Manage Subscription", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            var w = new SubscriptionWindow(Auth.AuthState.UserId);
            w.Owner = this;
            w.ShowDialog();
            _ = UpdateSubscriptionStatusAsync();
        }

        private void BtnSettings_Click(object sender, RoutedEventArgs e)
        {
            var w = new SettingsWindow(pollIntervalSeconds, ChkAutoRefresh.IsChecked == true, defaultTier, enableDevFeatures);
            w.Owner = this;
            var result = w.ShowDialog();
            if (result == true)
            {
                pollIntervalSeconds = w.PollInterval;
                ChkAutoRefresh.IsChecked = w.AutoStartPolling;
                defaultTier = w.DefaultTier;
                enableDevFeatures = w.EnableDevFeatures;
                SaveSettings();
            }
        }

        private void BtnWebhookSimulator_Click(object sender, RoutedEventArgs e)
        {
            if (!enableDevFeatures)
            {
                MessageBox.Show("Dev features not enabled. Open Settings to enable.", "Webhook Simulator", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            var w = new WebhookSimulatorWindow();
            w.Owner = this;
            w.ShowDialog();
        }

        private void BtnStreamObs_Click(object sender, RoutedEventArgs e)
        {
            if (overlayWindow == null)
            {
                MessageBox.Show("Open the overlay first before streaming.", "Stream to OBS", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            var w = new StreamingWindow();
            w.Owner = this;
            overlayWindow.SetObsStreaming(w.StreamingService);
            w.ShowDialog();
            overlayWindow.SetObsStreaming(null);
        }

        private void BtnVoiceChat_Click(object sender, RoutedEventArgs e)
        {
            var w = new VoiceChatWindow();
            w.Owner = this;
            w.ShowDialog();
        }

        private void BtnPriceAlerts_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(Auth.AuthState.UserId))
            {
                MessageBox.Show("Please sign in first.", "Price Alerts", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            var w = new PriceAlertsWindow();
            w.Owner = this;
            w.Initialize(Auth.AuthState.UserId, ApiConfig.GetApiBaseUrl());
            w.ShowDialog();
        }

        private void BtnPortfolio_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(Auth.AuthState.UserId))
            {
                MessageBox.Show("Please sign in first.", "Portfolio", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            var w = new PortfolioWindow();
            w.Owner = this;
            w.Initialize(Auth.AuthState.UserId, ApiConfig.GetApiBaseUrl());
            w.ShowDialog();
        }

        private async void BtnCheckout_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(Auth.AuthState.UserId))
            {
                MessageBox.Show("Please sign in before subscribing.", "Subscription", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            try
            {
                var http = new HttpClient();
                var payload = new { user_id = Auth.AuthState.UserId, tier = "pro" };
                var resp = await http.PostAsJsonAsync(ApiConfig.GetFullUrl("subscriptions/create_checkout"), payload);
                if (!resp.IsSuccessStatusCode)
                {
                    MessageBox.Show($"Checkout failed: {resp.StatusCode}", "Subscription", MessageBoxButton.OK, MessageBoxImage.Error);
                    return;
                }
                var data = await resp.Content.ReadFromJsonAsync<System.Text.Json.JsonElement>();
                if (data.TryGetProperty("checkout_url", out var urlElem))
                {
                    var url = urlElem.GetString();
                    if (!string.IsNullOrEmpty(url))
                    {
                        Process.Start(new ProcessStartInfo(url) { UseShellExecute = true });
                        // schedule a refresh in case the webhook updates the tier
                        _ = System.Threading.Tasks.Task.Run(async () => { await System.Threading.Tasks.Task.Delay(10000); await UpdateSubscriptionStatusAsync(); });
                        return;
                    }
                }
                MessageBox.Show("No checkout URL returned.", "Subscription", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Checkout error: " + ex.Message, "Subscription", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void BtnLogin_Click(object sender, RoutedEventArgs e)
        {
            var win = new LoginWindow();
            var result = win.ShowDialog();
            UpdateLoginStatus();
        }

        private void BtnOpenOverlay_Click(object sender, RoutedEventArgs e)
        {
            if (overlayWindow == null)
            {
                overlayWindow = new OverlayWindow();
                overlayWindow.Show();
            }
            else
            {
                overlayWindow.Close();
                overlayWindow = null;
            }
        }

        private async void BtnStartStream_Click(object sender, RoutedEventArgs e)
        {
            if (overlayWindow == null)
            {
                overlayWindow = new OverlayWindow();
                overlayWindow.Show();
            }

            if (int.TryParse(TxtFps.Text, out var fps) == false) fps = 2;
            await overlayWindow.StartStreamingAsync(fps);
        }

        private void BtnStopStream_Click(object sender, RoutedEventArgs e)
        {
            if (overlayWindow != null)
            {
                overlayWindow.StopStreaming();
            }
        }

        private async void BtnStartWebcam_Click(object sender, RoutedEventArgs e)
        {
            if (_webcamService == null)
            {
                _webcamService = new WebcamVisionService(ApiConfig.BaseUrl);
                _webcamService.ResultReceived += OnWebcamResult;
                _webcamService.Log += message => Dispatcher.Invoke(() => TxtWebcamStatus.Text = message);
            }

            try
            {
                await _webcamService.StartAsync();
                TxtWebcamStatus.Text = "Running";
            }
            catch (Exception ex)
            {
                TxtWebcamStatus.Text = "Error: " + ex.Message;
            }
        }

        private void BtnStopWebcam_Click(object sender, RoutedEventArgs e)
        {
            _webcamService?.Stop();
            TxtWebcamStatus.Text = "Stopped";
        }

        private void OnWebcamResult(WebcamAnalysisResult result)
        {
            Dispatcher.Invoke(() =>
            {
                TxtWebcamAttention.Text = $"Attention: {result.Attention:P0}";
                _webcamFaceDescriptions.Clear();
                for (int i = 0; i < result.Faces.Count; i++)
                {
                    var face = result.Faces[i];
                    _webcamFaceDescriptions.Add($"Face {i + 1}: {face.Width}x{face.Height} at ({face.X},{face.Y})");
                }
                LstWebcamFaces.ItemsSource = _webcamFaceDescriptions.ToList();
            });
        }

        protected override void OnClosed(EventArgs e)
        {
            _webcamService?.Dispose();
            overlayWindow?.Close();
            base.OnClosed(e);
        }
    }
}
