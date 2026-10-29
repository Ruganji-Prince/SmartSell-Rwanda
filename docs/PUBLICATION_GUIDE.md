# Human publication and submission guide

This guide contains future commands for the team to run after reviewing the prepared files. No remote repository, deployment, recording or submission has been created automatically. The software is a historical prototype: latest available observed price data end on 14 October 2026, and current advice is withheld.

## 1. Confirm people, privacy and source rights

Confirm the real team name, team leader details, both members' student eligibility and the required Rwandan citizenship condition. Only the original academic author's attribution is known from supplied files; it does not establish a final roster. Review source redistribution terms and the supplied competition IP/originality conditions. No open-source license has been added.

Student eligibility evidence is potentially private. Submission Webinar 2 slide 17 lists eligibility evidence among repository contents; clarify a private/redacted route with the organizer and review the exact documents with both members before public disclosure. IDs are ignored and package-excluded by default. Do not override this protection simply to fill a checklist. See [student-card instructions](../student_cards/README.md).

## 2. Reproduce locally

Use Python 3.14 (verified on 3.14.2). In the project root, PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/prepare_data.py
.\.venv\Scripts\python.exe scripts/train_models.py
.\.venv\Scripts\python.exe scripts/evaluate_models.py
.\.venv\Scripts\python.exe scripts/build_submission_assets.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/quality_check.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

On Linux/macOS substitute `.venv/bin/python`. If `python` opens the Windows Store, use the installed Python 3.14 executable/launcher to create the environment, then use its relative interpreter above. Do not replace the pinned dependencies or select a different forecasting model simply for presentation. Preparation also extracts NISR tables; no unavailable microdata or API key is required. For a source-copy reproduction with the invoking environment: `python scripts/verify_reproducibility.py`. The final readiness record documents the separately installed clean-environment run.

Rehearse Tomato -> Nyarugenge -> Nyabugogo -> Historical replay -> 28 September 2026, 100 kg, 1% daily loss, 100 RWF/day storage, zero other costs. Forecasts remain 500 RWF/kg and SELL NOW. Equality thresholds are 506.06, 512.19 and 518.40 RWF/kg; waiting must exceed them. Visit all four pages. Browser layout and the eventual public-cloud build need human review beyond the automated AppTest checks.

## 3. Choose the publication source

Use the reviewed `dist/SmartSell_Rwanda_submission.zip` and accompanying `dist/publication_file_inventory.csv` and `dist/package_manifest.json`. Extract the ZIP into a new empty publication folder. Do not upload the ZIP itself as the only repository file: `app.py`, README and directories must appear at the GitHub root. This clean-folder route keeps the working virtual environment, caches, unrelated local documents and private files outside the repository.

The allowlist retains actual source/data, official agricultural/submission documents, generated evidence and legitimate academic history under `docs/legacy_aisd/`. The original development ZIP is intentional provenance, including raw CSV preservation checks; it is not duplicate analytic training data. `DHS2000_HIV.pdf` is unrelated and remains local only. No student ID is included. The inventory is an external review aid; it need not be added to the repository or embedded inside itself.

## 4. Create or select the public GitHub repository

Install Git and authenticate through GitHub's supported sign-in flow. Do not paste tokens into commands or files. Create an **empty public repository** on GitHub; do not initialize it with a README, gitignore or license because these files are supplied. Copy its actual HTTPS remote URL. A new empty repository is the simplest path.

Git was not available on PATH in the verification environment. Check `git --version` after installing/configuring it, or use GitHub Desktop's reviewed staging/commit/publish flow. This does not affect the Python app or the successful reproducibility checks.

In the extracted publication folder:

```powershell
git init -b main
git add .
git status --short
git diff --cached --stat
git diff --cached --name-only
git diff --cached --check
```

Review the staged filenames against the publication inventory, then inspect actual staged content. `git diff --cached --name-only` should not include `.venv`, caches, `.env`, secrets, unrelated health PDFs or identity documents. Use the root README to verify headline results remain visible. Inspect any personal attribution intentionally retained; do not add private team contacts by default.

Only after that review, replace `YOUR_GITHUB_USERNAME` and `YOUR_REPOSITORY` with the actual values:

```powershell
git commit -m "Prepare SmartSell Rwanda NISR hackathon submission"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY.git
git remote -v
git push -u origin main
```

These commands have **not** been run by the assistant. If you instead select an existing repository with history, inspect its branch/remotes first with `git status`, `git branch --show-current` and `git remote -v`; use a normal reviewed branch/merge workflow. Do not force-push or overwrite existing history. If `origin` already exists, inspect it rather than blindly adding/replacing it.

After pushing, open the repository in a private/incognito browser. Check public access, README rendering, local links, figures, actual `app.py`, processed history/NISR CSVs and `models/metadata.json`. No binary estimator is needed for persistence. Confirm the main README opens as SmartSell Rwanda, with academic instructions confined to the explicitly archived history.

Official reference: [GitHub: adding locally hosted code](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).

## 5. Deploy to Streamlit Community Cloud

1. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) using GitHub and grant access to the intended repository.
2. Choose **Create app**, then the option for an existing app/repository. Select the actual repository and the branch containing the reviewed files, normally `main`.
3. Set the main file path to **app.py**. It must be the extracted root entrypoint, not a ZIP path or a local-machine path.
4. Open **Advanced settings**, select **Python 3.14**, and save. This is the locally tested runtime family covered by the documented support policy. Pinned package metadata/Linux candidate wheels were checked; a successful Community Cloud build is not claimed until the actual deployment completes. No secrets are needed.
5. Choose an available app address and deploy. Inspect build logs for dependency, import or missing-file errors. Do not train at app startup or upload `.venv`; the shipped assets support the demo.
6. Open the returned public URL. Verify SmartSell Advisor, Market Trends, NISR Agricultural Context and Methodology & Limitations. Current stale advice must remain withheld.
7. Test the exact historical path above. Confirm 500 RWF/kg forecasts, SELL NOW, the break-even thresholds, required uplift and editable sensitivity. Check that NISR labels say vegetable-sector context.
8. Repeat in a private/incognito window without signing in, then on the intended demo device/narrow screen. This verifies actual public access and layout, which local automated tests cannot establish.

Official reference: [Streamlit deployment workflow](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy). Public app/repository URLs are still placeholders until you perform these actions.

## 6. Add real links and the reviewed recording

Replace README's pending repository/app/video placeholders with actual values. If regenerating README using `scripts/build_submission_assets.py`, its template also contains placeholders: update the template or reapply the real links after generation. Do not invent links. The final demo script targets 2:45; record the actual screen, check duration <=3:00, and retain the historical-data and uncertainty disclosures. Do not manufacture a WAIT result.

Video files are ignored by default. After reviewing the actual file and permitted format/size, intentionally add the recording, for example:

```powershell
git add README.md scripts/build_submission_assets.py
git add -f demo/smartsell-demo.webm
git diff --cached --stat
git diff --cached --check
git commit -m "Add verified public links and reviewed demonstration"
git push
```

Use the real recording filename, not a nonexistent example. If a permitted external video link is used, update README with that link and follow the form's requirements. Keep eligibility documents private unless the organizer's explicit requirement and the team's review justify the exact public artifact. Do not use a broad force-add command for IDs or secrets.

## 7. Final NISR submission order

1. Confirm team name, team leader/contact details and both members' eligibility; resolve the identity-document privacy route and review IP/source/originality requirements.
2. Review the final source and measured results, create/push the public GitHub repository, and verify its unauthenticated rendering.
3. Deploy the reviewed branch to Streamlit; verify the public app and the exact historical replay in incognito and on the presentation device.
4. Add actual GitHub/app URLs; record and add the real <=3-minute demo; include only intentionally reviewed eligibility evidence through the permitted route.
5. Commit/push final changes; confirm GitHub links, recording access and deployed revision match the submission. Open the app shortly before organizer review so it is ready.
6. Complete the [official NISR submission form](https://statistics.gov.rw/form/2026-hackathon-submission-form) with the actual links, team/eligibility information and required evidence. Confirm the truthful final submission declaration and retain the real receipt/confirmation.

The supplied webinar states **30 October 2026**; verify the exact organizer cutoff and any updates directly. Do not claim the form is complete until you actually submit it. No form, repository or cloud account action has been performed automatically.
