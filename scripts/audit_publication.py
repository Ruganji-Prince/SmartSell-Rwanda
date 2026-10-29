"""Read-only reconstruction of scientific evidence; writes only results/audit/."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import csv
import hashlib
import json
import re
import zipfile
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from src.utilities import ROOT,save_json,sha256
from src.preprocessing import clean_prices,IDENTITY,REQUIRED
from src.feature_engineering import build_history,make_examples,temporal_split,eligible_keys,filter_eligible,FEATURES
from src.forecasting import predict,metrics,macro_mae,residual_bands,forecast_row,availability
from src.decision_engine import evaluate_options

OUT=ROOT/'results/audit'


def audit_app():
    from datetime import date
    from unittest.mock import patch
    from streamlit.testing.v1 import AppTest
    with patch('src.utilities.today_rwanda',return_value=date(2026,10,29)):
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
        assert not app.exception
        live={'errors':[x.value for x in app.error],'warnings':[x.value for x in app.warning]}
        assert any('INSUFFICIENT DATA' in x for x in live['errors'])
        for label,value in [('Crop','Tomato'),('District','Nyarugenge'),('Market','Nyabugogo')]:
            next(s for s in app.selectbox if s.label==label).select(value).run()
        app.toggle[0].set_value(True).run()
        selected=next(s for s in app.selectbox if s.label=='Historical decision date')
        assert selected.value==date(2026,9,28)
        table=app.dataframe[1].value
        np.testing.assert_allclose(table['Net RWF'],[50000,49400,48805,48214.95])
        replay={'selected_date':str(selected.value),'subheaders':[x.value for x in app.subheader],
                 'warnings':[x.value for x in app.warning],
                 'metrics':[dict(label=x.label,value=x.value) for x in app.metric],
                 'forecasts':app.dataframe[0].value.astype(str).to_dict('records'),
                 'revenue_table':table.astype(object).where(pd.notna(table),None).to_dict('records'),
                 'storage_loss_sensitivity':app.dataframe[2].value.to_dict('records')}
        pages={}
        for page in ['Market Trends','NISR Agricultural Context','Methodology & Limitations']:
            app.sidebar.radio[0].set_value(page).run()
            assert not app.exception
            pages[page]={'exception_count':len(app.exception),'dataframe_count':len(app.dataframe)}
        save_json(OUT/'app_walkthrough.json',dict(live_as_of='2026-10-29',live=live,replay=replay,pages=pages,
                  browser_and_mobile_visual_testing='Not performed'))


def main():
    OUT.mkdir(exist_ok=True)
    raw=pd.concat([pd.read_csv(p) for p in sorted((ROOT/'data/raw').glob('*.csv'))],ignore_index=True)
    cleaned,invalid,conflicts,summary=clean_prices(raw)
    crop_rows=[]
    normalized=raw.copy(); normalized['product']=normalized['product'].replace({'Tomatos':'Tomato'})
    for crop,g in normalized.groupby('product'):
        c=cleaned[cleaned['product']==crop]; bad=conflicts[conflicts['product']==crop]
        dates=pd.to_datetime(g.observed_date,errors='coerce'); price=pd.to_numeric(g.price,errors='coerce')
        inv=invalid[invalid['product']==crop]
        crop_rows.append(dict(crop=crop,raw_rows=len(g),clean_rows=len(c),total_rows_removed=len(g)-len(c),
               conflicting_rows_quarantined=len(bad),invalid_rows=len(inv),equal_price_duplicates_removed=len(g)-len(c)-len(bad)-len(inv),
               invalid_dates=int(dates.isna().sum()),missing_or_nonnumeric_price=int(price.isna().sum()),
               nonpositive_or_nonfinite_price=int((price.le(0)|~np.isfinite(price)).sum()),
               first_date=str(c.observed_date.min().date()),last_date=str(c.observed_date.max().date()),
               crop_market_series=c.market_id.nunique(),distinct_dates=c.observed_date.nunique()))
    pd.DataFrame(crop_rows).to_csv(OUT/'cleaning_by_crop.csv',index=False)
    missing=pd.DataFrame({'column':raw.columns,'missing_n':raw.isna().sum().values,'raw_rows':len(raw)})
    missing.to_csv(OUT/'raw_missingness.csv',index=False)
    scrape_lag=(pd.to_datetime(raw.scraped_at,utc=True).dt.tz_convert(None).dt.normalize()-pd.to_datetime(raw.observed_date)).dt.days
    pd.DataFrame({'lag_days':scrape_lag}).value_counts().rename('raw_rows').reset_index().sort_values('lag_days').to_csv(OUT/'scrape_date_lags.csv',index=False)
    market_rows=[]; gaps=[]
    for (crop,market),g in cleaned.groupby(['product','market_id']):
        delta=g.observed_date.diff().dt.days.dropna()
        gaps.extend(dict(crop=crop,market_id=market,gap_days=int(x)) for x in delta)
        market_rows.append(dict(crop=crop,market_id=market,n=len(g),first_date=str(g.observed_date.min().date()),
                      last_date=str(g.observed_date.max().date()),median_gap_days=float(delta.median()) if len(delta) else None,
                      maximum_gap_days=int(delta.max()) if len(delta) else None,
                      fraction_one_day_gaps=float(delta.eq(1).mean()) if len(delta) else None))
    pd.DataFrame(market_rows).to_csv(OUT/'market_history_inventory.csv',index=False)
    gap=pd.DataFrame(gaps)
    gap.groupby(['crop','gap_days']).size().rename('gap_count').reset_index().to_csv(OUT/'observation_gap_distribution.csv',index=False)
    months=pd.date_range(cleaned.observed_date.min().replace(day=1),cleaned.observed_date.max(),freq='MS').strftime('%Y-%m')
    monthly=cleaned.assign(month=cleaned.observed_date.dt.strftime('%Y-%m')).groupby(['product','month']).size().unstack(fill_value=0).reindex(columns=months,fill_value=0)
    monthly.to_csv(OUT/'monthly_observations.csv')
    label_map=[]
    for col in ['product','region','location','unit','channel','currency']:
        for value in raw[col].dropna().unique():
            working=str(value).strip()
            if col=='product' and working=='Tomatos': working='Tomato'
            if col=='region': working=working.title()
            label_map.append(dict(field=col,original=value,normalized=working,changed=str(value)!=working))
    pd.DataFrame(label_map).to_csv(OUT/'normalization_crosswalk.csv',index=False)
    prices=pd.read_csv(ROOT/'data/processed/prices.csv',parse_dates=['observed_date'])
    history=build_history(prices)
    examples=make_examples(history)
    tr,va,te,split=temporal_split(examples)
    keys=eligible_keys(tr)
    train,val,test=[filter_eligible(f,keys).reset_index(drop=True) for f in [tr,va,te]]
    saved=pd.read_csv(ROOT/'results/test_predictions.csv',parse_dates=['observed_date','target_date'])
    pd.testing.assert_frame_equal(test[['product','market_id','observed_date','target_date','horizon','target_price']].reset_index(drop=True),
                                  saved[['product','market_id','observed_date','target_date','horizon','target_price']].reset_index(drop=True),check_dtype=False)
    # Freeze headline artifact hashes; this audit never rewrites the benchmark.
    headline={str(p.relative_to(ROOT)):sha256(p) for p in [ROOT/'results/model_comparison.csv',ROOT/'results/decision_metrics.csv',ROOT/'models/selection.json']}
    comparison=pd.read_csv(ROOT/'results/model_comparison.csv')
    selection=json.loads((ROOT/'models/selection.json').read_text())
    assert selection['selected_model']==comparison[comparison.partition.eq('validation')].sort_values('macro_mae').iloc[0].model=='persistence'
    for name,g in comparison.groupby('model'):
        assert np.isfinite(saved[name]).all()
        independent=metrics(test,saved[name].to_numpy(),name,'test')[0]
        for k in ['mae','rmse','n']:
            assert np.isclose(independent[k],g[g.partition=='test'].iloc[0][k])
    assert np.array_equal(saved.persistence.to_numpy(),saved.price.to_numpy())
    compact=comparison.pivot(index='model',columns='partition',values=['macro_mae','mae','rmse','n'])
    compact.columns=['_'.join(c) for c in compact.columns]
    compact.reset_index().to_csv(OUT/'model_comparison_compact.csv',index=False)
    assert train.target_date.max()<pd.Timestamp(split['validation_start'])
    assert val.target_date.max()<pd.Timestamp(split['test_start'])
    # Exhaustive prefix-invariance across every series: no future values enter features.
    checked=0
    for _,g in prices.groupby(['product','market_id']):
        g=g.sort_values('observed_date')
        split_at=max(1,len(g)//2)
        prefix=build_history(g.iloc[:split_at])
        full=build_history(g).iloc[:split_at]
        numeric=[c for c in FEATURES if c not in ['horizon','product','market_id']]
        np.testing.assert_allclose(prefix[numeric],full[numeric],equal_nan=True)
        checked+=1
    # Coverage waterfall over all clean origins in the fixed test period.
    origins=history[history.observed_date>=pd.Timestamp(split['test_start'])].copy()
    observed={(r.product,r.market_id,r.observed_date):r.price for r in history.itertuples()}
    raw_valid=normalized.copy(); raw_valid['observed_date']=pd.to_datetime(raw_valid.observed_date)
    raw_valid['region']=raw_valid.region.str.strip().str.title(); raw_valid['location']=raw_valid.location.str.strip()
    raw_valid['market_id']=raw_valid.region+' | '+raw_valid.location
    raw_lookup=set(raw_valid[['product','market_id','observed_date']].itertuples(index=False,name=None))
    coverage=[]
    for r in origins.itertuples():
        available=[h for h in [1,2,3] if (r.product,r.market_id,r.observed_date+pd.Timedelta(days=h)) in observed]
        raw_available=[h for h in [1,2,3] if (r.product,r.market_id,r.observed_date+pd.Timedelta(days=h)) in raw_lookup]
        eligible_available=[h for h in available if (r.product,r.market_id,h) in keys]
        all_keys=all((r.product,r.market_id,h) in keys for h in [1,2,3])
        coverage.append(dict(crop=r.product,market_id=r.market_id,origin_date=str(r.observed_date.date()),
                future_observed_n=len(available),future_observed_horizons=','.join(map(str,available)),
                raw_future_n=len(raw_available),eligible_observed_horizons_n=len(eligible_available),
                eligible_all_horizons=all_keys,recent_count=r.trailing_7d_count,
                complete=len(available)==3 and all_keys and r.trailing_7d_count>=2))
    cover=pd.DataFrame(coverage)
    cover.to_csv(OUT/'simulation_origin_coverage.csv',index=False)
    denominator=cover[cover.future_observed_n>0]
    eligible=denominator[denominator.eligible_observed_horizons_n>0]
    complete_targets=eligible[eligible.future_observed_n==3]
    all_eligible=complete_targets[complete_targets.eligible_all_horizons]
    recent=all_eligible[all_eligible.recent_count>=2]
    assert len(recent)==20 and len(denominator)==249
    waterfall=[dict(stage='All clean observed test-period origins',remaining=len(cover),removed_at_stage=0),
       dict(stage='At least one observed exact future price (published coverage denominator)',remaining=len(denominator),removed_at_stage=len(cover)-len(denominator)),
       dict(stage='At least one future target survives horizon-specific training eligibility',remaining=len(eligible),removed_at_stage=len(denominator)-len(eligible)),
       dict(stage='All three future calendar-day prices actually observed',remaining=len(complete_targets),removed_at_stage=len(eligible)-len(complete_targets)),
       dict(stage='Training eligible for all three horizons',remaining=len(all_eligible),removed_at_stage=len(complete_targets)-len(all_eligible)),
       dict(stage='At least two observations in trailing seven days',remaining=len(recent),removed_at_stage=len(all_eligible)-len(recent))]
    pd.DataFrame(waterfall).to_csv(OUT/'simulation_coverage_waterfall.csv',index=False)
    patterns=denominator.groupby(['crop','future_observed_horizons']).size().rename('origins').reset_index()
    patterns.to_csv(OUT/'future_horizon_patterns.csv',index=False)
    # Every displayed NISR number is verified against its workbook source cell.
    workbook=load_workbook(ROOT/'SAS 2024_Annual Tables.xlsx',data_only=True)
    provenance=[]
    veg=pd.read_csv(ROOT/'data/processed/nisr/vegetable_district_context.csv')
    use=pd.read_csv(ROOT/'data/processed/nisr/production_use.csv')
    sowing=pd.read_csv(ROOT/'data/processed/nisr/sowing_windows.csv')
    for _,r in veg.iterrows():
        provenance.append(dict(workbook='SAS 2024_Annual Tables.xlsx',sheet=f'Table {r.table}',source_cell=r.source_cell,year=2024,
                 season=r.season,district=r.district,statistic=r.indicator,value=r.value,
                 unit={'production_mt':'metric tonnes','yield_kg_ha':'kg/ha','harvested_area_ha':'ha'}[r.indicator],
                 interpretation=f'Published Vegetables group {r.indicator}; not Tomato/Carrot-specific'))
    for _,r in use[use.crop_group.str.lower()=='vegetables'].iterrows():
        if r.use not in ['Sold','Stored','Post harvesting losses']: continue
        provenance.append(dict(workbook='SAS 2024_Annual Tables.xlsx',sheet=f'Table {r.table}',source_cell=r.source_cell,year=2024,
                  season=r.season,district='Rwanda (national)',statistic=r.use,value=r.percent,unit='% of vegetable-group production',
                  interpretation='National vegetable-sector production-use share, not district-specific or a daily loss rate'))
    for _,r in sowing[(sowing.entity_type=='crop_group') & (sowing.entity=='Vegetables')].iterrows():
        provenance.append(dict(workbook='SAS 2024_Annual Tables.xlsx',sheet=f'Table {r.table}',source_cell=r.source_cell,year=2024,
                  season=r.season,district='Rwanda (national)',statistic=r.sowing_window,value=r.percent,unit='published sowing-distribution percent',
                  interpretation='Vegetable-sector sowing window, not a measured harvest date or price-observation season'))
    provenance=pd.DataFrame(provenance)
    verified=[]
    for r in provenance.itertuples():
        source=workbook[r.sheet][r.source_cell].value
        verified.append(np.isclose(float(source),r.value) if pd.notna(r.value) else source is None or source=='-')
    provenance['matches_workbook']=verified
    assert all(verified)
    provenance.to_csv(OUT/'nisr_displayed_statistic_register.csv',index=False)
    workbook.close()
    # Independently reconstruct economics, break-even and what-if examples.
    economic=[]
    for h in [0,1,2,3]:
        retained=100*.99**h; costs=h*100
        economic.append(dict(horizon=h,price_rwf_kg=500,retained_kg=retained,loss_kg=100-retained,
                             gross_rwf=500*retained,waiting_cost_rwf=costs,net_rwf=500*retained-costs,
                             break_even_future_price_rwf_kg=(50000+costs)/retained))
    econ=pd.DataFrame(economic)
    computed,action=evaluate_options(500,{1:500,2:500,3:500},100,1,100)
    np.testing.assert_allclose(econ.net_rwf,computed.net_revenue_rwf)
    econ.to_csv(OUT/'manual_economic_trace.csv',index=False)
    sensitivity=[]
    for future in [500.,506.,507.,520.]:
        t,d=evaluate_options(500.,{1:future},100.,1.,100.)
        sensitivity.append(dict(analysis='WHAT-IF SCENARIO; not historical forecast',forecast_1_day_rwf_kg=future,
                  future_net_rwf=float(t.iloc[1].net_revenue_rwf),advantage_vs_sell_now_rwf=float(t.iloc[1].net_revenue_rwf-50000),action=d['action']))
    pd.DataFrame(sensitivity).to_csv(OUT/'what_if_sensitivity.csv',index=False)
    simulations=pd.read_csv(ROOT/'results/decision_simulations.csv')
    decomposition=[]
    for scenario,g in simulations.groupby('scenario',sort=False):
        decomposition.append(dict(scenario=scenario,n=len(g),recommended_wait_n=int(g.recommended_horizon.gt(0).sum()),
                 actual_oracle_wait_n=int(g.oracle_horizon.gt(0).sum()),mean_oracle_regret_rwf=float(g.simulated_regret_rwf.mean()),
                 recommendation_driver='Flat persistence; positive losses/costs penalize waiting, zero-loss/cost ties favor immediate sale'))
    pd.DataFrame(decomposition).to_csv(OUT/'decision_decomposition.csv',index=False)
    # Original-data conflicts may remove origins, not just future dates.
    raw_test_origins=set(raw_valid.loc[raw_valid.observed_date>=pd.Timestamp(split['test_start']),['product','market_id','observed_date']].itertuples(index=False,name=None))
    clean_test_origins=set(origins[['product','market_id','observed_date']].itertuples(index=False,name=None))
    summary.update(dict(cleaning_by_crop=crop_rows,split=split,train_rows=len(train),validation_rows=len(val),test_rows=len(test),
              prefix_invariance_series_checked=checked,nisr_displayed_cells_verified=len(provenance),
              coverage_waterfall=waterfall,simulation_coverage=20/249,
              test_origins_removed_by_cleaning=len(raw_test_origins-clean_test_origins),
              raw_to_clean_future_horizon_cells_lost=int((cover.raw_future_n-cover.future_observed_n).sum()),
              mean_gap_days=float(gap.gap_days.mean()),median_gap_days=float(gap.gap_days.median()),
              one_day_gap_fraction=float(gap.gap_days.eq(1).mean()),maximum_gap_days=int(gap.gap_days.max()),
              gaps_over_seven_days=int(gap.gap_days.gt(7).sum()),
              raw_rows_scraped_after_observation_day=int(scrape_lag.gt(0).sum()),
              publication_availability='WARNING: scrape date does not establish source publication time; all metrics are conditional on same-day availability',
              headline_hashes_unchanged=headline,
              changed_normalizations=pd.DataFrame(label_map).query('changed').to_dict('records')))
    assert all(sha256(ROOT/p)==value for p,value in headline.items())
    save_json(OUT/'scientific_audit.json',summary)
    audit_app()
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
