using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Windows;
using System.Windows.Controls;

namespace TradeSensei.UI
{
    public partial class WebhookSimulatorWindow : Window
    {
        public WebhookSimulatorWindow()
        {
            InitializeComponent();
        }

        private async void BtnSimulate_Click(object sender, RoutedEventArgs e)
        {
            var userId = TxtUserId.Text?.Trim();
            var tier = (CmbTier.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "free";
            var amount = TxtAmount.Text ?? "9.99";

            if (string.IsNullOrEmpty(userId))
            {
                TxtStatus.Text = "Error: User ID required";
                return;
            }

            try
            {
                TxtStatus.Text = "Sending webhook...";
                var http = new HttpClient();
                var payload = new { user_id = userId, tier = tier, amount = double.Parse(amount), status = "completed" };
                var resp = await http.PostAsJsonAsync(ApiConfig.GetFullUrl("subscriptions/webhook"), payload);
                if (resp.IsSuccessStatusCode)
                {
                    TxtStatus.Text = $"Success: {tier} tier set for {userId}";
                }
                else
                {
                    TxtStatus.Text = $"Failed: {resp.StatusCode}";
                }
            }
            catch (Exception ex)
            {
                TxtStatus.Text = "Error: " + ex.Message;
            }
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
        }
    }
}
