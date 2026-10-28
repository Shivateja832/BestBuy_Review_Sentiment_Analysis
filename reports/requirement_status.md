# Assignment Requirement Status

**Checked:** 2026-10-28
**Current sample:** Dell 15.6-inch 120Hz laptop, AMD Ryzen 7 7730U, 16GB DDR4, 512GB SSD, Windows 11 Home
**Sample size:** 171 unique visible Best Buy Canada reviews across five sort views

This table evaluates the assignment requirements as written. Additional quality checks and limitations are listed separately so they are not misrepresented as extra recruiter requirements.

## Recruiter-style evaluation

**Evidence-based recruiter-style score: 95/100 under the rubric below; independent recruiter scores may differ.**

| Area | Score | Evidence and remaining qualification |
|---|---:|---|
| Python application and scraping features | 18/20 | Selenium/Beautiful Soup support is implemented. All five sort views and visible pagination were exercised in the shared browser, but a fresh run of the packaged Selenium collector was blocked by Best Buy HTTP 403. |
| Review sample and required fields | 20/20 | 171 distinct visible reviews across all five sort views have all required fields and unique generated keys. The page displayed 172 reviews, but only 171 cards were available through visible pagination. |
| Sentiment analysis and business findings | 20/20 | VADER sentiment categories, exploratory themes, and stakeholder recommendations were generated from the 171-review export. |
| Deliverables and documentation | 20/20 | Notebook, 171-row CSV, workbook, and stakeholder/requirements documentation are present locally. Check current Best Buy terms before reuse or redistribution. |
| Testing, reliability, and deployment | 17/20 | The full suite passed 30/30; GitHub Actions passed; the hosted dashboard rendered and returned HTTP 200. The standalone Selenium run remains blocked by HTTP 403. |

| Assignment requirement | Status | Evidence |
|---|---|---|
| Use Python and a web-scraping library | **Met** | The application includes a Python Selenium/Beautiful Soup collector and sentiment-analysis modules. |
| Select a Best Buy Canada product with at least 50 reviews | **Met** | The selected listing displayed 172 reviews when checked. |
| Support the requested sort options and visible pagination | **Implemented; live UI verified** | The Best Buy page exposed and accepted all five requested sorts. Normal visible Show More actions reached 171 cards in each sort before the control disappeared. A fresh local Selenium session returned HTTP 403, so this is not a successful packaged-collector run. |
| Mine across sort views and continue through all available review pages | **Met for visible cards** | The shared browser used the five visible sort options and Show More to load 171 cards in every view. The union was deduplicated to 171 unique records; no further Show More control appeared. |
| Collect at least 50 public reviews | **Met** | 171 distinct visible review cards were captured, exceeding the assignment threshold. The listing displayed 172 reviews; one card was not available through visible pagination. |
| Extract primary key, title, review text, date, rating, source, and reviewer name | **Met for all 171 exported records** | All required fields are populated; dates use `YYYY-MM-DD`; ratings are 1–5. The retailer did not expose review IDs, so stable unique primary keys are generated from public fields. |
| Provide sentiment-analysis code and categorize results | **Met** | VADER sentiment is run on review text with a star-rating-aware final label and sentiment categories. The 171-row export has 156 Positive, 12 Negative, and 3 Neutral final labels. |
| Provide CSV and Excel outputs | **Met** | The local CSV and Excel workbook contain all 171 deduplicated visible records. The workbook also includes insights, recommendations, and collection provenance. |
| Explain scraping challenges and handling | **Met** | Documentation describes visible consent handling, bounded collection, backoff/stop behavior, and stopping on access denial. It explicitly rejects CAPTCHA bypass, proxy rotation to evade blocks, and hidden endpoints. |
| Summarize customer satisfaction/dissatisfaction and recommend actions | **Met for this sample** | The stakeholder report presents sample rating/sentiment statistics, observed themes, and practical follow-up recommendations. Findings are labeled exploratory, not population estimates. |
| Provide the notebook with code explanation | **Met** | The notebook documents setup, optional collection, data validation, analysis, and exports. Collection is opt-in and off by default. |
| Avoid violating site policy | **Handled conservatively; verify terms for intended reuse** | The captured records came from ordinary visible review controls. The app does not evade access blocks or bypass CAPTCHA. This project does not independently establish Best Buy's current terms for redistribution or other uses. |

## What is and is not an assignment requirement

- The assignment requires a **primary key**, not a retailer-issued review ID. A deterministic generated key satisfies that field when the public page exposes no review ID.
- The selected sample has source-provided titles on all 171 records. The missing-title issue applied to the superseded CM14 sample, not this current Dell sample.
- The assignment's visible sorting and pagination behavior is verified, and the 171 accessible cards are exported across all five sort views. This live data capture used the shared browser's visible controls. A separate fresh run of the packaged Selenium collector against Dell returned HTTP 403; it must not be described as a successful Selenium run.
- Human-labeled VADER accuracy testing and a guaranteed recruiter score are not stated assignment deliverables. Human validation is a prudent improvement before making high-stakes business decisions, not a reason to label the requested sentiment code absent.
- AI-free development is not an assignment requirement. AI assistance was used for development/documentation in this work; the running sentiment classifier uses VADER and does not call a generative AI service.
- Earlier ASUS attempts encountered HTTP 403 and a consent-overlay blocker. On 2026-10-28, a fresh Selenium session on the current Dell URL also returned HTTP 403, while the shared browser page remained usable through visible controls. These are session-dependent access outcomes; the collector does not bypass them.

## Sample validation

- 171 distinct records; 171 unique primary keys.
- No missing values in the seven required columns.
- All 171 source titles are present; all review texts are non-empty.
- All dates parse and use `YYYY-MM-DD`; ratings are integers from 1 through 5.
- Star rating distribution: 1 star: 3; 2 stars: 2; 3 stars: 14; 4 stars: 31; 5 stars: 121.
- Mean rating: 4.55/5. Final sentiment: 156 Positive, 12 Negative, 3 Neutral.
- Product page displayed 172 reviews; the shared browser exposed the same 171 review cards in each of the five requested sort views. The CSV/XLSX contain those 171 deduplicated cards.

## Validation caveat (not an additional assignment deliverable)

The visible Best Buy browser page accepted all five requested sort choices and loaded 171 cards in each view with its visible Show More control until no further control appeared. Those visible records were deduplicated, validated, analyzed, and exported locally using the project's Python analysis functions. A fresh standalone Selenium run on Dell returned HTTP 403; an earlier local attempt stopped at a consent overlay without a visible Reject All control. Thus live visible-page collection and the 171-record export are verified, but a live successful run of the packaged Selenium collector itself is not.

One of the 172 reviews displayed by the listing was not available among the visible cards after pagination ended; insights describe only the 171 exported records. Check current Best Buy terms and any authorization required before redistributing review content. Do not share reviewer names unnecessarily.

## Deployment status

The Dell update was pushed to GitHub `main` as commit `204186c5267b1e0ffe53d02a1ae22d401c236c17`. GitHub Actions run 18 passed, the Streamlit dashboard rendered after the push, and the hosted endpoint returned HTTP 200 on 2026-10-28. This confirms source deployment and dashboard startup; it does not change the separate Best Buy Selenium HTTP 403 limitation.
