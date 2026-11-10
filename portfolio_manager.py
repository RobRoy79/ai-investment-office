

"""
AI Investment Office
Portfolio Manager

Tracks simulated cash, holdings and realized profit/loss.
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


def calculate_portfolio(starting_capital=STARTING_CAPITAL):

    if starting_capital <= 0:
        raise ValueError("Starting capital must be positive.")

    trades = load_trades()

    cash = float(starting_capital)
    holdings = {}
    rejected_trades = []
    realized_profit_loss = 0.0

    for row_number, trade in enumerate(trades, start=2):

        try:
            ticker = trade["ticker"].strip().upper()
            asset_type = trade["asset_type"].strip().lower()
            action = trade["action"].strip().upper()
            quantity = float(trade["quantity"])
            price = float(trade["price"])

            if not ticker or not asset_type:
                raise ValueError("Missing ticker or asset type.")

            if action not in ("BUY", "SELL"):
                raise ValueError("Invalid trade action.")

            if quantity <= 0 or price <= 0:
                raise ValueError("Quantity and price must be positive.")

            value = quantity * price
            key = (asset_type, ticker)

            if key not in holdings:
                holdings[key] = {
                    "ticker": ticker,
                    "asset_type": asset_type,
                    "quantity": 0.0,
                    "invested": 0.0
                }

            position = holdings[key]

            if action == "BUY":

                if value > cash:
                    raise ValueError("Insufficient cash for this purchase.")

                cash -= value
                position["quantity"] += quantity
                position["invested"] += value

            elif action == "SELL":

                if quantity > position["quantity"]:
                    raise ValueError("Not enough units to sell.")

                average_cost = (
                    position["invested"] / position["quantity"]
                )

                cost_of_sold_units = average_cost * quantity

                realized_profit_loss += value - cost_of_sold_units

                position["quantity"] -= quantity
                position["invested"] -= cost_of_sold_units
                cash += value

        except (KeyError, ValueError, TypeError) as error:
            rejected_trades.append({
                "row": row_number,
                "reason": str(error)
            })

    active_holdings = [
        {
            "ticker": data["ticker"],
            "asset_type": data["asset_type"],
            "quantity": round(data["quantity"], 6),
            "invested": round(data["invested"], 2),
            "average_cost": round(
                data["invested"] / data["quantity"], 2
            ) if data["quantity"] > 0 else 0
        }
        for data in holdings.values()
        if data["quantity"] > 0
    ]

    total_invested = sum(
        position["invested"] for position in active_holdings
    )

    return {
        "starting_capital": round(starting_capital, 2),
        "cash": round(cash, 2),
        "total_invested": round(total_invested, 2),
        "realized_profit_loss": round(realized_profit_loss, 2),
        "holdings": active_holdings,
        "number_of_positions": len(active_holdings),
        "rejected_trades": rejected_trades
    }


if __name__ == "__main__":

    portfolio = calculate_portfolio()

    print("AI INVESTMENT OFFICE - PORTFOLIO")
    print(portfolio)
