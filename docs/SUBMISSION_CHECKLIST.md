# Deployment and submission checklist

GitHub publication succeeded: **130 public files** on `main` at [https://github.com/Ruganji-Prince/SmartSell-Rwanda](https://github.com/Ruganji-Prince/SmartSell-Rwanda), using the authorized GitHub integration. `sell-time-estimation-aisd-main.zip` is an **intentionally excluded, redundant development archive**. The owner does not approve its public upload; it is not required to run or reproduce the final application. Streamlit deployment, the real demo recording, eligibility-document upload and form submission remain pending.

## Automatically completed

- [x] Main README describing data, purpose, interaction, limitations and reproduction.
- [x] Portable source scripts, `app.py`, pinned requirements, processed assets and selected-model metadata.
- [x] Preserved price exports, supplied NISR workbook, source links/acknowledgements and extraction provenance.
- [x] Real benchmark/simulation results, tests, technical audit and <=3-minute recording script.
- [x] Eligibility-folder instructions only; **no identity documents** or video have been fabricated or published.
- [x] Advisor break-even prices, required uplift, zero-retention handling and explicitly illustrative sensitivity.
- [x] Human publication guide with exact GitHub commands, staged-file review, Streamlit instructions and submission order.
- [x] Rebuildable public source package and a separate per-file byte-size/SHA-256 inventory in `dist/`.

## Human actions still required

Confirm final team name and team leader details; verify both members' eligibility and reviewed disclosure route; review IP/source terms; deploy the Streamlit app; add the actual app URL; verify private-window/device access; record/add the real <=3-minute demo; commit final reviewed artifacts; complete the official NISR form and truthful final declaration. These are not automatically completed by having local software ready.

Follow [the publication guide](PUBLICATION_GUIDE.md) for exact commands and the ordered handoff. The guide records the verified repository URL; app/video links remain pending and no team identity is fabricated.

## Reproduce and inspect

- [ ] Install Python 3.14 and run the README's environment, preparation, benchmark, simulation and report-generation commands.
- [ ] Run `python -m pytest -q` and `python scripts/quality_check.py` in the activated environment; inspect `results/quality_checks.json`.
- [ ] Review `results/forecast_metrics.csv`, `results/model_comparison.csv`, `results/decision_metrics.csv` and the small decision-coverage denominator.
- [ ] Run `streamlit run app.py`. Check all four pages, historical replay, stale/missing/unsupported handling and the editable scenario arithmetic.
- [ ] Confirm `app.py`, `requirements.txt`, reproducible scripts, README, original source data/workbook, processed app assets, model metadata and all linked documents are present.
- [ ] Acknowledge NISR plus TangaBid/Esoko; review source-data redistribution terms and supplied competition IP/originality conditions. Do not add a new license by default.
- [ ] Review the actual team roster, second member, student status and citizen eligibility; no identity or proof is fabricated.

## Exact Streamlit Community Cloud deployment

For GitHub, first use [the staged-file review and publication commands](PUBLICATION_GUIDE.md#4-create-or-select-the-public-github-repository). Prefer extracting the reviewed source ZIP into an empty folder; do not upload a working virtual environment or only the unopened ZIP.

1. Create a public GitHub repository under the team's authorized account. Upload the reviewed project root, including `app.py`, `requirements.txt`, `src/`, `.streamlit/config.toml`, `data/raw/`, `data/processed/`, `models/`, `results/`, `figures/`, `docs/` and the supplied annual workbook. Include the data documentation and source acknowledgements. Git's ignore file intentionally excludes environments, secrets, caches and student IDs.
2. Confirm the `main` branch (or your chosen branch) contains generated `data/processed/history.csv`, NISR extracts and `models/metadata.json`. Persistence needs no binary model. If a future measured winner is ML, also include its generated `models/selected_model.joblib`.
3. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub and authorize access to the intended repository.
4. Choose **Create app**, select the repository and branch, and enter **app.py** as the main file path. In advanced settings choose **Python 3.14**, the locally tested interpreter family covered by the documented support policy. Pinned package metadata and Linux candidate wheels have been checked, but the actual Cloud build remains unverified until deployment. No secrets are required. Choose an available public app address and deploy.
5. Inspect the build log. Dependencies install from root `requirements.txt`; the app loads shipped assets and does not train at startup. Do not deploy `.venv` or machine-specific paths.
6. Open the returned public URL and visit all four pages. Confirm stale current advice is withheld and a supported held-out historical replay displays the revenue calculation. Test the public link in a private/incognito window without being logged in.
7. Put the actual GitHub and deployed app URLs in README. No URL is claimed before the service returns it.

Official deployment reference: [Deploy your app on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy). Dependency reference: [App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies). These instructions follow the current documented repository/branch/entrypoint workflow; Python/runtime availability should be checked in the actual deployment UI.

## Final submission

- [x] Public GitHub URL works for an unauthenticated reviewer; every README local link exists.
- [ ] Public deployed app works in incognito, including on the intended demo device. Open it shortly before judging/submission so it is ready.
- [ ] Demo is a real screen recording <=3 minutes using `docs/DEMO_SCRIPT.md`; check duration and add its actual path or permitted public link. Follow the form's upload requirements.
- [ ] Review both members' authentic eligibility documents and any public exposure with their permission. Submission Webinar 2, slide 17, explicitly lists eligibility evidence among repository contents. Confirm with the organizer whether a private route or redacted evidence is acceptable before publishing sensitive originals. `student_cards/` is ignored except its instructions; nothing is automatically uploaded. Public inclusion requires that explicit competition requirement and the team's review; do not publish identity material otherwise.
- [ ] Review automated secret/path/file-size findings, then manually review public artifacts for private information. `python scripts/package_submission.py` produces a source ZIP without IDs, environments or caches.
- [ ] Commit and push final reviewed code, links, permitted documents and recording. Verify repository status and deployed revision match the submission.
- [ ] Truthfully declare originality and acknowledge all sources, including the preserved academic development history and tool-assisted work as required by the form.
- [ ] Complete the [NISR submission form](https://statistics.gov.rw/form/2026-hackathon-submission-form) with the actual repository/app URLs and required evidence. The supplied submission webinar states **30 October 2026**; verify the organizer's exact cutoff and any updates.

Local automated completion is documented in `FINAL_STATUS.md` and `results/quality_checks.json`. GitHub publication is complete. Remaining unchecked boxes require subsequent team actions, deployment verification, a real recording or submission.
