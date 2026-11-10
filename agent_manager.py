
"""
AI Investment Office
Agent Manager

Coordinates technical and news analysis.
Rule-based research only.
No live AI model or real broker orders.
"""

from signal_engine import generate_signal
from news_analyzer import analyze_news


def run_analysis(
    ticker: str,
    current_price: float,
    sma20: float,
    sma50: float,
    headlines: list
) -> dict:
    """Combines technical signals and news analysis."""

    if not isinstance(ticker, str) or not ticker.strip():
        return {
            "success": False,
            "recommendation": "HOLD",
            "reason": "A valid ticker is required.",
            "status": "RESEARCH ONLY - NOT A REAL ORDER"
        }

    if not isinstance(headlines, list):
        headlines = []

    ticker = ticker.strip().upper()

    # Technical analysis
    technical = generate_signal(
        current_price=current_price,
        sma20=sma20,
        sma50=sma50
    )

    # Never issue BUY or SELL if market data is invalid
    if technical["score"] == 0 and technical["strength"] == 0:
        return {
            "success": False,
            "ticker": ticker,
            "recommendation": "HOLD",
            "technical_signal": "HOLD",
            "technical_score": 0,
            "news_score": 0,
            "combined_score": 0,
            "news_analysis": [],
            "explanation": (
                "Technical analysis could not be completed. "
                "News cannot override invalid market data."
            ),
            "status": "RESEARCH ONLY - NOT A REAL ORDER"
        }

    # News analysis
    news_results = []

    for headline in headlines:
        if isinstance(headline, str) and headline.strip():
            news_results.append(analyze_news(headline))

    news_score = sum(
        item["score"] for item in news_results
    )

    combined_score = technical["score"] + news_score

    # Combined recommendation
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
            "Recommendation combines technical indicators "
            "and simple keyword-based news analysis. "
            "It is not a guaranteed prediction."
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

