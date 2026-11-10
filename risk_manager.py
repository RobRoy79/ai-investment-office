from dataclasses import dataclass


@dataclass
class RiskSettings:
    # Startkapital i kronor
    starting_capital: float = 10000.0

    # Försiktig grundinställning: 1 % risk per affär
    risk_per_trade: float = 0.01

    # Högsta andel av kapitalet i en enskild position
    max_position_percent: float = 0.20

    # Högsta sammanlagda investerade andel
    max_total_exposure: float = 0.80


def calculate_risk_amount(
    capital: float,
    settings: RiskSettings
) -> float:
    """Beräknar högsta planerade riskbelopp per affär."""
    return max(0.0, capital * settings.risk_per_trade)


def calculate_position_size(
    capital: float,
    price: float,
    stop_loss_percent: float,
    settings: RiskSettings
) -> dict:
    """Beräknar möjlig positionsstorlek utifrån risk och stop loss."""

    if capital <= 0 or price <= 0:
        return {"approved": False, "reason": "Ogiltigt kapital eller pris."}

    if not 0 < stop_loss_percent < 1:
        return {"approved": False, "reason": "Ogiltig stop loss."}

    risk_amount = calculate_risk_amount(capital, settings)

    position_value = risk_amount / stop_loss_percent

    max_position = capital * settings.max_position_percent

    position_value = min(position_value, max_position)

    units = position_value / price

    return {
        "approved": True,
        "risk_amount": round(risk_amount, 2),
        "position_value": round(position_value, 2),
        "units": round(units, 6),
        "stop_loss_percent": stop_loss_percent * 100
    }


def check_portfolio_risk(
    capital: float,
    invested_amount: float,
    settings: RiskSettings
) -> dict:
    """Kontrollerar hur mycket kapital som redan är investerat."""

    if capital <= 0 or invested_amount < 0:
        return {"approved": False, "reason": "Ogiltiga belopp."}

    max_invested = capital * settings.max_total_exposure

    remaining = max(0.0, max_invested - invested_amount)

    return {
        "approved": remaining > 0,
        "max_invested": round(max_invested, 2),
        "remaining_capacity": round(remaining, 2)
    }


if __name__ == "__main__":
    settings = RiskSettings()

    result = calculate_position_size(
        capital=settings.starting_capital,
        price=100.0,
        stop_loss_percent=0.05,
        settings=settings
    )

    print("AI INVESTMENT OFFICE - RISK MANAGER")
    print(result)
