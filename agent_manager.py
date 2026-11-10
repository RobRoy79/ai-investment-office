

"""
AI Investment Office
Agent Manager

Coordinates technical and news analysis.
Rule-based research only.
No live AI model or real broker orders.
"""

import math

from signal_engine import generate_signal
from news_analyzer import analyze_news


def run_analysis(
    ticker: str,
    current_price: float,
    sma20: float,
    sma50: float,
    headlines: list
) -> dict:

    if not isinstance(ticker, str) or not ticker.strip():
        return {
            "success": False,
            "recommendation": "HOLD",
            "explanation": "A valid ticker is required.",
            "status": "RESEARCH ONLY - NOT A REAL ORDER"
        }

    ticker = ticker.strip().upper()

    # Validate market data before analysis
    try:
        prices = [
            float(current_price),
            float(sma20),
            float(sma50)
        ]

        if any(
            not math.isfinite(value) or value <= 0
            for value in prices
        ):
            raise ValueError("Invalid prices")

    except (TypeError, ValueError):
        return {
            "success": False,
            "ticker": ticker,
            "recommendation": "HOLD",
            "explanation": "Market data is invalid.",
            "status": "RESEARCH ONLY - NOT A REAL ORDER"
        }

    current_price, sma20, sma50 = prices

    technical = generate_signal(
        current_price=current_price,
        sma20=sma20,
        sma50=sma50
    )

    # Analyze valid news headlines only
    if not isinstance(headlines, list):
        headlines = []

    news_results = [
        analyze_news(headline)
        for headline in headlines
        if isinstance(headline, str) and headline.strip()
    ]

    raw_news_score = sum(
        item["score"] for item in news_results
    )

    # Prevent many headlines from dominating the analysis
    news_score = max(-2, min(2, raw_news_score))

    combined_score = technical["score"] + news_score

    if combined_score >= 2:
        recommendation = "BUY"
    elif combined_score <= -2:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    return {
        "success": True,
        "ticker": ticker,
        "recommendation": recommendation,
        "technical_signal": technical["signal"],
        "technical_score": technical["score"],
        "technical_strength": technical["strength"],
        "news_score": news_score,
        "combined_score": combined_score,
        "news_analysis": news_results,
        "explanation": (
            "Combines technical indicators and keyword-based "
            "news analysis. News influence is limited. "
            "This is not an AI prediction or guaranteed result."
        ),
        "status": "RESEARCH ONLY - NOT A REAL ORDER"
    }


if __name__ == "__main__":

    result = run_analysis(
        ticker="EXAMPLE",
        current_price=110,
        sma20=105,
        sma50=100,
        headlines=[
            "Company reports strong results",
            "Company announces expansion"
        ]
    )

    print("AI INVESTMENT OFFICE - AGENT MANAGER")
    print(result)

