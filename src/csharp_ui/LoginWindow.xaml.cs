using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using System.Windows;
using TradeSensei.UI.Auth;

namespace TradeSensei.UI
{
    public partial class LoginWindow : Window
    {
        private readonly HttpClient http = new HttpClient();

        public LoginWindow()
        {
            InitializeComponent();
        }

        private void BtnCancel_Click(object sender, RoutedEventArgs e)
        {
            this.DialogResult = false;
            this.Close();
        }

        private async void BtnSignin_Click(object sender, RoutedEventArgs e)
        {
            BtnSignin.IsEnabled = false;
            var email = TxtEmail.Text?.Trim();
            var pwd = TxtPassword.Password ?? "";
            if (string.IsNullOrEmpty(email) || string.IsNullOrEmpty(pwd))
            {
                MessageBox.Show("Enter email and password", "Sign In", MessageBoxButton.OK, MessageBoxImage.Warning);
                BtnSignin.IsEnabled = true;
                return;
            }

            try
            {
                var payload = new { email = email, password = pwd };
                var resp = await http.PostAsJsonAsync(ApiConfig.GetFullUrl("auth/signin"), payload);
                if (!resp.IsSuccessStatusCode)
                {
                    MessageBox.Show($"Sign-in failed: {resp.StatusCode}", "Sign In", MessageBoxButton.OK, MessageBoxImage.Error);
                    BtnSignin.IsEnabled = true;
                    return;
                }

                var data = await resp.Content.ReadFromJsonAsync<System.Text.Json.JsonElement>();
                if (data.TryGetProperty("ok", out var ok) && ok.GetBoolean())
                {
                    var userId = data.GetProperty("user_id").GetString();
                    var token = data.GetProperty("access_token").GetString();
                    AuthState.UserId = userId;
                    AuthState.AccessToken = token;
                    this.DialogResult = true;
                    this.Close();
                    return;
                }

                var reason = data.TryGetProperty("reason", out var r) ? r.GetString() : "unknown";
                MessageBox.Show($"Sign-in failed: {reason}", "Sign In", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Sign-in error: " + ex.Message, "Sign In", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                BtnSignin.IsEnabled = true;
            }
        }
    }
}
