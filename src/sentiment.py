"""Review sentiment scoring, topic cues, and business insight generation."""

from __future__ import annotations

import re
from collections import Counter

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

NEGATIVE_WORDS = {
    "bad",
    "broken",
    "cheap",
    "disappoint",
    "fail",
    "issue",
    "poor",
    "problem",
    "return",
    "slow",
    "waste",
}
STOP_WORDS = {
    "about", "after", "again", "also", "and", "are", "because", "been", "being",
    "but", "can", "could", "did", "does", "for", "from", "get", "got", "had",
    "has", "have", "her", "here", "him", "his", "how", "its", "just", "like",
    "might", "more", "most", "not", "our", "out", "over", "really", "she", "some",
    "than", "that", "the", "their", "them", "then", "there", "they", "this",
    "too", "very", "was", "were", "what", "when", "which", "who", "will", "with",
    "would", "you", "your", "able", "all", "another", "asus", "back", "basic", "best",
    "buy", "bought", "business", "calls", "chromebook", "collected", "computer",
    "considering", "day", "days", "decent", "device", "died", "don", "ever",
    "everything", "experience", "far", "first", "four", "getting", "google", "great",
    "good", "haven", "high", "however", "item", "items", "isn", "laptop", "less",
    "look", "looking", "low", "make", "makes", "made", "many", "maybe", "month",
    "months", "much", "need", "needed", "new", "now", "old", "one", "only", "part",
    "pretty", "product", "products", "promotion", "purchased", "purchasing", "quick",
    "recommend", "review", "reviews", "right", "runs", "say", "school", "set", "sign",
    "something", "stars", "still", "student", "taken", "thank", "thanks", "thing",
    "things", "time", "today", "tried", "try", "two", "use", "used", "using", "way",
    "well", "within", "work", "works",
}


def analyze_sentiment(reviews: pd.DataFrame) -> pd.DataFrame:
    """Add VADER text polarity and a low-rating-aware sentiment category."""
    if "review_text" not in reviews.columns:
        raise ValueError("Input data must contain a review_text column.")
    result = reviews.copy()
    analyzer = SentimentIntensityAnalyzer()
    texts = result["review_text"].fillna("").astype(str)
    compound = texts.map(lambda text: analyzer.polarity_scores(text)["compound"])
    result["sentiment_score"] = compound.round(4)
    result["text_sentiment"] = compound.map(
        lambda score: "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
    )

    ratings = pd.to_numeric(result.get("rating", pd.Series(index=result.index, dtype=float)), errors="coerce")
    result["sentiment"] = result["text_sentiment"]
    result.loc[ratings.le(2), "sentiment"] = "Negative"

    def category(row: pd.Series) -> str:
        sentiment = str(row["sentiment"])
        rating = row["_rating_for_category"]
        if sentiment == "Positive" and pd.notna(rating) and rating >= 4:
            return "Good Design Quality (Pos)"
        if sentiment == "Positive" and pd.notna(rating) and rating <= 3:
            return "Satisfactory / Recommended (Pos)"
        if sentiment == "Negative" and pd.notna(rating) and rating <= 2:
            return "Poor Experience (Neg)"
        if sentiment == "Negative":
            return "Needs Review (Neg)"
        return "Mixed / Neutral"

    result["_rating_for_category"] = ratings
    result["sentiment_category"] = result.apply(category, axis=1)
    return result.drop(columns="_rating_for_category")


def top_terms(reviews: pd.DataFrame, sentiment: str, limit: int = 8) -> list[tuple[str, int]]:
    """Return frequent, interpretable words from one sentiment segment."""
    subset = reviews.loc[reviews["sentiment"] == sentiment, "review_text"].fillna("")
    words = (
        word.lower()
        for text in subset
        for word in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", str(text))
        if word.lower() not in STOP_WORDS and not word.isnumeric()
    )
    return Counter(words).most_common(limit)


def build_insights(reviews: pd.DataFrame) -> dict[str, object]:
    """Create transparent, data-derived summary statistics without causal claims."""
    if reviews.empty:
        return {
            "review_count": 0,
            "average_rating": None,
            "positive_share": 0.0,
            "negative_share": 0.0,
            "top_positive_terms": [],
            "top_negative_terms": [],
        }
    ratings = pd.to_numeric(reviews.get("rating", pd.Series(dtype=float)), errors="coerce")
    sentiment = reviews.get("sentiment", pd.Series("Neutral", index=reviews.index))
    return {
        "review_count": int(len(reviews)),
        "average_rating": round(float(ratings.mean()), 2) if ratings.notna().any() else None,
        "positive_share": round(float((sentiment == "Positive").mean()), 4),
        "negative_share": round(float((sentiment == "Negative").mean()), 4),
        "top_positive_terms": top_terms(reviews, "Positive"),
        "top_negative_terms": top_terms(reviews, "Negative"),
    }


def recommendations(insights: dict[str, object]) -> list[str]:
    """Map observed rating/sentiment patterns to cautious, testable actions."""
    actions: list[str] = []
    positives = insights["top_positive_terms"]
    negatives = insights["top_negative_terms"]
    if positives:
        actions.append(
            "Protect and reinforce strengths customers mention most often: "
            + ", ".join(term for term, _ in positives[:3])
            + ". Validate these themes against the underlying reviews."
        )
    if negatives:
        actions.append(
            "Prioritize root-cause checks for recurring negative themes: "
            + ", ".join(term for term, _ in negatives[:3])
            + ". Pair review themes with support and return data before committing resources."
        )
    rating = insights["average_rating"]
    if rating is not None and rating < 3.5:
        actions.append(
            "Investigate low-rating journeys by product variant, date, and issue theme; "
            "test a targeted fix and measure rating/recontact changes."
        )
    if not actions:
        actions.append(
            "Collect a larger, multi-sort sample and validate sentiment labels against a "
            "human-reviewed subset before making product decisions."
        )
    return actions
