# Best Buy Canada Review Sentiment Analysis

## Executive summary

A 50-review sample was collected from the visible customer-review cards on the Best Buy Canada listing for a Dell 15.6-inch 120Hz laptop with AMD Ryzen 7 7730U, 16GB DDR4, and 512GB SSD. The page displayed 172 reviews when checked. The sample's average star rating is 4.42/5: 33 five-star, 8 four-star, 7 three-star, 1 two-star, and 1 one-star review. These are sample statistics and should not be treated as estimates for all 172 reviews.

The final text/rating-aware sentiment labels are 45 Positive, 4 Negative, and 1 Neutral. VADER is a transparent lexicon-based technique, not a trained product-specific model. Theme counts and generated recommendations are exploratory signals for follow-up, not proof of product defects or causal drivers.

## Collection method and scope

- Product: Dell 15.6-inch 120Hz laptop, AMD Ryzen 7 7730U, 16GB DDR4, 512GB SSD, Windows 11 Home, Carbon Black.
- Product URL: <https://www.bestbuy.ca/en-ca/product/dell-15-6-120hz-laptop-amd-ryzen-7-7730u-16gb-ddr4-512gb-ssd-windows-11-home-carbon-black/19821568>
- Review page: <https://www.bestbuy.ca/en-ca/product/dell-15-6-120hz-laptop-amd-ryzen-7-7730u-16gb-ddr4-512gb-ssd-windows-11-home-carbon-black/19821568/review>
- Displayed review total at collection: 172.
- Sort view used for the sample: Most Helpful. The visible page offered and accepted Most Helpful, Newest, Highest Rating, Lowest Rating, and Most Relevant.
- Pagination: ordinary visible Show More clicks were verified through 171 visible cards in each of the five requested sort views, after which Show More disappeared. The submitted sample remains the first 50 Most Helpful records.
- Required fields: primary key, source title, review text, date, rating, source, reviewer name. All 50 records passed non-empty-field checks; dates are normalized as `YYYY-MM-DD`.
- No retailer-issued review ID was exposed, so each primary key is a deterministic SHA-256 hash of available public review fields.
- The shared browser UI was used to capture the submitted 50 visible cards; the Python sentiment and export functions processed them. A separate fresh local Selenium run was not successful.
- Exports are stored locally under `outputs/` and are git-ignored to avoid publishing reviewer names and full review text.

## Sentiment approach and results

VADER produces a text-only compound score and `text_sentiment` label. The final sentiment keeps that signal while applying the documented low-rating rule: ratings of 1–2 are Negative; for other ratings, VADER thresholds classify Positive (compound >= 0.05), Negative (<= -0.05), or Neutral. Both raw text polarity and final sentiment remain in the output for audit.

| Final sentiment | Reviews | Share |
|---|---:|---:|
| Positive | 45 | 90% |
| Negative | 4 | 8% |
| Neutral | 1 | 2% |

The mean customer star rating is 4.42/5. Sentiment is not identical to star rating: it uses the review text and the documented low-rating override. A human-coded sample should be compared with the model before operational decisions, particularly for sarcasm, mixed sentiment, and language variation.

## Observed signals and recommendations

The sample's most frequent positive text terms included price, purchase, nice, screen, battery, fast, performance, and ease-related language. Negative text signals included battery/heat, returns, and performance issues. Word counts do not account for context; they identify review passages worth reading, not definitive feature rankings.

Recommendations for follow-up:

1. Review the low-star records individually and classify the issue type (battery/heat, reliability/performance, display, or other) before prioritizing engineering work.
2. Compare review signals with return reasons, support contacts, and warranty outcomes for this exact listing/model.
3. Keep value, screen quality, and performance as hypotheses for satisfaction drivers; validate them with aspect-level coding rather than keyword frequency alone.
4. Manually label a stratified subset of reviews and compare human sentiment with VADER, reporting precision/recall or agreement before using scores for decisions.
5. Repeat the sample at another time and compare themes, while noting that the first 50 Most Helpful-ordered reviews are not a random sample.

## Scraping challenges and safe handling

- Collection used a direct Best Buy Canada product review page and ordinary visible sort and Show More controls.
- The requested sort choices were available and accepted in the browser. Each sort view reached 171 visible cards using ordinary Show More controls; only the 50-record Most Helpful sample is included in the deliverables.
- A fresh Selenium session on the Dell URL returned HTTP 403; an earlier local run encountered a consent overlay without a visible Reject All control. The collector stops when it encounters a blocked/ambiguous consent control, access denial, CAPTCHA, or rate limit.
- Use a visible site-provided consent option when present. If no valid visible choice is available, stop and ask the site owner or use an authorized route.
- Use bounded page actions and respectful pauses. On transient network errors, retry only within conservative limits and stop if the site continues to deny access; do not use retries to evade a block.
- Do not rotate proxies to evade restrictions, bypass CAPTCHA, automate hidden endpoints, reuse login cookies, or defeat rate limits. These are not appropriate fixes for access denial.
- Current Best Buy terms and any authorization required for redistribution must be checked before sharing review text. Reviewer names should be handled as personal data and omitted from external summaries unless needed and permitted.

## Deliverables and limitations

- Review-level CSV: `outputs/dell_15_6_laptop_bestbuy_reviews_sentiment.csv`
- Excel workbook: `outputs/dell_15_6_laptop_bestbuy_reviews_sentiment.xlsx` (Reviews, Insights, Recommendations, and Collection sheets)
- Python Streamlit application, visible-page Selenium collector, notebook, tests, and requirement matrix are included in the project.
- This is a 50-record sample, not a full export of the 171 visible cards or the page's displayed total of 172 reviews.
- The visible-page sorting and pagination behavior is verified. The packaged Selenium collector did not complete live because Best Buy returned HTTP 403 in a fresh session; this is not hidden or reported as a successful collection.
- The former ASUS CM14 page also returned HTTP 403 in an earlier session. The current Dell sample is distinct from that superseded sample.
