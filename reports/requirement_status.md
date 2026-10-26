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
| Requested sort views and Show More pagination | Met for visible-site interaction | The page exposed and accepted Most Helpful, Newest, Highest Rating, Lowest Rating, and Most Relevant. Visible pagination loaded 10, 20, 30, 40, then 50 cards. A live run of the packaged Selenium collector is not verified. |
| Required fields on every sample record | Not met | The source exposed no stable review IDs, so keys are SHA-256-derived; one card had no visible title and its title remains blank rather than being invented. The other 49 records have the requested visible fields. |
| Sentiment labels and categories | Met | VADER text polarity is preserved as `text_sentiment`; ratings of 1–2 force the final label to Negative to prevent a known VADER mismatch. The run produced 43 Positive, 5 Negative, and 2 Neutral final labels. Human validation remains advisable. |
| Genuine CSV and Excel deliverables | Met | `outputs/asus_cm14_bestbuy_reviews_sentiment.csv` and `.xlsx` contain the 50-row sample, sentiment results, insights, recommendations, and provenance. The files are git-ignored to avoid publishing reviewer names. |
| Product-specific insights and recommendations | Not met for CM14-specific claims | The listing average was 4.59/5 on 434 reviews. The 50-card sample mean is 4.50/5: 37 five-star, 7 four-star, 3 three-star, and 3 one-star. Eight sampled review texts mention CX14, seven mention Intel Celeron, six mention 64GB, only one mentions CM14, and none mention MediaTek, Kompanio, or 128GB. This mismatch prevents confidently attributing themes to the CM14 hardware; the report labels them exploratory listing-level signals. |
| Scraping constraints and stakeholder report | Met for documentation | The report documents visible-control collection, stop conditions, privacy, and non-evasion guidance. Current terms/authorization must still be checked by the user before reuse or redistribution. |
| Deployment and tested upload workflow | Met | Commit `e527bcb` is published to `main`; its GitHub Actions run passed. The hosted app analyzed a synthetic-only 50-row upload, then clearing the upload removed the old metrics and returned the app to its empty state. |

## Data validation

- 50 records and 50 unique primary keys.
- 50 non-empty review texts, dates in `YYYY-MM-DD`, ratings between 1 and 5.
- 1 missing title, left blank because no title was visible on that card.
- The review page did not expose stable review IDs; primary keys are deterministic hashes of the available public fields.
- The visible page showed 434 total reviews; only 50 were collected.
- The visible review text includes multiple references to CX14 / Intel Celeron / 64GB while the product listing is CM14 / MediaTek / 128GB. This is a listing-to-review fit limitation and must be resolved before making model-specific claims.

## Scope and external constraints

1. The sample was gathered through visible browser interactions; a live run of the packaged Selenium collector is not verified.
2. Current Best Buy terms and any required authorization for reuse or redistribution are an operator/site-owner decision. A public page and robots.txt allowance are not permission by themselves; authorization for reuse/redistribution is not independently confirmed here.
3. The site's later redirect to a one-time-passcode sign-in page was not pursued; no credentials, cookies, or access-control workarounds were used.

These are evidence and source-data limitations, not failed unit tests. A CM14-specific conclusion and an end-to-end Selenium collection are not verified; the sample is not exhaustive, and automated sentiment requires human validation.

## Recruiter-style score breakdown

| Dimension | Score | Rationale |
|---|---:|---|
| Application design and implementation | 18/20 | Complete Streamlit workflow, visible-page collector, upload validation, sentiment labels, export actions, and documented safe-stop behavior. |
| Data acquisition and field quality | 12/20 | 50 genuine visible records and pagination/sort controls were verified, but one title is unavailable, stable source IDs are absent, and review text contains cross-model references. |
| Sentiment analysis and business value | 14/20 | Sample metrics and recommendations are reproducible; VADER is heuristic and the listing-to-review model fit prevents strong product-specific conclusions. |
| Documentation and stakeholder communication | 18/20 | Notebook, requirement matrix, provenance, limitations, and recommendations are documented; current terms/authorization remain an operator/site decision. |
| Testing, reliability, and deployment | 18/20 | 23 tests passed with warnings treated as errors; notebook workflow execution, CI, and hosted upload/removal smoke checks passed. The packaged Selenium live collection was not run. |
| **Total** | **80/100** | **Strong working project with material evidence limits; not a fully validated, product-specific assessment yet.** |

The score rates demonstrated work, not the absence of external constraints. It should not be represented as a flawless or fully exhaustive scrape.
