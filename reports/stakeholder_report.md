# Best Buy Canada Review Sentiment Analysis

## Executive summary

A 50-review sample was collected from the visible review cards on the ASUS CM14 14-inch Chromebook review page on 2026-10-26. The page displayed 434 total reviews and a 4.59/5 listing average. The sample's mean star rating is 4.50/5: 37 five-star, 7 four-star, 3 three-star, and 3 one-star reviews. These are sample statistics, not estimates for all 434 reviews.

**Important product-match caveat:** the listing is for a CM14 with MediaTek/Kompanio and 128GB storage, while 8 of the 50 captured review texts mention CX14, 7 mention Intel Celeron, 6 mention 64GB, only 1 mentions CM14, and none mention MediaTek, Kompanio, or 128GB. Treat the dataset as a sample attached to this listing, not verified CM14-specific customer feedback. The review text most often praised screen, price/value, battery, keyboard, and memory. Low-star reviews mentioned compatibility/sign-in, camera, screen/warranty, and battery concerns; these are investigation leads, not product defect estimates.

## Collection method and scope

- Product: ASUS CM14 14-inch Chromebook, Pure Grey.
- Product URL: <https://www.bestbuy.ca/en-ca/product/asus-cm14-14-chromebook-mediatek-kompanio-540-4gb-lpddr5x-128gb-emmc-chromeos-pure-grey/19826852>
- Review-page URL: <https://www.bestbuy.ca/en-ca/product/asus-cm14-14-chromebook-mediatek-kompanio-540-4gb-lpddr5x-128gb-emmc-chromeos-pure-grey/19826852/review>
- Sort sample: Most Relevant; the public page's Most Helpful, Newest, Highest Rating, and Lowest Rating views were also selected and confirmed.
- Pagination: visible Show More interaction increased the loaded cards 10 -> 20 -> 30 -> 40 -> 50.
- Record fields: primary key, display title, `title_source`, review text, date, rating, source, reviewer name, product URL, collection sort, collection date, VADER score, raw text sentiment, final sentiment, and category.
- No stable public review ID was exposed in the visible cards. The primary key is a deterministic SHA-256 digest of the product/page and available review fields. One card had no source title; its display title is derived from the opening review sentence and `title_source` explicitly identifies that fallback.
- The live sample was captured through visible browser interactions and processed with the project's Python sentiment/export code. A successful live run of the packaged Selenium collector itself has not been demonstrated.
- A normal Best Buy search for a CX14 listing matching the review text returned HTTP 403 during the audit. No matching product page or review count could be verified, so model-specific insights must not be presented as established findings.
- The sample workbook and CSV are generated under `outputs/` and are git-ignored so reviewer names are not published in the public repository.

## Sentiment approach and results

VADER produces a text-only compound score from -1 to +1 and a `text_sentiment` label. During validation, VADER gave a positive score to a clearly one-star complaint mentioning slow performance and freezing. To avoid labeling a 1–2 star review as favorable, the final `sentiment` field applies a documented low-rating override: ratings of 1 or 2 are Negative; other reviews use the VADER threshold (>= 0.05 Positive, <= -0.05 Negative, otherwise Neutral). Both the raw text label and final label are retained for audit.

| Final sentiment | Reviews | Share |
|---|---:|---:|
| Positive | 43 | 86% |
| Negative | 5 | 10% |
| Neutral | 2 | 4% |

This rule is a transparent heuristic, not a trained product-specific model. A human-coded sample is needed before decisions, especially for mixed-language, sarcastic, or contradictory text/rating records.

## Potential drivers and recommended actions

### Satisfaction signals observed

- Screen/display quality and keyboard usability are recurring positive comments.
- Value/price, ease of setup, and suitability for basic school, browsing, and streaming tasks are also mentioned.
- Battery is a mixed theme: some customers liked runtime, while a lower-star review expected longer life.

### Dissatisfaction signals observed

- One one-star review described slow performance, freezes, software/browser incompatibility, and difficulty signing in as administrator.
- Other low-rating comments described a camera access issue and a failed screen with a warranty concern.
- One three-star review liked the value but expected better battery life.

### Recommendations

1. Review compatibility guidance and setup instructions for browser requirements, administrator access, and account configuration before purchase.
2. Check camera permission troubleshooting guidance and support resolution outcomes before attributing the issue to hardware.
3. Review screen-failure and warranty cases for recurring patterns by model/production date; do not infer a defect rate from one review.
4. Compare battery expectations in product claims with tests under common school/browsing workloads.
5. Manually code all low-star reviews and a stratified sample of other ratings, then compare human labels with VADER and the rating override.
6. Repeat collection at documented intervals and compare themes with returns, service, and support-contact data before prioritizing investment.

## Scraping constraints and safe-stop behavior

- Use only a direct Best Buy Canada product URL; the project rejects search URLs and checks robots.txt before its Selenium collection run.
- Check current terms and the applicable authorization for the intended collection and redistribution. A public product page alone does not establish permission. The terms could not be confirmed during this work.
- Respect visible consent choices. The collector only uses a visible site-provided Reject All control; if the choice is unavailable or the control remains blocked, stop.
- Do not rotate proxies, bypass CAPTCHA, use private endpoints, log in, reuse cookies, defeat rate limits, or automate around access-denied pages.
- Use bounded page counts and pauses. Stop on 403/429, CAPTCHA, access denial, sign-in/OTP redirect, changed markup, or a blocked control. Do not treat retries as a way around a block.
- The browser later redirected to an OTP sign-in page after sort interactions. No sign-in, one-time code, session cookie, or workaround was attempted.
- The packaged Selenium collector was run against the selected public page. It reached the review page, but Show More was intercepted by a OneTrust consent overlay with no visible Reject All control; it stopped without bypassing the overlay. The 50 records in this report were captured via visible browser interactions and processed locally, not by that collector run.
- Reviewer names are personal data. Keep exports access-controlled, share only when permitted, and consider anonymizing reviewer names in recruiter-facing copies.

## Deliverables and limitations

- Local review-level CSV: `outputs/asus_cm14_bestbuy_reviews_sentiment.csv`
- Local Excel workbook: `outputs/asus_cm14_bestbuy_reviews_sentiment.xlsx` (Reviews, Insights, Recommendations, Collection sheets)
- Python analysis application, visible-page Selenium collector, notebook, and tests are in the project.
- This is a 50-card sample, not a complete export of 434 reviews. One source title was unavailable and is transparently derived in the display field; review text indicates possible cross-model aggregation. Current terms and any required reuse/redistribution authorization are the operator's responsibility.
- The requirement matrix gives the project a recruiter-style evidence score of 80/100, with deductions for field/model fit, lack of a live packaged-Selenium run, and the heuristic sentiment method.
