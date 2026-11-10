
import yfinance as yf
import pandas as pd


def get_stock_data(symbol, period="6mo"):
    """
    Download historical stock prices.
    Example Swedish ticker: VOLV-B.ST
    """

    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)

        if data.empty:
            return None

        data = data.dropna(subset=["Close"])

        return data

    except Exception as error:
        print(f"Could not retrieve stock data: {error}")
        return None


def get_latest_price(symbol):
    data = get_stock_data(symbol, period="5d")

    if data is None or data.empty:
        return None

    return float(data["Close"].iloc[-1])


def get_closing_prices(symbol, period="6mo"):
    data = get_stock_data(symbol, period)

    if data is None or data.empty:
        return []

    return data["Close"].astype(float).tolist()
