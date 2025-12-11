using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Windows;

namespace TradeSensei.UI.Capture
{
    public static class CaptureService
    {
        // Prototype capture implementation (GDI CopyFromScreen).
        // Replace with Desktop Duplication API for production for higher FPS and lower CPU.
        public static Bitmap CapturePrimaryScreen()
        {
            var screenWidth = (int)SystemParameters.PrimaryScreenWidth;
            var screenHeight = (int)SystemParameters.PrimaryScreenHeight;
            var bmp = new Bitmap(screenWidth, screenHeight, PixelFormat.Format24bppRgb);
            using (var g = Graphics.FromImage(bmp))
            {
                g.CopyFromScreen(0, 0, 0, 0, bmp.Size);
            }
            return bmp;
        }
    }
}
