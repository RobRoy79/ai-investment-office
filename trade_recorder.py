
"""
AI Investment Office
Paper Trading Trade Recorder

Records simulated trades only.
Checks available cash and holdings before recording.
Never sends real orders to a broker.
"""

import csv
import math
import os
from datetime import datetime, timezone

from investment_rules import validate_investment
from portfolio_manager import calculate_portfolio

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


def record_paper_trade(
    action: str,
    ticker: str,
    asset_type: str,
    quantity: float,
    price: float,
    isk_eligible: bool,
    available_at_broker: bool,
    is_leveraged: bool = False
) -> dict:
    """Validate and record a simulated trade."""

    if not isinstance(action, str):
        return {"success": False, "message": "Invalid action."}

    if not isinstance(ticker, str) or not isinstance(asset_type, str):
        return {
            "success": False,
            "message": "Ticker and asset type must be text."
        }

    action = action.upper().strip()
    ticker = ticker.upper().strip()
    asset_type = asset_type.lower().strip()

    if action not in ("BUY", "SELL"):
        return {
            "success": False,
            "message": "Action must be BUY or SELL."
        }

    if not ticker or not asset_type:
        return {
            "success": False,
            "message": "Ticker and asset type cannot be empty."
        }

    if (
        isinstance(quantity, bool)
        or isinstance(price, bool)
    ):
        return {
            "success": False,
            "message": "Quantity and price must be numeric."
        }

    try:
        quantity = float(quantity)
        price = float(price)
    except (TypeError, ValueError):
        return {
            "success": False,
            "message": "Quantity and price must be numeric."
        }

    if not math.isfinite(quantity) or not math.isfinite(price):
        return {
            "success": False,
            "message": "Quantity and price must be finite numbers."
        }

    if quantity <= 0 or price <= 0:
        return {
            "success": False,
            "message": "Quantity and price must be positive."
        }

    check = validate_investment(
        asset_type=asset_type,
        isk_eligible=isk_eligible,
        available_at_broker=available_at_broker,
        is_leveraged=is_leveraged
    )

    if not check["approved"]:
        return {
            "success": False,
            "message": check["reason"]
        }

    value = round(quantity * price, 2)

    # Check the existing portfolio before recording the trade.
    try:
        portfolio = calculate_portfolio(STARTING_CAPITAL)
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {
            "success": False,
            "message": f"Could not verify portfolio: {error}"
        }

    if portfolio["rejected_trades"]:
        return {
            "success": False,
            "message": (
                "Existing trade history contains rejected trades. "
                "Resolve them before recording another trade."
            )
        }

    if action == "BUY" and value > portfolio["cash"]:
        return {
            "success": False,
            "message": "Insufficient cash for this purchase."
        }

    if action == "SELL":
        matching_position = next(
            (
                position for position in portfolio["holdings"]
                if position["ticker"] == ticker
                and position["asset_type"] == asset_type
            ),
            None
        )

        if matching_position is None:
            return {
                "success": False,
                "message": "No matching position exists to sell."
            }

        if quantity > matching_position["quantity"]:
            return {
                "success": False,
                "message": "Not enough units available to sell."
            }

    # Check that the CSV file has the expected structure.
    file_exists = os.path.exists(TRADE_LOG)
    write_header = not file_exists or os.path.getsize(TRADE_LOG) == 0

    if file_exists and not write_header:
        try:
            with open(
                TRADE_LOG, "r", newline="", encoding="utf-8"
            ) as file:
                reader = csv.reader(file)
                existing_header = next(reader, [])

            if existing_header != FIELDNAMES:
                return {
                    "success": False,
                    "message": "Trade log has an unexpected CSV header."
                }

        except OSError as error:
            return {
                "success": False,
                "message": f"Could not check trade log: {error}"
            }

    trade = {
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "action": action,
        "ticker": ticker,
        "asset_type": asset_type,
        "quantity": quantity,
        "price": price,
        "value": value,
        "status": "PAPER TRADE - NOT REAL"
    }

    try:
        with open(
            TRADE_LOG, "a", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)

            if write_header:
                writer.writeheader()

            writer.writerow(trade)

        return {
            "success": True,
            "message": "Simulated trade saved successfully.",
            "trade": trade
        }

    except OSError as error:
        return {
            "success": False,
            "message": f"Could not save paper trade: {error}"
        }


if __name__ == "__main__":

    result = record_paper_trade(
        action="BUY",
        ticker="EXAMPLE",
        asset_type="stock",
        quantity=2,
        price=100,
        isk_eligible=True,
        available_at_broker=True
    )

    print("AI INVESTMENT OFFICE - PAPER TRADING")
    print(result)

