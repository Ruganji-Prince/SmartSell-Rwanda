"""NISR-inspired local palette; no remote assets or government branding."""
import streamlit as st

# Palette reference: statistics.gov.rw custom CivicTheme stylesheets.
CSS = """
<style>
:root { --primary:#005cab; --primary-dark:#143465; --ink:#0d2343;
    --muted:#526171; --paper:#fcfdfc; --line:#d8dfe5; --pale:#edf3f8; }
html { scroll-behavior:auto; }
[data-testid="stAppViewContainer"] { background:var(--paper); }
[data-testid="stMainBlockContainer"] { max-width:1160px; padding:2.25rem 2.5rem 3rem; }
h1,h2,h3 { color:var(--ink); letter-spacing:-.035em; line-height:1.2; }
h1 { font-size:2.65rem; font-weight:750; }
h2 { font-size:1.75rem; }
h3 { font-size:1.2rem; }
p,li,[data-testid="stWidgetLabel"] p { font-size:1.03rem; line-height:1.65; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p,
[data-testid="stCaption"], [data-testid="stCaption"] p { font-size:.9rem; color:#526171 !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaption"] { opacity:1 !important; }
a { color:var(--primary); text-underline-offset:3px; }
[data-testid="stSidebar"] { background:#e6e9eb; border-right:1px solid var(--line); }
[data-testid="stSidebarUserContent"] { padding-top:2rem; }
.brand { display:flex; align-items:center; gap:.7rem; margin-bottom:.4rem; }
.brand-mark { width:42px; height:42px; display:grid; place-items:center; background:var(--primary);
    color:white; border-radius:13px; font-size:1.5rem; }
.brand-name { font-size:1.3rem; font-weight:750; color:var(--ink); }
.brand-sub { color:var(--muted); font-size:.85rem; margin-bottom:2rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding:.7rem .65rem;
    border-radius:9px; margin:.18rem 0; min-height:48px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#dbe5ef; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) { background:#005cab; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p { color:#ffffff; font-weight:700; }
.eyebrow { color:var(--primary); font-size:.8rem; font-weight:750; letter-spacing:.13em;
    text-transform:uppercase; margin-bottom:1rem; }
.st-key-home_hero { background:#e6e9eb; border:1px solid #ccd8e3; border-radius:24px;
    padding:2.6rem; margin-bottom:1.5rem; }
.st-key-home_hero h1 { font-size:clamp(2rem,3.8vw,3.6rem); max-width:650px; }
.hero-copy { color:#37404d; max-width:600px; font-size:1.1rem; }
.journey { margin-top:1.7rem; padding:1.7rem; background:#ffffff; border-radius:18px;
    border:1px solid #ccd8e3; }
.journey-icon { font-size:2.3rem; margin-bottom:1rem; }
.journey h3 { margin:0 0 .8rem; font-size:1.35rem; }
.journey p { color:var(--muted); }
.journey-step { border-top:1px solid var(--line); padding:.8rem 0; color:var(--ink); }
.benefit { padding:1.4rem; background:white; border:1px solid var(--line);
    border-radius:16px; height:100%; min-height:205px; }
.benefit-icon { font-size:1.6rem; margin-bottom:.8rem; }
.benefit h3 { margin:0 0 .65rem; }
.benefit p { color:var(--muted); margin:0; }
.status-strip { display:flex; align-items:center; flex-wrap:wrap; gap:1rem 2.2rem;
    margin:1rem 0 .5rem; padding:1rem 0; border-bottom:1px solid var(--line); }
.status-item span { display:block; color:var(--muted); font-size:.8rem; }
.status-item strong { font-size:.98rem; color:var(--ink); font-weight:650; }
.badge { border-radius:99px; padding:.45rem .8rem; font-size:.85rem; font-weight:650; }
.badge.recent { color:#006a68; background:#e1f3f1; }
.badge.aging { color:#79500f; background:#fbefcf; }
.badge.historical { color:#8e3a2a; background:#f8e9e3; }
.badge.unknown { color:#526171; background:#e6e9eb; }
.freshness-note { color:#745337; padding:.3rem 0 .8rem; font-size:.92rem; }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius:16px; }
[data-testid="stForm"] { border-radius:16px; border-color:var(--line); background:white; padding:1.35rem; }
[data-testid="stMetric"] { border:1px solid var(--line); border-radius:14px; padding:1.2rem;
    background:white; height:100%; }
[data-testid="stMetricValue"] { color:var(--primary-dark); font-size:clamp(1.45rem,2.2vw,2rem); }
[data-testid="stMetricLabel"] { white-space:normal; }
button[kind="primary"],button[kind="primaryFormSubmit"] { background:var(--primary); border-color:var(--primary); }
button[kind="primary"]:hover,button[kind="primaryFormSubmit"]:hover { background:var(--primary-dark); border-color:var(--primary-dark); }
[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button,
[data-testid="stDownloadButton"] button { min-height:48px; padding:.65rem 1.15rem; border-radius:9px; }
button:focus-visible,input:focus-visible { outline:3px solid #855cd7; outline-offset:3px; }
[data-baseweb="select"] > div,[data-testid="stNumberInputContainer"] { min-height:48px; border-radius:9px; }
.st-key-recommendation { background:#edf3f8; border:1px solid #a5c5e1; border-radius:18px; padding:1.6rem; }
.st-key-recommendation h2,.st-key-recommendation h3 { color:var(--primary-dark); font-size:2.3rem; }
.st-key-recommendation p { color:#0d2343; }
.historical-notice { border-left:4px solid #b57d29; background:#fbf1db; color:#644b24;
    padding:1rem 1.2rem; border-radius:0 10px 10px 0; margin:1rem 0; }
.historical-notice strong { display:block; margin-bottom:.3rem; }
.selection { color:var(--primary-dark); background:#edf3f8; padding:.7rem 1rem; border-radius:9px; }
.small-note { color:var(--muted); font-size:.9rem; }
[data-testid="stExpander"] { background:#ffffff; border-radius:12px; border-color:var(--line); }
[data-testid="stExpander"] summary { min-height:48px; }
[data-testid="stDataFrame"] { max-width:100%; }
[data-testid="stVerticalBlock"], [data-testid="stElementContainer"],
[data-testid="stTabs"], [data-baseweb="tab-panel"] { min-width:0; }
[data-testid="stMarkdownContainer"] { min-width:0; max-width:100%; }
[data-testid="stMarkdownContainer"] table { display:block; width:100%; max-width:100%; overflow-x:auto; }
[data-testid="stMarkdownContainer"] pre { max-width:100%; overflow-x:auto; }
.footer { border-top:1px solid var(--line); margin-top:2.5rem; padding-top:1.2rem; color:var(--muted); font-size:.85rem; }
@media (max-width:768px) {
    [data-testid="stMainBlockContainer"] { padding:1.4rem 1rem 2rem; }
    [data-testid="stHorizontalBlock"] { flex-direction:column; gap:1rem; }
    [data-testid="stColumn"] { width:100% !important; flex:1 1 100% !important; min-width:0 !important; }
    .st-key-home_hero { padding:1.4rem; border-radius:17px; }
    .st-key-home_hero h1 { font-size:2.25rem; }
    .journey { display:none; }
    .benefit { min-height:0; }
    .status-strip { gap:.7rem 1.5rem; }
    h1 { font-size:2.1rem; }
    h2 { font-size:1.5rem; }
    [data-testid="stMetricValue"] { font-size:1.75rem; }
    [data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button { width:100%; }
    [data-testid="stForm"] { padding:1rem; }
}
@media (prefers-reduced-motion:reduce) { html { scroll-behavior:auto; } }
</style>
"""


def apply_styles():
    st.markdown(CSS, unsafe_allow_html=True)
