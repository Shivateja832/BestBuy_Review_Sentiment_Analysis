# BestBuy Review Sentiment Analysis

A policy-aware Streamlit application for analyzing public Best Buy Canada product reviews. It supports CSV upload, optional visible-page collection, VADER sentiment labels, exploratory theme counts, stakeholder recommendations, and CSV/Excel downloads.

## Status

- Application: implemented and locally testable.
- Genuine review sample: 50 visible ASUS CM14 reviews collected on 2026-10-26 and analyzed locally.
- Data-quality flags: one review card had no visible title; it remains blank. The page exposed no review IDs, so deterministic SHA-256 keys are used. Review text includes references to CX14/Intel Celeron/64GB hardware, while the selected listing is CM14/MediaTek/128GB; treat findings as listing-level until this fit is resolved.
- Site compliance: collection used visible sort and Show More controls only, with no private API, login, proxy rotation, CAPTCHA bypass, or access-control evasion. Verify current terms and authorization before reuse or redistribution.
- Repository: source uploaded to `Shivateja832/BestBuy_Review_Sentiment_Analysis` on `main`.
- Streamlit Community Cloud: the hosted app loaded successfully. A synthetic-only 50-row upload rendered analysis and downloads; removing it cleared the prior analysis and restored the empty state.

App URL: <https://shivateja832-bestbuy-review-sentiment-analysis-app-bnlojz.streamlit.app/>

See [`reports/requirement_status.md`](./reports/requirement_status.md) for a requirement-by-requirement completion matrix and [`reports/stakeholder_report.md`](./reports/stakeholder_report.md) for the sample analysis.

The [ASUS CM14 Chromebook review page](https://www.bestbuy.ca/en-ca/product/asus-cm14-14-chromebook-mediatek-kompanio-540-4gb-lpddr5x-128gb-emmc-chromeos-pure-grey/19826852/review) displayed 434 reviews when selected. The sample contains 50 distinct visible cards in the Most Relevant view, loaded in observed increments of 10 with the visible Show More control. All five requested sort labels were selected and confirmed on the live page. The sample is not an export of all 434 reviews.

The generated CSV and Excel files are in `outputs/` on this workstation and are git-ignored to avoid publishing reviewer names or full review text. The workbook includes review results, insights, recommendations, and collection provenance. The sample mean rating is 4.50/5 (37 five-star, 7 four-star, 3 three-star, and 3 one-star reviews). Because some review texts describe different model specifications, do not treat the sample as verified CM14-specific evidence; the stakeholder report explains this qualification.

## Quick start (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

For CSV-only analysis, upload a CSV containing a `review_text` column. Empty or malformed files are reported clearly, and blank review rows are excluded before scoring. Recommended fields are `primary_key`, `title`, `review_text`, `date`, `rating`, `source`, and `reviewer_name`. The app provides VADER text sentiment, a low-rating-aware final label, a sentiment category, and CSV/Excel downloads.

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
- `outputs/asus_cm14_bestbuy_reviews_sentiment.csv` and `.xlsx` — 50-record public-page sample and analysis, stored locally and git-ignored.
- `outputs/review_template.csv` — field-header template.
