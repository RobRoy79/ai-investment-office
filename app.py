
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
# HEADER
# --------------------------------------------------

st.title("📈 AI Investment Office")

st.caption(
    "Ditt personliga investeringskontor – "
    "marknadsbevakning, analys och riskkontroll."
)

st.info(
    "Systemet utför endast analyser och pappershandel. "
    "Inga riktiga köp eller försäljningar genomförs."
)

st.divider()


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

st.subheader("🌍 Global marknadsskanning")

col1, col2 = st.columns(2)

with col1:
    st.metric("Startkapital", f"{STARTING_CAPITAL:,.0f} kr")

with col2:
    st.metric("Handelstyp", "Paper trading")

st.write(
    "Systemet kombinerar en grundlista med dynamisk sökning "
    "efter nya aktiekandidater."
)

st.divider()


# --------------------------------------------------
# DISCOVERY ENGINE
# --------------------------------------------------

st.subheader("🔎 Discovery Engine")

st.write(
    "Sökningen försöker hitta nya småbolag, "
    "tillväxtbolag och undervärderade tillväxtbolag."
)

if st.button(
    "Starta global skanning",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Söker efter nya aktier och analyserar marknaden..."
    ):

        try:

            result = run_discovery_scan(
                dynamic_discovery=True,
                max_per_screen=20
            )

            st.session_state["discovery_result"] = result

            st.success("Skanningen är genomförd.")

        except Exception as error:

            st.error("Ett fel uppstod under skanningen.")
            st.exception(error)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

result = st.session_state.get("discovery_result")

if result:

    st.divider()

    st.subheader("📊 Sammanfattning")

    discovery_info = result.get("discovery_info") or {}

    initial_count = discovery_info.get(
        "initial_count", 0
    )

    total_count = discovery_info.get(
        "total_count", result.get("scanned", 0)
    )

    new_candidates = discovery_info.get(
        "new_candidates", 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Ursprungliga aktier",
            initial_count
        )

    with col2:
        st.metric(
            "Nya kandidater",
            new_candidates
        )

    with col3:
        st.metric(
            "Totalt insamlade",
            total_count
        )

    with col4:
        st.metric(
            "Analyserade",
            result.get("successful", 0)
        )

    st.write(
        f"Misslyckade datahämtningar: "
        f"{result.get('failed', 0)}"
    )

    # ----------------------------------------------
    # SCREENING DIAGNOSTICS
    # ----------------------------------------------

    st.divider()

    st.subheader("🕵️ Resultat från de dynamiska sökningarna")

    screen_results = discovery_info.get(
        "screen_results", {}
    )

    screen_names = {
        "small_cap_gainers": "Småbolag med kursuppgång",
        "growth_technology_stocks": "Teknik- och tillväxtbolag",
        "undervalued_growth_stocks": "Undervärderade tillväxtbolag"
    }

    if screen_results:

        for screen_name, count in screen_results.items():

            readable_name = screen_names.get(
                screen_name, screen_name
            )

            st.write(
                f"**{readable_name}:** {count} aktier hittades"
            )

    else:

        st.warning(
            "Inga resultat från screeningarna kunde visas."
        )

    screening_errors = discovery_info.get("errors", [])

    if screening_errors:

        st.error(
            f"{len(screening_errors)} sökning(ar) rapporterade fel."
        )

        for error in screening_errors:

            with st.expander(
                f"Fel i sökning: {error.get('screen', 'Okänd')}"
            ):

                st.code(
                    error.get("error", "Okänt fel")
                )

    else:

        st.success(
            "Inga tekniska fel rapporterades av screeningarna."
        )

    # ----------------------------------------------
    # ANALYSIS RESULTS
    # ----------------------------------------------

    st.divider()

    st.subheader("📈 Analyserade aktier")

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
            "classification": "Analysprioritet",
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

        st.subheader("⭐ Fem högst rankade kandidater")

        for candidate in candidates[:5]:

            with st.expander(
                f"{candidate['company']} – "
                f"{candidate['discovery_score']} poäng"
            ):

                st.write(
                    f"**Aktiesymbol:** {candidate['symbol']}"
                )

                st.write(
                    f"**Analysprioritet:** "
                    f"{candidate['classification']}"
                )

                st.write(
                    f"**Senaste kurs:** {candidate['price']}"
                )

                st.write(
                    f"**RSI:** {candidate['rsi']}"
                )

                st.write("**Identifierade faktorer:**")

                for reason in candidate.get("reasons", []):
                    st.write(f"• {reason}")

    else:

        st.warning(
            "Inga aktier kunde analyseras."
        )

    # ----------------------------------------------
    # FAILED STOCKS
    # ----------------------------------------------

    failed_stocks = result.get("errors", [])

    if failed_stocks:

        with st.expander(
            f"Visa aktier som inte kunde analyseras ({len(failed_stocks)})"
        ):

            st.write(", ".join(failed_stocks))

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
    "Startkapital: 10 000 kr. "
    "Portföljhantering, riskanalys och pappersaffärer "
    "byggs ut i kommande utvecklingssteg."
)

st.warning(
    "Den nuvarande Discovery Engine använder tekniska "
    "indikatorer. Den utför ännu inte fullständig "
    "fundamental analys eller AI-baserad nyhetsanalys."
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Investment Office | Paper Analysis Only | "
    "Inga riktiga order genomförs."
)
