# Assignment Requirement Status

**Checked:** 2026-10-29
**Current sample:** Dell 15.6-inch 120Hz laptop, AMD Ryzen 7 7730U, 16GB DDR4, 512GB SSD, Windows 11 Home
**Sample size:** 171 unique visible Best Buy Canada reviews across five sort views

This table evaluates the assignment requirements as written. Additional quality checks and limitations are listed separately so they are not misrepresented as extra recruiter requirements.

## Recruiter-style evaluation

**Evidence-based recruiter-style score: 94/100 under the rubric below; independent recruiter scores may differ.** This is a reasoned estimate against the stated assignment, not a recruiter-issued result or a claim that every external integration was verified.

| Area | Score | Evidence and remaining qualification |
|---|---:|---|
| Python application and scraping features | 18/20 | Selenium collection, visible sort/pagination controls, and a Beautiful Soup saved-page route are implemented. Visible browser controls were used across all five sorts. Packaged Selenium sessions were blocked or timed out, and parsing an authentic saved Best Buy page through the deployed upload flow has not been verified. |
| Review sample and required fields | 19/20 | The local deliverable has 171 unique records and all seven required fields populated. The listing displayed 172 reviews, but only 171 cards were available through visible pagination; the unavailable card was not fabricated. |
| Sentiment analysis and business findings | 18/20 | VADER labels, exploratory review themes, and recommendations are provided. There is no human-coded validation sample, so model accuracy is not measured. |
| Deliverables and documentation | 20/20 | The notebook, CSV, Excel workbook, and stakeholder/requirements reports are present locally. The current sample and reuse caveats are documented; check Best Buy's current terms before reuse or redistribution. |
| Testing, reliability, and deployment | 19/20 | The local suite passed 35/35. GitHub Actions run 24 passed for the deployed commit. GitHub `main` and the Streamlit dashboard are live, and the hosted interface shows both input routes. The saved-page parser is unit-tested, but an authentic saved Best Buy page was not processed end-to-end through the hosted app. |

| Assignment requirement | Status | Evidence |
|---|---|---|
| Use Python and a web-scraping library | **Met** | The application includes a Python Selenium/Beautiful Soup collector and sentiment-analysis modules. |
| Select a Best Buy Canada product with at least 50 reviews | **Met** | The selected listing displayed 172 reviews when checked. |
| Support the requested sort options and visible pagination | **Implemented; visible-site controls verified** | The Best Buy page exposed and accepted all five requested sorts. Normal visible Show More actions reached 171 cards in each sort before the control disappeared. A fresh packaged Selenium session returned HTTP 403 or timed out, so the browser evidence is not a successful standalone collector run. |
| Provide a supported public-page collection path when standalone Selenium is denied | **Implemented; unit-tested** | The app accepts saved Best Buy review pages captured after visible sort and pagination; Beautiful Soup parses, validates required fields, and deduplicates overlapping cards. The hosted upload controls were verified, but a real Best Buy saved page has not been processed end-to-end in the hosted app. No access-control evasion is used. |
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
- The assignment's visible sorting and pagination behavior is verified, and the 171 accessible cards are exported across all five sort views. The standalone Selenium collector is not successful in this environment. The Beautiful Soup saved-page route is implemented, unit-tested, and deployed; an authentic saved Best Buy page has not yet been uploaded and processed through the hosted UI. Do not describe the standalone Selenium session or the authentic-page fallback integration as fully verified.
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

The visible Best Buy browser page accepted all five requested sort choices and loaded 171 cards in each view with its visible Show More control until no further control appeared. Those visible records were deduplicated, validated, analyzed, and exported locally using the project's Python analysis functions. A fresh standalone Selenium run on Dell returned HTTP 403; a visible Selenium run later timed out while clicking Show More. The app provides a deployed Beautiful Soup fallback whose parser has synthetic-fixture unit coverage. The authentic saved-page upload flow remains unverified end-to-end.

One of the 172 reviews displayed by the listing was not available among the visible cards after pagination ended; insights describe only the 171 exported records. Check current Best Buy terms and any authorization required before redistributing review content. Do not share reviewer names unnecessarily.

## Deployment status

Application code commit `14f93192a88747ec0bc144df8450e2adb62b62ec` passed [GitHub Actions run 24](https://github.com/Shivateja832/BestBuy_Review_Sentiment_Analysis/actions/runs/40879454992). The score/status refresh at `b55006ccc9d304f9cad2ea04ccc1ed6a35bab7ba` passed [run 25](https://github.com/Shivateja832/BestBuy_Review_Sentiment_Analysis/actions/runs/40883110223); both are on GitHub `main`. The Streamlit Cloud app was rebooted after its first post-push start used a mismatched cached module and raised `ImportError`. After reboot and the subsequent documentation push, the deployed dashboard was reloaded and rendered with CSV and saved-HTML uploaders visible; the HTML upload control reports a 20 MB per-file limit. No authentic saved Best Buy HTML was uploaded for an end-to-end check. Fresh standalone Selenium remains subject to Best Buy's HTTP 403/timeout behavior.
