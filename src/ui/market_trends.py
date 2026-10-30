"""Observed prices with understandable summaries and optional detailed records."""
import pandas as pd
import streamlit as st
from src.ui.components import page_intro, freshness, market_selection, price_chart


def render(history, today):
    page_intro("Market Prices", "See how observed prices have changed for your crop.")
    freshness(history, today)
    chosen = market_selection(history, "prices")
    if chosen is None:
        return
    crop, district, market, series = chosen
    last = series.iloc[-1]
    window = series[series.observed_date >= last.observed_date - pd.Timedelta(days=30)]
    change = (window.iloc[-1].price / window.iloc[0].price - 1) * 100 if len(window) > 1 and window.iloc[0].price > 0 else None
    cols = st.columns(4)
    cols[0].metric("Latest available price", f"{last.price:,.0f} RWF/kg")
    cols[1].metric("Lowest recent price", f"{window.price.min():,.0f} RWF/kg")
    cols[2].metric("Highest recent price", f"{window.price.max():,.0f} RWF/kg")
    cols[3].metric("Recent change", "Not enough records" if change is None else f"{change:+.1f}%")
    st.write(f"Latest price for this market: **{last.observed_date:%d %B %Y}**. Recent summaries use the 30 calendar days ending on that date, not a live price window.")
    price_chart(series)
    st.caption("Observed prices, not current buyer offers. Dates are irregular; connecting lines do not imply observed prices on missing dates. Recent change compares the first and last observations in the recent window.")
    with st.expander("View detailed price records"):
        st.write(f"{len(window)} observations in the recent window; price standard deviation {window.price.std():,.1f} RWF/kg.")
        st.dataframe(series[["observed_date", "price"]].sort_values("observed_date", ascending=False).rename(columns={"observed_date": "Observation date", "price": "Price (RWF/kg)"}), hide_index=True)
