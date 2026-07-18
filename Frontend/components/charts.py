import streamlit as st
import plotly.graph_objects as go
from config import CHART_HEIGHT
from theme import TOKENS

PLOTLY_FONT = dict(family="Plus Jakarta Sans, sans-serif", color=TOKENS["text_muted"], size=12)


def _base_layout(title: str) -> dict:
    return dict(
        title=dict(text=title, font=dict(family="Plus Jakarta Sans, sans-serif", size=15, color=TOKENS["text"])),
        height=CHART_HEIGHT,
        margin=dict(l=10, r=10, t=48, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=PLOTLY_FONT,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, font=PLOTLY_FONT),
        hoverlabel=dict(bgcolor="white", bordercolor=TOKENS["border"], font=PLOTLY_FONT),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=TOKENS["border"], zeroline=False),
        transition=dict(duration=250, easing="cubic-in-out"),
    )


def render_forecast_chart(forecast_data: dict, anomaly_data: dict = None):
    if not forecast_data:
        st.warning("No forecast data available")
        return

    forecast = forecast_data.get("forecast", [])
    dates = forecast_data.get("dates", [])
    lower = forecast_data.get("lower", [])
    upper = forecast_data.get("upper", [])
    sku = forecast_data.get("sku", "")
    hist_dates = forecast_data.get("history_dates", [])
    hist_actuals = forecast_data.get("history_actuals", [])

    if not forecast:
        st.warning("Forecast data is empty")
        return

    fig = go.Figure()

    # ── Historical actuals (context leading into the forecast) ────────────
    if hist_dates and hist_actuals:
        fig.add_trace(go.Scatter(
            x=hist_dates, y=hist_actuals, mode="lines", name="Actual demand",
            line=dict(color=TOKENS["text_faint"], width=2, dash="dot"),
            hovertemplate="%{x}<br>Actual: %{y:.0f} units<extra></extra>",
        ))

        # ── Anomalies — correctly placed on the historical segment ────────
        if anomaly_data and anomaly_data.get("anomalies"):
            anomalies = anomaly_data["anomalies"]
            hist_set = set(hist_dates)
            in_view = [a for a in anomalies if a.get("date") in hist_set]
            if in_view:
                fig.add_trace(go.Scatter(
                    x=[a.get("date") for a in in_view],
                    y=[a.get("demand") for a in in_view],
                    mode="markers", name="Anomaly",
                    marker=dict(color=TOKENS["danger"], size=11, symbol="diamond",
                                line=dict(color="white", width=1)),
                    hovertemplate="%{x}<br>Anomaly: %{y:.0f} units<extra></extra>",
                ))

    # ── Confidence band ──────────────────────────────────────────────────
    if lower and upper and len(lower) == len(upper):
        fig.add_trace(go.Scatter(
            x=dates + dates[::-1], y=upper + lower[::-1], fill="toself",
            fillcolor="rgba(138,92,246,0.12)", line=dict(color="rgba(0,0,0,0)"),
            name="Confidence band", hoverinfo="skip",
        ))

    # ── Forecast bars + trend line ──────────────────────────────────────
    fig.add_trace(go.Bar(
        x=dates, y=forecast, marker_color=TOKENS["primary"], name=f"{sku} forecast",
        marker=dict(cornerradius=4),
        hovertemplate="%{x}<br>Forecast: %{y:.0f} units<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=forecast, mode="lines", line=dict(color=TOKENS["primary_dark"], width=2),
        name="Trend", hoverinfo="skip",
    ))

    fig.update_layout(**_base_layout(f"Demand Forecast — {sku}"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
