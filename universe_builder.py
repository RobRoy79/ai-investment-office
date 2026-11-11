
"""
AI Investment Office
Dynamic Investment Universe – Version 1.0

Finds additional stock candidates using Yahoo Finance screeners.
This module does not make investment recommendations or execute trades.
"""

import yfinance as yf


# --------------------------------------------------
# SCREENER SETTINGS
# --------------------------------------------------

SCREENERS = [
    "small_cap_gainers",
    "growth_technology_stocks",
    "undervalued_growth_stocks",
]


# --------------------------------------------------
# EXTRACT STOCKS FROM YAHOO FINANCE
# --------------------------------------------------

def extract_candidates(response):

    candidates = {}

    if not isinstance(response, dict):
        return candidates

    quotes = response.get("quotes", [])

    if not isinstance(quotes, list):
        return candidates

    for item in quotes:

        if not isinstance(item, dict):
            continue

        symbol = item.get("symbol")

        if not symbol:
            continue

        name = (
            item.get("shortName")
            or item.get("longName")
            or symbol
        )

        candidates[str(symbol)] = str(name)

    return candidates


# --------------------------------------------------
# BUILD DYNAMIC INVESTMENT UNIVERSE
# --------------------------------------------------

def build_discovery_universe(
    base_universe=None,
    max_per_screen=20
):

    universe = dict(base_universe or {})

    initial_count = len(universe)

    screen_results = {}
    errors = []

    max_per_screen = max(
        1,
        min(int(max_per_screen), 100)
    )

    for screen_name in SCREENERS:

        try:

            response = yf.screen(
                screen_name,
                count=max_per_screen
            )

            candidates = extract_candidates(response)

            screen_results[screen_name] = len(candidates)

            universe.update(candidates)

        except Exception as error:

            screen_results[screen_name] = 0

            errors.append({
                "screen": screen_name,
                "error": str(error)
            })

    new_candidates = len(universe) - initial_count

    return {
        "universe": universe,
        "initial_count": initial_count,
        "total_count": len(universe),
        "new_candidates": new_candidates,
        "screen_results": screen_results,
        "errors": errors,
        "status": "DYNAMIC DISCOVERY - PAPER ANALYSIS ONLY"
    }
