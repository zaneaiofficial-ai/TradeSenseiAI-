import cv2
import numpy as np

# Vision pipeline simple implementation (prototype)
# - Finds the largest contour in the screenshot and returns its center as a POI
# - Later replacements will include candle parsing, liquidity, BOS/CHoCH, etc.


def detect_chart_features(frame):
    """Run a basic OpenCV analysis on BGR frame and return detected features.

    Returns a dict with keys: 'poi' (x,y) or None, 'candles' list, 'zones' list
    """
    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return {'poi': (w // 2, h // 2), 'candles': [], 'zones': []}

    import cv2
    import numpy as np


    # Vision pipeline extended prototype
    # - Extracts a rough "price series" by finding strong edge/contrast rows per x-column
    # - Computes simple indicators: short/long SMA, linear regression slope (trend)
    # - Returns features useful for the prototype trading advisor


    def _extract_price_series(frame, downsample=1):
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Enhance edges
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        series = []
        # For each x, find the y with the strongest edge response (sum over small vertical window)
        for x in range(0, w, downsample):
            column = edges[:, x]
            # smooth column to avoid noise
            col_blur = cv2.GaussianBlur(column.reshape(-1, 1), (7, 1), 0).flatten()
            # take index of maximum response
            idx = int(np.argmax(col_blur))
            series.append(idx)

        return series


    def _sma(series, period):
        if len(series) < period:
            return []
        res = []
        cum = 0.0
        for i, v in enumerate(series):
            cum += v
            if i >= period:
                cum -= series[i - period]
            if i >= period - 1:
                res.append(cum / period)
        return res


    def _linear_slope(series):
        # Compute slope of series using linear regression (y ~ ax + b)
        n = len(series)
        if n < 2:
            return 0.0
        x = np.arange(n)
        y = np.array(series)
        x_mean = x.mean()
        y_mean = y.mean()
        num = ((x - x_mean) * (y - y_mean)).sum()
        den = ((x - x_mean) ** 2).sum()
        if den == 0:
            return 0.0
        a = num / den
        return float(a)


    def detect_chart_features(frame):
        """Analyze frame and return prototype features.

        Returned dict keys:
          - 'poi': (x,y) last visible price location
          - 'price_series': list of y positions (int)
          - 'sma_short': list of SMA values (aligned to series index period-1)
          - 'sma_long': list of SMA values
          - 'slope': linear slope of the recent series
        """
        h, w = frame.shape[:2]
        series = _extract_price_series(frame, downsample=2)
        if not series:
            return {'poi': (w // 2, h // 2), 'price_series': [], 'sma_short': [], 'sma_long': [], 'slope': 0.0}

        # Normalize series length
        # Map series x index to screen x
        last_x = (len(series) - 1) * 2
        last_y = series[-1]

        # Simple SMAs on the series (use period in samples)
        sma_short = _sma(series, max(3, int(len(series) * 0.03)))
        sma_long = _sma(series, max(8, int(len(series) * 0.10)))

        slope = _linear_slope(series[-min(len(series), 60):])

        features = {
            'poi': (int(last_x), int(last_y)),
            'price_series': series,
            'sma_short': sma_short,
            'sma_long': sma_long,
            'slope': slope,
        }
        return features
