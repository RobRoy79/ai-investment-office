

"""
AI Investment Office
Signal Engine

Combines technical indicators into a simple signal.
Research and paper trading only.
No real orders are placed.
"""


def generate_signal(
    current_price: float,
    sma20: float,
    sma50: float
) -> dict:
    """
    Generates a basic technical trading signal.

    Returns BUY, SELL or HOLD.
    This is rule-based analysis, not an AI prediction.
    """

    # Validate market data
    try:
        current_price = float(current_price)
        sma20 = float(sma20)
        sma50 = float(sma50)
    except (TypeError, ValueError):
        return {
            "signal": "HOLD",
            "strength": 0,
            "score": 0,
            "reason": "Market data must be numeric."
        }

    if current_price <= 0 or sma20 <= 0 or sma50 <= 0:
        return {
            "signal": "HOLD",
            "strength": 0,
            "score": 0,
            "reason": "Invalid market data."
        }

    score = 0
    reasons = []

    # Compare current price with the 20-day average
    if current_price > sma20:
        score += 1
        reasons.append("Price is above SMA20.")
    elif current_price < sma20:
        score -= 1
        reasons.append("Price is below SMA20.")

    # Compare short-term and long-term averages
    if sma20 > sma50:
        score += 1
        reasons.append("SMA20 is above SMA50.")
    elif sma20 < sma50:
        score -= 1
        reasons.append("SMA20 is below SMA50.")

    if score == 2:
        signal = "BUY"
    elif score == -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    strength = abs(score) * 50

    return {
        "signal": signal,
        "strength": strength,
        "score": score,
        "reason": " ".join(reasons)
    }


if __name__ == "__main__":

    result = generate_signal(
        current_price=110,
        sma20=105,
        sma50=100
    )

    print("AI INVESTMENT OFFICE - SIGNAL ENGINE")
    print(result)
