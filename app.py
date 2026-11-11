

import streamlit as st
import pandas as pd

from datetime import datetime
from discovery_engine import run_discovery_scan


# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Investment Office",
    page_icon="📈",
    layout="wide"
)

STARTING_CAPITAL = 10000


# --------------------------------------------------
# DESIGN
# --------------------------------------------------

st.title("📈 AI Investment Office")

st.caption(
    "Ditt personliga investeringskontor – "
    "marknadsbevakning, analys och riskkontroll."
)

st.info(
    "Analysen är ett beslutsunderlag och inte en köporder. "
    "Systemet använder endast pappersanalys."
)

st.divider()


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

st.subheader("🌍 Global marknadsskanning")

st.write(
    "Låt systemet söka efter intressanta aktier "
    "på svenska, amerikanska och europeiska marknader."
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Startkapital",
        f"{STARTING_CAPITAL:,.0f} kr"
    )

with col2:
    st.metric(
        "Handelstyp",
        "Paper trading"
    )

st.divider()


# --------------------------------------------------
# DISCOVERY ENGINE
# --------------------------------------------------

st.subheader("🔎 AI Discovery Engine")

st.write(
    "Discovery Engine rangordnar aktier efter trend, "
    "momentum, handelsvolym och volatilitet."
)

if st.button(
    "Starta global skanning",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Söker igenom marknaden. Detta kan ta en stund..."
    ):

        try:
            result = run_discovery_scan()

            if result.get("success"):

                st.session_state["discovery_result"] = result

                st.success(
                    "Skanningen är klar!"
                )

            else:
                st.error(
                    "Skanningen kunde inte slutföras."
                )

        except Exception as error:
            st.error(
                f"Ett fel uppstod: {error}"
            )


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

result = st.session_state.get("discovery_result")

if result:

    st.divider()

    st.subheader("📊 Resultat från marknadsskanningen")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Analyserade aktier",
            result.get("successful", 0)
        )

    with col2:
        st.metric(
            "Misslyckade hämtningar",
            result.get("failed", 0)
        )

    with col3:
        st.metric(
            "Totalt i universum",
            result.get("scanned", 0)
        )

    candidates = result.get("candidates", [])

    if candidates:

        df = pd.DataFrame(candidates)

        display_columns = [
            "company",
            "symbol",
            "price",
            "discovery_score",
            "classification",
            "return_20d",
            "return_60d",
            "rsi",
            "volatility"
        ]

        df = df[display_columns].copy()

        df = df.rename(columns={
            "company": "Företag",
            "symbol": "Aktie",
            "price": "Senaste kurs",
            "discovery_score": "Poäng",
            "classification": "Prioritet",
            "return_20d": "Utveckling 20 dagar %",
            "return_60d": "Utveckling 60 dagar %",
            "rsi": "RSI",
            "volatility": "Volatilitet %"
        })

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("⭐ Intressantaste kandidaterna")

        for candidate in candidates[:5]:

            with st.expander(
                f"{candidate['company']} – "
                f"{candidate['discovery_score']} poäng"
            ):

                st.write(
                    f"**Aktie:** {candidate['symbol']}"
                )

                st.write(
                    f"**Prioritet:** {candidate['classification']}"
                )

                st.write(
                    f"**Kurs:** {candidate['price']}"
                )

                st.write(
                    f"**RSI:** {candidate['rsi']}"
                )

                st.write("**Analysens positiva faktorer:**")

                if candidate["reasons"]:

                    for reason in candidate["reasons"]:
                        st.write(f"• {reason}")

                else:
                    st.write(
                        "Inga särskilda positiva faktorer identifierades."
                    )

    else:

        st.warning(
            "Inga aktier kunde analyseras. "
            "Kontrollera marknadsdata och försök igen."
        )

    st.caption(
        "Senaste skanning: "
        + datetime.now().strftime("%Y-%m-%d %H:%M")
    )


# --------------------------------------------------
# PORTFOLIO INFORMATION
# --------------------------------------------------

st.divider()

st.subheader("💼 Investeringsportfölj")

st.write(
    "Startkapitalet är inställt på 10 000 kr. "
    "Portföljhantering och registrering av pappersaffärer "
    "kopplas in i nästa utvecklingssteg."
)

st.warning(
    "Discovery Engine använder tekniska indikatorer. "
    "Den gör ännu ingen fullständig fundamental analys "
    "eller AI-baserad nyhetsanalys."
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Investment Office | Version 1.0 | "
    "Endast analys och pappershandel – inga riktiga order."
)
