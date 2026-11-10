
"""
AI Investment Office
News Analyzer

First version: prepares and scores financial news.
AI interpretation will be connected later.
"""

POSITIVE_KEYWORDS = [
    "growth",
    "profit",
    "strong results",
    "upgrade",
    "partnership",
    "expansion",
    "beat expectations",
    "positive outlook"
]

NEGATIVE_KEYWORDS = [
    "loss",
    "decline",
    "fraud",
    "investigation",
    "downgrade",
    "debt crisis",
    "miss expectations",
    "bankruptcy"
]


def analyze_news(headline: str, summary: str = "") -> dict:
    text = f"{headline} {summary}".lower()

    positive_hits = [
        word for word in POSITIVE_KEYWORDS
        if word in text
    ]

    negative_hits = [
        word for word in NEGATIVE_KEYWORDS
        if word in text
    ]

    score = len(positive_hits) - len(negative_hits)

    if score > 0:
        sentiment = "POSITIVE"
    elif score < 0:
        sentiment = "NEGATIVE"
    else:
        sentiment = "NEUTRAL"

    return {
        "sentiment": sentiment,
        "score": score,
        "positive_terms": positive_hits,
        "negative_terms": negative_hits,
        "headline": headline,
        "warning": (
            "Keyword analysis only. "
            "This is not a full AI news interpretation."
        )
    }


if __name__ == "__main__":
    example = analyze_news(
        "Company reports strong results",
        "Profit growth exceeded expectations."
    )

    print("AI INVESTMENT OFFICE - NEWS ANALYZER")
    print(example)
