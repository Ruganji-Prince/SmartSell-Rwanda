"""Previously missing critical forecast, extraction, and freshness boundaries."""
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from src.utilities import ROOT
from src.forecasting import forecast_row,availability,make_model
from src.feature_engineering import build_history,FEATURES,NUMERIC
from src.nisr_context import extract_annual_tables
from scripts.quality_check import verification_failed
from scripts.publication_files import publication_file
from pathlib import Path


def test_persistence_forecasts_are_exact_prices_and_calendar_dates():
    history=pd.read_csv(ROOT/'data/processed/history.csv',parse_dates=['observed_date'])
    row=history[(history['product']=='Tomato')&(history.market_id=='Nyarugenge | Nyabugogo')].iloc[-1]
    predictions=forecast_row(row,'persistence',None)
    assert predictions.predicted_price.tolist()==[500.,500.,500.]
    assert predictions.forecast_date.dt.strftime('%Y-%m-%d').tolist()==['2026-09-29','2026-09-30','2026-10-01']


def test_real_nisr_extractor_preserves_source_values_and_empty_quarantine_schema(tmp_path):
    workbook=ROOT/'SAS 2024_Annual Tables.xlsx'
    veg,use=extract_annual_tables(workbook,tmp_path)
    source=load_workbook(workbook,data_only=True)
    for r in veg.itertuples():
        assert np.isclose(r.value,source[f'Table {r.table}'][r.source_cell].value)
    row=use[(use.crop_group=='Vegetables')&(use.season=='A')&(use.use=='Post harvesting losses')].iloc[0]
    assert np.isclose(row.percent,source[f'Table {row.table}'][row.source_cell].value)
    assert pd.read_csv(tmp_path/'quarantine.csv').empty
    source.close()


def test_training_preprocessor_uses_training_medians_and_accepts_unseen_market():
    prices=pd.DataFrame({'product':['Tomato']*30,'market_id':['Training market']*30,
                        'price':np.arange(100.,130.),'observed_date':pd.date_range('2026-01-01',periods=30)})
    history=build_history(prices); history['horizon']=1
    model=make_model('hist_gradient_boosting')
    model.fit(history[FEATURES],history.price+1)
    imputer=model.named_steps['preprocessor'].named_transformers_['numeric']
    assert np.isclose(imputer.statistics_[NUMERIC.index('price')],history.price.median())
    assert set(model.named_steps['preprocessor'].named_transformers_['category'].categories_[1])=={'Training market'}
    unseen=history.tail(1).copy(); unseen['market_id']='Never fitted market'
    assert np.isfinite(model.predict(unseen[FEATURES])).all()
    assert set(model.named_steps['preprocessor'].named_transformers_['category'].categories_[1])=={'Training market'}


def test_freshness_boundary_is_seven_days_and_same_day_required():
    history=build_history(pd.DataFrame({'product':['Tomato']*2,'market_id':['Test']*2,
              'price':[100.,101.],'observed_date':pd.to_datetime(['2026-01-01','2026-01-02'])}))
    keys={('Tomato','Test',h) for h in [1,2,3]}
    assert 'No price observed' in availability(history,'Tomato','Test','2026-01-09',keys)[1]
    assert '8 days old' in availability(history,'Tomato','Test','2026-01-10',keys)[1]
    assert availability(history,'Tomato','Test','2026-01-02',keys)[1] is None


def test_quality_gate_cannot_report_pass_with_recorded_test_or_startup_failure():
    assert verification_failed({'automated_tests':{'failures':1,'errors':0}})
    assert verification_failed({'automated_tests':{'failures':0,'errors':1}})
    assert verification_failed({'streamlit_startup':{'/':500}})
    assert not verification_failed({'automated_tests':{'failures':0,'errors':0},'streamlit_startup':{'/':200}})


def test_publication_boundary_excludes_private_and_local_files():
    for relative in ['README.md','app.py','.streamlit/config.toml','data/raw/prices.csv','student_cards/README.md','docs/legacy_aisd/README.md']:
        assert publication_file(Path(relative))
    for relative in ['.venv/pyvenv.cfg','.env','.streamlit/secrets.toml','docs/.env.production',
                     'student_cards/student-id.pdf','student_cards/private/README.md','src/private.key',
                     '.aws/credentials','DHS2000_HIV.pdf','local-notes.md','dist/build.zip','src/__pycache__/x.pyc']:
        assert not publication_file(Path(relative))
