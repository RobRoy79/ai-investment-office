
"""
AI Investment Office
Central investment rules.

All recommendations are for research and paper trading.
No live orders are placed.
"""

ALLOWED_ASSET_TYPES = {
    "stock",
    "gold",
    "silver",
    "oil",
    "crypto_certificate"
}

BLOCKED_ASSET_TYPES = {
    "fund",
    "direct_crypto",
    "leveraged_product"
}

REQUIRE_ISK_ELIGIBILITY = True
REQUIRE_NORDNET_AVAILABILITY = True

DEFAULT_RISK_PER_TRADE = 0.01
MAX_POSITION_PERCENT = 0.20


def validate_investment(
    asset_type: str,
    isk_eligible: bool,
    available_at_broker: bool,
    is_leveraged: bool = False
) -> dict:
    """
    Checks whether an investment can be considered
    under the project's current rules.

    Eligibility and broker availability must be verified
    using reliable, current information.
    """

    asset_type = asset_type.lower().strip()

    if asset_type in BLOCKED_ASSET_TYPES:
        return {
            "approved": False,
            "reason": "This type of investment is excluded."
        }

    if asset_type not in ALLOWED_ASSET_TYPES:
        return {
            "approved": False,
            "reason": "Unknown or unsupported asset type."
        }

    if is_leveraged:
        return {
            "approved": False,
            "reason": "Leveraged products are excluded."
        }

    if REQUIRE_ISK_ELIGIBILITY and not isk_eligible:
        return {
            "approved": False,
            "reason": "ISK eligibility has not been confirmed."
        }

    if REQUIRE_NORDNET_AVAILABILITY and not available_at_broker:
        return {
            "approved": False,
            "reason": "Availability at Nordnet has not been confirmed."
        }

    return {
        "approved": True,
        "reason": "Candidate meets the current investment rules."
    }


if __name__ == "__main__":
    print("AI INVESTMENT OFFICE - INVESTMENT RULES")

    example = validate_investment(
        asset_type="crypto_certificate",
        isk_eligible=True,
        available_at_broker=True
    )

    print(example)
