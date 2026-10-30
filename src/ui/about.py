"""Full scientific evidence remains accessible away from the main workflow."""
import pandas as pd
import streamlit as st
from src.utilities import ROOT
from src.ui.components import page_intro


def render():
    page_intro("About SmartSell", "Understand the comparison, where the data comes from, and what the results can and cannot tell you.")
    how, sources, performance, limitations, research = st.tabs(["How it works", "Data sources", "Model performance", "Limitations", "For researchers"])
    with how:
        st.subheader("A price rise is only part of the story")
        st.write("SmartSell compares selling your harvest on the decision date with waiting one, two or three days. Waiting may mean fewer saleable kg and extra costs. A higher price only helps if it covers both.")
        st.write("You choose the quantity, daily crop-loss estimate, costs and maximum waiting time. The existing forecast and decision engine calculate expected net revenue. If two options are equal, the earlier sale wins.")
        st.write("The price needed to break even only matches selling now. Waiting must exceed it to provide an advantage. Forecasts are uncertain and storage-loss values are your assumptions.")
        st.info("Historical examples use past data and are not advice for today. A current recommendation requires a same-day observation; prices more than seven days old are marked historical.")
    with sources:
        st.markdown((ROOT / "docs/DATA_SOURCES.md").read_text(encoding="utf-8"))
    with performance:
        st.subheader("Measured forecast comparison")
        st.write("The selected model remains Persistence. These are recorded retrospective results, not a promise of future accuracy or income.")
        st.dataframe(pd.read_csv(ROOT / "results/model_comparison.csv").round(3), hide_index=True)
        st.subheader("Simulated retrospective decision outcomes")
        st.dataframe(pd.read_csv(ROOT / "results/decision_metrics.csv").round(3), hide_index=True)
        st.markdown((ROOT / "docs/DECISION_EVALUATION.md").read_text(encoding="utf-8"))
    with limitations:
        st.markdown((ROOT / "docs/ASSUMPTIONS_AND_LIMITATIONS.md").read_text(encoding="utf-8"))
    with research:
        st.subheader("Methodology and evidence")
        st.markdown((ROOT / "docs/METHODOLOGY.md").read_text(encoding="utf-8"))
        with st.expander("Detailed model evaluation"):
            st.markdown((ROOT / "docs/MODEL_EVALUATION.md").read_text(encoding="utf-8"))
        st.caption("NISR 2026 Big Data Hackathon · Track 1: Agricultural Productivity. No government partnership, endorsement or realized farmer-income improvement is claimed.")
