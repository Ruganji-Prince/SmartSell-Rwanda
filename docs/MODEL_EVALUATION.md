# Forecast evaluation

Selected model: **persistence**, chosen using macro validation MAE (equal weight to each crop/horizon group), before examining the test metrics. Persistence forecasts the latest origin price for each future day; this has lower MAE than the tested tree models here. This does not establish that prices never change.

| model | partition | macro_mae | mae | rmse | n | macro_mae_difference_vs_persistence | selected |
| --- | --- | --- | --- | --- | --- | --- | --- |
| persistence | validation | 48.999 | 48.693 | 84.773 | 657 | 0.000 | True |
| rolling_median | validation | 59.058 | 58.871 | 91.845 | 657 | 10.060 | False |
| hist_gradient_boosting | validation | 54.879 | 54.602 | 79.304 | 657 | 5.880 | False |
| xgboost | validation | 55.067 | 54.807 | 78.540 | 657 | 6.068 | False |
| persistence | test | 41.682 | 41.245 | 80.477 | 314 | 0.000 | True |
| rolling_median | test | 44.116 | 43.928 | 80.658 | 314 | 2.434 | False |
| hist_gradient_boosting | test | 59.913 | 59.882 | 86.213 | 314 | 18.231 | False |
| xgboost | test | 55.209 | 55.201 | 83.484 | 314 | 13.527 | False |

Validation begins 2026-01-31; test begins 2026-05-09. Purged, eligible rows: 4734 training, 657 validation, 314 test. The final model is training-only, not refit after testing. Numerical preprocessing and category encoding fit each training partition. Three expanding-window diagnostic folds appear in `results/expanding_window_metrics.csv`.

## Selected model by crop and horizon

| model | partition | crop | horizon | n | mae | rmse | directional_accuracy_on_changes | changed_target_n | unchanged_target_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| persistence | validation | Carrot | 1 | 117 | 43.043 | 76.015 | 0.000 | 50 | 0.573 |
| persistence | validation | Carrot | 2 | 107 | 56.150 | 94.256 | 0.000 | 53 | 0.505 |
| persistence | validation | Carrot | 3 | 110 | 58.800 | 88.711 | 0.000 | 59 | 0.464 |
| persistence | validation | Tomato | 1 | 118 | 32.686 | 67.940 | 0.000 | 39 | 0.669 |
| persistence | validation | Tomato | 2 | 100 | 45.190 | 85.149 | 0.000 | 38 | 0.620 |
| persistence | validation | Tomato | 3 | 105 | 58.124 | 95.593 | 0.000 | 47 | 0.552 |
| persistence | test | Carrot | 1 | 64 | 34.375 | 73.421 | 0.000 | 19 | 0.703 |
| persistence | test | Carrot | 2 | 46 | 47.826 | 99.455 | 0.000 | 14 | 0.696 |
| persistence | test | Carrot | 3 | 45 | 51.133 | 84.188 | 0.000 | 21 | 0.533 |
| persistence | test | Tomato | 1 | 66 | 42.167 | 80.894 | 0.000 | 23 | 0.652 |
| persistence | test | Tomato | 2 | 48 | 36.812 | 71.849 | 0.000 | 16 | 0.667 |
| persistence | test | Tomato | 3 | 45 | 37.778 | 72.265 | 0.000 | 15 | 0.667 |

Directional accuracy is restricted to changing targets; see the reported denominator. The persistence model predicts no change and cannot predict the direction of a genuine change. All candidate predictions and target dates are saved in `results/test_predictions.csv`. Model comparison uses the same eligible rows for every candidate; overall and macro metrics answer different weighting questions.

![Measured forecast comparison](../figures/model_comparison.png)

Residual bands and held-out empirical coverage are in `results/interval_coverage.csv`. These are descriptive uncertainty indicators with no guaranteed future coverage. Previous academic exploration touched parts of this history, and same-day source availability is assumed. New observations are required for independently prospective verification.
