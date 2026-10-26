# Assignment Requirement Status

**Checked:** 2026-10-26
**Live sample product:** ASUS CM14 14-inch Chromebook
**Recruiter-style evaluation:** 80/100, evidence-based and provisional

This report separates verified application behavior from external/source-data qualifications. The sample below came from visible Best Buy Canada review cards; it is not synthetic and does not represent every review for the product.

| Assignment requirement | Status | Evidence and limitation |
|---|---|---|
| Python application and documented notebook | Met | Streamlit app, Selenium/Beautiful Soup collector, sentiment module, tests, and notebook are present. The notebook points to the sampled ASUS product and sample CSV. |
| Product with at least 50 reviews | Met | The product review page displayed 434 reviews when checked. |
| Collect at least 50 genuine reviews | Met for the stated sample deliverable | 50 distinct review cards were extracted from the visible Most Relevant view on 2026-10-26. This satisfies a 50-review sample, not an exhaustive export. |
| Requested sort views and Show More pagination | Met for the manually verified page interaction | The page exposed and accepted Most Helpful, Newest, Highest Rating, Lowest Rating, and Most Relevant. Visible pagination loaded 10, 20, 30, 40, then 50 cards. The packaged collector's live attempt reached the page but stopped before completing pagination because of the consent overlay (see next row). |
| Run the packaged Selenium collector end to end against Best Buy | Not met | A bounded live run launched local Chrome and reached the visible review page, but the next Show More click was intercepted by Best Buy's OneTrust consent overlay. The collector found no visible Reject All control and stopped safely. This exact six-page run did not complete; no bypass or consent choice was forced. |
| Required fields on every sample record, including source-provided title | Not met | 49 source titles were extracted. The remaining source card exposed no title. A display title is derived from its review text and marked `generated_from_review_text` in `title_source`, but it is not the retailer-provided title. All rows have review text, date, rating, source, reviewer name, and unique SHA-256 primary keys because no stable review IDs were exposed. |
| Sentiment labels and categories | Met | VADER text polarity is preserved as `text_sentiment`; ratings of 1–2 force the final label to Negative to prevent a known VADER mismatch. The run produced 43 Positive, 5 Negative, and 2 Neutral final labels. Human validation remains advisable. |
| Genuine CSV and Excel deliverables | Met | `outputs/asus_cm14_bestbuy_reviews_sentiment.csv` and `.xlsx` contain the 50-row sample, sentiment results, insights, recommendations, and provenance. The files are git-ignored to avoid publishing reviewer names. |
| Product-specific insights and recommendations | Not met for CM14-specific claims | The listing average was 4.59/5 on 434 reviews. The 50-card sample mean is 4.50/5: 37 five-star, 7 four-star, 3 three-star, and 3 one-star. Eight sampled review texts mention CX14, seven mention Intel Celeron, six mention 64GB, only one mentions CM14, and none mention MediaTek, Kompanio, or 128GB. This mismatch prevents confidently attributing themes to the CM14 hardware; the report labels them exploratory listing-level signals. |
| Scraping constraints and stakeholder report | Met for documentation | The report documents visible-control collection, stop conditions, privacy, and non-evasion guidance. Current terms/authorization must still be checked by the user before reuse or redistribution. |
| Deployment and tested upload workflow | Met | Commit `e7360ca` is published to `main`; GitHub Actions run #16 passed. The hosted app analyzed a synthetic-only 50-row CSV with a generated-title provenance notice and download controls; removing the file cleared the analysis and restored the empty state. |

## Data validation

- 50 records and 50 unique primary keys.
- 50 non-empty review texts, dates in `YYYY-MM-DD`, ratings between 1 and 5.
- 0 blank display titles. One source card had no title; the display title is derived from review text and `title_source` records this provenance.
- The review page did not expose stable review IDs; primary keys are deterministic hashes of the available public fields.
- The visible page showed 434 total reviews; only 50 were collected.
- The visible review text includes multiple references to CX14 / Intel Celeron / 64GB while the product listing is CM14 / MediaTek / 128GB. This is a listing-to-review fit limitation and must be resolved before making model-specific claims.

## Scope and external constraints

1. The sample was gathered through visible browser interactions. The packaged Selenium collector was run once against the product page: it reached the review page, but Show More was intercepted by `.onetrust-pc-dark-filter`; no visible Reject All control was available and the collector stopped.
2. Current Best Buy terms and any required authorization for reuse or redistribution are an operator/site-owner decision. A public page and robots.txt allowance are not permission by themselves; authorization for reuse/redistribution is not independently confirmed here.
3. The site's later redirect to a one-time-passcode sign-in page was not pursued; no credentials, cookies, or access-control workarounds were used.
4. A normal Best Buy search for a CX14 listing matching the sampled review text returned HTTP 403 during this audit. No alternative listing, review count, or replacement sample could therefore be verified.
5. `robots.txt` allowed the product route and local Chrome/Selenium started; these checks do not establish permission under the site's terms. The diagnostic set the collector's confirmation parameter only to exercise its runtime path; it did not independently confirm current terms or reuse authorization.

The title fallback resolves the blank display-field issue without pretending to recover an absent retailer title. The original source-title requirement for that one record remains not met. The live Selenium blocker is now localized: the consent overlay blocks Show More and presents no visible Reject All control to this automated browser session. The safe response is to stop; code must not click through an invisible/ambiguous consent UI. A user-provided authorized export or a visible permitted consent flow is needed for a successful pagination run. The product-to-review mismatch and authorization uncertainty are source/evidence limitations, not bugs. CM14-specific conclusions are not verified; the sample is not exhaustive, and automated sentiment requires human validation.

## Recruiter-style score breakdown

The 20-point deduction is a score gap, not 20% broken application code. It reflects missing evidence and analysis limits: the packaged collector safely stopped when a consent overlay blocked pagination without a visible reject control; Best Buy search for a matching CX14 page returned 403; the sampled review text does not consistently fit the CM14 listing; one original source title and stable source review IDs were not exposed; VADER is a heuristic without a human-labelled validation set; and current reuse authorization was not independently confirmed. A code-only change cannot honestly erase these source/evidence limits.

| Dimension | Score | Rationale |
|---|---:|---|
| Application design and implementation | 18/20 | Complete Streamlit workflow, visible-page collector, upload validation, sentiment labels, export actions, and documented safe-stop behavior. |
| Data acquisition and field quality | 12/20 | 50 genuine visible records and pagination/sort controls were verified. One display title is transparently generated because the source omitted it; stable source IDs are absent, and review text contains cross-model references that prevent confident CM14-specific analysis. |
| Sentiment analysis and business value | 14/20 | Sample metrics and recommendations are reproducible; VADER is heuristic and the listing-to-review model fit prevents strong product-specific conclusions. |
| Documentation and stakeholder communication | 18/20 | Notebook, requirement matrix, provenance, limitations, and recommendations are documented; current terms/authorization remain an operator/site decision. |
| Testing, reliability, and deployment | 18/20 | 27 tests passed with warnings treated as errors; all notebook code cells executed against the 50-row sample, CI passed, and hosted upload/removal smoke checks passed. A live Selenium run confirmed the consent-overlay safe-stop, not successful pagination. |
| **Total** | **80/100** | **Strong working project with material evidence limits; not a fully validated, product-specific assessment yet.** |

The score rates demonstrated work, not the absence of external constraints. It should not be represented as a flawless or fully exhaustive scrape.
