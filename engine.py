
"""
AI Investment Office
Core investment engine - Version 1.0

Initial paper-trading engine.
No real orders are placed.
"""

from dataclasses import dataclass


@dataclass
class StockAnalysis:
    symbol: str
    price: float
    sma_short: float
    sma_long: float
    signal: str
    confidence: str


def calculate_average(prices, period):
    if len(prices) < period:
        raise ValueError("Not enough price data")

    return sum(prices[-period:]) / period


def analyze_stock(symbol, prices):
    if len(prices) < 50:
        raise ValueError("At least 50 prices are required")

    if any(price <= 0 for price in prices):
        raise ValueError("Prices must be positive")

    short_average = calculate_average(prices, 20)
    long_average = calculate_average(prices, 50)

    current_price = prices[-1]

    if short_average > long_average and current_price > short_average:
        signal = "BUY"
        confidence = "Medium"

    elif short_average < long_average and current_price < short_average:
        signal = "SELL"
        confidence = "Medium"

    else:
        signal = "HOLD"
        confidence = "Low"

    return StockAnalysis(
        symbol=symbol,
        price=current_price,
        sma_short=round(short_average, 2),
        sma_long=round(long_average, 2),
        signal=signal,
        confidence=confidence
    )


def calculate_position_size(capital, risk_percent, entry_price, stop_price):
    if capital <= 0 or entry_price <= 0:
        raise ValueError("Capital and entry price must be positive")

    if not 0 < risk_percent <= 100:
        raise ValueError("Risk percent must be between 0 and 100")

    risk_per_share = entry_price - stop_price

    if risk_per_share <= 0:
        raise ValueError("Stop price must be below entry price")

    risk_amount = capital * (risk_percent / 100)

    shares = int(risk_amount / risk_per_share)

    return shares


def main():
    print("AI INVESTMENT OFFICE")
    print("Investment engine initialized.")
    print("Mode: PAPER TRADING")
    print("Real trading: DISABLED")


if __name__ == "__main__":
    main()
