"""Public, no-login Streamlit interface. Uses shipped lightweight artifacts."""
import pandas as pd
import streamlit as st
from src.utilities import ROOT, today_rwanda
from src.forecasting import availability, forecast_row, load_metadata
from src.decision_engine import evaluate_options,waiting_break_even,storage_loss_sensitivity
from src.localization import TEXT

st.set_page_config(page_title="SmartSell Rwanda", page_icon="🌱", layout="wide")


@st.cache_data
def assets():
    history = pd.read_csv(ROOT / "data/processed/history.csv", parse_dates=["observed_date"])
    vegetables = pd.read_csv(ROOT / "data/processed/nisr/vegetable_district_context.csv")
    uses = pd.read_csv(ROOT / "data/processed/nisr/production_use.csv")
    return history, vegetables, uses, load_metadata()


@st.cache_resource
def fitted_model(name):
    if name in ["persistence", "rolling_median"]:
        return None
    import joblib
    return joblib.load(ROOT / "models/selected_model.joblib")


def show_context(vegetables, uses, district, season):
    st.subheader(TEXT["context_label"])
    st.caption("Official historical statistics for Vegetables as a group. These are not measurements for Tomato or Carrot, and are not current market observations.")
    g = vegetables[(vegetables.district == district) & (vegetables.season == season)]
    if not g.empty:
        v = dict(zip(g.indicator, g.value))
        cols = st.columns(3)
        for col, key, label in zip(cols, ["production_mt", "harvested_area_ha", "yield_kg_ha"],
                                 ["Vegetables production (tonnes)", "Harvested area (ha)", "Published yield (kg/ha)"]):
            value = v.get(key)
            col.metric(label, f"{value:,.1f}" if pd.notna(value) else "Not reported")
        st.caption(f"{district}, Season {season}, 2024. Published seasonal yields are shown directly; they need not equal a ratio reconstructed from rounded aggregates.")
    else:
        st.info("No vegetable-sector district indicators available for this selection.")
    use = uses[(uses.crop_group.str.lower() == "vegetables") & (uses.season == season)]
    selected = use[use.use.isin(["Sold", "Stored", "Post harvesting losses"])][["use", "percent"]]
    st.write(f"National vegetable-sector use of production — Season {season}, 2024")
    st.dataframe(selected.rename(columns={"use":"Production use", "percent":"Share of production (%)"}), hide_index=True)
    st.caption("Denominator: published vegetable-group production. Post-harvest losses cover the reported production-use category, not a measured storage-only daily loss rate. Stored share is not a retention probability.")
    st.caption('Official vegetable-sector production, yield, area and production-use evidence motivates accounting for storage risk in marketing decisions. It does not supply the daily loss assumptions or storage costs used in your break-even calculation.')


try:
    history, vegetables, uses, meta = assets()
except FileNotFoundError:
    st.error("Prepared assets are missing. Run python scripts/prepare_data.py, then python scripts/train_models.py.")
    st.stop()

st.title(TEXT["title"])
st.write(TEXT["tagline"])
st.caption("NISR 2026 Big Data Hackathon · Track 1: Agricultural Productivity")
latest = history.observed_date.max().date()
st.info(f"Data last updated: {latest:%d %B %Y} (latest observation date). Historical TangaBid exports identify Esoko Rwanda as source. No live price feed.")
today = today_rwanda()
if (today - latest).days > 7:
    st.warning(f"Price data are stale: the newest observation is {(today-latest).days} days old. Current-date recommendations are withheld. Use clearly labelled historical replay to explore the prototype.")

page = st.sidebar.radio("Explore", ["SmartSell Advisor", "Market Trends", "NISR Agricultural Context", "Methodology & Limitations"])
st.sidebar.caption("Decision support under assumptions. Verify a buyer's offered price and actual crop condition before selling or storing.")

if page in ["SmartSell Advisor", "Market Trends"]:
    cols = st.columns(3)
    crop = cols[0].selectbox("Crop", sorted(history["product"].unique(), reverse=True))
    crop_frame = history[history["product"].eq(crop)]
    if page == 'SmartSell Advisor':
        eligible = {tuple(k) for k in meta['eligible_keys']}
        supported = [m for m in crop_frame.market_id.unique() if all((crop,m,h) in eligible for h in [1,2,3])]
        crop_frame = crop_frame[crop_frame.market_id.isin(supported)]
        st.caption('Advisor choices require enough training pairs at all three horizons. Market Trends includes the wider observed market coverage.')
        if crop_frame.empty:
            st.error('INSUFFICIENT DATA — no supported market has enough training pairs for this crop.')
            st.stop()
    district = cols[1].selectbox("District", sorted(crop_frame.region.unique()))
    district_frame = crop_frame[crop_frame.region.eq(district)]
    location = cols[2].selectbox("Market", sorted(district_frame.location.unique()))
    series = district_frame[district_frame.location.eq(location)].sort_values("observed_date")
    market_id = series.market_id.iloc[0]
    last = series.iloc[-1]

if page == "SmartSell Advisor":
    replay = st.toggle("Historical replay (demonstration only)", value=False)
    if replay:
        replay_series = series[series.observed_date >= pd.Timestamp(meta['split']['test_start'])]
        date_options = list(reversed(replay_series.observed_date.dt.date.tolist()))
        if not date_options:
            st.info('No observations in the held-out replay period for this market. Choose another market.')
            st.stop()
        as_of = st.selectbox("Historical decision date", date_options, format_func=lambda d:d.strftime("%d %B %Y"))
        st.warning(f"HISTORICAL REPLAY — decision as of {as_of:%d %B %Y}. This is not advice for today. Only observations dated on or before the selected date are used. Same-day source availability is assumed, not verified.")
    else:
        as_of = today
        st.caption(f"Current decision date: {today:%d %B %Y} (Rwanda time).")
    keys = {tuple(k) for k in meta['eligible_keys']}
    row, reason = availability(history,crop,market_id,as_of,keys)
    if row is not None:
        st.metric("Latest available observed price (RWF/kg)", f"{row.price:,.0f}")
        st.caption(f"Observed on {row.observed_date:%d %B %Y} · age on decision date: {(pd.Timestamp(as_of)-row.observed_date).days} days")
    recent = series[series.observed_date <= pd.Timestamp(as_of)].tail(35)
    st.line_chart(recent.set_index("observed_date")[["price"]], y_label="Observed price (RWF/kg)")
    st.subheader(TEXT['storage_label'])
    st.caption("Illustrative daily quantity-loss assumptions: Low 0.5%, Moderate 1%, High 3%. These defaults are not measured NISR rates. You can change every rate. Loss compounds on remaining quantity each day.")
    c1,c2,c3 = st.columns(3)
    quantity = c1.number_input("Saleable quantity available (kg)", min_value=0.0, value=100.0, step=10.0)
    scenario = c2.selectbox("Illustrative storage scenario", ["Moderate (illustrative)","Low (illustrative)","High (illustrative)","Custom"])
    default = {"Moderate (illustrative)":1.0,"Low (illustrative)":.5,"High (illustrative)":3.0,"Custom":0.0}[scenario]
    loss = c3.number_input("Expected quantity loss per day (%) — assumption", min_value=0.0,max_value=100.0,value=default,step=.1,key=f"loss_{scenario}")
    c1,c2,c3 = st.columns(3)
    storage = c1.number_input("Storage cost (RWF per day, whole lot)",min_value=0.0,value=100.0,step=50.0)
    other = c2.number_input("Other waiting costs (RWF per day, whole lot)",min_value=0.0,value=0.0,step=50.0)
    maximum = c3.selectbox("Maximum waiting time (days)",[3,2,1])
    st.caption("Waiting costs apply once per day to the whole lot. Immediate sale has zero waiting costs; common sale costs are excluded equally from all options.")
    if reason:
        st.error(TEXT['insufficient'])
        st.write(reason)
    elif quantity <= 0:
        st.error("Enter a quantity greater than zero to compare sale options.")
    else:
        forecasts = forecast_row(row,meta['selected_model'],fitted_model(meta['selected_model']))
        bands = {(b['crop'],b['horizon']):b for b in meta['residual_bands']}
        forecasts['validation_band_half_width'] = [bands.get((crop,int(h)),{}).get('half_width_rwf_kg',float('nan')) for h in forecasts.horizon]
        forecasts['lower_price'] = (forecasts.predicted_price-forecasts.validation_band_half_width).clip(lower=0)
        forecasts['upper_price'] = forecasts.predicted_price+forecasts.validation_band_half_width
        st.subheader("Prices for the next three calendar days")
        st.dataframe(forecasts[['forecast_date','horizon','predicted_price','lower_price','upper_price']].rename(columns={
            'predicted_price':'Expected price (RWF/kg)','lower_price':'Empirical lower band','upper_price':'Empirical upper band'}),hide_index=True)
        st.caption(f"Selected forecast: {meta['selected_model']}. Bands use the 90th percentile of validation absolute errors by crop and horizon; future coverage is not guaranteed. A zero-width band reflects unchanged validation prices, not certainty.")
        costs, recommendation = evaluate_options(float(row.price),dict(zip(forecasts.horizon.head(maximum),forecasts.predicted_price.head(maximum))),quantity,loss,storage,other)
        thresholds=waiting_break_even(costs)
        st.caption('Recommendation')
        st.subheader(recommendation['action'])
        st.write('**Why**')
        st.write(recommendation['explanation'])
        st.metric("Expected advantage versus selling now (RWF)", f"{recommendation['expected_gain_rwf']:,.0f}")
        st.write('**Current economics**')
        current_columns=st.columns(3)
        current_columns[0].metric('Saleable quantity (kg)',f'{quantity:,.2f}')
        current_columns[1].metric('Observed price (RWF/kg)',f'{row.price:,.2f}')
        current_columns[2].metric('Sell-now revenue (RWF)',f'{row.price*quantity:,.2f}')
        st.subheader('Will the price rise enough to make waiting worthwhile?')
        st.caption('The break-even price matches selling now after assumed quantity loss and waiting costs. Waiting must exceed this threshold to be more profitable. Equality favors selling now. Displayed thresholds are rounded; calculations use full precision.')
        for column,threshold in zip(st.columns(len(thresholds)),thresholds.itertuples(index=False)):
            label=f'Break-even after {threshold.horizon} day(s) (RWF/kg)'
            if pd.isna(threshold.break_even_price):
                column.metric(label,'No finite price')
                column.caption('No quantity remains to sell under this loss assumption.')
            else:
                column.metric(label,f'{threshold.break_even_price:,.2f}')
                column.caption(f'Required price uplift: {threshold.required_price_increase_rwf_kg:,.2f} RWF/kg ({threshold.required_price_increase_percent:.2f}%) to match selling now. {threshold.forecast_vs_break_even}.')
        first=thresholds.iloc[0]
        if pd.notna(first.break_even_price):
            st.write(f"To justify waiting one day under your current storage assumptions, tomorrow's price must exceed **{first.break_even_price:,.2f} RWF/kg** (about **{first.required_price_increase_percent:.2f}%** above the current price). The forecast is **{forecasts.predicted_price.iloc[0]:,.2f} RWF/kg**.")
        st.write('**Waiting economics**')
        st.write("Quantity retained = starting quantity × (1 − daily loss / 100)^days")
        st.write("Net revenue = expected price × retained kg − storage cost − other waiting costs")
        display = costs.merge(thresholds,on='horizon',how='left',validate='one_to_one').rename(columns={'horizon':'Days waited','predicted_price':'Price RWF/kg','price_change_percent':'Price change %',
            'retained_kg':'Retained kg','lost_kg':'Lost kg','storage_cost_rwf':'Storage RWF','other_cost_rwf':'Other RWF',
            'gross_revenue_rwf':'Gross RWF','net_revenue_rwf':'Net RWF','break_even_price':'Break-even RWF/kg',
            'required_price_increase_rwf_kg':'Required uplift RWF/kg','required_price_increase_percent':'Required uplift %',
            'forecast_vs_break_even':'Forecast versus threshold'}).drop(columns='retention_fraction')
        st.dataframe(display.round(2),hide_index=True)
        st.download_button("Download this scenario calculation",display.to_csv(index=False).encode(),file_name="smartsell_scenario.csv",mime="text/csv")
        st.subheader('Data confidence')
        st.caption(f'Observation date: {row.observed_date:%d %B %Y}. Forecasts and thresholds refer to this decision date; historical replay is not current advice. Empirical forecast-error bands appear above and do not guarantee the future price or profit. Storage loss and costs remain your assumptions.')
        h = recommendation['horizon']
        if h:
            low = float(forecasts.loc[forecasts.horizon.eq(h),'lower_price'].iloc[0])
            cautious = low * quantity * (1-loss/100)**h - h*(storage+other) - row.price*quantity
            if cautious <= 0:
                st.warning("Low decision confidence: the suggested gain disappears at the lower empirical price band. Selling now may be safer if you cannot absorb a loss.")
            else:
                st.info("The expected gain remains positive at the lower empirical price band under these assumptions. This is not a guarantee.")
        else:
            st.info("Data-quality indicator: supported market, sufficient training pairs, and recent local history. SELL NOW maximizes point-estimate revenue; future market prices and crop condition remain uncertain.")
        st.subheader('Storage-loss sensitivity — illustrative/user-defined scenarios')
        st.caption('Edit the daily loss assumptions below. Defaults 0%, 1%, 2% and 5% are illustrative, not observed NISR spoilage rates. Quantity and waiting costs stay as entered above. These scenarios change break-even thresholds, not the selected forecast or historical benchmark.')
        sensitivity_rates=[]
        for i,(column,default_rate) in enumerate(zip(st.columns(4),[0.0,1.0,2.0,5.0]),1):
            sensitivity_rates.append(column.number_input(f'Scenario {i}: daily loss (%)',min_value=0.0,max_value=100.0,value=default_rate,step=.5,key=f'sensitivity_loss_{i}'))
        sensitivity=storage_loss_sensitivity(float(row.price),quantity,sorted(set(sensitivity_rates)),storage,other)
        sensitivity_display=sensitivity.rename(columns={'daily_loss_percent':'Assumed daily loss %','horizon':'Days waited',
            'break_even_price':'Break-even RWF/kg','required_price_increase_rwf_kg':'Required uplift RWF/kg',
            'required_price_increase_percent':'Required uplift %'})
        st.dataframe(sensitivity_display.round(2),hide_index=True)
        finite=sensitivity[sensitivity.break_even_price.notna()]
        if not finite.empty:
            chart=finite.pivot(index='daily_loss_percent',columns='horizon',values='break_even_price')
            chart.columns=[f'Wait {int(h)} day(s)' for h in chart.columns]
            st.line_chart(chart,x_label='Assumed daily quantity loss (%)',y_label='Break-even future price (RWF/kg)')
        if sensitivity.break_even_price.isna().any():
            st.info('A 100% daily loss leaves no saleable quantity: no finite future price can make waiting worthwhile. Blank sensitivity cells mean unattainable, not zero.')
        st.write('Under the same price, quantity and costs, higher assumed deterioration raises the future price needed to justify waiting. Better retention lowers that hurdle. This shows the economic role of post-harvest management without claiming a measured storage improvement.')
    with st.expander("Official vegetable-sector context for this district"):
        season=st.selectbox("Historical SAS season",['A','B','C'])
        show_context(vegetables,uses,district,season)

elif page == "Market Trends":
    st.subheader(f"{crop} · {location}, {district}")
    st.metric("Latest available observed price (RWF/kg)",f"{last.price:,.0f}")
    st.caption(f"Observed on {last.observed_date:%d %B %Y}. Irregular observation dates; connecting lines do not imply observed prices on missing dates.")
    st.line_chart(series.set_index('observed_date')[['price']],y_label='RWF/kg')
    window=series[series.observed_date >= last.observed_date-pd.Timedelta(days=30)]
    st.write(f"Last 30 calendar days ending at the latest observation: {len(window)} observations; price standard deviation {window.price.std():,.1f} RWF/kg.")
    st.dataframe(series[['observed_date','price']].sort_values('observed_date',ascending=False),hide_index=True)

elif page == "NISR Agricultural Context":
    c1,c2=st.columns(2)
    district=c1.selectbox('District',sorted(vegetables.district.unique()))
    season=c2.selectbox('SAS 2024 season',['A','B','C'])
    show_context(vegetables,uses,district,season)
    st.subheader('District patterns: Vegetables production')
    ranked=vegetables[(vegetables.season==season)&(vegetables.indicator=='production_mt')].sort_values('value',ascending=False)
    st.bar_chart(ranked.set_index('district')[['value']],y_label='Production (tonnes)')
    sowing=pd.read_csv(ROOT/'data/processed/nisr/sowing_windows.csv')
    timing=sowing[(sowing.entity_type=='crop_group')&(sowing.entity=='Vegetables')&(sowing.season==season)]
    with st.expander('Vegetable-sector sowing windows'):
        st.dataframe(timing[['sowing_window','percent']],hide_index=True)
        st.caption('Sowing distributions describe 2024 planting. They do not identify harvest dates or assign a crop season to a later market observation.')
    st.caption('Source: supplied SAS 2024_Annual Tables.xlsx, Tables 13–18, 21–28. Clean CSVs retain table numbers and Excel cell coordinates for review.')

else:
    st.subheader('How SmartSell works')
    st.markdown((ROOT/'docs/METHODOLOGY.md').read_text(encoding='utf-8'))
    st.subheader('Measured forecast comparison')
    st.dataframe(pd.read_csv(ROOT/'results/model_comparison.csv').round(3),hide_index=True)
    st.subheader('Simulated retrospective decision outcomes')
    st.dataframe(pd.read_csv(ROOT/'results/decision_metrics.csv').round(3),hide_index=True)
    st.markdown((ROOT/'docs/ASSUMPTIONS_AND_LIMITATIONS.md').read_text(encoding='utf-8'))

st.divider()
st.caption('SmartSell Rwanda · Farmer assumptions are editable scenarios. No claim of realized farmer income, live data, NISR partnership, or policy endorsement.')
