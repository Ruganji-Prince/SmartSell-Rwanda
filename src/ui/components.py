"""Small, reusable, accessible presentation elements."""
from html import escape
import streamlit as st
import altair as alt
from src.localization import TEXT
from src.ui.data import get_latest_data_date, get_freshness_status


def navigate(page):
    st.session_state.navigation = page


def freshness(history, today):
    latest = get_latest_data_date(history)
    code, label = get_freshness_status(latest, today)
    symbols = {"recent": "🟢", "aging": "🟠", "historical": "🔴", "unknown": "○"}
    latest_text = latest.strftime("%d %B %Y") if latest else "Not available"
    st.markdown(f'''<div class="status-strip" aria-label="Market data freshness">
        <div class="status-item"><span>Today · Rwanda</span><strong>{today:%d %B %Y}</strong></div>
        <div class="status-item"><span>Latest market data</span><strong>{latest_text}</strong></div>
        <div class="badge {code}">{symbols[code]} {label}</div></div>''', unsafe_allow_html=True)
    if code == "historical":
        st.markdown(f'<div class="freshness-note">{TEXT["stale_notice"]}</div>', unsafe_allow_html=True)
    elif code == "unknown":
        st.info("A valid market observation date is needed before checking a recommendation.")
    return code


def selection(crop, district, market):
    st.markdown(f'<p class="selection"><strong>{escape(crop)}</strong> · {escape(market)}, {escape(district)}</p>', unsafe_allow_html=True)


def market_selection(history, prefix, meta=None):
    cols = st.columns(3)
    crop = cols[0].selectbox(TEXT["crop"], sorted(history["product"].unique(), reverse=True), key=f"{prefix}_crop")
    frame = history[history["product"].eq(crop)]
    if meta is not None:
        eligible = {tuple(k) for k in meta["eligible_keys"]}
        supported = [m for m in frame.market_id.unique() if all((crop, m, h) in eligible for h in (1, 2, 3))]
        frame = frame[frame.market_id.isin(supported)]
    if frame.empty:
        st.info("There is not enough price history to compare selling options for this crop yet.")
        return None
    district = cols[1].selectbox(TEXT["district"], sorted(frame.region.unique()), key=f"{prefix}_district")
    district_frame = frame[frame.region.eq(district)]
    market = cols[2].selectbox(TEXT["market"], sorted(district_frame.location.unique()), key=f"{prefix}_market")
    series = district_frame[district_frame.location.eq(market)].sort_values("observed_date")
    selection(crop, district, market)
    return crop, district, market, series


def price_chart(series):
    chart = alt.Chart(series[["observed_date", "price"]]).mark_line(color="#005cab", point=alt.OverlayMarkDef(color="#005cab")).encode(
        x=alt.X("observed_date:T", title="Observation date", axis=alt.Axis(format="%d %b", labelAngle=-30, tickCount=5)),
        y=alt.Y("price:Q", title="Price (RWF/kg)", scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("observed_date:T", title="Observed", format="%d %B %Y"), alt.Tooltip("price:Q", title="RWF/kg", format=",.0f")],
    ).properties(height=280)
    st.altair_chart(chart, width="stretch")


def page_intro(title, message):
    st.title(title)
    st.write(message)


def footer():
    st.markdown('<div class="footer">🌱 SmartSell Rwanda · A comparison under your assumptions, not a guaranteed price or profit.<br>Historical market data. No claim of realized farmer-income improvement, live data, NISR partnership or policy endorsement.</div>', unsafe_allow_html=True)
