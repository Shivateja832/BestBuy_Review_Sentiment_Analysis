import pandas as pd

from src.sentiment import analyze_sentiment, build_insights, recommendations


def test_analyze_sentiment_adds_expected_fields_and_categories():
    input_reviews = pd.DataFrame(
        {
            "review_text": [
                "Excellent quality, easy setup, I love this.",
                "Terrible, broken and disappointing.",
                "It is an item.",
            ],
            "rating": [5, 1, 3],
        }
    )
    analyzed = analyze_sentiment(input_reviews)
    assert analyzed["sentiment"].tolist() == ["Positive", "Negative", "Neutral"]
    assert analyzed["sentiment_category"].tolist() == [
        "Good Design Quality (Pos)",
        "Poor Experience (Neg)",
        "Mixed / Neutral",
    ]
    assert analyzed["sentiment_score"].between(-1, 1).all()
    assert analyzed["text_sentiment"].tolist() == ["Positive", "Negative", "Neutral"]


def test_low_rating_prevents_misleading_positive_sentiment_label():
    review = pd.DataFrame(
        {
            "review_text": [
                "I honestly do not like it. It runs super slow and constantly freezes."
            ],
            "rating": [1],
        }
    )

    analyzed = analyze_sentiment(review)

    assert analyzed.loc[0, "text_sentiment"] == "Positive"
    assert analyzed.loc[0, "sentiment"] == "Negative"
    assert analyzed.loc[0, "sentiment_category"] == "Poor Experience (Neg)"


def test_insights_are_data_derived_and_recommendations_are_nonempty():
    analyzed = analyze_sentiment(
        pd.DataFrame(
            {
                "review_text": ["Great screen quality", "Broken screen problem"],
                "rating": [5, 1],
            }
        )
    )
    insights = build_insights(analyzed)
    assert insights["review_count"] == 2
    assert insights["average_rating"] == 3.0
    assert recommendations(insights)


def test_fifty_review_sentiment_workflow_smoke_test():
    """Exercise the assignment's minimum sample through scoring and insight generation."""
    reviews = pd.DataFrame(
        [
            {
                "primary_key": f"test-{index:03}",
                "title": "Smoke-test review",
                "review_text": (
                    "Quiet washer, excellent cleaning, and easy to use."
                    if index < 35
                    else "Noisy washer, poor cleaning, and disappointing results."
                ),
                "date": "2026-01-01",
                "rating": 5 if index < 35 else 1,
                "source": "synthetic test fixture",
                "reviewer_name": "",
            }
            for index in range(50)
        ]
    )

    analyzed = analyze_sentiment(reviews)
    insights = build_insights(analyzed)

    assert len(analyzed) == 50
    assert {"sentiment_score", "sentiment", "sentiment_category"} <= set(analyzed.columns)
    assert analyzed["sentiment"].value_counts().to_dict() == {"Positive": 35, "Negative": 15}
    assert insights["review_count"] == 50
    assert insights["average_rating"] == 3.8
    assert insights["positive_share"] == 0.7
    assert insights["negative_share"] == 0.3
    assert recommendations(insights)
