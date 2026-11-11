"""
AI Investment Office
Fundamental Analyzer – Version 1.0

Analyses company fundamentals using Yahoo Finance data.
Research and paper analysis only. No real trades.
"""

import yfinance as yf


def safe_number(value):
    """Convert a value to a usable number, or return None."""
    try:
        if value is None:
            return None

        number = float(value)

        if number != number:
            return None

        return number
    except (TypeError, ValueError):
        return None


def score_quality(info):
    """Evaluate the financial quality of a company."""
    score = 0
    reasons = []

    roe = safe_number(info.get("returnOnEquity"))
    profit_margin = safe_number(info.get("profitMargins"))
    revenue_growth = safe_number(info.get("revenueGrowth"))
    debt_to_equity = safe_number(info.get("debtToEquity"))
    operating_margin = safe_number(info.get("operatingMargins"))

    if roe is not None:
        if roe >= 0.20:
            score += 25
            reasons.append("Strong return on equity")
        elif roe >= 0.10:
            score += 15
            reasons.append("Good return on equity")
        elif roe > 0:
            score += 5

    if profit_margin is not None:
        if profit_margin >= 0.20:
            score += 20
            reasons.append("High profit margin")
        elif profit_margin >= 0.10:
            score += 12
        elif profit_margin > 0:
            score += 5

    if revenue_growth is not None:
        if revenue_growth >= 0.15:
            score += 20
            reasons.append("Strong revenue growth")
        elif revenue_growth >= 0.05:
            score += 12
        elif revenue_growth > 0:
            score += 5

    if debt_to_equity is not None:
        if debt_to_equity < 50:
            score += 20
            reasons.append("Low debt level")
        elif debt_to_equity < 100:
            score += 12
        elif debt_to_equity > 200:
            score -= 10
            reasons.append("High debt level")

    if operating_margin is not None:
        if operating_margin >= 0.20:
            score += 15
            reasons.append("Strong operating margin")
        elif operating_margin >= 0.10:
            score += 10
        elif operating_margin > 0:
            score += 5

    return max(0, min(100, score)), reasons


def score_valuation(info):
    """Evaluate whether a company appears reasonably valued."""
    score = 0
    reasons = []

    pe = safe_number(info.get("trailingPE"))
    forward_pe = safe_number(info.get("forwardPE"))
    price_to_sales = safe_number(info.get("priceToSalesTrailing12Months"))
    peg = safe_number(info.get("pegRatio"))

    if forward_pe is not None and forward_pe > 0:
        if forward_pe < 15:
            score += 30
            reasons.append("Attractive forward P/E")
        elif forward_pe < 25:
            score += 20
        elif forward_pe < 35:
            score += 10

    elif pe is not None and pe > 0:
        if pe < 15:
            score += 30
            reasons.append("Attractive P/E")
        elif pe < 25:
            score += 20
        elif pe < 35:
            score += 10

    if price_to_sales is not None and price_to_sales > 0:
        if price_to_sales < 3:
            score += 25
            reasons.append("Reasonable price-to-sales ratio")
        elif price_to_sales < 6:
            score += 15
        elif price_to_sales < 10:
            score += 5

    if peg is not None and peg > 0:
        if peg < 1:
            score += 25
            reasons.append("Attractive PEG ratio")
        elif peg < 2:
            score += 15
        elif peg < 3:
            score += 5

    if pe is not None and pe <= 0:
        reasons.append("Company currently has negative earnings")

    return max(0, min(100, score)), reasons


def analyze_fundamentals(symbol):
    """Retrieve and analyse fundamental data for one stock."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}

        if not info:
            return {
                "symbol": symbol,
                "company": symbol,
                "error": "No fundamental data available."
            }

        quality_score, quality_reasons = score_quality(info)
        valuation_score, valuation_reasons = score_valuation(info)

        fundamental_score = round(
            (quality_score * 0.60) + (valuation_score * 0.40)
        )

        if fundamental_score >= 75:
            recommendation = "Strong fundamentals"
        elif fundamental_score >= 60:
            recommendation = "Positive fundamentals"
        elif fundamental_score >= 40:
            recommendation = "Mixed fundamentals"
        else:
            recommendation = "Weak fundamentals"

        return {
            "symbol": symbol,
            "company": info.get("longName") or info.get("shortName") or symbol,
            "fundamental_score": fundamental_score,
            "quality_score": quality_score,
            "valuation_score": valuation_score,
            "recommendation": recommendation,
            "currency": info.get("currency"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": safe_number(info.get("marketCap")),
            "trailing_pe": safe_number(info.get("trailingPE")),
            "forward_pe": safe_number(info.get("forwardPE")),
            "profit_margin": safe_number(info.get("profitMargins")),
            "revenue_growth": safe_number(info.get("revenueGrowth")),
            "return_on_equity": safe_number(info.get("returnOnEquity")),
            "debt_to_equity": safe_number(info.get("debtToEquity")),
            "quality_reasons": quality_reasons,
            "valuation_reasons": valuation_reasons,
            "error": None
        }

    except Exception as error:
        return {
            "symbol": symbol,
            "company": symbol,
            "error": str(error)
        }


def analyze_multiple_fundamentals(symbols):
    """Analyse several stocks and return their results."""
    results = []

    for symbol in symbols:
        result = analyze_fundamentals(symbol)
        results.append(result)

    return results