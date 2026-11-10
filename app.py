

"""
AI Investment Office
Main Streamlit Dashboard

Connects analysis, risk management,
portfolio management and paper trading.

Paper trading only. No real orders are placed.
"""

import streamlit as st

from agent_manager import run_analysis
from market_data import get_closing_prices
from risk_manager import (
    RiskSettings,
    calculate_position_size,
    check_portfolio_risk
)
from portfolio_manager import calculate_portfolio
from trade_recorder import record_paper_trade


STARTING_CAPITAL = 10000.0


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Investment Office",
    page_icon="📈",
    layout="wide"
)

st.title("🏦 AI INVESTMENT OFFICE")
st.subheader("Your Personal Investment Dashboard")

st.info(
    "PAPER TRADING MODE – Simulated investments only. "
    "No real money or broker orders are involved."
)


# --------------------------------------------------
# LOAD PORTFOLIO
# --------------------------------------------------

try:
    portfolio = calculate_portfolio(STARTING_CAPITAL)

except Exception as error:
    st.error(f"Could not load portfolio: {error}")
    st.stop()


if "trade_message" in st.session_state:
    st.success(st.session_state.pop("trade_message"))


# --------------------------------------------------
# PORTFOLIO OVERVIEW
# --------------------------------------------------

st.header("💼 Portfolio Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Starting Capital",
    f"{portfolio['starting_capital']:,.2f} SEK"
)

col2.metric(
    "Available Cash",
    f"{portfolio['cash']:,.2f} SEK"
)

col3.metric(
    "Invested Amount",
    f"{portfolio['total_invested']:,.2f} SEK"
)

col4.metric(
    "Open Positions",
    portfolio["number_of_positions"]
)

if portfolio["holdings"]:
    st.subheader("Current Holdings")
    st.dataframe(
        portfolio["holdings"],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No investments have been recorded yet.")

if portfolio["rejected_trades"]:
    st.warning(
        "Some historical trades were rejected. "
        "Check the trade history before continuing."
    )
    st.write(portfolio["rejected_trades"])


st.divider()


# --------------------------------------------------
# RISK MANAGEMENT
# --------------------------------------------------

st.header("🛡️ Risk Management")

settings = RiskSettings(
    starting_capital=STARTING_CAPITAL
)

risk_status = check_portfolio_risk(
    capital=STARTING_CAPITAL,
    invested_amount=portfolio["total_invested"],
    settings=settings
)

risk_col1, risk_col2 = st.columns(2)

risk_col1.metric(
    "Maximum Risk Per Trade",
    f"{settings.risk_per_trade * 100:.1f}%"
)

risk_col2.metric(
    "Maximum Portfolio Exposure",
    f"{settings.max_total_exposure * 100:.0f}%"
)

if risk_status["approved"]:
    st.success(
        f"Remaining investment capacity: "
        f"{risk_status['remaining_capacity']:,.2f} SEK"
    )
else:
    st.warning(
        "The portfolio has reached its maximum "
        "investment exposure."
    )


st.divider()


# --------------------------------------------------
# MARKET ANALYSIS
# --------------------------------------------------

st.header("📊 Market Analysis")

st.caption(
    "Automatic historical stock prices are currently "
    "retrieved through Yahoo Finance."
)

symbol = st.text_input(
    "Stock ticker",
    value="VOLV-B.ST"
).strip().upper()

headlines_text = st.text_area(
    "Financial news headlines (optional)",
    placeholder=(
        "Enter one headline per line.\n"
        "Example: Company reports strong results"
    )
)

stop_loss_percent = st.slider(
    "Proposed stop-loss distance (%)",
    min_value=1,
    max_value=20,
    value=5,
    step=1
)

if st.button("Analyze Investment", type="primary"):

    if not symbol:
        st.error("Please enter a valid stock ticker.")

    else:
        with st.spinner("Analyzing market data..."):

            prices = get_closing_prices(
                symbol,
                period="6mo"
            )

            if len(prices) < 50:
                st.error(
                    "Not enough historical price data. "
                    "At least 50 closing prices are required."
                )

            else:
                current_price = float(prices[-1])
                sma20 = sum(prices[-20:]) / 20
                sma50 = sum(prices[-50:]) / 50

                headlines = [
                    line.strip()
                    for line in headlines_text.splitlines()
                    if line.strip()
                ]

                result = run_analysis(
                    ticker=symbol,
                    current_price=current_price,
                    sma20=sma20,
                    sma50=sma50,
                    headlines=headlines
                )

                if not result["success"]:
                    st.error(result["explanation"])

                else:
                    st.subheader("Analysis Results")

                    price_col, sma20_col, sma50_col = st.columns(3)

                    price_col.metric(
                        "Latest Price",
                        f"{current_price:.2f}"
                    )

                    sma20_col.metric(
                        "20-Day Average",
                        f"{sma20:.2f}"
                    )

                    sma50_col.metric(
                        "50-Day Average",
                        f"{sma50:.2f}"
                    )

                    st.subheader("Investment Recommendation")

                    recommendation = result["recommendation"]

                    if recommendation == "BUY":
                        st.success("BUY SIGNAL")

                    elif recommendation == "SELL":
                        st.error("SELL SIGNAL")

                    else:
                        st.warning("HOLD SIGNAL")

                    st.write(
                        "Technical signal:",
                        result["technical_signal"]
                    )

                    st.write(
                        "Technical score:",
                        result["technical_score"]
                    )

                    st.write(
                        "News score:",
                        result["news_score"]
                    )

                    st.write(
                        "Combined score:",
                        result["combined_score"]
                    )

                    st.write(result["explanation"])

                    st.caption(
                        "News analysis uses simple keywords, "
                        "not a full AI model. Headlines must "
                        "be supplied manually."
                    )

                    # Calculate illustrative position size
                    risk_result = calculate_position_size(
                        capital=portfolio["cash"],
                        price=current_price,
                        stop_loss_percent=(
                            stop_loss_percent / 100
                        ),
                        settings=settings
                    )

                    st.subheader("Position Sizing")

                    if risk_result["approved"]:

                        st.metric(
                            "Illustrative Position Value",
                            f"{risk_result['position_value']:,.2f} SEK"
                        )

                        st.metric(
                            "Illustrative Number of Units",
                            f"{risk_result['units']:.4f}"
                        )

                        st.caption(
                            "Calculation only. This does not "
                            "place or authorize an order."
                        )

                    else:
                        st.warning(risk_result["reason"])


st.divider()


# --------------------------------------------------
# PAPER TRADING
# --------------------------------------------------

st.header("📝 Paper Trading")

st.warning(
    "All transactions below are simulated. "
    "Nothing is sent to Nordnet."
)

with st.form("paper_trade_form"):

    action = st.selectbox(
        "Transaction",
        ["BUY", "SELL"]
    )

    ticker = st.text_input(
        "Instrument ticker",
        placeholder="Example: VOLV-B.ST"
    )

    asset_type = st.selectbox(
        "Investment type",
        [
            "stock",
            "gold",
            "silver",
            "oil",
            "crypto_certificate"
        ]
    )

    quantity = st.number_input(
        "Quantity",
        min_value=0.000001,
        value=1.0,
        step=1.0
    )

    price = st.number_input(
        "Price per unit (SEK)",
        min_value=0.000001,
        value=100.0,
        step=1.0
    )

    isk_verified = st.checkbox(
        "I have verified that this exact instrument "
        "is eligible for ISK."
    )

    broker_verified = st.checkbox(
        "I have verified that this exact instrument "
        "is available at Nordnet."
    )

    leveraged = st.checkbox(
        "This instrument uses leverage."
    )

    submitted = st.form_submit_button(
        "Record Simulated Transaction"
    )

    if submitted:

        if not ticker.strip():
            st.error("Please enter an instrument ticker.")

        elif not isk_verified or not broker_verified:
            st.error(
                "Both ISK eligibility and Nordnet availability "
                "must be verified before recording."
            )

        else:
            result = record_paper_trade(
                action=action,
                ticker=ticker,
                asset_type=asset_type,
                quantity=quantity,
                price=price,
                isk_eligible=isk_verified,
                available_at_broker=broker_verified,
                is_leveraged=leveraged
            )

            if result["success"]:
                st.session_state["trade_message"] = (
                    result["message"]
                )
                st.rerun()

            else:
                st.error(result["message"])


st.divider()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "AI Investment Office | Paper Trading Only | "
    "Starting Capital: 10,000 SEK | "
    "No real broker connection | "
    "Research and educational prototype"
)
