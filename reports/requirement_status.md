# Assignment Requirement Status

**Checked:** 2026-10-25  
**Application commit:** [`ebfdf47`](https://github.com/Shivateja832/BestBuy_Review_Sentiment_Analysis/commit/ebfdf47a0180668e83815ebdd352ab958f841cb6)

This document distinguishes implemented and tested application behavior from deliverables that require successful, authorized access to live Best Buy review content. Synthetic test fixtures validate code only; they are not customer reviews and are not included as scraped results.

| Assignment requirement | Status | Evidence and limitation |
|---|---|---|
| Python application and documented notebook | Implemented | Streamlit app, scraper modules, and `BestBuy_Review_Sentiment_Analysis.ipynb` are in the repository. |
| Select a product displaying at least 50 reviews | Product selected; displayed threshold observed | The selected washer review page displayed 4,289 reviews when checked. A displayed count does not establish that those reviews were collected. |
| Scrape public reviews through visible controls | Implemented; live execution blocked/unverified | Selenium reads visible review cards and controls only. In the tested browser session Best Buy returned an access-denied response; another observed session showed a consent overlay without a visible Reject All control. The collector stops in these cases. |
| Apply requested sort options and paginate with Show More | Implemented; successful complete extraction unverified | The collector supports the requested sort labels and visible Show More control. No live multi-sort, multi-page export was completed. |
| Extract review ID, title, text, date, rating, source, and reviewer | Implemented; real output unverified | Parser and unit tests cover these fields. Missing values are not invented. No collected dataset is available to verify field completeness on the live layout. |
| Analyze review sentiment and categorize results | Implemented and tested | VADER scoring, rating-aware categories, summary statistics, and recommendations are exercised by tests. The 50-review smoke test uses clearly synthetic fixtures, not Best Buy reviews. |
| Produce CSV and Excel results | Export functionality implemented; real-data deliverables pending | The app generates downloads from uploaded or collected data. No genuine Best Buy CSV or Excel output has been produced. The repository CSV is a header-only template. |
| Explain scraping challenges and give stakeholder recommendations | Implemented as general guidance | The stakeholder report documents safe stop conditions and data-validation recommendations. Product-specific satisfaction/dissatisfaction findings require genuine collected reviews and are not available. |
| Deploy and test the application | Deployed; application tests pass | Streamlit Community Cloud serves the app. Commit `ebfdf47` passed GitHub Actions; 20 local tests passed; the live app displayed the empty-CSV validation message without crashing. |

## Outstanding requirements

1. Obtain an authorized way to access Best Buy reviews that does not require bypassing consent, access denial, CAPTCHA, or other access controls.
2. Run the visible-page collector successfully for the selected product, across the requested sorts and pagination.
3. Validate at least 50 genuine review records, including their dates, ratings, and required fields.
4. Generate and inspect CSV/Excel downloads from that genuine dataset.
5. Recompute and report product-specific sentiment themes and stakeholder recommendations from those reviews.

These items cannot be marked complete based on unit tests, synthetic data, a public review count, or a working upload/download feature.

## Hosting diagnostic

During the browser check, the hosted Streamlit page rendered the application and also returned a 404 for `/api/v2/user/details`. This request is served by Streamlit Community Cloud, not by an application route in this repository. The dashboard and tested CSV-upload flow continued to work. This repository cannot change that platform endpoint; if it persists or affects use, consult Streamlit Community Cloud support or move to an independently managed host.
