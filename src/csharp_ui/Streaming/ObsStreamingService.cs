using System;
using System.Drawing;
using System.IO;
using System.Threading.Tasks;

namespace TradeSensei.UI.Streaming
{
    /// <summary>
    /// OBS/Virtual Camera integration for streaming overlay to OBS or other streaming software.
    /// This module provides frame serialization and streaming endpoints.
    /// </summary>
    public class ObsStreamingService
    {
        private string? outputPath;
        private bool isStreaming;
        private int frameCount;

        public bool IsStreaming => isStreaming;
        public int FrameCount => frameCount;

        public ObsStreamingService(string? obsOutputPath = null)
        {
            outputPath = obsOutputPath ?? Path.Combine(Path.GetTempPath(), "TradeSensei_OBS_Stream");
            Directory.CreateDirectory(outputPath);
        }

        /// <summary>
        /// Start streaming frames to OBS output directory or named pipe.
        /// </summary>
        public void StartStreaming()
        {
            isStreaming = true;
            frameCount = 0;
        }

        /// <summary>
        /// Stop streaming.
        /// </summary>
        public void StopStreaming()
        {
            isStreaming = false;
        }

        /// <summary>
        /// Write a frame to the OBS output (as PNG or to streaming pipe).
        /// Simulates sending to OBS VirtualCam via file-based interchange.
        /// </summary>
        public async Task WriteFrameAsync(Bitmap frame)
        {
            if (!isStreaming || frame == null) return;

            try
            {
                var framePath = Path.Combine(outputPath ?? "", $"frame_{frameCount:D6}.png");
                frame.Save(framePath, System.Drawing.Imaging.ImageFormat.Png);
                frameCount++;

                // Optional: Keep only the last N frames to avoid disk bloat
                if (frameCount % 100 == 0)
                {
                    var oldFiles = Directory.GetFiles(outputPath ?? "", "frame_*.png");
                    if (oldFiles.Length > 50)
                    {
                        Array.Sort(oldFiles);
                        for (int i = 0; i < oldFiles.Length - 50; i++)
                        {
                            try { File.Delete(oldFiles[i]); }
                            catch { }
                        }
                    }
                }

                await Task.CompletedTask;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"OBS streaming error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get the output directory path for OBS to monitor.
        /// </summary>
        public string GetOutputPath()
        {
            return outputPath ?? "";
        }

        /// <summary>
        /// Get latest frame for preview or other uses.
        /// </summary>
        public string? GetLatestFramePath()
        {
            if (!Directory.Exists(outputPath)) return null;
            var files = Directory.GetFiles(outputPath, "frame_*.png");
            if (files.Length == 0) return null;
            Array.Sort(files);
            return files[^1];
        }
    }
}
