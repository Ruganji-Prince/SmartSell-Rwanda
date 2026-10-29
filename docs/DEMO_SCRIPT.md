# Final screen-recording script - target 2 minutes 45 seconds

Record only after human review. No video is created automatically. Use the actual historical prototype, preserve its warnings and do not manufacture a WAIT recommendation.

| Time | Screen action | Suggested narration |
| --- | --- | --- |
| 0:00-0:20 | Open SmartSell Advisor; keep the freshness warning visible | "Farmers may face a higher price tomorrow but still earn less after crop deterioration and waiting costs. SmartSell Rwanda asks whether a future price would rise enough to make storage worthwhile." |
| 0:20-0:40 | Point to the source/date banner and official-context expander | "We use TangaBid farm-gate exports naming Esoko Rwanda as source, plus official NISR SAS 2024 vegetable-sector tables. The prices are historical; current advice is withheld. Storage loss and costs are editable assumptions." |
| 0:40-1:40 | Select Tomato -> Nyarugenge -> Nyabugogo. Enable Historical replay, choose 28 September 2026. Set 100 kg, 1% daily loss, 100 RWF/day storage and zero other costs. Show forecasts, SELL NOW and break-even cards | "On this historical date the observed price is 500 francs per kilogram. Persistence won our benchmark and forecasts 500 at each horizon. Selling now gives 50,000 francs. Tomorrow's break-even price is about 506.06, or 1.21 percent higher, merely to match selling now. The system is not saying the price can never increase. It is saying the future price must exceed this economic threshold before waiting is worthwhile. A hypothetical whole-franc quote of 507 would be profitable under these assumptions; the actual forecast remains 500." |
| 1:40-2:05 | Change daily loss from 1% to 3%. Point to the one-day threshold rising to 516.49, then the illustrative sensitivity chart | "Higher assumed deterioration raises the price hurdle. Better retention lowers it when other costs stay the same. These scenarios are not NISR measured daily spoilage. Empirical forecast-error bands show uncertainty, without guaranteeing a buyer's price or profit." |
| 2:05-2:25 | Open NISR Agricultural Context; choose Nyarugenge and Season A | "Official NISR tables provide production, yield, area and production-use context, including storage and post-harvest loss, for Vegetables as a group. They motivate accounting for storage risk, without supplying Tomato- or Carrot-specific daily rates." |
| 2:25-2:45 | Open Methodology & Limitations; show measured results and mention scripts/tests | "Our reproducible retrospective evaluation covers only 20 complete windows: 8.03 percent coverage, all SELL NOW and zero simulated gain. The value is transparent economic tradeoffs. Fresh data and farmer evaluation are still needed before claiming real income benefits." |

## Verified figures and rehearsal notes

The exact path is Tomato -> Nyarugenge -> Nyabugogo -> Historical replay -> 28 September 2026. The three forecast dates are 29 September, 30 September and 1 October, all at 500 RWF/kg. Empirical price bands are 400-600, 300-700 and 300-700 RWF/kg; these are validation-error bands without guaranteed future coverage. Observation-date availability is assumed, not verified publication timing.

At 100 kg, 1% daily loss, 100 RWF/day storage and zero other costs, net revenues for days 0/1/2/3 are 50,000; 49,400; 48,805; 48,214.95 RWF. Equality thresholds are 506.060606, 512.192633 and 518.396907 RWF/kg, with uplifts about 1.2121%, 2.4385% and 3.6794%. Waiting must strictly exceed the equality threshold. A hypothetical quote of 507 tomorrow nets 50,093 RWF; it is not a replacement forecast or measured gain.

At 3% daily loss, the one-day threshold is 50100/97 = 516.494845 RWF/kg. Restore 1% after rehearsal if desired. The separate sensitivity defaults 0%, 1%, 2%, 5% are editable illustrative assumptions. No current/live price feed, routing, verified Cloud deployment or realized farmer-income improvement should be claimed.

Rehearse clicks before recording. Keep the actual video <=3:00; the planned sequence ends at 2:45. Review the final file and disclosure, then add its actual path/link. See `results/enhancement/demo_break_even.csv`, `results/enhancement/demo_storage_sensitivity.csv`, and `docs/PUBLICATION_GUIDE.md`. This task prepares the script only.
