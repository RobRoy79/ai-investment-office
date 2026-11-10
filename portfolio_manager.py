
"""
AI Investment Office
Portfolio Manager

Tracks simulated cash, holdings and portfolio value.
Paper trading only. No real broker transactions.
"""

import csv
import os

TRADE_LOG = "paper_trades.csv"
STARTING_CAPITAL = 10000.0


def load_trades():
    if not os.path.exists(TRADE_LOG):
        return []

    with open(TRADE_LOG, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def calculate_portfolio():
    trades = load_trades()

    cash = STARTING_CAPITAL
    holdings = {}

    for trade in trades:
        ticker = trade["ticker"]
        action = trade["action"]
        quantity = float(trade["quantity"])
        price = float(trade["price"])
        value = quantity * price

        if ticker not in holdings:
            holdings[ticker] = {
                "quantity": 0.0,
                "invested": 0.0
            }

        if action == "BUY":
            if value > cash:
                continue

            cash -= value
            holdings[ticker]["quantity"] += quantity
            holdings[ticker]["invested"] += value

        elif action == "SELL":
            current_quantity = holdings[ticker]["quantity"]

            if quantity > current_quantity:
                continue

            average_cost = (
                holdings[ticker]["invested"] / current_quantity
                if current_quantity > 0 else 0
            )

            holdings[ticker]["quantity"] -= quantity
            holdings[ticker]["invested"] -= average_cost * quantity
            cash += value

    active_holdings = {
        ticker: data
        for ticker, data in holdings.items()
        if data["quantity"] > 0
    }

    return {
        "starting_capital": STARTING_CAPITAL,
        "cash": round(cash, 2),
        "holdings": active_holdings,
        "number_of_positions": len(active_holdings)
    }


if __name__ == "__main__":
    portfolio = calculate_portfolio()

    print("AI INVESTMENT OFFICE - PORTFOLIO")
    print(portfolio)
