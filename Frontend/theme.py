"""
Design system — single source of truth for colors, spacing, and the global
CSS injected once from app.py. Components reference TOKENS for inline
styles so the palette never drifts between files.
"""

TOKENS = {
    "bg":        "#FFFFFF",
    "bg_alt":    "#FAFAF8",
    "surface":   "#FFFFFF",
    "border":    "#EBEAF2",
    "text":      "#1A1A2E",
    "text_muted": "#6B6B7B",
    "text_faint": "#A0A0AC",
    "primary":   "#8A5CF6",
    "primary_dark": "#6D28D9",
    "success":   "#22C55E",
    "warning":   "#F59E0B",
    "danger":    "#F43F5E",
    "info":      "#3B82F6",
    "radius_sm": "8px",
    "radius_md": "12px",
    "radius_lg": "16px",
    "shadow_sm": "0 1px 2px rgba(26,26,46,0.05)",
    "shadow_md": "0 4px 16px rgba(26,26,46,0.08)",
    "shadow_lg": "0 12px 32px rgba(26,26,46,0.12)",
}

GLOBAL_CSS = f"""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: {TOKENS['bg']};
  --bg-alt: {TOKENS['bg_alt']};
  --border: {TOKENS['border']};
  --text: {TOKENS['text']};
  --text-muted: {TOKENS['text_muted']};
  --text-faint: {TOKENS['text_faint']};
  --primary: {TOKENS['primary']};
  --primary-dark: {TOKENS['primary_dark']};
  --success: {TOKENS['success']};
  --warning: {TOKENS['warning']};
  --danger: {TOKENS['danger']};
  --radius-sm: {TOKENS['radius_sm']};
  --radius-md: {TOKENS['radius_md']};
  --radius-lg: {TOKENS['radius_lg']};
  --shadow-sm: {TOKENS['shadow_sm']};
  --shadow-md: {TOKENS['shadow_md']};
  --shadow-lg: {TOKENS['shadow_lg']};
}}

html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
h1, h2, h3 {{ font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.02em; }}

/* ── Layout rhythm ─────────────────────────────────────────────────── */
.block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1240px; }}
[data-testid="stVerticalBlock"] > div {{ gap: 0.5rem; }}

/* ── Sidebar ───────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{ background: var(--bg-alt); border-right: 1px solid var(--border); }}
[data-testid="stSidebar"] .stButton button {{
  transition: transform 120ms ease, box-shadow 120ms ease;
}}
[data-testid="stSidebar"] .stButton button:hover {{
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}}

/* ── Buttons — smooth hover/press feedback everywhere ────────────────── */
.stButton button, .stDownloadButton button {{
  border-radius: var(--radius-sm) !important;
  transition: transform 120ms ease, box-shadow 120ms ease, background-color 120ms ease !important;
}}
.stButton button:active {{ transform: scale(0.98); }}

/* ── Tabs ──────────────────────────────────────────────────────────── */
[data-baseweb="tab"] {{ transition: color 150ms ease; font-weight: 600; }}
[data-baseweb="tab-highlight"] {{ background-color: var(--primary) !important; transition: left 200ms ease; }}

/* ── Metrics ───────────────────────────────────────────────────────── */
[data-testid="stMetric"] {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px 16px 10px;
  transition: box-shadow 180ms ease, transform 180ms ease;
}}
[data-testid="stMetric"]:hover {{ box-shadow: var(--shadow-md); transform: translateY(-2px); }}
[data-testid="stMetricValue"] {{ font-weight: 800 !important; }}
[data-testid="stMetricLabel"] {{ color: var(--text-muted) !important; font-size: 12px !important; }}

/* ── Expanders / containers as cards ──────────────────────────────────── */
[data-testid="stExpander"] {{
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 180ms ease;
}}
[data-testid="stExpander"]:hover {{ box-shadow: var(--shadow-md); }}

/* ── Dataframes / tables ───────────────────────────────────────────── */
[data-testid="stDataFrame"] {{ border-radius: var(--radius-md); overflow: hidden; border: 1px solid var(--border); }}

/* ── Embedded iframes (Folium map, coordination map) ──────────────────── */
iframe {{ border-radius: var(--radius-md); border: 1px solid var(--border); }}

/* ── Coordination hub node cards ──────────────────────────────────────── */
.node-card:hover {{ box-shadow: var(--shadow-md); transform: translateY(-2px); }}

/* ── Skeleton shimmer for loading states ──────────────────────────────── */
@keyframes shimmer {{
  0%   {{ background-position: -400px 0; }}
  100% {{ background-position: 400px 0; }}
}}
.skeleton {{
  background: linear-gradient(90deg, #F0EEF8 25%, #F8F7FC 37%, #F0EEF8 63%);
  background-size: 800px 100%;
  animation: shimmer 1.4s ease infinite;
  border-radius: var(--radius-md);
}}

/* ── Fade-in for freshly rendered content ─────────────────────────────── */
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(4px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
.fade-in {{ animation: fadeIn 320ms ease both; }}

/* ── Focus visibility for keyboard navigation (accessibility) ───────────── */
button:focus-visible, [role="button"]:focus-visible, a:focus-visible,
input:focus-visible, [data-baseweb="select"]:focus-within {{
  outline: 2px solid var(--primary) !important;
  outline-offset: 2px !important;
}}

/* ── Responsive tightening for tablet/mobile ──────────────────────────── */
@media (max-width: 900px) {{
  .block-container {{ padding-left: 1rem; padding-right: 1rem; padding-top: 1.25rem; }}
  [data-testid="stMetric"] {{ padding: 10px 12px 8px; }}
}}
@media (max-width: 640px) {{
  h1 {{ font-size: 1.5rem !important; }}
  .block-container {{ padding-left: 0.75rem; padding-right: 0.75rem; }}
}}
</style>
"""
