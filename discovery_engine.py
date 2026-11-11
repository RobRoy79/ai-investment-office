
"""
AI Investment Office
Discovery Engine – Version 2.0

Dynamic stock discovery and technical candidate ranking.
Paper analysis only. No real trades.
"""

import pandas as pd
import numpy as np

from market_data import get_stock_data
from universe_builder import build_discovery_universe


# --------------------------------------------------
# ORIGINAL WATCHLIST
# --------------------------------------------------

DEFAULT_UNIVERSE = {
    # Sweden
    "VOLV-B.ST": "Volvo",
    "ATCO-A.ST": "Atlas Copco",
    "ASSA-B.ST": "Assa Abloy",
    "ABB.ST": "ABB",
    "ERIC-B.ST": "Ericsson",
    "SEB-A.ST": "SEB",
    "SWED-A.ST": "Swedbank",
    "INVE-B.ST": "Investor",
    "SAND.ST": "Sandvik",
    "EVO.ST": "Evolution",

    # United States
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "META": "Meta",
    "AAPL": "Apple",
    "AVGO": "Broadcom",
    "AMD": "AMD",
    "JPM": "JPMorgan",
    "LLY": "Eli Lilly",
    "COST": "Costco",
    "TSLA": "Tesla",

    # Europe
    "ASML.AS": "ASML",
    "SAP.DE": "SAP",
    "MC.PA": "LVMH",
    "RMS.PA": "Hermes",
    "NOVO-B.CO": "Novo Nordisk",
    "NESN.SW": "Nestle",
    "SIE.DE": "Siemens",
    "SU.PA": "Schneider Electric",
}


# --------------------------------------------------
# RSI CALCULATION
# --------------------------------------------------

def calculate_rsi(prices, period=14):

    delta = prices.diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    average_gain = gains.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    average_loss = losses.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    relative_strength = (
        average_gain / average_loss.replace(0, np.nan)
    )

    return 100 - (100 / (1 + relative_strength))


# --------------------------------------------------
# ANALYZE ONE STOCK
# --------------------------------------------------

def analyze_candidate(symbol, company_name):

    try:

        data = get_stock_data(symbol, period="6mo")

        if data is None or data.empty:
            return None

        if "Close" not in data.columns:
            return None

        prices = pd.to_numeric(
            data["Close"],
            errors="coerce"
        ).dropna()

        if len(prices) < 60:
            return None

        current_price = float(prices.iloc[-1])

        if current_price <= 0:
            return None

        sma20 = float(prices.rolling(20).mean().iloc[-1])
        sma50 = float(prices.rolling(50).mean().iloc[-1])

        return_20 = (
            current_price / float(prices.iloc[-21]) - 1
        ) * 100

        return_60 = (
            current_price / float(prices.iloc[-60]) - 1
        ) * 100

        rsi = calculate_rsi(prices).iloc[-1]

        if pd.isna(rsi) or pd.isna(sma20) or pd.isna(sma50):
            return None

        daily_returns = prices.pct_change().dropna()

        volatility = float(
            daily_returns.tail(30).std() * np.sqrt(252) * 100
        )

        volume_ratio = None

        if "Volume" in data.columns:

            volumes = pd.to_numeric(
                data["Volume"],
                errors="coerce"
            ).dropna()

            if len(volumes) >= 20:

                average_volume = volumes.tail(20).mean()

                if average_volume > 0:
                    volume_ratio = float(
                        volumes.iloc[-1] / average_volume
                    )

        # ------------------------------------------
        # SCORING
        # ------------------------------------------

        score = 0
        reasons = []

        # Trend
        if current_price > sma50:
            score += 15
            reasons.append("Kurs över 50-dagars medelvärde")

        if sma20 > sma50:
            score += 10
            reasons.append("Positiv trend")

        # Momentum
        if return_20 > 5:
            score += 15
            reasons.append("Starkt momentum på 20 dagar")
        elif return_20 > 0:
            score += 8

        if return_60 > 10:
            score += 15
            reasons.append("Stark utveckling på 60 dagar")
        elif return_60 > 0:
            score += 8

        # RSI
        if 50 <= rsi <= 65:
            score += 15
            reasons.append("Positiv RSI utan extrem nivå")
        elif 45 <= rsi < 50 or 65 < rsi <= 70:
            score += 10
        elif 40 <= rsi < 45 or 70 < rsi <= 75:
            score += 5

        # Volume
        if volume_ratio is not None:

            if 1.2 <= volume_ratio <= 2.5:
                score += 10
                reasons.append("Ökad handelsvolym")

            elif volume_ratio > 1:
                score += 5

        # Volatility
        if volatility < 20:
            score += 20
            reasons.append("Relativt låg volatilitet")

        elif volatility < 30:
            score += 15

        elif volatility < 45:
            score += 10

        elif volatility < 60:
            score += 5

        score = min(score, 100)

        if score >= 75:
            classification = "Hög analysprioritet"

        elif score >= 55:
            classification = "Möjlig kandidat"

        else:
            classification = "Låg prioritet"

        return {
            "symbol": symbol,
            "company": company_name,
            "price": round(current_price, 2),
            "discovery_score": score,
            "classification": classification,
            "return_20d": round(return_20, 2),
            "return_60d": round(return_60, 2),
            "rsi": round(float(rsi), 1),
            "volatility": round(volatility, 2),
            "volume_ratio": (
                round(volume_ratio, 2)
                if volume_ratio is not None else None
            ),
            "reasons": reasons,
        }

    except Exception:
        return None


# --------------------------------------------------
# GLOBAL DISCOVERY SCAN
# --------------------------------------------------

def run_discovery_scan(
    universe=None,
    dynamic_discovery=True,
    max_per_screen=20
):

    base_universe = dict(universe or DEFAULT_UNIVERSE)

    discovery_info = None

    if dynamic_discovery:

        discovery_info = build_discovery_universe(
            base_universe=base_universe,
            max_per_screen=max_per_screen
        )

        selected_universe = discovery_info["universe"]

    else:

        selected_universe = base_universe

    results = []
    errors = []

    for symbol, company_name in selected_universe.items():

        candidate = analyze_candidate(symbol, company_name)

        if candidate is not None:
            results.append(candidate)

        else:
            errors.append(symbol)

    results.sort(
        key=lambda item: item["discovery_score"],
        reverse=True
    )

    return {
        "success": True,
        "scanned": len(selected_universe),
        "successful": len(results),
        "failed": len(errors),
        "candidates": results,
        "errors": errors,
        "discovery_info": discovery_info,
        "message": (
            "Dynamisk marknadsskanning genomförd. "
            "Kandidaterna behöver ytterligare analys."
        ),
        "status": "PAPER ANALYSIS ONLY - NO REAL TRADES",
    }


# --------------------------------------------------
# TOP OPPORTUNITIES
# --------------------------------------------------

def get_top_opportunities(limit=10):

    result = run_discovery_scan()

    return result["candidates"][:limit]

