"""Transparent scenario arithmetic; no hidden crop-specific spoilage defaults."""
from numbers import Real
import math
import pandas as pd


def nonnegative(name, value):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite nonnegative number.")


def evaluate_options(current_price, forecasts, quantity_kg, daily_loss_percent=0,
                     storage_cost_per_day=0, other_cost_per_day=0):
    for name, value in [("Current price", current_price), ("Quantity", quantity_kg),
                        ("Storage cost", storage_cost_per_day), ("Other cost", other_cost_per_day),
                        ("Daily loss", daily_loss_percent)]:
        nonnegative(name, value)
    if quantity_kg == 0 or current_price == 0:
        raise ValueError("Quantity and current price must be greater than zero.")
    if daily_loss_percent > 100:
        raise ValueError("Daily loss must be between 0 and 100 percent.")
    if not forecasts:
        raise ValueError("Missing future price forecasts.")
    for h, price in forecasts.items():
        if isinstance(h, bool) or h not in [1, 2, 3]:
            raise ValueError("Forecast horizons must be 1, 2, or 3 calendar days.")
        nonnegative("Forecast price", price)
    rows = []
    for h, price in [(0, current_price)] + sorted(forecasts.items()):
        retained = quantity_kg * (1 - daily_loss_percent / 100) ** h
        gross = price * retained
        storage = storage_cost_per_day * h
        other = other_cost_per_day * h
        rows.append(dict(horizon=h, predicted_price=price, price_change_percent=(price/current_price-1)*100,
                         retention_fraction=retained/quantity_kg, retained_kg=retained,
                         lost_kg=quantity_kg-retained, storage_cost_rwf=storage, other_cost_rwf=other,
                         gross_revenue_rwf=gross, net_revenue_rwf=gross-storage-other))
    table = pd.DataFrame(rows)
    # Stable order means ties prefer the earliest sale.
    best = table.loc[table.net_revenue_rwf.idxmax()]
    h = int(best.horizon)
    action = "SELL NOW" if h == 0 else f"WAIT {h} DAY" + ("S" if h > 1 else "")
    gain = float(best.net_revenue_rwf - table.iloc[0].net_revenue_rwf)
    explanation = ("Selling now gives the highest expected net revenue (ties favor the earliest sale). "
                   "Any forecast price gain does not outweigh the assumed quantity loss and waiting costs."
                   if h == 0 else f"Waiting {h} day(s) gives {gain:,.0f} RWF more expected net revenue under your assumptions.")
    return table, dict(action=action, horizon=h, expected_gain_rwf=gain, explanation=explanation)


def break_even_price(net_now_rwf, retained_quantity_kg, waiting_cost_rwf):
    """Equality price in RWF/kg. Waiting must exceed it to beat immediate sale.

    A positive immediate sale with zero retained kg has no finite break-even price.
    Reject that denominator here; the UI adapter explicitly labels it unattainable.
    """
    for name,value in [("Sell-now revenue",net_now_rwf), ("Retained quantity",retained_quantity_kg),
                       ("Waiting cost",waiting_cost_rwf)]:
        nonnegative(name,value)
    if retained_quantity_kg == 0:
        raise ValueError("Retained quantity must be greater than zero; no finite break-even price exists.")
    return (net_now_rwf + waiting_cost_rwf) / retained_quantity_kg


def waiting_break_even(options):
    """Add explanatory thresholds to the existing, unchanged revenue calculation.

    Exact thresholds use unrounded whole-lot values. Equality is not a profitable
    wait because the existing decision rule favors the earlier sale on ties.
    """
    now=options.loc[options.horizon.eq(0)].iloc[0]
    records=[]
    for row in options.loc[options.horizon.gt(0)].itertuples(index=False):
        if row.retained_kg == 0:
            threshold=None
            comparison="No finite price: no retained quantity"
        else:
            threshold=break_even_price(float(now.net_revenue_rwf),float(row.retained_kg),
                                       float(row.storage_cost_rwf+row.other_cost_rwf))
            if math.isclose(row.predicted_price,threshold,rel_tol=1e-12,abs_tol=1e-9):
                comparison="Forecast matches break-even; no advantage over selling now"
            elif row.predicted_price > threshold:
                comparison="Forecast above break-even"
            else:
                comparison="Forecast below break-even"
        records.append(dict(horizon=int(row.horizon),break_even_price=threshold,
                  required_price_increase_rwf_kg=None if threshold is None else threshold-now.predicted_price,
                  required_price_increase_percent=None if threshold is None else (threshold/now.predicted_price-1)*100,
                  forecast_vs_break_even=comparison))
    return pd.DataFrame(records)


def storage_loss_sensitivity(current_price, quantity_kg, loss_rates,
                             storage_cost_per_day=0, other_cost_per_day=0):
    """Illustrative user-defined assumptions, never measured loss or new forecasts."""
    if not loss_rates:
        raise ValueError("Choose at least one daily loss assumption.")
    frames=[]
    for rate in loss_rates:
        options,_=evaluate_options(current_price,{1:current_price,2:current_price,3:current_price},
                                  quantity_kg,rate,storage_cost_per_day,other_cost_per_day)
        frame=waiting_break_even(options)
        frame["daily_loss_percent"]=rate
        # No forecast comparison: these are thresholds under alternative assumptions.
        frames.append(frame.drop(columns="forecast_vs_break_even"))
    return pd.concat(frames,ignore_index=True)
