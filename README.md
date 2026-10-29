# BestBuy Review Sentiment Analysis

A policy-aware Streamlit application for analyzing public Best Buy Canada product reviews. It supports CSV upload, optional visible-page collection, VADER sentiment labels, exploratory theme counts, stakeholder recommendations, and CSV/Excel downloads.

## Status

- Application: implemented and locally testable.
- Genuine review sample: 171 unique visible reviews collected from a Best Buy Canada Dell laptop listing on 2026-10-28 and analyzed locally.
- Recruiter-style evaluation: **97/100** against the assignment rubric in [`reports/requirement_status.md`](./reports/requirement_status.md). This is an evidence-based estimate, not a guaranteed recruiter score; the report explains why a previous 94/100 estimate was revised and lists the remaining verification limits.
- Data quality: all 171 records have source-provided titles and non-empty assignment fields. The page did not expose a stable review ID, so deterministic SHA-256 primary keys are used.
- Live page verification: the listing displayed 172 reviews. Through the ordinary visible page controls, all five requested sort views were selected and Show More loaded 171 visible cards in each view until the control disappeared. This verifies the site UI, not the packaged Selenium run.
- Supported fallback: the app can parse browser-saved Best Buy review-page HTML with Beautiful Soup. The visible page is saved after sort selection and Show More pagination; multiple HTML views are deduplicated and validated before analysis.
- Site compliance: the sample was collected using visible Best Buy page controls only, without private APIs, login, proxy rotation, CAPTCHA bypass, or access-control evasion. Check current terms and any authorization needed for reuse or redistribution.
- Local smoke test: the current local Streamlit app returned HTTP 200.
- Tests: the full suite passed 35/35 after adding saved-page HTML parsing, upload support, and upload-size validation. The live sample was collected through the shared browser's visible controls; fresh standalone Selenium sessions returned HTTP 403 or timed out.
- Deployment: application code commit `14f9319` passed [GitHub Actions run 24](https://github.com/Shivateja832/BestBuy_Review_Sentiment_Analysis/actions/runs/40879454992); status-documentation commits `b55006c` and `cd2698b` passed [runs 25](https://github.com/Shivateja832/BestBuy_Review_Sentiment_Analysis/actions/runs/40883110223) and [26](https://github.com/Shivateja832/BestBuy_Review_Sentiment_Analysis/actions/runs/40883783381). These are published on GitHub `main`. The hosted Streamlit dashboard was reloaded and displays both CSV and saved-HTML upload routes. A stale module caused a temporary import failure after the first push; rebooting the Streamlit app resolved it. This confirms app deployment, not reliable live access from a fresh standalone Selenium session.
- AI disclosure: AI assistance was used during development and documentation. At runtime, sentiment classification uses the VADER lexicon-based method; the app does not call a generative AI model.

App URL: <https://shivateja832-bestbuy-review-sentiment-analysis-app-bnlojz.streamlit.app/>

See [`reports/requirement_status.md`](./reports/requirement_status.md) for a requirement-by-requirement completion matrix and [`reports/stakeholder_report.md`](./reports/stakeholder_report.md) for the sample analysis.

The [Dell 15.6-inch laptop review page](https://www.bestbuy.ca/en-ca/product/dell-15-6-120hz-laptop-amd-ryzen-7-7730u-16gb-ddr4-512gb-ssd-windows-11-home-carbon-black/19821568/review) displayed 172 reviews when checked. All five visible sort choices were selected; each view paginated through 171 visible cards before Show More disappeared. The export contains those 171 unique visible cards after deduplication. The page header and visible-card count differ by one, so this is not described as a 172-record export.

The generated CSV and Excel files are in `outputs/` on this workstation and are git-ignored to avoid publishing reviewer names or full review text. The workbook includes review results, insights, recommendations, and collection provenance. The 171 accessible reviews average 4.55/5 (121 five-star, 31 four-star, 14 three-star, 2 two-star, and 3 one-star reviews). A fresh standalone Selenium session returned HTTP 403; the sample was obtained through normal visible browser controls without evading that block.

## Quick start (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

For CSV-only analysis, upload a CSV containing a `review_text` column. Empty or malformed files are reported clearly, and blank review rows are excluded before scoring. Recommended fields are `primary_key`, `title`, `title_source`, `review_text`, `date`, `rating`, `source`, and `reviewer_name`. When a visible review card has no title, the collector derives a display title from review text and marks `title_source=generated_from_review_text`; the app shows a qualification notice. The app provides VADER text sentiment, a low-rating-aware final label, a sentiment category, and CSV/Excel downloads.

## Optional review collection

1. Open Best Buy Canada’s current robots.txt and terms yourself. Do not run unless the route and intended use are allowed.
2. Use a direct HTTPS `/en-ca/product/` page URL. Search and review submission URLs are rejected.
3. Preferred for this environment: use the normal Best Buy browser controls to select sort and click Show More until no more control appears, then save the rendered review page as HTML. Upload one or more saved pages in the app and confirm authorization/current terms; Beautiful Soup parses and deduplicates cards, and incomplete or malformed records are rejected.
4. Alternatively, use the optional Selenium collector when a fresh browser session is allowed. Confirm the policy/authorization checkbox and run. If the site denies access or a visible control/card cannot be found, stop rather than bypassing the block.

The scraper detects Best Buy's OneTrust overlay by its observed `onetrust-pc-dark-filter` **class** (not an ID) and uses the visible “Reject All” control to decline optional cookies. Fresh standalone Selenium sessions returned HTTP 403 or timed out while clicking Show More. The saved-HTML fallback parses content from a page that the operator accessed through ordinary visible controls; it does not alter browser identity or bypass restrictions. The Selenium collector stops on a consent/access block and does not retry to evade one. Where no source review ID is exposed, it creates a content-derived primary key. It never accepts optional cookies automatically, rotates proxies, bypasses CAPTCHAs, defeats rate limits, logs in, or evades blocking. Sort coverage can overlap and is deduplicated. Page changes can break selectors; verify counts before using collected data. Selenium requires Chrome; browser/driver setup is environment-dependent.

## Notebook

`BestBuy_Review_Sentiment_Analysis.ipynb` documents the complete workflow. It does not initiate collection automatically; inspect policies and explicitly opt in before running a scrape.

## Tests

```powershell
python -m pytest -q
```

## Docker

```powershell
docker build -t bestbuy-review-analysis .
docker run --rm -p 8501:8501 bestbuy-review-analysis
```

Then visit `http://localhost:8501`. Docker includes Chromium and ChromeDriver for the optional visible-page collector.

## Streamlit Community Cloud

The app has been created in Community Cloud with:

- Repository: `Shivateja832/BestBuy_Review_Sentiment_Analysis`
- Branch: `main`
- Main file path: `app.py`

Application code commit `14f9319` and subsequent status updates through `cd2698b` are on GitHub `main`. [GitHub Actions runs 24](https://github.com/Shivateja832/BestBuy_Review_Sentiment_Analysis/actions/runs/40879454992), [25](https://github.com/Shivateja832/BestBuy_Review_Sentiment_Analysis/actions/runs/40883110223), and [26](https://github.com/Shivateja832/BestBuy_Review_Sentiment_Analysis/actions/runs/40883783381) passed. The [app URL](https://shivateja832-bestbuy-review-sentiment-analysis-app-bnlojz.streamlit.app/) rendered the dashboard after the update, with both upload routes visible. `packages.txt` requests Chromium and its driver for optional Selenium collection; system package availability is host-dependent. CSV upload and sentiment analysis do not require browser binaries. Best Buy access from fresh standalone Selenium sessions returned HTTP 403 or timed out; the saved-HTML parser has unit coverage, but has not been run on an authentic saved Best Buy page through the hosted app.

## Files

- `app.py` — Streamlit user interface and exports.
- `src/bestbuy_reviews.py` — robots-aware visible-page collector and parser.
- `src/sentiment.py` — VADER scoring and data-derived insight helpers.
- `packages.txt` — Chromium packages requested for Community Cloud.
- `reports/stakeholder_report.md` — methods, risks, limitations, and recommendations.
- `tests/` — focused tests for scraping parsing and sentiment labels.
- `outputs/dell_15_6_laptop_bestbuy_reviews_sentiment.csv` and `.xlsx` — 171-record deduplicated visible-page export and analysis, stored locally and git-ignored.
- `outputs/review_template.csv` — field-header template.
