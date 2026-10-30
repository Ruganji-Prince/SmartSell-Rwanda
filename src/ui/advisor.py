"""Guided farmer workflow; forecasts and economics use the existing backend."""
import pandas as pd
import streamlit as st
from src.forecasting import availability, forecast_row
from src.decision_engine import evaluate_options, waiting_break_even, storage_loss_sensitivity
from src.localization import TEXT, LOSS_SCENARIOS
from src.ui.components import page_intro, market_selection, freshness
from src.ui.data import fitted_model


def compare(row, meta, quantity, loss, storage, other, maximum):
    """Presentation adapter preserving all existing calculations and bands."""
    forecasts = forecast_row(row, meta["selected_model"], fitted_model(meta["selected_model"]))
    bands = {(b["crop"], b["horizon"]): b for b in meta["residual_bands"]}
    forecasts["validation_band_half_width"] = [bands.get((row["product"], int(h)), {}).get("half_width_rwf_kg", float("nan")) for h in forecasts.horizon]
    forecasts["lower_price"] = (forecasts.predicted_price - forecasts.validation_band_half_width).clip(lower=0)
    forecasts["upper_price"] = forecasts.predicted_price + forecasts.validation_band_half_width
    costs, recommendation = evaluate_options(float(row.price), dict(zip(forecasts.horizon.head(maximum), forecasts.predicted_price.head(maximum))), quantity, loss, storage, other)
    return forecasts, costs, recommendation, waiting_break_even(costs)


def _past_example(series, meta, today):
    replay, as_of = False, today
    with st.expander(TEXT["replay_heading"]):
        st.write("Explore a dated example. It does not provide current advice.")
        replay = st.toggle(TEXT["replay_toggle"], key="historical_example")
        if replay:
            examples = series[series.observed_date >= pd.Timestamp(meta["split"]["test_start"])]
            dates = list(reversed(examples.observed_date.dt.date.tolist()))
            if not dates:
                st.info("No held-out past examples are available here. Choose another market.")
                return replay, None
            as_of = st.selectbox(TEXT["replay_date"], dates, format_func=lambda d: d.strftime("%d %B %Y"), key=f"example_date_{series.market_id.iloc[0]}_{series['product'].iloc[0]}")
            st.caption("Only observations dated on or before the decision date are used. Same-day source availability is assumed, not verified.")
    if replay and as_of:
        st.markdown(f'<div class="historical-notice"><strong>Historical example · Decision date: {as_of:%d %B %Y}</strong>{TEXT["replay_notice"]}</div>', unsafe_allow_html=True)
    return replay, as_of


def render(history, vegetables, uses, meta, today, version):
    page_intro(TEXT["advisor_heading"], TEXT["advisor_intro"])
    freshness(history, today)
    st.subheader(TEXT["step_crop"])
    chosen = market_selection(history, "advisor", meta)
    if chosen is None:
        return
    crop, district, market, series = chosen
    replay, as_of = _past_example(series, meta, today)
    if as_of is None:
        return
    st.subheader(TEXT["step_harvest"])
    scenario = st.selectbox(TEXT["scenario"], list(LOSS_SCENARIOS), index=1, key="loss_scenario")
    st.write(TEXT["assumption_note"])
    signature = (crop, district, market, as_of, replay, scenario, version)
    with st.form("harvest_form", border=True):
        c1, c2 = st.columns(2)
        quantity = c1.number_input(TEXT["quantity"], min_value=0.0, value=100.0, step=10.0, key="harvest_quantity")
        loss = c2.number_input(TEXT["loss"], min_value=0.0, max_value=100.0, value=LOSS_SCENARIOS[scenario], step=0.1, help=TEXT["loss_help"], key=f"harvest_loss_{scenario}")
        c1, c2 = st.columns(2)
        storage = c1.number_input(TEXT["storage_cost"], min_value=0.0, value=100.0, step=50.0, help=TEXT["cost_help"], key="harvest_storage")
        other = c2.number_input(TEXT["other_cost"], min_value=0.0, value=0.0, step=50.0, help=TEXT["cost_help"], key="harvest_other")
        maximum = st.selectbox(TEXT["max_wait"], [3, 2, 1], key="harvest_max_wait")
        st.caption("Waiting costs apply to the whole harvest once per day. Selling now has no waiting costs; common sale costs are excluded equally.")
        st.subheader(TEXT["step_check"])
        st.write("Check your entries, then compare selling now with waiting.")
        submitted = st.form_submit_button(TEXT["submit"], type="primary", width="stretch")
    if submitted:
        st.session_state.advisor_submission = dict(signature=signature, quantity=quantity, loss=loss, storage=storage, other=other, maximum=maximum)
    saved = st.session_state.get("advisor_submission")
    if saved and saved["signature"] == signature:
        _result(history, crop, series.market_id.iloc[0], meta, as_of, replay, saved)
    elif saved:
        st.info("Your crop, market, date or storage scenario changed. Check your entries and compare again for an updated result.")
    else:
        st.caption("Your result will appear here after you check the best selling time.")
    with st.expander("Official agriculture statistics for this district"):
        from src.ui.agriculture_context import show_context
        season = st.selectbox("Historical SAS season", ["A", "B", "C"], key="advisor_season")
        show_context(vegetables, uses, district, season)


def _result(history, crop, market_id, meta, as_of, replay, saved):
    if saved["quantity"] <= 0:
        st.error(TEXT["zero_quantity"])
        return
    row, reason = availability(history, crop, market_id, as_of, {tuple(k) for k in meta["eligible_keys"]})
    if reason:
        st.error(TEXT["no_current"])
        with st.expander("Why is a recommendation unavailable?"):
            st.write(reason)
            st.write("A supported market, sufficient history and a same-day observation are required. No price is filled in for a missing date.")
        return
    forecasts, costs, recommendation, thresholds = compare(row, meta, **{key: saved[key] for key in ("quantity", "loss", "storage", "other", "maximum")})
    h = recommendation["horizon"]
    with st.container(key="recommendation"):
        st.caption("YOUR HISTORICAL COMPARISON" if replay else "YOUR SELLING COMPARISON")
        st.subheader(("✅ " if h == 0 else "⏳ ") + recommendation["action"])
        if h == 0:
            st.write("Selling on the decision date gives the highest expected return under the storage conditions you entered. Waiting does not beat selling now; ties favour the earlier sale.")
        else:
            st.write(f"Waiting {h} day(s) may give a higher expected return if the forecast price is reached and your storage-loss and cost estimates are accurate.")
        st.write(f"Decision date: **{as_of:%d %B %Y}** · {saved['quantity']:,.2f} kg · {saved['loss']:g}% assumed daily loss")
    st.caption("Results use your last checked entries. After editing any amount, press Check the best selling time again.")
    now = costs.iloc[0]
    cols = st.columns(4)
    cols[0].metric("Current price on decision date", f"{row.price:,.0f} RWF/kg")
    cols[1].metric("Your quantity", f"{saved['quantity']:,.2f} kg")
    cols[2].metric("Expected revenue if sold now", f"{now.net_revenue_rwf:,.0f} RWF")
    cols[3].metric("Best expected option", "Sell now" if h == 0 else f"Wait {h} day(s)")
    st.subheader("Is waiting worth it?")
    first, predicted = thresholds.iloc[0], forecasts.predicted_price.iloc[0]
    c1, c2 = st.columns(2)
    c1.metric("Tomorrow's forecast", f"{predicted:,.2f} RWF/kg")
    if pd.isna(first.break_even_price):
        c2.metric("Price needed to match selling now", "No finite price")
        st.write("No saleable crop remains after one day under your loss estimate. No future price can make waiting worthwhile.")
    else:
        c2.metric("Price needed to match selling now", f"{first.break_even_price:,.2f} RWF/kg")
        gap = predicted - first.break_even_price
        if "matches" in first.forecast_vs_break_even:
            st.write("The forecast matches the price needed to break even. Selling now wins the tie.")
        else:
            position = "above" if gap > 0 else "below"
            st.write(f"The one-day forecast is **{abs(gap):,.2f} RWF/kg {position}** the price needed to match selling now.")
        st.write(f"A rise of **{first.required_price_increase_percent:.2f}%** would only match selling now after your losses and waiting costs. The price must exceed **{first.break_even_price:,.2f} RWF/kg** for waiting one day to pay more.")
    st.caption("This is the one-day comparison. The recommendation compares all allowed days using full precision; displayed amounts are rounded.")
    st.write(TEXT["uncertainty"])
    with st.expander("See detailed calculation"):
        st.write(recommendation["explanation"])
        st.metric("Expected advantage versus selling now", f"{recommendation['expected_gain_rwf']:,.0f} RWF")
        st.write(f"Checked waiting costs: storage **{saved['storage']:,.0f} RWF/day**, other **{saved['other']:,.0f} RWF/day**, for the whole harvest.")
        st.write("Quantity retained = starting quantity × (1 − daily loss / 100)^days")
        st.write("Net revenue = expected price × retained kg − storage cost − other waiting costs")
        display = costs.merge(thresholds, on="horizon", how="left", validate="one_to_one").rename(columns={
            "horizon": "Days waited", "predicted_price": "Price RWF/kg", "price_change_percent": "Price change %",
            "retained_kg": "Retained kg", "lost_kg": "Lost kg", "storage_cost_rwf": "Storage RWF", "other_cost_rwf": "Other RWF",
            "gross_revenue_rwf": "Gross RWF", "net_revenue_rwf": "Net RWF", "break_even_price": "Break-even RWF/kg",
            "required_price_increase_rwf_kg": "Required uplift RWF/kg", "required_price_increase_percent": "Required uplift %",
            "forecast_vs_break_even": "Forecast versus threshold",
        }).drop(columns="retention_fraction")
        st.dataframe(display.round(2), hide_index=True)
        st.download_button("Download this calculation", display.to_csv(index=False).encode(), file_name="smartsell_scenario.csv", mime="text/csv")
    with st.expander("How reliable is this estimate?"):
        st.write("Data checks passed for this decision date: sufficient training history and recent observations are available. These checks do not measure the probability of profit.")
        st.write(f"Observed price date: **{row.observed_date:%d %B %Y}**. Forecasts and thresholds refer to the decision date above. Historical examples are not current advice.")
        if h:
            low = float(forecasts.loc[forecasts.horizon.eq(h), "lower_price"].iloc[0])
            cautious, _ = evaluate_options(float(row.price), {h: low}, saved["quantity"], saved["loss"], saved["storage"], saved["other"])
            if cautious.iloc[1].net_revenue_rwf <= cautious.iloc[0].net_revenue_rwf:
                st.warning("The suggested gain disappears at the lower empirical price band. Selling now may be safer if you cannot absorb a loss.")
            else:
                st.info("The expected gain remains positive at the lower empirical price band under these assumptions. This is not a guarantee.")
        st.write(f"Selected forecast: **{meta['selected_model']}**. Bands use the 90th percentile of validation absolute errors by crop and horizon, not a guaranteed price range or probability of profit. A zero-width band reflects unchanged validation prices, not certainty.")
        st.dataframe(forecasts[["forecast_date", "horizon", "predicted_price", "lower_price", "upper_price"]].rename(columns={"predicted_price": "Expected price (RWF/kg)", "lower_price": "Empirical lower band", "upper_price": "Empirical upper band"}), hide_index=True)
        st.write("Same-day source availability is assumed, not verified. The chronological benchmark is retrospective; earlier academic exploration inspected parts of the history. See About SmartSell for complete limitations.")
    _sensitivity(float(row.price), saved)


def _sensitivity(price, saved):
    with st.expander("What if more of my crop is lost in storage?"):
        st.write("Compare illustrative daily loss rates, not observed NISR spoilage rates. Your last checked quantity and costs stay fixed; forecasts and historical benchmarks do not change.")
        rates = [col.number_input(f"Scenario {i}: daily loss (%)", min_value=0.0, max_value=100.0, value=rate, step=0.5, key=f"sensitivity_loss_{i}") for i, (col, rate) in enumerate(zip(st.columns(4), [0.0, 1.0, 2.0, 5.0]), 1)]
        sensitivity = storage_loss_sensitivity(price, saved["quantity"], sorted(set(rates)), saved["storage"], saved["other"])
        display = sensitivity.rename(columns={"daily_loss_percent": "Assumed daily loss %", "horizon": "Days waited", "break_even_price": "Break-even RWF/kg", "required_price_increase_rwf_kg": "Required uplift RWF/kg", "required_price_increase_percent": "Required uplift %"})
        st.dataframe(display.round(2), hide_index=True)
        finite = sensitivity[sensitivity.break_even_price.notna()]
        if not finite.empty:
            chart = finite.pivot(index="daily_loss_percent", columns="horizon", values="break_even_price")
            chart.columns = [f"Wait {int(h)} day(s)" for h in chart.columns]
            st.line_chart(chart, x_label="Assumed daily quantity loss (%)", y_label="Break-even future price (RWF/kg)")
        if sensitivity.break_even_price.isna().any():
            st.info("A 100% daily loss leaves no saleable quantity: no finite future price can make waiting worthwhile. Blank cells mean unattainable, not zero.")
        st.write("More crop loss means a higher future price is needed to cover waiting. Better retention lowers that hurdle. This does not claim a measured storage improvement.")
