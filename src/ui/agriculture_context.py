"""Readable NISR sector context with all original category and measurement caveats."""
import pandas as pd
import streamlit as st
from src.utilities import ROOT
from src.ui.components import page_intro


def show_context(vegetables, uses, district, season):
    st.write("**These statistics describe Vegetables as a group, not Tomato or Carrot specifically.** They are official historical statistics, not current market observations.")
    g = vegetables[(vegetables.district == district) & (vegetables.season == season)]
    if not g.empty:
        v = dict(zip(g.indicator, g.value))
        for col, key, label in zip(st.columns(3), ["production_mt", "harvested_area_ha", "yield_kg_ha"], ["Vegetable production (tonnes)", "Harvested area (ha)", "Yield (kg/ha)"]):
            value = v.get(key)
            col.metric(label, f"{value:,.1f}" if pd.notna(value) else "Not reported")
        st.caption(f"{district} · Season {season}, 2024. Published seasonal yields are shown directly; they need not equal a ratio reconstructed from rounded aggregates.")
    else:
        st.info("No vegetable-sector district indicators are available for this selection.")
    st.subheader("How vegetables were used nationally")
    use = uses[(uses.crop_group.str.lower() == "vegetables") & (uses.season == season)]
    selected = use[use.use.isin(["Sold", "Stored", "Post harvesting losses"])][["use", "percent"]]
    labels = {"Sold": "Sold", "Stored": "Stored", "Post harvesting losses": "Post-harvest losses"}
    for col, source_label in zip(st.columns(3), labels):
        values = selected[selected.use.eq(source_label)].percent
        col.metric(labels[source_label], f"{values.iloc[0]:.2f}%" if not values.empty else "Not reported")
    st.write(f"Season {season}, 2024 · Shares of national vegetable-group production. These categories do not show every production use and need not add up to 100%.")
    st.write("Post-harvest losses describe the survey's production-use category, not a measured daily storage-loss rate. The stored share is not a retention probability. These figures do not set the daily loss estimates or storage costs in your selling comparison.")
    with st.expander("See the official context records"):
        st.dataframe(selected.rename(columns={"use": "Production use", "percent": "Share of production (%)"}), hide_index=True)
        st.write("Official vegetable-sector evidence motivates considering storage risk. It does not measure the benefit of any particular storage improvement.")


def render(vegetables, uses):
    page_intro("Agriculture in your area", "Official NISR agricultural statistics help show the broader production conditions in your district.")
    c1, c2 = st.columns(2)
    district = c1.selectbox("District", sorted(vegetables.district.unique()), key="context_district")
    season = c2.selectbox("SAS 2024 season", ["A", "B", "C"], key="context_season")
    show_context(vegetables, uses, district, season)
    with st.expander("Compare vegetable production across districts"):
        ranked = vegetables[(vegetables.season == season) & (vegetables.indicator == "production_mt")].sort_values("value", ascending=False)
        st.bar_chart(ranked.set_index("district")[["value"]], y_label="Production (tonnes)")
    with st.expander("Vegetable-sector sowing windows"):
        sowing = pd.read_csv(ROOT / "data/processed/nisr/sowing_windows.csv")
        timing = sowing[(sowing.entity_type == "crop_group") & (sowing.entity == "Vegetables") & (sowing.season == season)]
        st.dataframe(timing[["sowing_window", "percent"]], hide_index=True)
        st.write("Sowing distributions describe 2024 planting. They do not identify harvest dates or assign a crop season to a later market observation.")
    st.caption("Source: supplied SAS 2024_Annual Tables.xlsx, Tables 13–18, 21–28. Clean CSVs retain table numbers and Excel cell coordinates for review.")
