
"""
AI Investment Office
Paper Trading Trade Recorder

Records simulated trades only.
Never sends real orders to a broker.
"""

import csv
import os
from datetime import datetime, timezone

from investment_rules import validate_investment

TRADE_LOG = "paper_trades.csv"

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

    action = action.upper().strip()
    ticker = ticker.upper().strip()

    if action not in ("BUY", "SELL"):
        return {"success": False, "message": "Action must be BUY or SELL."}

    if not ticker:
        return {"success": False, "message": "Ticker cannot be empty."}

    if quantity <= 0 or price <= 0:
        return {
            "success": False,
            "message": "Quantity and price must be positive."
        }

    if not all(map(lambda x: isinstance(x, (int, float)), [quantity, price])):
        return {
            "success": False,
            "message": "Quantity and price must be numeric."
        }

    check = validate_investment(
        asset_type=asset_type,
        isk_eligible=isk_eligible,
        available_at_broker=available_at_broker,
        is_leveraged=is_leveraged
    )

    if not check["approved"]:
        return {"success": False, "message": check["reason"]}

    trade = {
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "action": action,
        "ticker": ticker,
        "asset_type": asset_type,
        "quantity": quantity,
        "price": price,
        "value": round(quantity * price, 2),
        "status": "PAPER TRADE - NOT REAL"
    }

    file_exists = os.path.exists(TRADE_LOG)
    write_header = not file_exists or os.path.getsize(TRADE_LOG) == 0

    try:
        with open(TRADE_LOG, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)

            if write_header:
                writer.writeheader()

            writer.writerow(trade)

        return {
            "success": True,
            "message": "Simulated trade saved.",
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

    print(result)
