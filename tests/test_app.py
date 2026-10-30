"""Product workflow checks; backend tests and accepted artifacts remain unchanged."""
from datetime import date, timedelta
import os
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from src.utilities import ROOT
from src.localization import TEXT
from src.forecasting import availability, forecast_row, load_metadata
from src.decision_engine import evaluate_options, waiting_break_even
from src.ui.advisor import compare
from src.ui.data import get_latest_data_date, get_data_age_days, get_freshness_status


def start():
    app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=60).run()
    assert not app.exception
    return app


def go(app, page):
    app.sidebar.radio[0].set_value(page).run()
    assert not app.exception, page


def select(app, label, value):
    next(s for s in app.selectbox if s.label == label).select(value).run()
    assert not app.exception


def submit(app):
    next(b for b in app.button if b.label == TEXT['submit']).click().run()
    assert not app.exception


def example(app):
    go(app, 'Sell or Wait')
    select(app, TEXT['crop'], 'Tomato')
    select(app, TEXT['district'], 'Nyarugenge')
    select(app, TEXT['market'], 'Nyabugogo')
    app.toggle[0].set_value(True).run()
    select(app, TEXT['replay_date'], date(2026, 9, 28))


def revenue(app):
    return next(frame.value for frame in app.dataframe if 'Net RWF' in frame.value.columns)


def test_landing_page_and_primary_calls_to_action():
    app = start()
    assert TEXT['home_heading'] in app.title[0].value
    assert not app.exception and not app.error
    assert not app.selectbox and not app.metric
    assert not any('SELL NOW' in h.value for h in app.subheader)
    next(b for b in app.button if b.label == TEXT['check_crop']).click().run()
    assert app.sidebar.radio[0].value == 'Sell or Wait'
    assert app.title[0].value == TEXT['advisor_heading']
    go(app, 'Home')
    next(b for b in app.button if b.label == TEXT['market_cta']).click().run()
    assert app.sidebar.radio[0].value == 'Market Prices'


def test_navigation_all_pages_and_scientific_disclosures():
    app = start()
    for page in ['Sell or Wait', 'Market Prices', 'Agriculture Insights', 'About SmartSell', 'Home']:
        go(app, page)
    go(app, 'Agriculture Insights')
    assert any('Vegetables as a group, not Tomato or Carrot specifically' in m.value for m in app.markdown)
    go(app, 'About SmartSell')
    assert [t.label for t in app.tabs] == ['How it works', 'Data sources', 'Model performance', 'Limitations', 'For researchers']
    assert any('Simulated retrospective' in h.value for h in app.subheader)


def test_rwanda_today_and_dataset_date_are_generated_dynamically(monkeypatch):
    fixed_today = date(2031, 2, 3)
    monkeypatch.setattr('src.utilities.today_rwanda', lambda: fixed_today)
    app = start()
    content = '\n'.join(m.value for m in app.markdown)
    latest = pd.read_csv(ROOT / 'data/processed/history.csv', parse_dates=['observed_date']).observed_date.max().date()
    assert fixed_today.strftime('%d %B %Y') in content
    assert latest.strftime('%d %B %Y') in content
    assert TEXT['stale_notice'] in content
    assert 'Historical data' in content


@pytest.mark.parametrize('age,expected', [(0, 'recent'), (1, 'aging'), (7, 'aging'), (8, 'historical'), (-1, 'unknown')])
def test_freshness_uses_actual_age_and_seven_day_boundary(age, expected):
    today = date(2030, 1, 15)
    latest = today - timedelta(days=age)
    assert get_data_age_days(latest, today) == age
    assert get_freshness_status(latest, today)[0] == expected
    frame = pd.DataFrame({'observed_date': pd.to_datetime([latest])})
    assert get_latest_data_date(frame) == latest
    assert get_freshness_status(None, today)[0] == 'unknown'


def test_stale_current_advice_is_withheld_after_explicit_check(monkeypatch):
    monkeypatch.setattr('src.utilities.today_rwanda', lambda: date(2031, 2, 3))
    app = start()
    go(app, 'Sell or Wait')
    assert not app.error
    submit(app)
    assert any(TEXT['no_current'] in e.value for e in app.error)
    assert not any('SELL NOW' in h.value for h in app.subheader)
    assert not any('Net RWF' in d.value.columns for d in app.dataframe)


def test_guided_historical_example_and_accepted_economic_outputs():
    app = start()
    example(app)
    assert not any('SELL NOW' in h.value for h in app.subheader)
    assert any(TEXT['replay_notice'] in m.value and '28 September 2026' in m.value for m in app.markdown)
    submit(app)
    assert any('SELL NOW' in h.value for h in app.subheader)
    table = revenue(app)
    assert table['Net RWF'].tolist() == [50000, 49400, 48805, 48214.95]
    assert table['Break-even RWF/kg'].iloc[1] == pytest.approx(506.06, abs=.01)
    assert table['Required uplift %'].iloc[1] == pytest.approx(1.21, abs=.01)
    assert any(m.value == '506.06 RWF/kg' for m in app.metric)
    assert any('6.06 RWF/kg below' in m.value for m in app.markdown)
    sensitivity = next(d.value for d in app.dataframe if 'Assumed daily loss %' in d.value.columns)
    assert sorted(sensitivity['Assumed daily loss %'].unique()) == [0., 1., 2., 5.]
    next(n for n in app.number_input if n.label == 'Scenario 4: daily loss (%)').set_value(100.0).run()
    sensitivity = next(d.value for d in app.dataframe if 'Assumed daily loss %' in d.value.columns)
    assert sensitivity.query('`Assumed daily loss %` == 100')['Break-even RWF/kg'].isna().all()


def test_form_results_use_last_submission_and_scenario_changes_invalidate_results():
    app = start()
    example(app)
    submit(app)
    select(app, TEXT['scenario'], 'High loss')
    assert not any('SELL NOW' in h.value for h in app.subheader)
    assert next(n for n in app.number_input if n.label == TEXT['loss']).value == 3.0
    submit(app)
    threshold = revenue(app)['Break-even RWF/kg'].iloc[1]
    assert threshold > 506.06
    next(n for n in app.number_input if n.label == TEXT['loss']).set_value(100.0)
    assert revenue(app)['Break-even RWF/kg'].iloc[1] == threshold
    submit(app)
    assert revenue(app)['Break-even RWF/kg'].iloc[1:].isna().all()
    assert any(m.value == 'No finite price' for m in app.metric)
    select(app, TEXT['crop'], 'Carrot')
    assert not any('SELL NOW' in h.value for h in app.subheader)


def test_zero_quantity_is_rejected_before_comparison():
    app = start()
    example(app)
    next(n for n in app.number_input if n.label == TEXT['quantity']).set_value(0.0)
    submit(app)
    assert any(TEXT['zero_quantity'] in e.value for e in app.error)
    assert not any('SELL NOW' in h.value for h in app.subheader)


@pytest.mark.parametrize('loss,storage,other,maximum', [(0,0,0,3), (1,100,0,3), (3,100,50,2), (100,100,0,1)])
def test_frontend_adapter_matches_existing_backend_exactly(loss, storage, other, maximum):
    history = pd.read_csv(ROOT / 'data/processed/history.csv', parse_dates=['observed_date'])
    meta = load_metadata()
    row, reason = availability(history, 'Tomato', 'Nyarugenge | Nyabugogo', '2026-09-28', {tuple(k) for k in meta['eligible_keys']})
    assert reason is None
    forecasts, costs, recommendation, thresholds = compare(row, meta, 100, loss, storage, other, maximum)
    original_forecasts = forecast_row(row, 'persistence', None)
    pd.testing.assert_frame_equal(forecasts[original_forecasts.columns], original_forecasts)
    expected_costs, expected_recommendation = evaluate_options(500.0, {h:500.0 for h in range(1, maximum+1)}, 100, loss, storage, other)
    pd.testing.assert_frame_equal(costs, expected_costs)
    pd.testing.assert_frame_equal(thresholds, waiting_break_even(expected_costs))
    assert recommendation == expected_recommendation


def test_csv_update_invalidates_ui_asset_cache(tmp_path, monkeypatch):
    from src.ui import data
    for name in data.ASSET_PATHS:
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('observed_date,price\n2030-01-01,100\n' if name.endswith('history.csv') else ('{}' if name.endswith('.json') else 'value\n1\n'), encoding='utf-8')
    monkeypatch.setattr(data, 'ROOT', tmp_path)
    monkeypatch.setattr(data, 'load_metadata', lambda: {})
    data._read_assets.clear()
    first = data.load_assets()
    assert get_latest_data_date(first[0]) == date(2030, 1, 1)
    p = tmp_path / data.ASSET_PATHS[0]
    old_ns = p.stat().st_mtime_ns
    p.write_text('observed_date,price\n2030-02-02,200\n', encoding='utf-8')
    os.utime(p, ns=(old_ns + 1000000000, old_ns + 1000000000))
    second = data.load_assets()
    assert get_latest_data_date(second[0]) == date(2030, 2, 2)
    assert second[-1] != first[-1]
    data._read_assets.clear()
