

"""
AI Investment Office
Paper Trading Trade Recorder

Records simulated trades only.
Enforces portfolio and position risk limits.
Never sends real orders to a broker.
"""

import csv
import math
import os
from datetime import datetime, timezone

from investment_rules import validate_investment
from portfolio_manager import calculate_portfolio
from risk_manager import RiskSettings

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

RISK_SETTINGS = RiskSettings(
    starting_capital=STARTING_CAPITAL
)


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

    if not all(
        isinstance(flag, bool)
        for flag in (
            isk_eligible,
            available_at_broker,
            is_leveraged
        )
    ):
        return {
            "success": False,
            "message": "Investment verification values must be true or false."
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

    if isinstance(quantity, bool) or isinstance(price, bool):
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

    raw_value = quantity * price

    if not math.isfinite(raw_value):
        return {
            "success": False,
            "message": "Trade value is too large or invalid."
        }

    value = round(raw_value, 2)

    if value <= 0:
        return {
            "success": False,
            "message": "Trade value must be at least 0.01 SEK."
        }

    # Verify investment rules
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

    # Load and verify the current portfolio
    try:
        portfolio = calculate_portfolio(STARTING_CAPITAL)

        cash = portfolio["cash"]
        total_invested = portfolio["total_invested"]
        holdings = portfolio["holdings"]
        rejected_trades = portfolio["rejected_trades"]

    except (OSError, ValueError, KeyError, TypeError) as error:
        return {
            "success": False,
            "message": f"Could not verify portfolio: {error}"
        }

    if rejected_trades:
        return {
            "success": False,
            "message": (
                "Existing trade history contains rejected trades. "
                "Resolve them before recording another trade."
            )
        }

    # Find an existing matching position
    matching_position = next(
        (
            position for position in holdings
            if position["ticker"] == ticker
            and position["asset_type"] == asset_type
        ),
        None
    )

    if action == "BUY":

        if value > cash:
            return {
                "success": False,
                "message": "Insufficient cash for this purchase."
            }

        # Maximum 20% of starting capital in one position
        existing_position_value = (
            matching_position["invested"]
            if matching_position else 0.0
        )

        new_position_value = existing_position_value + value

        maximum_position = (
            STARTING_CAPITAL * RISK_SETTINGS.max_position_percent
        )

        if new_position_value > maximum_position + 0.001:
            return {
                "success": False,
                "message": (
                    f"Position limit exceeded. Maximum allowed "
                    f"per position is {maximum_position:.2f} SEK."
                )
            }

        # Maximum 80% of starting capital invested in total
        maximum_exposure = (
            STARTING_CAPITAL * RISK_SETTINGS.max_total_exposure
        )

        if total_invested + value > maximum_exposure + 0.001:
            return {
                "success": False,
                "message": (
                    f"Portfolio exposure limit exceeded. "
                    f"Maximum total investment is "
                    f"{maximum_exposure:.2f} SEK."
                )
            }

    elif action == "SELL":

        if matching_position is None:
            return {
                "success": False,
                "message": "No matching position exists to sell."
            }

        if quantity > matching_position["quantity"] + 0.000001:
            return {
                "success": False,
                "message": "Not enough units available to sell."
            }

    # Check CSV structure before writing
    file_exists = os.path.exists(TRADE_LOG)

    try:
        write_header = (
            not file_exists
            or os.path.getsize(TRADE_LOG) == 0
        )

        if file_exists and not write_header:
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
