import streamlit as st
from theme import TOKENS

METRICS = [
    {"label": "Service Level",      "key": "service_level",      "format": "{:.1f}%",    "good": "up",   "icon": "🎯", "help": "Blended on-time + lead-time consistency score."},
    {"label": "Total Cost",         "key": "total_cost",         "format": "${:,.0f}",   "good": "down", "icon": "💰", "help": "Estimated daily network operating cost for the selected route."},
    {"label": "CO₂ Emissions",      "key": "co2_kg",              "format": "{:,.0f} kg", "good": "down", "icon": "🌱", "help": "Estimated daily CO₂ output for the selected route."},
    {"label": "On-Time Delivery",   "key": "on_time_delivery",   "format": "{:.1f}%",    "good": "up",   "icon": "🚚", "help": "Share of shipments delivered within their promised window."},
    {"label": "Inventory Turnover", "key": "inventory_turnover", "format": "{:.2f}x",    "good": "up",   "icon": "🔄", "help": "Annual units sold divided by average stock on hand — higher is leaner."},
]


def render_kpi_cards(kpi_data: dict, comparison: dict = None):
    if not kpi_data:
        st.warning("KPI data unavailable — check backend connection.")
        return

    cols = st.columns(len(METRICS))
    for col, m in zip(cols, METRICS):
        value = kpi_data.get(m["key"])
        label = f"{m['icon']}  {m['label']}"

        if value is None:
            col.metric(label=label, value="N/A", help=m["help"])
            continue
        try:
            display = m["format"].format(value)
        except Exception:
            display = str(value)

        delta_str, delta_color = None, "normal"
        if comparison:
            baseline = comparison.get(m["key"])
            if baseline and baseline != 0:
                delta = value - baseline
                pct = (delta / baseline) * 100
                delta_str = f"{pct:+.1f}%"
                delta_color = ("normal" if delta >= 0 else "inverse") if m["good"] == "up" else ("inverse" if delta >= 0 else "normal")

        col.metric(label=label, value=display, delta=delta_str, delta_color=delta_color, help=m["help"])


def render_kpi_status_badge(kpi_data: dict):
    if not kpi_data:
        return

    sl, otd = kpi_data.get("service_level", 100), kpi_data.get("on_time_delivery", 100)
    if not isinstance(sl, (int, float)) or not isinstance(otd, (int, float)):
        return

    if sl >= 95 and otd >= 92:
        bg, border, dot, text, label = "#F0FDF4", "#86EFAC", TOKENS["success"], "#15803D", "System healthy — all KPIs on target"
    elif sl >= 88 or otd >= 80:
        bg, border, dot, text, label = "#FFFBEB", "#FCD34D", TOKENS["warning"], "#B45309", "Warning — one or more KPIs below target"
    else:
        bg, border, dot, text, label = "#FFF1F2", "#FDA4AF", TOKENS["danger"], "#BE123C", "Critical — immediate action required"

    st.markdown(f"""
<div class="fade-in" style="display:inline-flex;align-items:center;gap:8px;background:{bg};
            border:1px solid {border};border-radius:20px;padding:6px 14px;margin-bottom:1rem;">
  <span style="width:7px;height:7px;border-radius:50%;background:{dot};display:inline-block;"></span>
  <span style="font-size:12px;font-weight:600;color:{text};font-family:'Plus Jakarta Sans',sans-serif;">
    {label}
  </span>
</div>""", unsafe_allow_html=True)
