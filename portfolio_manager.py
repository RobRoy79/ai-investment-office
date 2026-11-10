
"""
AI Investment Office
Portfolio Manager

Tracks simulated cash, holdings and realized profit/loss.
Paper trading only. No real broker transactions.
"""

import csv
import math
import os

TRADE_LOG = "paper_trades.csv"
STARTING_CAPITAL = 10000.0

FIELDNAMES = [
    "date",
    "action",
    "ticker",
    "asset_type",
    "quantity",
    "price",
    "value",
    "status"
]


def load_trades():
    """Load simulated trades from the CSV file."""

    if not os.path.exists(TRADE_LOG):
        return []

    with open(
        TRADE_LOG, "r", newline="", encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames != FIELDNAMES:
            raise ValueError(
                "Trade log has an unexpected CSV structure."
            )

        return list(reader)


def calculate_portfolio(starting_capital=STARTING_CAPITAL):
    """
    Calculate cash, holdings and realized profit/loss.

    Uses average purchase cost when calculating
    profit or loss on sold units.
    """

    try:
        starting_capital = float(starting_capital)
    except (TypeError, ValueError):
        raise ValueError("Starting capital must be numeric.")

    if (
        not math.isfinite(starting_capital)
        or starting_capital <= 0
    ):
        raise ValueError("Starting capital must be positive.")

    trades = load_trades()

    cash = starting_capital
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

            status = trade["status"].strip()

            if status != "PAPER TRADE - NOT REAL":
                raise ValueError(
                    "Trade is not marked as a paper trade."
                )

            if not ticker or not asset_type:
                raise ValueError(
                    "Missing ticker or asset type."
                )

            if action not in ("BUY", "SELL"):
                raise ValueError("Invalid trade action.")

            if (
                not math.isfinite(quantity)
                or not math.isfinite(price)
            ):
                raise ValueError(
                    "Quantity and price must be finite numbers."
                )

            if quantity <= 0 or price <= 0:
                raise ValueError(
                    "Quantity and price must be positive."
                )

            value = quantity * price

            if not math.isfinite(value):
                raise ValueError("Invalid trade value.")

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

                if value > cash + 0.000001:
                    raise ValueError(
                        "Insufficient cash for this purchase."
                    )

                cash -= value
                position["quantity"] += quantity
                position["invested"] += value

            elif action == "SELL":

                if position["quantity"] <= 0:
                    raise ValueError(
                        "No units available to sell."
                    )

                if quantity > position["quantity"] + 0.000001:
                    raise ValueError(
                        "Not enough units available to sell."
                    )

                average_cost = (
                    position["invested"] / position["quantity"]
                )

                cost_of_sold_units = average_cost * quantity

                realized_profit_loss += (
                    value - cost_of_sold_units
                )

                position["quantity"] -= quantity
                position["invested"] -= cost_of_sold_units

                if abs(position["quantity"]) < 0.000001:
                    position["quantity"] = 0.0
                    position["invested"] = 0.0

                cash += value

        except (KeyError, ValueError, TypeError, AttributeError) as error:

            rejected_trades.append({
                "row": row_number,
                "reason": str(error)
            })

    active_holdings = []

    for data in holdings.values():

        if data["quantity"] > 0:

            active_holdings.append({
                "ticker": data["ticker"],
                "asset_type": data["asset_type"],
                "quantity": round(data["quantity"], 6),
                "invested": round(data["invested"], 2),
                "average_cost": round(
                    data["invested"] / data["quantity"], 2
                )
            })

    total_invested = sum(
        position["invested"]
        for position in active_holdings
    )

    return {
        "starting_capital": round(starting_capital, 2),
        "cash": round(cash, 2),
        "total_invested": round(total_invested, 2),
        "realized_profit_loss": round(
            realized_profit_loss, 2
        ),
        "holdings": active_holdings,
        "number_of_positions": len(active_holdings),
        "rejected_trades": rejected_trades,
        "status": "PAPER TRADING ONLY"
    }


if __name__ == "__main__":

    portfolio = calculate_portfolio()

    print("AI INVESTMENT OFFICE - PORTFOLIO")
    print("--------------------------------")

    print("Starting capital:", portfolio["starting_capital"])
    print("Available cash:", portfolio["cash"])
    print("Invested amount:", portfolio["total_invested"])
    print("Realized profit/loss:", portfolio["realized_profit_loss"])

    print("Number of positions:", portfolio["number_of_positions"])
    print("Holdings:", portfolio["holdings"])
    print("Rejected trades:", portfolio["rejected_trades"])

    print("Status:", portfolio["status"])

