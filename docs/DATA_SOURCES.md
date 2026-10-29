# Data sources and provenance

| Supplied source | Actual use | Limits |
| --- | --- | --- |
| `data/raw/tangabid_market_prices.csv` | Tomato farm-gate price history | Original label `Tomatos`; source field Esoko Rwanda |
| `data/raw/tangabid_market_prices_carrots.csv` | Carrot farm-gate price history | RWF/kg; irregular observations |
| `SAS 2024_Annual Tables.xlsx` (repository root) | Official NISR vegetable-sector district/season and national production-use/sowing context | Aggregated Vegetables category; no crop-specific daily loss |
| `ddi-documentation-english-113.pdf` (repository root) | Survey schema/methodology review | Documentation is not raw survey observations |
| `2026 NISR Hackathon Webinar.pdf` and `2026 NISR Hackathon Webinar 2.pdf` | Competition context and submission requirements | Supplied webinar instructions, not a hosting-service guarantee |
| `docs/legacy_aisd/` | Prior development strategy, notebook and attribution | Historical exploratory work, not final measured model results |
| `DHS2000_HIV.pdf` (local repository root) | Not used analytically; omitted from public source package and ignored by Git | No extractable text was found; unrelated document preserved locally, no agricultural evidence assumed |

Price export access: [TangaBid data access](https://tangabid.com/data-access/). Acknowledge both TangaBid as export provider and Esoko Rwanda as the named price source. The supplied exports' last observation is 14 October 2026; scrape timestamps in the CSVs are collection provenance, not proof of publication time. No claim of live access is made.

Official survey catalogue: [NISR microdata portal](https://microdata.statistics.gov.rw/index.php/catalog). Supplied DDI identifier: `RWA-NISR-SAS-2024-v01`. The workbook is supplied locally; do not substitute a guessed direct download URL. Raw SAS 2024/2025 microdata are not included or required by this implementation.

Extraction provenance and workbook SHA-256: `data/processed/nisr/extraction_metadata.json`. Raw CSV hashes and measured audit counts: `results/data_quality_summary.json`. District crosswalk: `data/processed/nisr/district_mapping.csv`. Original files are retained byte-for-byte, including the source ZIP. Processing writes only new output files.

Reproduce with `python scripts/prepare_data.py`. District indicators preserve their original crop-group headings, with a separate normalized Vegetables-only subset. Use-of-production percentages retain their original numeric precision; they are already percentages, so no guessed denominator division is performed. Blank/dash values remain missing. Quarantine outputs record invalid figures rather than replacing them.

Data access and redistribution remain subject to each provider's terms; no new data license is granted here. The competition webinar (preparatory, slide 7) describes assignment/transfer of submission IP to NISR. Review its actual wording before final submission; this repository does not provide a legal interpretation or add an MIT/Apache license.
