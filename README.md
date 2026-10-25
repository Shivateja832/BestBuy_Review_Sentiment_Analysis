# BestBuy Review Sentiment Analysis

A policy-aware Streamlit application for analyzing public Best Buy Canada product reviews. It supports CSV upload, optional visible-page collection, VADER sentiment labels, exploratory theme counts, stakeholder recommendations, and CSV/Excel downloads.

## Status

- Application: implemented and locally testable.
- Live Best Buy data: **not bundled**. No review content is fabricated.
- Site compliance: the collector rechecks robots.txt and requires the operator to confirm current terms and authorization. The Best Buy terms page was unavailable during preparation; independently verify it before collection.
- Repository: source uploaded to `Shivateja832/BestBuy_Review_Sentiment_Analysis` on `main`.
- Streamlit Community Cloud: **not yet deployed**. The deployment page requires the repository owner's sign-in and app creation; no authenticated owner session is available here.

At preparation time Best Buy robots.txt disallowed `/en-ca/search` and allowed `/en-ca/product/`. The UI and URL validator prohibit search URLs. Always verify the current robots rules and terms before running.

## Quick start (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

For CSV-only analysis, upload a CSV containing a `review_text` column. Recommended fields are `primary_key`, `title`, `review_text`, `date`, `rating`, `source`, and `reviewer_name`. The app creates sentiment score, sentiment, and sentiment category fields and offers CSV and Excel downloads.

## Optional review collection

1. Open Best Buy Canada’s current robots.txt and terms yourself. Do not run unless the route and intended use are allowed.
2. Use a direct HTTPS `/en-ca/product/` page URL. Search and review submission URLs are rejected.
3. Select one or more visible sort views and bounded pagination. Collection checks robots.txt, pauses between page actions, and reads visible review cards through Selenium.
4. Confirm the policy/authorization checkbox and run. If a visible control or review card cannot be found, collection reports an error instead of using a private API or bypass.

The scraper intentionally does not rotate proxies, bypass CAPTCHAs, defeat rate limits, log in, or evade blocking. Stop when blocked. Sort coverage can overlap and the result is deduplicated. Page changes can break selectors; verify collected counts before using the data. Selenium requires Chrome; browser/driver setup is environment-dependent.

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

The repository is ready for Community Cloud. The owner must sign in at [Streamlit Community Cloud](https://share.streamlit.io/) and create an app with:

- Repository: `Shivateja832/BestBuy_Review_Sentiment_Analysis`
- Branch: `main`
- Main file path: `app.py`

Or open the [pre-filled deployment page](https://share.streamlit.io/deploy?repository=Shivateja832%2FBestBuy_Review_Sentiment_Analysis&branch=main&mainModule=app.py). Hosted deployment is not complete until the owner completes this authenticated step and Streamlit reports the app as running. CSV upload and analysis need no browser binary; the optional Selenium collection requires Chrome/ChromeDriver, which is not verified in Community Cloud. Use local Chrome or Docker for that feature.

## Files

- `app.py` — Streamlit user interface and exports.
- `src/bestbuy_reviews.py` — robots-aware visible-page collector and parser.
- `src/sentiment.py` — VADER scoring and data-derived insight helpers.
- `reports/stakeholder_report.md` — methods, risks, limitations, and recommendations.
- `tests/` — focused tests for scraping parsing and sentiment labels.
- `outputs/review_template.csv` — field-header template only, not scraped records.
