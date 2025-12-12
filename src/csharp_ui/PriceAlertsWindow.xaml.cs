using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

namespace TradeSensei.UI
{
    public partial class PriceAlertsWindow : Window
    {
        private string _userId = string.Empty;
        private string _apiBaseUrl = string.Empty;
        private List<Dictionary<string, object>> _alerts = new();

        public PriceAlertsWindow()
        {
            InitializeComponent();
        }

        public void Initialize(string userId, string apiBaseUrl)
        {
            _userId = userId;
            _apiBaseUrl = apiBaseUrl;
            LoadAlerts();
        }

        private async void LoadAlerts()
        {
            try
            {
                using var client = new HttpClient();
                var response = await client.GetAsync($"{_apiBaseUrl}/alerts/{_userId}");
                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    var doc = JsonDocument.Parse(json);
                    var alerts = doc.RootElement.GetProperty("alerts");

                    AlertsListBox.Items.Clear();
                    foreach (var alert in alerts.EnumerateArray())
                    {
                        var symbol = alert.GetProperty("symbol").GetString();
                        var condition = alert.GetProperty("condition").GetString();
                        var price = alert.GetProperty("price").GetDouble();
                        var triggered = alert.GetProperty("triggered").GetBoolean();

                        AlertsListBox.Items.Add(new
                        {
                            Symbol = symbol,
                            Condition = condition,
                            Price = price,
                            Status = triggered ? "✓ TRIGGERED" : "⏳ Active",
                            AlertId = alert.GetProperty("id").GetString()
                        });
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading alerts: {ex.Message}");
            }
        }

        private async void BtnCreateAlert_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(TxtSymbol.Text) || 
                string.IsNullOrWhiteSpace(TxtPrice.Text) ||
                CmbCondition.SelectedItem == null ||
                CmbNotificationType.SelectedItem == null)
            {
                MessageBox.Show("Please fill in all fields");
                return;
            }

            try
            {
                var payload = new
                {
                    user_id = _userId,
                    symbol = TxtSymbol.Text.ToUpper(),
                    condition = ((ComboBoxItem)CmbCondition.SelectedItem).Content.ToString().ToLower(),
                    price = double.Parse(TxtPrice.Text),
                    notification_type = ((ComboBoxItem)CmbNotificationType.SelectedItem).Content.ToString().ToLower()
                };

                using var client = new HttpClient();
                var json = JsonSerializer.Serialize(payload);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
                var response = await client.PostAsync($"{_apiBaseUrl}/alerts/create", content);

                if (response.IsSuccessStatusCode)
                {
                    MessageBox.Show("Alert created successfully!");
                    TxtSymbol.Clear();
                    TxtPrice.Clear();
                    CmbCondition.SelectedIndex = 0;
                    CmbNotificationType.SelectedIndex = 0;
                    LoadAlerts();
                }
                else
                {
                    MessageBox.Show("Failed to create alert");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

        private async void BtnDeleteAlert_Click(object sender, RoutedEventArgs e)
        {
            if (AlertsListBox.SelectedItem == null)
            {
                MessageBox.Show("Please select an alert to delete");
                return;
            }

            var selected = AlertsListBox.SelectedItem as dynamic;
            try
            {
                using var client = new HttpClient();
                var response = await client.DeleteAsync($"{_apiBaseUrl}/alerts/{_userId}/{selected.AlertId}");

                if (response.IsSuccessStatusCode)
                {
                    MessageBox.Show("Alert deleted");
                    LoadAlerts();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

        private async void BtnRefreshPrices_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                PricesListBox.Items.Clear();
                var symbols = new[] { "BTC", "ETH", "XRP", "ADA" };

                foreach (var symbol in symbols)
                {
                    using var client = new HttpClient();
                    var response = await client.GetAsync($"{_apiBaseUrl}/price/{symbol}");
                    if (response.IsSuccessStatusCode)
                    {
                        var json = await response.Content.ReadAsStringAsync();
                        var doc = JsonDocument.Parse(json);
                        var price = doc.RootElement.GetProperty("price").GetDouble();
                        PricesListBox.Items.Add($"{symbol}: ${price:F2}");
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }
    }
}
