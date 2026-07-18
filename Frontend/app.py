import streamlit as st

st.set_page_config(
    page_title="CognixOps — Logistics AI",
    page_icon="◈",
    layout="wide",
)

# ── Imports ─────────────────────────────────────────────────────────────
from config import SKUS
from theme import GLOBAL_CSS
from components.scenario_controls import render_sidebar, render_playbook
from components.kpi_cards import render_kpi_cards, render_kpi_status_badge
from components.charts import render_forecast_chart
from components.map_view import render_route_map
from components.coordination import render_coordination_hub
from services.api import (
    get_kpis, get_forecast, get_all_forecasts,
    get_optimization, get_simulation, get_anomalies, health_check,
)
from utils.helpers import empty_state, error_state, section_header, skeleton_block

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Sidebar Controls ─────────────────────────────────────────────────────
controls = render_sidebar()

disruption     = controls["disruption"]
sku            = controls["sku"]
horizon        = controls["horizon"]
show_all_skus  = controls["show_all_skus"]
show_anomalies = controls["show_anomalies"]
sensitivity    = controls["sensitivity"]
run_clicked    = controls["run"]

# ── State ────────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = {}
if "backend_up" not in st.session_state:
    st.session_state.backend_up = None

# ── Run Analysis ─────────────────────────────────────────────────────────
if run_clicked:
    if not health_check():
        st.session_state.backend_up = False
        st.toast("Can't reach the backend — check it's running.", icon="🚫")
    else:
        st.session_state.backend_up = True
        with st.spinner("Running analysis..."):
            forecast_data = get_forecast(sku, horizon)
            kpi_data = get_kpis()
            anomaly_data = get_anomalies(sku, sensitivity) if show_anomalies else None

            st.session_state.results = {
                "kpis": kpi_data if isinstance(kpi_data, dict) else None,
                "forecast": forecast_data if isinstance(forecast_data, dict) else None,
                "all_forecasts": get_all_forecasts(SKUS, horizon) if show_all_skus else [],
                "optimization": get_optimization(disruption),
                "simulation": get_simulation(disruption) if disruption != "none" else None,
                "anomalies": anomaly_data,
            }

        if st.session_state.results.get("kpis"):
            st.toast("Analysis complete.", icon="✅")
        else:
            st.toast("Analysis finished with errors — see below.", icon="⚠️")

results = st.session_state.results

# ── Header ───────────────────────────────────────────────────────────────
st.markdown(
    '<p style="font-family:\'DM Mono\',monospace;font-size:11px;color:#AAAAAA;'
    'letter-spacing:0.15em;text-transform:uppercase;margin-bottom:2px;">'
    'AI Logistics Intelligence</p>',
    unsafe_allow_html=True,
)
st.title("CognixOps")

if st.session_state.backend_up is False:
    error_state(
        "Backend unreachable",
        "Start the FastAPI server and confirm API_URL points to it, then click Run Analysis again.",
    )

tab_overview, tab_coordination = st.tabs(["📊 Overview", "🔗 Coordination Hub"])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — Overview
# ══════════════════════════════════════════════════════════════════════════
with tab_overview:

    # ── KPI Section ──────────────────────────────────────────────────────
    if results.get("kpis"):
        render_kpi_status_badge(results["kpis"])
        render_kpi_cards(results["kpis"])
    elif run_clicked and st.session_state.backend_up:
        skeleton_block(height=90, count=5, columns=True)
    else:
        empty_state("Click Run Analysis to load KPIs", icon="📊")

    st.divider()

    # ── Forecast Section ─────────────────────────────────────────────────
    section_header("Demand Forecast", f"{horizon}-day horizon · trend + seasonality model", icon="📈")
    forecast_data = results.get("forecast")
    anomaly_data = results.get("anomalies")

    if forecast_data and forecast_data.get("forecast"):
        render_forecast_chart(forecast_data, anomaly_data)
        c1, c2 = st.columns(2)
        c1.metric("Model MAE", f"{forecast_data.get('model_mae', 0):.1f}",
                   help="Mean absolute error of the trend+seasonality model on a 14-day backtest.")
        c2.metric("Naive baseline MAE", f"{forecast_data.get('baseline_mae', 0):.1f}",
                   help="Error of a naive 'tomorrow = today' forecast on the same backtest, for comparison.")
    else:
        st.warning("No forecast data available")

    st.divider()

    # ── Optimization Section ────────────────────────────────────────────
    section_header("Route Optimization", "Selected fulfilment lane and network map", icon="🛣️")
    optimization = results.get("optimization")

    if optimization:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Cost", f"${optimization.get('total_cost', 0):,.0f}", help="Cost of the currently selected route.")
        c2.metric("Total CO₂", f"{optimization.get('total_co2', 0):,.0f} kg", help="CO₂ output of the currently selected route.")
        c3.metric("Service Level", f"{optimization.get('service_level', 0):.1f}%", help="Estimated service level under the current scenario.")
        render_route_map(optimization, disruption_active=(disruption != "none"))
    else:
        empty_state("Run analysis to compute routes", icon="🗺️")

    st.divider()

    # ── Simulation Section ──────────────────────────────────────────────
    section_header("Disruption Scenario", "Projected impact and recommended playbook", icon="🚨")
    simulation = results.get("simulation")

    if disruption == "none":
        st.info("No disruption selected — pick one in the sidebar to see its projected impact.")
    elif simulation:
        render_playbook(simulation)
    else:
        empty_state("Run analysis to simulate disruption", icon="🧭")

    st.divider()

    # ── Anomaly Section ──────────────────────────────────────────────────
    section_header("Anomaly Detection", f"Z-score ≥ {sensitivity}σ on {sku} demand history", icon="🔍")
    anomalies = results.get("anomalies")

    if anomalies and anomalies.get("anomalies"):
        for a in anomalies["anomalies"]:
            direction = "▲ spike" if a["z_score"] > 0 else "▼ drop"
            st.markdown(
                f"**{a['date']}** — demand {a['demand']:.0f} "
                f"({direction}, z = {a['z_score']:+.2f})"
            )
    elif show_anomalies:
        empty_state("No anomalies detected in this window", icon="✨")
    else:
        st.info("Anomaly overlay is off — enable it in the sidebar.")

# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — Coordination Hub
# ══════════════════════════════════════════════════════════════════════════
with tab_coordination:
    render_coordination_hub(results)
