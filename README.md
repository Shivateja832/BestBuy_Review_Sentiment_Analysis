# BestBuy Review Sentiment Analysis

A policy-aware Streamlit application for analyzing public Best Buy Canada product reviews. It supports CSV upload, optional visible-page collection, VADER sentiment labels, exploratory theme counts, stakeholder recommendations, and CSV/Excel downloads.

## Status

- Application: implemented and locally testable.
- Live Best Buy data: **not bundled**. No review content is fabricated.
- Site compliance: the collector rechecks robots.txt and requires the operator to confirm current terms and authorization. The Best Buy terms page was unavailable during preparation; independently verify it before collection.
- Repository: source uploaded to `Shivateja832/BestBuy_Review_Sentiment_Analysis` on `main`.
- Streamlit Community Cloud: app created from `main` / `app.py`; the live page rendered the dashboard successfully.

App URL: <https://shivateja832-bestbuy-review-sentiment-analysis-app-bnlojz.streamlit.app/>

See [`reports/requirement_status.md`](./reports/requirement_status.md) for a requirement-by-requirement completion matrix. The public review count, synthetic tests, and working download controls do not count as a genuine 50-review export. Live Best Buy collection was not completed because the observed browser session returned access denial or a consent overlay without a visible Reject All control.

The selected [Samsung WF45T6000AW/A5 washer product page](https://www.bestbuy.ca/en-ca/product/samsung-5-2-cu-ft-iec-front-load-washer-with-smart-care-and-self-clean-energy-star-wf45t6000aw-a5-white/14400381) showed 4,289 public reviews (4.57/5) when inspected on 2026-10-25. Its visible review route showed ten cards initially with sort and “Show More” controls. This count is a public-site display, not a claim that the application exported all 4,289 reviews.

At preparation time Best Buy robots.txt disallowed `/en-ca/search` and allowed `/en-ca/product/`. The UI and URL validator prohibit search URLs. Always verify the current robots rules and terms before running. A local browser collection attempt encountered an access challenge/overlay and was stopped without evasion; no genuine output CSV is bundled.

## Quick start (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

For CSV-only analysis, upload a CSV containing a `review_text` column. Empty or malformed files are reported clearly, and blank review rows are excluded before scoring. Recommended fields are `primary_key`, `title`, `review_text`, `date`, `rating`, `source`, and `reviewer_name`. The app creates sentiment score, sentiment, and sentiment category fields and offers CSV and Excel downloads.

## Optional review collection

1. Open Best Buy Canada’s current robots.txt and terms yourself. Do not run unless the route and intended use are allowed.
2. Use a direct HTTPS `/en-ca/product/` page URL. Search and review submission URLs are rejected.
3. Select one or more visible sort views and bounded pagination. Collection checks robots.txt for the review route, pauses between page actions, and reads visible review cards through Selenium.
4. Confirm the policy/authorization checkbox and run. If a visible control or review card cannot be found, collection reports an error instead of using a private API or bypass.

The scraper detects Best Buy's OneTrust overlay by its observed `onetrust-pc-dark-filter` **class** (not an ID) and uses the visible “Reject All” control to decline optional cookies. It does not infer review IDs from generic `id` or `data-testid` attributes; where the page provides no explicit review ID it creates a content-derived key. If no visible Reject All control is available, it stops without making a consent choice; the app does not offer a supported manual consent flow in its browser session. It never accepts optional cookies automatically, rotates proxies, bypasses CAPTCHAs, defeats rate limits, logs in, or evades blocking. Sort coverage can overlap and the result is deduplicated. Page changes can break selectors; verify collected counts before using the data. Selenium requires Chrome; browser/driver setup is environment-dependent.

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

Open the [app URL](https://shivateja832-bestbuy-review-sentiment-analysis-app-bnlojz.streamlit.app/) to check startup. The live page rendered the dashboard during verification. `packages.txt` requests Chromium and its driver for optional Selenium collection; verify Cloud build logs because system package availability is host-dependent. CSV upload and sentiment analysis do not require browser binaries.

## Files

- `app.py` — Streamlit user interface and exports.
- `src/bestbuy_reviews.py` — robots-aware visible-page collector and parser.
- `src/sentiment.py` — VADER scoring and data-derived insight helpers.
- `packages.txt` — Chromium packages requested for Community Cloud.
- `reports/stakeholder_report.md` — methods, risks, limitations, and recommendations.
- `tests/` — focused tests for scraping parsing and sentiment labels.
- `outputs/review_template.csv` — field-header template only, not scraped records.
