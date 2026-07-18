import streamlit as st
from theme import TOKENS


def format_currency(v): return f"${v:,.2f}" if v is not None else "N/A"
def format_pct(v):      return f"{v:.1f}%"  if v is not None else "N/A"
def format_kg(v):       return f"{v:,.0f} kg" if v is not None else "N/A"


def delta_badge(current, baseline, good_direction="up"):
    if baseline is None or baseline == 0:
        return ""
    pct = ((current - baseline) / baseline) * 100
    return f"{'▲' if pct >= 0 else '▼'} {abs(pct):.1f}%"


def section_header(title: str, subtitle: str = "", icon: str = ""):
    icon_html = f'<span style="margin-right:8px;">{icon}</span>' if icon else ""
    st.markdown(
        f"""<div class="fade-in" style="margin-bottom:1rem;">
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:20px;
                        font-weight:800;color:{TOKENS['text']};letter-spacing:-0.02em;margin-bottom:3px;">
                {icon_html}{title}
            </div>
            {"" if not subtitle else f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{TOKENS["text_faint"]};">{subtitle}</div>'}
        </div>""",
        unsafe_allow_html=True,
    )


def loading_spinner(message="Fetching from backend..."):
    return st.spinner(message)


def empty_state(message="No data yet — run analysis from the sidebar.", icon="📭"):
    st.markdown(
        f"""<div class="fade-in" style="text-align:center;padding:56px 24px;color:{TOKENS['text_faint']};
                font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;
                border:1.5px dashed {TOKENS['border']};border-radius:{TOKENS['radius_lg']};margin:1rem 0;
                background:{TOKENS['bg_alt']};">
            <div style="font-size:28px;margin-bottom:8px;">{icon}</div>
            {message}
        </div>""",
        unsafe_allow_html=True,
    )


def error_state(message: str, detail: str = "", icon: str = "⚠️"):
    """User-facing error card — for persistent errors (not transient toasts)."""
    detail_html = f'<div style="font-size:11px;color:{TOKENS["text_faint"]};margin-top:6px;">{detail}</div>' if detail else ""
    st.markdown(
        f"""<div class="fade-in" style="padding:16px 18px;border-radius:{TOKENS['radius_md']};
                background:#FFF1F2;border:1px solid #FDA4AF;margin:0.75rem 0;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:18px;">{icon}</span>
                <span style="font-weight:700;color:#BE123C;font-size:13px;">{message}</span>
            </div>
            {detail_html}
        </div>""",
        unsafe_allow_html=True,
    )


def skeleton_block(height: int = 90, count: int = 1, columns: bool = False):
    """Shimmer placeholder shown while a section is loading."""
    if columns:
        cols = st.columns(count)
        for c in cols:
            c.markdown(f'<div class="skeleton" style="height:{height}px;"></div>', unsafe_allow_html=True)
    else:
        for _ in range(count):
            st.markdown(f'<div class="skeleton" style="height:{height}px;margin-bottom:10px;"></div>', unsafe_allow_html=True)


def status_dot(color: str) -> str:
    return f'<span style="width:7px;height:7px;border-radius:50%;background:{color};display:inline-block;"></span>'
