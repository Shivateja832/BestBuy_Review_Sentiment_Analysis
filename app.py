from __future__ import annotations

from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from selenium.common.exceptions import WebDriverException

from src.bestbuy_reviews import (
    REVIEW_COLUMNS,
    SORT_OPTIONS,
    ScrapeSettings,
    parse_saved_review_pages,
    scrape_reviews,
)
from src.data_io import load_review_csv
from src.sentiment import analyze_sentiment, build_insights, recommendations

DEFAULT_PRODUCT_URL = (
    "https://www.bestbuy.ca/en-ca/product/"
    "dell-15-6-120hz-laptop-amd-ryzen-7-7730u-16gb-ddr4-512gb-ssd-windows-11-home-"
    "carbon-black/19821568"
)

st.set_page_config(
    page_title="BestBuy Review Intelligence",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #f5f7fb; }
    [data-testid="stHeader"] { background: rgba(245,247,251,.92); }
    .hero { padding: 1.6rem 1.8rem; border-radius: 18px; color: white;
      background: linear-gradient(115deg,#08285b 0%,#174ea6 58%,#2869c9 100%);
      margin-bottom: 1.1rem; }
    .hero h1 { margin: 0; font-size: 2.2rem; }
    .hero p { opacity: .9; margin: .45rem 0 0; }
    [data-testid="stMetric"] { background:white; padding:1rem; border-radius:12px;
      border:1px solid #e6eaf1; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><h1>BestBuy Review Intelligence</h1>'
    "<p>Policy-aware public review collection · transparent sentiment · actionable insights</p></div>",
    unsafe_allow_html=True,
)
with st.sidebar:
    st.subheader("Data source")
    uploaded = st.file_uploader("Upload an existing review CSV", type=["csv"])
    st.caption("CSV must include review_text. Other standard fields are retained when available.")
    html_uploads = st.file_uploader(
        "Or upload browser-saved Best Buy review pages",
        type=["html", "htm"],
        accept_multiple_files=True,
        help=(
            "Use Best Buy's visible sort and Show More controls, then save the rendered "
            "review page as HTML. Upload one or more sort views; overlapping cards are "
            "deduplicated. This is a compliant fallback when a fresh Selenium session is blocked."
        ),
    )
    html_policy_confirmed = st.checkbox(
        "I am authorized to analyze these pages and checked Best Buy's current terms.",
        disabled=not bool(html_uploads),
    )
    st.divider()
    st.subheader("Optional public-page collection")
    product_url = st.text_input(
        "Direct Best Buy Canada product URL",
        value=DEFAULT_PRODUCT_URL,
    )
    sort_options = st.multiselect("Sort views to collect", SORT_OPTIONS, default=["Most Relevant"])
    max_pages = st.number_input(
        "Show More pages per sort",
        min_value=1,
        max_value=100,
        value=100,
        help="Collection stops when Best Buy has no visible Show More control. If this cap is reached while more reviews remain, the run reports an incomplete collection instead of presenting it as complete.",
    )
    pause_seconds = st.slider("Pause between page actions (seconds)", 1.0, 10.0, 2.0, 0.5)
    acknowledge = st.checkbox(
        "I checked the current terms and robots.txt and am authorized to collect this public content."
    )
    st.caption(
        "The collector selects Reject All for optional cookies when that visible site control "
        "is available. No CAPTCHA bypass, proxy rotation, login, private API, or access-control "
        "evasion; collection stops if a consent choice is unavailable or access is blocked."
    )
    if uploaded is not None or html_uploads:
        st.caption("Remove uploaded review files before starting a new public-page collection.")
    scrape_button = st.button(
        "Collect public reviews",
        type="primary",
        use_container_width=True,
        disabled=uploaded is not None or bool(html_uploads),
    )

if "reviews" not in st.session_state:
    st.session_state.reviews = pd.DataFrame(columns=REVIEW_COLUMNS)
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if uploaded is not None and html_uploads:
    st.session_state.reviews = pd.DataFrame(columns=REVIEW_COLUMNS)
    st.session_state.uploaded_file_name = "conflicting review uploads"
    st.error("Upload either a review CSV or saved HTML pages, not both.")
elif uploaded is not None:
    st.session_state.uploaded_file_name = uploaded.name
    try:
        st.session_state.reviews = load_review_csv(uploaded)
    except ValueError as exc:
        st.session_state.reviews = pd.DataFrame(columns=REVIEW_COLUMNS)
        st.error(f"Could not read the selected CSV: {exc}")
elif html_uploads:
    st.session_state.uploaded_file_name = "html:" + "|".join(
        uploaded_page.name for uploaded_page in html_uploads
    )
    if not html_policy_confirmed:
        st.session_state.reviews = pd.DataFrame(columns=REVIEW_COLUMNS)
        st.error("Confirm authorization and current terms before analyzing saved review pages.")
    else:
        try:
            st.session_state.reviews = parse_saved_review_pages(
                [
                    (uploaded_page.name, uploaded_page.getvalue())
                    for uploaded_page in html_uploads
                ],
                product_url,
            )
            st.success(
                f"Parsed {len(st.session_state.reviews):,} unique reviews from saved visible pages."
            )
        except (ValueError, PermissionError) as exc:
            st.session_state.reviews = pd.DataFrame(columns=REVIEW_COLUMNS)
            st.error(f"Could not parse saved review pages: {exc}")
elif st.session_state.uploaded_file_name is not None:
    st.session_state.reviews = pd.DataFrame(columns=REVIEW_COLUMNS)
    st.session_state.uploaded_file_name = None

if scrape_button:
    if not product_url.strip():
        st.error("Enter a direct public product URL.")
    elif not acknowledge:
        st.error("Confirm policy and authorization before collecting reviews.")
    else:
        # A failed new run must not leave a previous collection looking current.
        st.session_state.reviews = pd.DataFrame(columns=REVIEW_COLUMNS)
        st.session_state.uploaded_file_name = None
        with st.spinner("Checking robots.txt and reading public review cards…"):
            try:
                scraped = scrape_reviews(
                    ScrapeSettings(
                        product_url=product_url,
                        sort_options=tuple(sort_options),
                        max_pages_per_sort=int(max_pages),
                        pause_seconds=float(pause_seconds),
                    ),
                    policy_confirmed=acknowledge,
                )
                st.session_state.reviews = scraped
                st.success(f"Collected {len(scraped):,} unique public reviews.")
            except (ValueError, PermissionError, RuntimeError, OSError) as exc:
                st.error(
                    f"Collection stopped: {exc} Previous results were cleared to avoid "
                    "showing stale reviews. Use an authorized saved page or CSV if available."
                )
            except WebDriverException as exc:
                st.error(
                    f"Browser collection failed: {exc}. Check Chrome availability and stop if "
                    "the site is blocking access; do not bypass the block. Previous results "
                    "were cleared to avoid showing stale reviews."
                )

raw_reviews = st.session_state.reviews.copy()
if raw_reviews.empty:
    st.info(
        "Upload a review CSV, browser-saved review page HTML, or use the optional collector. "
        "No scraped data is bundled, "
        "and this app never invents review content."
    )
    st.markdown(
        "The requested product-level 50-review minimum is checked after collection. "
        "A result below 50 is reported as insufficient rather than presented as a complete sample."
    )
    st.stop()

if "review_text" not in raw_reviews:
    st.error("The input is missing the required `review_text` column.")
    st.stop()

if "data_quality_note" in raw_reviews:
    quality_notes = raw_reviews["data_quality_note"].dropna().astype(str).str.strip().unique()
    for note in quality_notes:
        if note:
            st.warning(f"Dataset qualification: {note}")
if "title_source" in raw_reviews:
    generated_title_count = int(
        raw_reviews["title_source"].eq("generated_from_review_text").sum()
    )
    if generated_title_count:
        st.info(
            f"{generated_title_count} display title(s) were derived from review text; "
            "check the title_source column before treating them as source-provided titles."
        )

raw_reviews["review_text"] = raw_reviews["review_text"].fillna("").astype(str)
raw_reviews = raw_reviews.loc[raw_reviews["review_text"].str.strip().ne("")].copy()
if raw_reviews.empty:
    st.error("The input contains no non-empty review text to analyze.")
    st.stop()

try:
    analyzed = analyze_sentiment(raw_reviews)
except (ValueError, ImportError) as exc:
    st.error(f"Sentiment analysis could not run: {exc}")
    st.stop()

insights = build_insights(analyzed)
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reviews analyzed", f"{insights['review_count']:,}")
    c2.metric(
        "Average rating",
        "N/A" if insights["average_rating"] is None else f"{insights['average_rating']:.2f} / 5",
    )
    c3.metric("Positive", f"{insights['positive_share']:.1%}")
    c4.metric("Negative", f"{insights['negative_share']:.1%}")

if insights["review_count"] < 50:
    st.warning(
        f"Only {insights['review_count']} reviews are available; the assignment's 50-review "
        "product threshold is not met."
    )
else:
    st.success("The dataset meets the minimum 50-review threshold.")

left, right = st.columns([1.3, 1])
with left:
    st.subheader("Sentiment distribution")
    counts = analyzed["sentiment"].value_counts().reindex(
        ["Positive", "Neutral", "Negative"], fill_value=0
    )
    figure, axis = plt.subplots(figsize=(6, 3.5))
    bars = axis.bar(counts.index, counts.values, color=["#2869c9", "#8b98a9", "#d84a4a"])
    axis.set_ylabel("Review count")
    axis.spines[["top", "right"]].set_visible(False)
    axis.bar_label(bars, padding=3)
    axis.set_ylim(0, max(1, int(counts.max())) * 1.15)
    figure.tight_layout()
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)
with right:
    st.subheader("Potential satisfaction drivers")
    positive_terms = insights["top_positive_terms"]
    st.write(", ".join(f"{word} ({count})" for word, count in positive_terms) or "Not enough text.")
    st.subheader("Potential dissatisfaction drivers")
    negative_terms = insights["top_negative_terms"]
    st.write(", ".join(f"{word} ({count})" for word, count in negative_terms) or "Not enough text.")

st.subheader("Recommendations to validate")
for item in recommendations(insights):
    st.markdown(f"- {item}")
st.caption(
    "VADER is a general-purpose English lexicon model, not a product-specific truth label. "
    "Review keyword counts are exploratory and do not establish causality."
)

st.subheader("Review-level results")
preferred_columns = [
    "primary_key", "title", "title_source", "review_text", "date", "rating", "source",
    "reviewer_name", "sentiment_score", "text_sentiment", "sentiment",
    "sentiment_category",
]
visible_columns = [column for column in preferred_columns if column in analyzed.columns]
st.dataframe(analyzed[visible_columns], use_container_width=True, hide_index=True)

csv_bytes = analyzed.to_csv(index=False).encode("utf-8-sig")
xlsx_buffer = BytesIO()
with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
    analyzed.to_excel(writer, index=False, sheet_name="Reviews")
    pd.DataFrame(
        [{"metric": key, "value": str(value)} for key, value in insights.items()]
    ).to_excel(writer, index=False, sheet_name="Insights")

download_left, download_right = st.columns(2)
download_left.download_button(
    "Download analyzed CSV", csv_bytes, "bestbuy_reviews_sentiment.csv", "text/csv"
)
download_right.download_button(
    "Download analyzed Excel",
    xlsx_buffer.getvalue(),
    "bestbuy_reviews_sentiment.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.caption("Exports are generated for download; review data is not saved to the server.")
