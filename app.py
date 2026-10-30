"""SmartSell Rwanda: guided frontend over the validated forecast and decision engine."""
import streamlit as st
from src.utilities import today_rwanda
from src.localization import NAVIGATION
from src.ui.data import load_assets
from src.ui.styles import apply_styles
from src.ui.components import footer
from src.ui import home, advisor, market_trends, agriculture_context, about

st.set_page_config(page_title="SmartSell Rwanda", page_icon="🌱", layout="wide", initial_sidebar_state="auto")
apply_styles()

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark" aria-hidden="true">🌱</span><span class="brand-name">SmartSell Rwanda</span></div><div class="brand-sub">A little clarity for your harvest.</div>', unsafe_allow_html=True)
    page = st.radio("Go to", list(NAVIGATION), format_func=NAVIGATION.get, key="navigation", label_visibility="collapsed")
    st.divider()
    st.write("Your crop. Your market. Your decision.")
    st.caption("Check a buyer's offered price and the condition of your crop before selling or storing.")
    st.button("Refresh market data", help="Reloads the local files if they changed. There is no live price feed.")
    st.caption("English · Local data, no live feed")

try:
    history, vegetables, uses, meta, version = load_assets()
except (FileNotFoundError, ValueError, KeyError):
    st.error("Market information is temporarily unavailable. Please ask the person maintaining this app to check the prepared data files.")
    st.stop()

today = today_rwanda()
if page == "Home":
    home.render(history, today)
elif page == "Sell or Wait":
    advisor.render(history, vegetables, uses, meta, today, version)
elif page == "Market Prices":
    market_trends.render(history, today)
elif page == "Agriculture Insights":
    agriculture_context.render(vegetables, uses)
else:
    about.render()
footer()
