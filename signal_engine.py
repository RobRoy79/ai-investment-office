
"""
AI Investment Office
Signal Engine

Combines technical indicators into a simple signal.
This is a research signal, not a guaranteed prediction.
"""

def generate_signal(
    current_price: float,
    sma20: float,
    sma50: float
) -> dict:

    if current_price <= 0 or sma20 <= 0 or sma50 <= 0:
        return {
            "signal": "HOLD",
            "strength": 0,
            "reason": "Invalid market data."
        }

    score = 0
    reasons = []

    if current_price > sma20:
        score += 1
        reasons.append("Price is above SMA20.")
    else:
        score -= 1
        reasons.append("Price is below SMA20.")

    if sma20 > sma50:
        score += 1
        reasons.append("SMA20 is above SMA50.")
    else:
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

    print("AI INVESTMENT OFFICE - SIGNAL")
    print(result)
