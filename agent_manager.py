
"""
AI Investment Office
Agent Manager

Coordinates the technical and news analysis agents.
This version uses rule-based analysis, not a live AI model.
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

    # Run technical analysis
    technical = generate_signal(
        current_price=current_price,
        sma20=sma20,
        sma50=sma50
    )

    # Analyze available news headlines
    news_results = [
        analyze_news(headline)
        for headline in headlines
    ]

    news_score = sum(
        item["score"] for item in news_results
    )

    # Combine technical and news scores
    combined_score = technical["score"] + news_score

    if combined_score >= 2:
        recommendation = "BUY"
    elif combined_score <= -2:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    return {
        "ticker": ticker.upper(),
        "recommendation": recommendation,
        "technical_signal": technical["signal"],
        "technical_score": technical["score"],
        "news_score": news_score,
        "combined_score": combined_score,
        "news_analysis": news_results,
        "explanation": (
            "Recommendation combines technical indicators "
            "and simple keyword-based news analysis."
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
