"""Exercise actual Streamlit page scripts without a browser or login."""
from streamlit.testing.v1 import AppTest
from src.utilities import ROOT
import pytest


def select(app, label, value):
    next(s for s in app.selectbox if s.label == label).select(value).run()
    assert not app.exception


def test_all_pages_render_and_current_advice_is_withheld():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    assert not app.exception
    assert any('INSUFFICIENT DATA' in e.value for e in app.error)
    for page in ['Market Trends','NISR Agricultural Context','Methodology & Limitations']:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page


def test_historical_replay_shows_revenue_and_editable_assumptions():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    select(app,'Crop','Tomato')
    select(app,'District','Nyarugenge')
    select(app,'Market','Nyabugogo')
    app.toggle[0].set_value(True).run()
    assert not app.exception
    assert any('SELL NOW' in e.value for e in app.subheader)
    assert len(app.dataframe)>=3
    revenue=app.dataframe[1].value
    assert revenue['Net RWF'].tolist()==[50000,49400,48805,48214.95]
    assert revenue['Break-even RWF/kg'].iloc[1]==pytest.approx(506.06,abs=.01)
    assert revenue['Required uplift %'].iloc[1]==pytest.approx(1.21,abs=.01)
    sensitivity=app.dataframe[2].value
    assert sorted(sensitivity['Assumed daily loss %'].unique())==[0.,1.,2.,5.]
    next(n for n in app.number_input if n.label=='Scenario 4: daily loss (%)').set_value(100.0).run()
    assert not app.exception
    assert app.dataframe[2].value.query('`Assumed daily loss %` == 100')['Break-even RWF/kg'].isna().all()
    select(app,'Illustrative storage scenario','High (illustrative)')
    assert next(n for n in app.number_input if 'Expected quantity loss' in n.label).value==3.0
    assert app.dataframe[1].value['Break-even RWF/kg'].iloc[1]>506.06
    next(n for n in app.number_input if 'Expected quantity loss' in n.label).set_value(100.0).run()
    assert not app.exception
    assert app.dataframe[1].value['Break-even RWF/kg'].isna().all()
    assert any(m.value=='No finite price' for m in app.metric)
    next(n for n in app.number_input if 'Saleable quantity' in n.label).set_value(0.0).run()
    assert not app.exception
    assert any('greater than zero' in e.value for e in app.error)
