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
