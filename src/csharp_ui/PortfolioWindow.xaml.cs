using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

namespace TradeSensei.UI
{
    public partial class PortfolioWindow : Window
    {
        private string _userId = string.Empty;
        private string _apiBaseUrl = string.Empty;

        public PortfolioWindow()
        {
            InitializeComponent();
        }

        public void Initialize(string userId, string apiBaseUrl)
        {
            _userId = userId;
            _apiBaseUrl = apiBaseUrl;
            LoadPortfolio();
        }

        private async void LoadPortfolio()
        {
            try
            {
                using var client = new HttpClient();
                
                // Load positions
                var response = await client.GetAsync($"{_apiBaseUrl}/portfolio/{_userId}");
                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    var doc = JsonDocument.Parse(json);
                    
                    var positions = doc.RootElement.GetProperty("positions");
                    PositionsListBox.Items.Clear();
                    
                    foreach (var pos in positions.EnumerateArray())
                    {
                        var symbol = pos.GetProperty("symbol").GetString();
                        var side = pos.GetProperty("side").GetString();
                        var qty = pos.GetProperty("quantity").GetDouble();
                        var entry = pos.GetProperty("entry_price").GetDouble();
                        var sl = pos.GetProperty("stop_loss").GetDouble();
                        var tp = pos.GetProperty("take_profit").GetDouble();
                        
                        PositionsListBox.Items.Add($"{side.ToUpper()} {qty} {symbol} @ ${entry:F2} | SL: ${sl:F2} | TP: ${tp:F2}");
                    }
                    
                    // Load stats
                    var stats = doc.RootElement.GetProperty("stats");
                    UpdateStats(stats);
                }
                
                // Load portfolio stats separately
                var statsResponse = await client.GetAsync($"{_apiBaseUrl}/portfolio/stats/{_userId}");
                if (statsResponse.IsSuccessStatusCode)
                {
                    var json = await statsResponse.Content.ReadAsStringAsync();
                    var doc = JsonDocument.Parse(json);
                    UpdateStats(doc.RootElement);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading portfolio: {ex.Message}");
            }
        }

        private void UpdateStats(JsonElement stats)
        {
            try
            {
                var openPos = stats.TryGetProperty("open_positions", out var op) ? op.GetInt32() : 0;
                var longPos = stats.TryGetProperty("long_positions", out var lp) ? lp.GetInt32() : 0;
                var shortPos = stats.TryGetProperty("short_positions", out var sp) ? sp.GetInt32() : 0;
                var totalTrades = stats.TryGetProperty("total_trades", out var tt) ? tt.GetInt32() : 0;
                var winRate = stats.TryGetProperty("win_rate", out var wr) ? wr.GetDouble() : 0;
                var totalPnL = stats.TryGetProperty("total_pnl", out var tp) ? tp.GetDouble() : 0;
                var profitFactor = stats.TryGetProperty("profit_factor", out var pf) ? pf.GetDouble() : 0;

                TxtOpenPositions.Text = openPos.ToString();
                TxtLongPositions.Text = longPos.ToString();
                TxtShortPositions.Text = shortPos.ToString();
                TxtTotalTrades.Text = totalTrades.ToString();
                TxtWinRate.Text = $"{winRate:F1}%";
                TxtTotalPnL.Text = $"${totalPnL:F2}";
                TxtProfitFactor.Text = profitFactor.ToString("F2");
            }
            catch { }
        }

        private async void BtnAddPosition_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(TxtSymbol.Text) || 
                string.IsNullOrWhiteSpace(TxtEntryPrice.Text) ||
                string.IsNullOrWhiteSpace(TxtQuantity.Text) ||
                string.IsNullOrWhiteSpace(TxtStopLoss.Text) ||
                string.IsNullOrWhiteSpace(TxtTakeProfit.Text))
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
                    entry_price = double.Parse(TxtEntryPrice.Text),
                    quantity = double.Parse(TxtQuantity.Text),
                    side = ((ComboBoxItem)CmbSide.SelectedItem).Content.ToString().ToLower(),
                    stop_loss = double.Parse(TxtStopLoss.Text),
                    take_profit = double.Parse(TxtTakeProfit.Text)
                };

                using var client = new HttpClient();
                var json = JsonSerializer.Serialize(payload);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
                var response = await client.PostAsync($"{_apiBaseUrl}/portfolio/add-position", content);

                if (response.IsSuccessStatusCode)
                {
                    MessageBox.Show("Position added!");
                    ClearPositionFields();
                    LoadPortfolio();
                }
                else
                {
                    MessageBox.Show("Failed to add position");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

        private void ClearPositionFields()
        {
            TxtSymbol.Clear();
            TxtEntryPrice.Clear();
            TxtQuantity.Clear();
            TxtStopLoss.Clear();
            TxtTakeProfit.Clear();
            CmbSide.SelectedIndex = 0;
        }

        private void BtnRefresh_Click(object sender, RoutedEventArgs e)
        {
            LoadPortfolio();
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }
    }
}
