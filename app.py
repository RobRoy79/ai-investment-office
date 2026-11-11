
import os
import streamlit as st
import pandas as pd

from datetime import datetime
from discovery_engine import run_discovery_scan

# Fundamental Analyzer – appen ska kunna starta även
# om denna fil ännu inte finns i Streamlits miljö.
try:
    from fundamental_analyzer import analyze_fundamentals
    FUNDAMENTAL_ANALYZER_AVAILABLE = True
    FUNDAMENTAL_IMPORT_ERROR = None
except ModuleNotFoundError as error:
    analyze_fundamentals = None
    FUNDAMENTAL_ANALYZER_AVAILABLE = False
    FUNDAMENTAL_IMPORT_ERROR = str(error)


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
# DISPLAY HELPERS
# --------------------------------------------------

def format_number(value, decimals=2):
    if value is None:
        return "Saknas"

    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "Saknas"


def format_percent(value):
    if value is None:
        return "Saknas"

    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "Saknas"


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
# TEMPORARY FILE DIAGNOSTICS
# --------------------------------------------------

with st.expander("Teknisk filkontroll"):
    files = sorted(os.listdir())
    st.write("Filer som Streamlit hittar:")
    st.code("\n".join(files))

    if not FUNDAMENTAL_ANALYZER_AVAILABLE:
        st.error(
            "Fundamental Analyzer kunde inte laddas. "
            "Kontrollera att fundamental_analyzer.py "
            "finns i projektets rotmapp."
        )
        st.code(FUNDAMENTAL_IMPORT_ERROR)


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
            st.session_state.pop("fundamental_result", None)

            st.success("Skanningen är genomförd.")

        except Exception as error:
            st.error("Ett fel uppstod under skanningen.")
            st.exception(error)


# --------------------------------------------------
# DISPLAY DISCOVERY RESULTS
# --------------------------------------------------

result = st.session_state.get("discovery_result")

if result:

    st.divider()
    st.subheader("📊 Sammanfattning")

    discovery_info = result.get("discovery_info") or {}

    initial_count = discovery_info.get("initial_count", 0)
    total_count = discovery_info.get(
        "total_count", result.get("scanned", 0)
    )
    new_candidates = discovery_info.get("new_candidates", 0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Ursprungliga aktier", initial_count)

    with col2:
        st.metric("Nya kandidater", new_candidates)

    with col3:
        st.metric("Totalt insamlade", total_count)

    with col4:
        st.metric("Analyserade", result.get("successful", 0))

    st.write(
        f"Misslyckade datahämtningar: {result.get('failed', 0)}"
    )

    # ----------------------------------------------
    # SCREENING DIAGNOSTICS
    # ----------------------------------------------

    st.divider()
    st.subheader("🕵️ Resultat från de dynamiska sökningarna")

    screen_results = discovery_info.get("screen_results", {})

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
            st.write(f"**{readable_name}:** {count} aktier hittades")
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
                st.code(error.get("error", "Okänt fel"))
    else:
        st.success(
            "Inga tekniska fel rapporterades av screeningarna."
        )

    # ----------------------------------------------
    # TECHNICAL ANALYSIS
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

        # Missing columns should not crash the app.
        df = df.reindex(columns=display_columns)

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

            company = candidate.get("company", "Okänt företag")
            symbol = candidate.get("symbol", "Okänd symbol")
            score = candidate.get("discovery_score", "Saknas")

            with st.expander(f"{company} – {score} poäng"):

                st.write(f"**Aktiesymbol:** {symbol}")
                st.write(
                    f"**Analysprioritet:** "
                    f"{candidate.get('classification', 'Saknas')}"
                )
                st.write(
                    f"**Senaste kurs:** {candidate.get('price', 'Saknas')}"
                )
                st.write(f"**RSI:** {candidate.get('rsi', 'Saknas')}")

                st.write("**Identifierade faktorer:**")

                for reason in candidate.get("reasons", []):
                    st.write(f"• {reason}")

    else:
        st.warning("Inga aktier kunde analyseras.")

    failed_stocks = result.get("errors", [])

    if failed_stocks:
        with st.expander(
            f"Visa aktier som inte kunde analyseras ({len(failed_stocks)})"
        ):
            st.write(", ".join(map(str, failed_stocks)))

    st.caption(
        "Senaste skanning: "
        + datetime.now().strftime("%Y-%m-%d %H:%M")
    )


# --------------------------------------------------
# FUNDAMENTAL ANALYZER - SINGLE STOCK TEST
# --------------------------------------------------

st.divider()
st.subheader("🏦 Fundamental Analyzer")

if FUNDAMENTAL_ANALYZER_AVAILABLE:

    st.write(
        "Här testar vi den fundamentala analysmotorn "
        "på ett bolag innan vi kopplar in hela aktieuniversumet."
    )

    test_symbol = st.text_input(
        "Aktiesymbol att testa",
        value="MSFT",
        help="Exempel: MSFT, VOLV-B.ST eller NOVO-B.CO"
    ).strip().upper()

    if st.button(
        "Testa fundamental analys",
        use_container_width=True
    ):

        if not test_symbol:
            st.warning("Ange en aktiesymbol först.")

        else:
            with st.spinner(
                f"Hämtar bolagsinformation för {test_symbol}..."
            ):
                try:
                    fundamental_result = analyze_fundamentals(
                        test_symbol
                    )

                    st.session_state["fundamental_result"] = (
                        fundamental_result
                    )

                except Exception as error:
                    st.error("Fundamentalanalysen misslyckades.")
                    st.exception(error)

else:
    st.warning(
        "Fundamental Analyzer är tillfälligt otillgänglig. "
        "Discovery Engine kan fortfarande användas."
    )


# --------------------------------------------------
# FUNDAMENTAL ANALYSIS RESULTS
# --------------------------------------------------

fundamental_result = st.session_state.get(
    "fundamental_result"
)

if fundamental_result:

    st.divider()

    if not fundamental_result.get("success"):

        st.error(
            fundamental_result.get(
                "message",
                "Kunde inte hämta bolagsinformation."
            )
        )

    else:

        st.subheader(
            f"📋 Fundamental analys: "
            f"{fundamental_result.get('company', 'Okänt bolag')}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total fundamental poäng",
                format_number(
                    fundamental_result.get("fundamental_score"), 0
                ) + " / 100"
            )

        with col2:
            st.metric(
                "Bolagskvalitet",
                format_number(
                    fundamental_result.get("quality_score"), 0
                ) + " / 100"
            )

        with col3:
            st.metric(
                "Värderingspoäng",
                format_number(
                    fundamental_result.get("valuation_score"), 0
                ) + " / 100"
            )

        st.write(
            "**Bedömning:** "
            + fundamental_result.get(
                "classification", "Saknas"
            )
        )

        st.write(
            f"**Bransch:** "
            f"{fundamental_result.get('industry') or 'Saknas'}"
        )

        st.write(
            f"**Sektor:** "
            f"{fundamental_result.get('sector') or 'Saknas'}"
        )

        st.write(
            f"**Tillgängliga nyckeltal:** "
            f"{fundamental_result.get('available_metrics', 0)}"
        )

        metrics = {
            "Omsättningstillväxt": format_percent(
                fundamental_result.get("revenue_growth")
            ),
            "Vinstmarginal": format_percent(
                fundamental_result.get("profit_margin")
            ),
            "Rörelsemarginal": format_percent(
                fundamental_result.get("operating_margin")
            ),
            "Avkastning på eget kapital": format_percent(
                fundamental_result.get("return_on_equity")
            ),
            "Skuldsättning / eget kapital": format_number(
                fundamental_result.get("debt_to_equity")
            ),
            "Kassalikviditetsindikator": format_number(
                fundamental_result.get("current_ratio")
            ),
            "Fritt kassaflöde": format_number(
                fundamental_result.get("free_cash_flow"), 0
            ),
            "P/E-tal": format_number(
                fundamental_result.get("trailing_pe")
            ),
            "Framåtblickande P/E": format_number(
                fundamental_result.get("forward_pe")
            ),
            "Pris / omsättning": format_number(
                fundamental_result.get("price_to_sales")
            ),
            "EV / EBITDA": format_number(
                fundamental_result.get("ev_to_ebitda")
            ),
        }

        st.subheader("Finansiella nyckeltal")

        metrics_df = pd.DataFrame(
            list(metrics.items()),
            columns=["Nyckeltal", "Värde"]
        )

        st.dataframe(
            metrics_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            fundamental_result.get("message", "")
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
    "Fundamentalanalysen är ett preliminärt urvalsverktyg. "
    "Den ersätter inte fullständig bolagsanalys och "
    "utgör inte en köp- eller säljrekommendation."
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Investment Office | Paper Analysis Only | "
    "Inga riktiga order genomförs."
)

