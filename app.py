

"""
AI Investment Office
Huvudpanel för Streamlit

Kopplar samman analys, riskhantering,
portföljhantering och simulerad handel.

Endast simulerad handel. Inga riktiga order läggs.
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
# SIDINSTÄLLNINGAR
# --------------------------------------------------

st.set_page_config(
    page_title="AI Investment Office",
    page_icon="📈",
    layout="wide"
)

st.title("🏦 AI INVESTMENT OFFICE")
st.subheader("Ditt personliga investeringskontor")

st.info(
    "SIMULERAT HANDELSLÄGE – Endast investeringar i en "
    "simulerad miljö. Inga riktiga pengar eller "
    "mäklarorder används."
)


# --------------------------------------------------
# HÄMTA PORTFÖLJ
# --------------------------------------------------

try:
    portfolio = calculate_portfolio(STARTING_CAPITAL)

except Exception as error:
    st.error(f"Kunde inte läsa in portföljen: {error}")
    st.stop()


if "trade_message" in st.session_state:
    st.success(st.session_state.pop("trade_message"))


# --------------------------------------------------
# PORTFÖLJÖVERSIKT
# --------------------------------------------------

st.header("💼 Portföljöversikt")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Startkapital",
    f"{portfolio['starting_capital']:,.2f} kr"
)

col2.metric(
    "Tillgängligt kapital",
    f"{portfolio['cash']:,.2f} kr"
)

col3.metric(
    "Investerat belopp",
    f"{portfolio['total_invested']:,.2f} kr"
)

col4.metric(
    "Öppna positioner",
    portfolio["number_of_positions"]
)

if portfolio["holdings"]:
    st.subheader("Nuvarande innehav")
    st.dataframe(
        portfolio["holdings"],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Inga investeringar har registrerats ännu.")

if portfolio["rejected_trades"]:
    st.warning(
        "Vissa historiska transaktioner har avvisats. "
        "Kontrollera transaktionshistoriken innan du fortsätter."
    )
    st.write(portfolio["rejected_trades"])


st.divider()


# --------------------------------------------------
# RISKHANTERING
# --------------------------------------------------

st.header("🛡️ Riskhantering")

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
    "Maximal risk per affär",
    f"{settings.risk_per_trade * 100:.1f}%"
)

risk_col2.metric(
    "Maximal portföljexponering",
    f"{settings.max_total_exposure * 100:.0f}%"
)

if risk_status["approved"]:
    st.success(
        f"Återstående investeringsutrymme: "
        f"{risk_status['remaining_capacity']:,.2f} kr"
    )
else:
    st.warning(
        "Portföljen har nått sin maximala "
        "investeringsgräns."
    )


st.divider()


# --------------------------------------------------
# MARKNADSANALYS
# --------------------------------------------------

st.header("📊 Marknadsanalys")

st.caption(
    "Historiska aktiekurser hämtas automatiskt "
    "via Yahoo Finance."
)

symbol = st.text_input(
    "Aktiens börskod",
    value="VOLV-B.ST"
).strip().upper()

headlines_text = st.text_area(
    "Finansiella nyhetsrubriker (valfritt)",
    placeholder=(
        "Skriv en nyhetsrubrik per rad.\n"
        "Exempel: Företaget rapporterar starka resultat"
    )
)

stop_loss_percent = st.slider(
    "Föreslaget avstånd till stop-loss (%)",
    min_value=1,
    max_value=20,
    value=5,
    step=1
)

if st.button("Analysera investering", type="primary"):

    if not symbol:
        st.error("Ange en giltig börskod.")

    else:
        with st.spinner("Analyserar marknadsdata..."):

            prices = get_closing_prices(
                symbol,
                period="6mo"
            )

            if len(prices) < 50:
                st.error(
                    "Det finns inte tillräckligt med historiska "
                    "kursdata. Minst 50 stängningskurser krävs."
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
                    st.subheader("Analysresultat")

                    price_col, sma20_col, sma50_col = st.columns(3)

                    price_col.metric(
                        "Senaste kurs",
                        f"{current_price:.2f}"
                    )

                    sma20_col.metric(
                        "20-dagars medelvärde",
                        f"{sma20:.2f}"
                    )

                    sma50_col.metric(
                        "50-dagars medelvärde",
                        f"{sma50:.2f}"
                    )

                    st.subheader("Investeringsrekommendation")

                    recommendation = result["recommendation"]

                    if recommendation == "BUY":
                        st.success("KÖPSIGNAL")

                    elif recommendation == "SELL":
                        st.error("SÄLJSIGNAL")

                    else:
                        st.warning("AVVAKTA")

                    signal_translation = {
                        "BUY": "KÖP",
                        "SELL": "SÄLJ",
                        "HOLD": "AVVAKTA"
                    }

                    technical_signal = result["technical_signal"]

                    st.write(
                        "Teknisk signal:",
                        signal_translation.get(
                            technical_signal,
                            technical_signal
                        )
                    )

                    st.write(
                        "Tekniskt analysbetyg:",
                        result["technical_score"]
                    )

                    st.write(
                        "Nyhetsbetyg:",
                        result["news_score"]
                    )

                    st.write(
                        "Sammanvägt analysbetyg:",
                        result["combined_score"]
                    )

                    st.write(result["explanation"])

                    st.caption(
                        "Nyhetsanalysen använder enkla sökord "
                        "och är inte en fullständig AI-modell. "
                        "Nyhetsrubriker måste anges manuellt."
                    )

                    # Beräkna illustrativ positionsstorlek
                    risk_result = calculate_position_size(
                        capital=portfolio["cash"],
                        price=current_price,
                        stop_loss_percent=(
                            stop_loss_percent / 100
                        ),
                        settings=settings
                    )

                    st.subheader("Positionsberäkning")

                    if risk_result["approved"]:

                        st.metric(
                            "Beräknat positionsvärde",
                            f"{risk_result['position_value']:,.2f} kr"
                        )

                        st.metric(
                            "Beräknat antal enheter",
                            f"{risk_result['units']:.4f}"
                        )

                        st.caption(
                            "Detta är endast en beräkning. "
                            "Ingen order läggs eller godkänns."
                        )

                    else:
                        st.warning(risk_result["reason"])


st.divider()


# --------------------------------------------------
# SIMULERAD HANDEL
# --------------------------------------------------

st.header("📝 Simulerad handel")

st.warning(
    "Alla transaktioner nedan är simulerade. "
    "Ingenting skickas till Nordnet."
)

with st.form("paper_trade_form"):

    action = st.selectbox(
        "Transaktion",
        ["BUY", "SELL"],
        format_func=lambda x: {
            "BUY": "KÖP",
            "SELL": "SÄLJ"
        }[x]
    )

    ticker = st.text_input(
        "Instrumentets börskod",
        placeholder="Exempel: VOLV-B.ST"
    )

    asset_type = st.selectbox(
        "Investeringstyp",
        [
            "stock",
            "gold",
            "silver",
            "oil",
            "crypto_certificate"
        ],
        format_func=lambda x: {
            "stock": "Aktier",
            "gold": "Guld",
            "silver": "Silver",
            "oil": "Olja",
            "crypto_certificate": "Kryptocertifikat"
        }[x]
    )

    quantity = st.number_input(
        "Antal",
        min_value=0.000001,
        value=1.0,
        step=1.0
    )

    price = st.number_input(
        "Pris per enhet (kr)",
        min_value=0.000001,
        value=100.0,
        step=1.0
    )

    isk_verified = st.checkbox(
        "Jag har kontrollerat att exakt detta instrument "
        "är tillåtet på ISK."
    )

    broker_verified = st.checkbox(
        "Jag har kontrollerat att exakt detta instrument "
        "finns tillgängligt hos Nordnet."
    )

    leveraged = st.checkbox(
        "Detta instrument använder hävstång."
    )

    submitted = st.form_submit_button(
        "Registrera simulerad transaktion"
    )

    if submitted:

        if not ticker.strip():
            st.error("Ange instrumentets börskod.")

        elif not isk_verified or not broker_verified:
            st.error(
                "Både ISK-behörighet och tillgänglighet "
                "hos Nordnet måste kontrolleras först."
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
# SIDFOT
# --------------------------------------------------

st.caption(
    "AI Investment Office | Endast simulerad handel | "
    "Startkapital: 10 000 kr | "
    "Ingen verklig mäklarkoppling | "
    "Analys- och utbildningsprototyp"
)
