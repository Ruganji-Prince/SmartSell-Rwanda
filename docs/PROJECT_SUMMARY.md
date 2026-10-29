# SmartSell Rwanda

**A data-driven sell-or-store decision-support tool for Rwandan farmers.**

Farmers deciding when to sell must balance a possible price rise against lost saleable quantity and storage costs. SmartSell makes that tradeoff visible for Tomato and Carrot, comparing immediate sale with up to three calendar days of waiting.

**Will prices rise enough to compensate for quantity deterioration and storage cost?** The Advisor calculates the break-even future price and required price uplift for each waiting day. Even a correctly forecast higher price may be insufficient. For 100 kg at 500 RWF/kg, assumed 1% daily loss and 100 RWF/day storage, tomorrow's break-even price is 506.06 RWF/kg (about 1.21% uplift). A hypothetical 505 quote still nets only 49,895 RWF, below selling now at 50,000; a hypothetical 507 quote nets 50,093. These are transparent arithmetic scenarios, not new forecasts or historical improvements. Waiting must strictly exceed break-even; equality is not a gain.

The prototype uses 6,266 cleaned TangaBid/e-Soko farm-gate observations, from 2025-01-01 to 2026-10-14. Official NISR SAS 2024 tables contribute vegetable-sector district/season production, harvested area and yield, national sold/stored/loss shares, and sowing context. They are clearly labelled Vegetables; no Tomato/Carrot-specific loss or daily spoilage is invented.

That official sector evidence motivates incorporating storage risk into the farmer decision, without calibrating daily loss from seasonal shares. An editable storage-loss sensitivity view shows how assumed deterioration changes break-even prices while holding quantity and costs fixed. Better retention lowers the required price uplift, all else equal; no measured storage-improvement benefit is claimed.

Four methods were benchmarked with chronological partitions, target-date purging, training-only preprocessing and exact-date targets. **persistence won**, with validation macro MAE 49.00 RWF/kg and test MAE 41.25 RWF/kg on 314 examples. The app uses the measured winner instead of assuming a complex model is better.

The farmer enters quantity, daily loss assumption and whole-lot waiting costs. The engine compares expected price × retained quantity minus costs for each selling day and explains its result. Loss assumptions are editable sensitivity scenarios, separate from official NISR seasonal evidence. Empirical error bands and stale-data withholding make uncertainty visible.

Retrospective complete-window simulations cover 20 origins (8.03% coverage). Persistence recommends immediate sale, giving zero simulated advantage versus the sell-now baseline. The project makes no measured farmer-income claim. Its practical value is transparent comparison and preventing unsupported waiting recommendations; prospective farmer evaluation is still needed.

Four no-login pages support the advisor, market trends, official agricultural context, and methodological review. Current advice is withheld because prices are historical; a dated held-out replay demonstrates the system. The problem aligns with Rwanda's agricultural market-linkage and post-harvest-management priorities and NISR Track 1, without claiming policy endorsement.

Code, tests, generated results, source acknowledgements, deployment instructions and a <=3-minute demo script are supplied. Public account actions, final eligibility review and a real recording remain human submission steps.
