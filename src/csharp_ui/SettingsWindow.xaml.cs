using System;
using System.Windows;
using System.Windows.Controls;

namespace TradeSensei.UI
{
    public partial class SettingsWindow : Window
    {
        public int PollInterval { get; private set; }
        public bool AutoStartPolling { get; private set; }
        public string DefaultTier { get; private set; } = string.Empty;
        public bool EnableDevFeatures { get; private set; }

        public SettingsWindow(int currentInterval, bool autoStart, string defaultTier, bool enableDev)
        {
            InitializeComponent();
            TxtInterval.Text = currentInterval.ToString();
            ChkAutoStartPolling.IsChecked = autoStart;
            CmbDefaultTier.SelectedItem = CmbDefaultTier.Items[defaultTier == "pro" ? 1 : (defaultTier == "master" ? 2 : 0)];
            ChkEnableDev.IsChecked = enableDev;
        }

        private void BtnSave_Click(object sender, RoutedEventArgs e)
        {
            if (!int.TryParse(TxtInterval.Text, out var interval) || interval < 5)
            {
                MessageBox.Show("Poll interval must be at least 5 seconds.", "Settings", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            PollInterval = interval;
            AutoStartPolling = ChkAutoStartPolling.IsChecked == true;
            var tierItem = CmbDefaultTier.SelectedItem as ComboBoxItem;
            DefaultTier = tierItem?.Content.ToString() ?? "free";
            EnableDevFeatures = ChkEnableDev.IsChecked == true;
            this.DialogResult = true;
            this.Close();
        }

        private void BtnCancel_Click(object sender, RoutedEventArgs e)
        {
            this.DialogResult = false;
            this.Close();
        }
    }
}
