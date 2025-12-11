using System;
using System.Windows;
using TradeSensei.UI.Streaming;

namespace TradeSensei.UI
{
    public partial class StreamingWindow : Window
    {
        public ObsStreamingService StreamingService { get; private set; }

        public StreamingWindow()
        {
            InitializeComponent();
            StreamingService = new ObsStreamingService();
            TxtOutputPath.Text = StreamingService.GetOutputPath();
            UpdateStatus();
        }

        private void BtnStart_Click(object sender, RoutedEventArgs e)
        {
            StreamingService.StartStreaming();
            UpdateStatus();
            MessageBox.Show("Streaming started. Frames will be written to the output path.\nAdd an Image Sequence source in OBS to monitor this folder.", "Streaming", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void BtnStop_Click(object sender, RoutedEventArgs e)
        {
            StreamingService.StopStreaming();
            UpdateStatus();
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            if (StreamingService.IsStreaming)
            {
                StreamingService.StopStreaming();
            }
            this.Close();
        }

        private void BtnCopyPath_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                System.Windows.Forms.Clipboard.SetText(TxtOutputPath.Text);
                MessageBox.Show("Path copied to clipboard.", "Copy", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Failed to copy: " + ex.Message, "Copy", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void UpdateStatus()
        {
            Dispatcher.Invoke(() =>
            {
                if (StreamingService.IsStreaming)
                {
                    TxtStatus.Text = "Streaming ACTIVE";
                    TxtStatus.Foreground = (System.Windows.Media.Brush)Application.Current.FindResource("AccentBrush");
                }
                else
                {
                    TxtStatus.Text = "Not streaming";
                    TxtStatus.Foreground = (System.Windows.Media.Brush)Application.Current.FindResource("FreeBrush");
                }
                TxtFrameCount.Text = StreamingService.FrameCount.ToString();
            });
        }

        public void RefreshFrameCount()
        {
            Dispatcher.Invoke(UpdateStatus);
        }
    }
}
