using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Windows;

namespace TradeSensei.UI
{
    public partial class SubscriptionWindow : Window
    {
        public string UserId { get; set; }

        public SubscriptionWindow(string userId)
        {
            InitializeComponent();
            UserId = userId;
            _ = LoadAsync();
        }

        private async System.Threading.Tasks.Task LoadAsync()
        {
            if (string.IsNullOrEmpty(UserId)) return;
            try
            {
                var http = new HttpClient();
                var resp = await http.GetAsync(ApiConfig.GetFullUrl($"subscriptions/check?user_id={UserId}"));
                if (!resp.IsSuccessStatusCode) return;
                var data = await resp.Content.ReadFromJsonAsync<System.Text.Json.JsonElement>();
                if (data.TryGetProperty("tier", out var t)) TxtTier.Text = t.GetString() ?? "Free";
                if (data.TryGetProperty("is_premium", out var p)) TxtPremium.Text = p.GetBoolean() ? "Yes" : "No";
                if (data.TryGetProperty("expiry", out var e)) TxtExpiry.Text = e.GetString() ?? "N/A";
                if (data.TryGetProperty("next_billing", out var n)) TxtNextBilling.Text = n.GetString() ?? "N/A";
            }
            catch { /* ignore */ }
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
        }

        private async void BtnRefresh_Click(object sender, RoutedEventArgs e)
        {
            await LoadAsync();
        }

        private async void BtnUpgrade_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(UserId)) return;
            try
            {
                var http = new HttpClient();
                var payload = new { user_id = UserId, amount = 9.99, currency = "USD" };
                var resp = await http.PostAsJsonAsync(ApiConfig.GetFullUrl("subscriptions/create_checkout"), payload);
                if (!resp.IsSuccessStatusCode)
                {
                    MessageBox.Show("Upgrade request failed", "Upgrade", MessageBoxButton.OK, MessageBoxImage.Error);
                    return;
                }
                var data = await resp.Content.ReadFromJsonAsync<System.Text.Json.JsonElement>();
                if (data.TryGetProperty("checkout_url", out var urlElem))
                {
                    var url = urlElem.GetString();
                    if (!string.IsNullOrEmpty(url))
                    {
                        System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(url) { UseShellExecute = true });
                        await System.Threading.Tasks.Task.Delay(1000);
                        await LoadAsync();
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Upgrade error: " + ex.Message, "Upgrade", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
    }
}
