import math
import pytest
from src.decision_engine import evaluate_options


def test_sell_now_when_price_flat_and_storage_cost_positive():
    table, decision = evaluate_options(500,{1:500,2:500,3:500},100,1,100)
    assert decision['action']=='SELL NOW'
    assert table.iloc[0].net_revenue_rwf==50000


def test_wait_calculation_and_quantity():
    table, decision = evaluate_options(500,{1:520,2:600,3:530},100,1,100,50)
    row=table[table.horizon==2].iloc[0]
    assert row.retained_kg==pytest.approx(98.01)
    assert row.lost_kg==pytest.approx(1.99)
    assert row.net_revenue_rwf==pytest.approx(600*98.01-300)
    assert decision['horizon']==2


def test_price_rise_smaller_than_loss_penalty():
    _, d=evaluate_options(100,{1:101},100,3)
    assert d['horizon']==0


def test_price_rise_larger_than_loss_penalty_zero_cost():
    _, d=evaluate_options(100,{1:120},100,1,0)
    assert d['horizon']==1


def test_tie_prefers_sell_now_and_full_loss():
    _, d=evaluate_options(100,{1:100},10)
    assert d['horizon']==0
    t, d=evaluate_options(100,{1:1000},10,100)
    assert t.iloc[1].retained_kg==0
    assert d['horizon']==0


@pytest.mark.parametrize('kwargs',[
    {'quantity_kg':-1},{'quantity_kg':0},{'quantity_kg':float('nan')},
    {'daily_loss_percent':101},{'daily_loss_percent':-1},{'storage_cost_per_day':-1},
    {'other_cost_per_day':math.inf},{'current_price':0},{'forecasts':{}},
    {'forecasts':{1:-5}},{'forecasts':{4:100}},{'forecasts':{1:float('nan')}}])
def test_invalid_inputs(kwargs):
    args=dict(current_price=100,forecasts={1:100},quantity_kg=10)
    args.update(kwargs)
    with pytest.raises(ValueError): evaluate_options(**args)
