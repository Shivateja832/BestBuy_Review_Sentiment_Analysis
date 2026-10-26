# Assignment Requirement Status

**Checked:** 2026-10-26
**Live sample product:** ASUS CM14 14-inch Chromebook

This report separates completed local deliverables from limitations that cannot honestly be cleared from the current evidence. The sample below came from visible Best Buy Canada review cards; it is not synthetic and does not represent every review for the product.

| Assignment requirement | Status | Evidence and limitation |
|---|---|---|
| Python application and documented notebook | Implemented | Streamlit app, Selenium/Beautiful Soup collector, sentiment module, tests, and notebook are present. The notebook now points to the sampled ASUS product and sample CSV. |
| Product with at least 50 reviews | Met | The product review page displayed 434 reviews when checked. |
| Collect at least 50 genuine reviews | Met for a sample | 50 distinct review cards were extracted from the visible Most Relevant view on 2026-10-26. This is a sample, not an exhaustive export. |
| Requested sort views and Show More pagination | Live controls verified; application end-to-end collection not independently proven | The page exposed and accepted Most Helpful, Newest, Highest Rating, Lowest Rating, and Most Relevant. Visible pagination loaded 10, 20, 30, 40, then 50 cards. These checks used the public browser UI; a successful run of the packaged Selenium collector against the live page remains unverified. |
| Required fields | Partially met; one source field was absent | All 50 records have non-empty review text, normalized dates, 1–5 ratings, Best Buy Canada source, reviewer names, and distinct deterministic primary keys. The page exposed no review IDs, so keys are SHA-256-derived. One card had no visible title; it remains blank rather than being invented. |
| Sentiment labels and categories | Implemented and run on sample | VADER text polarity is preserved as `text_sentiment`; ratings of 1–2 force the final label to Negative to prevent a known VADER mismatch. The run produced 43 Positive, 5 Negative, and 2 Neutral final labels. Human validation is still recommended. |
| Genuine CSV and Excel deliverables | Generated locally | `outputs/asus_cm14_bestbuy_reviews_sentiment.csv` and `.xlsx` contain the 50-row sample, sentiment results, insights, recommendations, and provenance. The files are git-ignored to avoid publishing reviewer names. |
| Product-specific insights and recommendations | Completed as exploratory sample findings | The sample mean rating is 4.50/5: 37 five-star, 7 four-star, 3 three-star, and 3 one-star reviews. The report summarizes observed themes and cautions against generalizing from this non-random sample. |
| Scraping constraints and stakeholder report | Implemented and updated | The report documents visible-control collection, stop conditions, privacy, and non-evasion guidance. Current terms/authorization must still be checked by the user before reuse or redistribution. |
| Deployment | Hosted app exists; latest source revision needs live redeployment verification | The URL is in the README. Verify the deployed app after the source update before relying on the new sentiment correction or default product. |

## Data validation

- 50 records and 50 unique primary keys.
- 50 non-empty review texts, dates in `YYYY-MM-DD`, ratings between 1 and 5.
- 1 missing title, left blank because no title was visible on that card.
- The review page did not expose stable review IDs; primary keys are deterministic hashes of the available public fields.
- The visible page showed 434 total reviews; only 50 were collected.

## Remaining verification

1. Confirm the current Best Buy terms and authorized use/redistribution conditions. Storefront access by itself does not establish permission for downstream use.
2. Confirm Streamlit Cloud has redeployed the latest source and verify the changed default product and sentiment labels on the hosted app.
3. If the assignment requires proving that the packaged Selenium collector itself can complete a live run, that end-to-end run still needs verification. The current 50-row sample was obtained through visible browser controls and processed locally.
4. The site's later redirect to a one-time-passcode sign-in page was not pursued; no credentials, cookies, or access-control workarounds were used.

These limitations are disclosed rather than hidden. The generated sample and project tests do not establish permission, exhaustive coverage, or correctness of every automated sentiment label.
