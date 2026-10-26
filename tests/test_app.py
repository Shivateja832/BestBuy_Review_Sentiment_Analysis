import pandas as pd
from streamlit.testing.v1 import AppTest

from src.bestbuy_reviews import REVIEW_COLUMNS


def test_dashboard_analyzes_reviews_and_renders_exports_with_dataset_note():
    reviews = pd.DataFrame(
        [
            {
                "primary_key": f"sample-{index}",
                "title": f"Review {index}",
                "review_text": "Excellent screen and easy setup."
                if index < 45
                else "Broken screen and disappointing quality.",
                "date": "2026-01-01",
                "rating": 5 if index < 45 else 1,
                "source": "synthetic integration fixture",
                "reviewer_name": "",
                "data_quality_note": "Treat as a test sample.",
            }
            for index in range(50)
        ],
        columns=REVIEW_COLUMNS + ["data_quality_note"],
    )

    app = AppTest.from_file("app.py").run(timeout=30)
    app.session_state["reviews"] = reviews
    app.run(timeout=30)

    assert not app.exception
    assert [metric.label for metric in app.metric] == [
        "Reviews analyzed",
        "Average rating",
        "Positive",
        "Negative",
    ]
    assert any("Treat as a test sample." in warning.value for warning in app.warning)
    assert len(app.get("download_button")) == 2
    assert any("meets the minimum 50-review threshold" in item.value for item in app.success)
