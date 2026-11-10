
import streamlit as st
from engine import analyze_stock, calculate_position_size

st.set_page_config(
    page_title="AI Investment Office",
    page_icon="📈",
    layout="wide"
)

st.title("🏦 AI INVESTMENT OFFICE")
st.subheader("Your Personal AI Trading Dashboard")

st.info(
    "Version 1.0 – Paper Trading Mode. "
    "No real trades or orders are placed."
)

# Investment settings
st.header("Investment Settings")

capital = st.number_input(
    "Starting capital (SEK)",
    min_value=1000,
    value=10000,
    step=1000
)

risk = st.slider(
    "Risk per trade (%)",
    min_value=0.5,
    max_value=5.0,
    value=1.0,
    step=0.5
)

st.metric("Available investment capital", f"{capital:,.0f} SEK")

st.divider()

# Stock analysis
st.header("📊 Stock Analysis")

symbol = st.text_input(
    "Stock ticker",
    value="VOLV-B.ST"
)

prices_text = st.text_area(
    "Enter at least 50 historical closing prices, oldest first, separated by commas",
    placeholder="Example: 100, 101, 102, 103 ..."
)

stop_price = st.number_input(
    "Proposed stop-loss price (SEK)",
    min_value=0.01,
    value=90.0,
    step=1.0
)

if st.button("Analyze Stock", type="primary"):

    try:
        prices = [
            float(value.strip())
            for value in prices_text.split(",")
            if value.strip()
        ]

        if len(prices) < 50:
            st.error("Please enter at least 50 closing prices.")
        else:
            result = analyze_stock(symbol.upper(), prices)

            st.subheader("Analysis Results")

            col1, col2, col3 = st.columns(3)

            col1.metric("Latest price", f"{result.price:.2f}")
            col2.metric("20-day average", f"{result.sma_short:.2f}")
            col3.metric("50-day average", f"{result.sma_long:.2f}")

            st.subheader("Investment Signal")

            if result.signal == "BUY":
                st.success("BUY SIGNAL")
            elif result.signal == "SELL":
                st.error("SELL SIGNAL")
            else:
                st.warning("HOLD SIGNAL")

            st.write("Confidence:", result.confidence)

            if stop_price < result.price:
                shares = calculate_position_size(
                    capital,
                    risk,
                    result.price,
                    stop_price
                )

                st.metric("Calculated position size", f"{shares} shares")
                st.caption("Illustrative calculation only. No order is placed.")
            else:
                st.warning("Stop-loss must be below the latest price.")

    except ValueError as error:
        st.error(f"Input error: {error}")

st.divider()

st.caption(
    "AI Investment Office | Version 1.0 | "
    "Paper Trading Only | No live market data yet"
)
