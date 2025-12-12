import pandas as pd

def sma(series: pd.Series, period: int) -> pd.Series:
    """
    Calculates the Simple Moving Average (SMA).
    """
    period = int(period)
    if not isinstance(series, pd.Series):
        raise TypeError("Input 'series' must be a pandas Series.")
    if not isinstance(period, int) or period <= 0:
        raise ValueError("'period' must be a positive integer.")
    return series.rolling(window=period, min_periods=period).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculates the Relative Strength Index (RSI).
    """
    period = int(period)
    if not isinstance(series, pd.Series):
        raise TypeError("Input 'series' must be a pandas Series.")
    if not isinstance(period, int) or period <= 0:
        raise ValueError("'period' must be a positive integer.")
        
    delta = series.diff()
    
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Use exponential moving average for smoothing, which is common for RSI
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# More indicators like EMA, MACD, etc., can be added here as needed.
