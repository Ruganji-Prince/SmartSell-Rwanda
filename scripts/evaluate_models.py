"""Simulated held-out decisions on complete 0/1/2/3-day observed windows."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from src.utilities import ROOT, save_json
from src.forecasting import load_metadata
from src.decision_engine import evaluate_options

SCENARIOS = [("No loss or cost",0.,0.), ("Illustrative 1% daily loss",1.,100.), ("Illustrative 3% daily loss",3.,100.)]


def main():
    meta = load_metadata()
    test = pd.read_csv(ROOT / "results/test_predictions.csv", parse_dates=["observed_date"])
    all_test = pd.read_csv(ROOT / "data/processed/test_examples_before_eligibility.csv")
    origin_keys = ["product", "market_id", "observed_date"]
    denominator = len(all_test.drop_duplicates(origin_keys))
    rows=[]
    for key, g in test.groupby(origin_keys):
        # Do not select among observed horizons: require all to avoid optimistic missingness.
        if set(g.horizon) != {1,2,3} or g.trailing_7d_count.iloc[0] < 2:
            continue
        crop, market, origin = key
        current = float(g.price.iloc[0])
        forecasts = dict(zip(g.horizon, g[meta['selected_model']]))
        actual = dict(zip(g.horizon,g.target_price))
        for label, loss, cost in SCENARIOS:
            expected, decision = evaluate_options(current, forecasts,100.,loss,cost)
            observed, oracle = evaluate_options(current,actual,100.,loss,cost)
            chosen = float(observed.loc[observed.horizon.eq(decision['horizon']),'net_revenue_rwf'].iloc[0])
            sell = current*100
            best = float(observed.net_revenue_rwf.max())
            rows.append(dict(crop=crop, market_id=market, origin_date=str(origin.date()),scenario=label,
                             quantity_kg=100, daily_loss_percent=loss, storage_cost_rwf_day=cost,
                             recommended_horizon=decision['horizon'], oracle_horizon=oracle['horizon'],
                             sell_now_rwf=sell, chosen_realized_simulated_rwf=chosen, oracle_rwf=best,
                             simulated_difference_rwf=chosen-sell, simulated_regret_rwf=best-chosen))
    detail=pd.DataFrame(rows)
    if detail.empty:
        raise ValueError('No complete held-out windows for decision evaluation')
    detail.to_csv(ROOT / "results/decision_simulations.csv",index=False)
    metrics=[]
    for label, g in detail.groupby('scenario',sort=False):
        metrics.append(dict(scenario=label,n=len(g),eligible_test_origin_denominator=denominator,
                       coverage=len(g)/denominator,mean_simulated_gain_rwf=float(g.simulated_difference_rwf.mean()),
                       median_simulated_gain_rwf=float(g.simulated_difference_rwf.median()),
                       fraction_outperforming_sell_now=float(g.simulated_difference_rwf.gt(1e-8).mean()),
                       wait_fraction=float(g.recommended_horizon.gt(0).mean()),
                       mean_oracle_regret_rwf=float(g.simulated_regret_rwf.mean())))
    pd.DataFrame(metrics).to_csv(ROOT / "results/decision_metrics.csv",index=False)
    save_json(ROOT / "results/decision_evaluation_protocol.json",dict(quantity_kg=100,other_cost_per_day=0,
                  scenarios=SCENARIOS,coverage_denominator="All distinct test origins with at least one exact future target, before eligibility filtering",
                  inclusion="Training-eligible all horizons; >=2 recent observations; all 1/2/3 future dates actually observed",
                  warning="Simulated retrospective decision outcomes; no actual farmer income measured; complete-window selection may be unrepresentative"))
    print(pd.DataFrame(metrics).to_string(index=False))


if __name__=='__main__':
    main()
