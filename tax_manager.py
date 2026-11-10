
"""
AI Investment Office
Swedish ISK tax estimation.

This is an estimate, not an official tax calculation.
Rates and allowances must be checked for each tax year.
"""

# Swedish ISK rules for income year 2026
ISK_TAX_FREE_ALLOWANCE_2026 = 300000.0

# Effective tax rate: 30% of a 3.55% standard income
ISK_EFFECTIVE_TAX_RATE_2026 = 0.01065


def estimate_isk_tax(
    capital_base: float,
    tax_free_allowance: float = ISK_TAX_FREE_ALLOWANCE_2026,
    effective_tax_rate: float = ISK_EFFECTIVE_TAX_RATE_2026
) -> dict:
    """
    Estimates annual ISK tax for 2026.

    The tax-free allowance is shared across ISK,
    capital insurance (KF) and PEPP.

    The broker normally reports the ISK information
    to the Swedish Tax Agency.
    """

    if capital_base < 0:
        return {
            "valid": False,
            "error": "Capital base cannot be negative."
        }

    taxable_base = max(0.0, capital_base - tax_free_allowance)
    estimated_tax = taxable_base * effective_tax_rate

    return {
        "valid": True,
        "tax_year": 2026,
        "capital_base": round(capital_base, 2),
        "tax_free_allowance": tax_free_allowance,
        "taxable_base": round(taxable_base, 2),
        "effective_tax_rate_percent": effective_tax_rate * 100,
        "estimated_annual_tax": round(estimated_tax, 2),
        "tax_per_sale": 0.0,
        "note": (
            "ISK is taxed annually using a standard income calculation. "
            "Individual sales are not taxed separately."
        )
    }


def check_isk_eligibility(instrument_verified: bool) -> dict:
    """
    An instrument must be verified as ISK-eligible
    before the system can recommend it for an ISK account.
    """

    if instrument_verified:
        return {
            "eligible": True,
            "message": "ISK eligibility has been verified."
        }

    return {
        "eligible": False,
        "message": (
            "Do not recommend this instrument for ISK "
            "until its eligibility has been checked."
        )
    }


if __name__ == "__main__":
    result = estimate_isk_tax(500000)

    print("AI INVESTMENT OFFICE - SWEDISH TAX ESTIMATE")
    print(result)
