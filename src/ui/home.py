"""Welcoming starting point without technical controls or invented impact claims."""
import streamlit as st
from src.localization import TEXT
from src.ui.components import navigate, freshness


def render(history, today):
    with st.container(key="home_hero"):
        left, right = st.columns([1.55, 1], gap="large")
        with left:
            st.markdown('<div class="eyebrow">SmartSell Rwanda · For your next harvest decision</div>', unsafe_allow_html=True)
            st.title(TEXT["home_heading"])
            st.markdown(f'<p class="hero-copy">{TEXT["home_intro"]}</p>', unsafe_allow_html=True)
            st.button(TEXT["check_crop"], type="primary", on_click=navigate, args=("Sell or Wait",), key="home_crop")
            st.button(TEXT["market_cta"], on_click=navigate, args=("Market Prices",), key="home_prices")
            st.caption("Start with your crop, market and quantity. No account needed.")
        with right:
            st.markdown('''<div class="journey"><div class="journey-icon" aria-hidden="true">🌾</div>
                <h3>Your harvest. Your choice.</h3><p>A clearer way to weigh up selling now or storing a little longer.</p>
                <div class="journey-step">01 &nbsp; Choose your crop &amp; market</div>
                <div class="journey-step">02 &nbsp; Estimate your storage losses</div>
                <div class="journey-step">03 &nbsp; Compare expected returns</div></div>''', unsafe_allow_html=True)
    freshness(history, today)
    benefits = [
        ("💰", "Compare selling options", "See whether selling now or waiting may give better expected revenue."),
        ("📈", "Understand market prices", "Explore observed prices for your crop and market, with their actual dates."),
        ("🌾", "Account for storage losses", "See how much prices would need to rise to cover crop losses and waiting costs."),
    ]
    for col, (icon, title, message) in zip(st.columns(3), benefits):
        col.markdown(f'<div class="benefit"><div class="benefit-icon" aria-hidden="true">{icon}</div><h3>{title}</h3><p>{message}</p></div>', unsafe_allow_html=True)
