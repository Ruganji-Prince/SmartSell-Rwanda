"""Economic thresholds explain the unchanged decision engine."""
import math
import pandas as pd
import pytest
from src.decision_engine import evaluate_options,break_even_price,waiting_break_even,storage_loss_sensitivity


def thresholds(loss=0,cost=0,other=0):
    options,_=evaluate_options(500,{1:500,2:500,3:500},100,loss,cost,other)
    return waiting_break_even(options)


def test_zero_deterioration_and_zero_cost_matches_current_price_not_profit():
    result=thresholds()
    assert result.break_even_price.tolist()==[500,500,500]
    assert result.required_price_increase_percent.tolist()==[0,0,0]
    assert result.forecast_vs_break_even.str.contains('matches break-even').all()


@pytest.mark.parametrize('h',[1,2,3])
def test_daily_compounding_and_all_waiting_costs_are_included(h):
    row=thresholds(1,100,50).query('horizon==@h').iloc[0]
    expected=(50000+150*h)/(100*.99**h)
    assert row.break_even_price==pytest.approx(expected)
    assert row.required_price_increase_rwf_kg==pytest.approx(expected-500)
    assert row.required_price_increase_percent==pytest.approx((expected/500-1)*100)


def test_positive_deterioration_requires_uplift_without_cost():
    result=thresholds(1)
    assert result.iloc[0].break_even_price==pytest.approx(500/.99)
    assert result.break_even_price.is_monotonic_increasing


def test_zero_deterioration_positive_storage_cost():
    assert thresholds(0,100).break_even_price.tolist()==[501,502,503]


@pytest.mark.parametrize('retained',[-1,0,float('nan'),float('inf')])
def test_invalid_retained_quantity_is_rejected(retained):
    with pytest.raises(ValueError): break_even_price(50000,retained,100)


def test_complete_loss_is_explicitly_unattainable_not_divided_by_zero():
    result=thresholds(100,100)
    assert result.break_even_price.isna().all()
    assert result.required_price_increase_percent.isna().all()
    assert result.forecast_vs_break_even.str.contains('No finite price').all()


def test_sensitivity_monotonic_in_loss_and_storage_cost():
    rates=[0.,1.,2.,5.]
    cheap=storage_loss_sensitivity(500,100,rates,100)
    expensive=storage_loss_sensitivity(500,100,rates,200)
    for h in [1,2,3]:
        assert cheap[cheap.horizon==h].break_even_price.is_monotonic_increasing
    assert (expensive.break_even_price>=cheap.break_even_price).all()


def test_break_even_equality_and_prices_above_below_agree_with_existing_decision():
    threshold=break_even_price(50000,99,100)
    # Exact equality is independently verified by the revenue identity.
    assert threshold*99-100==pytest.approx(50000)
    _,below=evaluate_options(500,{1:506},100,1,100)
    _,above=evaluate_options(500,{1:507},100,1,100)
    assert below['action']=='SELL NOW'
    assert above['action']=='WAIT 1 DAY'
    assert above['expected_gain_rwf']==93


def test_explanation_does_not_modify_validated_options():
    options,_=evaluate_options(500,{1:500,2:500,3:500},100,1,100)
    original=options.copy(deep=True)
    waiting_break_even(options)
    pd.testing.assert_frame_equal(original,options)
